import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from langchain_core.runnables import RunnableConfig

from agents.base.agent import BaseAgent
from agents.base.context import AgentContext
from agents.base.models import AgentRequest, AgentResponse
from agents.base.registry import AgentRegistry
from agents.base.tool import ToolRegistry
from agents.graph.state import EnterpriseGraphState, PlanStep
from services.llm.ai_manager import AIManager


def resolve_placeholders(payload: Any, shared_memory: Dict[str, Any]) -> Any:
    """
    Recursively resolves template placeholders like '{step_1.meet_link}',
    '{{meeting_details.meet_link}}', or '{sprint_summary.summary_text}'
    using values stored in shared_memory.
    """
    if isinstance(payload, str):
        def replace_match(match):
            full_match = match.group(0)
            path_str = match.group(1).strip()
            path = path_str.split(".")
            step_key = path[0]
            field_key = path[1] if len(path) > 1 else None

            # 1. Direct step lookup (e.g. shared_memory["step_1"]["meet_link"])
            step_data = shared_memory.get(step_key)
            if isinstance(step_data, dict) and field_key:
                val = step_data.get(field_key)
                if val is not None:
                    return str(val)
                for k, v in step_data.items():
                    if k.lower() == field_key.lower():
                        return str(v)
                if any(k in field_key.lower() for k in ["link", "url", "meet"]):
                    val = step_data.get("meet_link") or step_data.get("meetLink") or step_data.get("link") or step_data.get("url")
                    if val:
                        return str(val)
                if any(k in field_key.lower() for k in ["summary", "text", "content", "desc", "body", "report"]):
                    val = step_data.get("summary_text") or step_data.get("summary") or step_data.get("response_text") or step_data.get("text")
                    if val:
                        return str(val)

            # 2. Check if whole step_data is string
            if step_data is not None and not isinstance(step_data, dict):
                return str(step_data)

            # 3. Direct lookup in shared_memory for top-level key
            if step_key in shared_memory:
                mem_val = shared_memory[step_key]
                if isinstance(mem_val, dict) and field_key:
                    return str(mem_val.get(field_key, full_match))
                if isinstance(mem_val, dict):
                    return mem_val.get("summary_text") or mem_val.get("summary") or mem_val.get("response_text") or str(mem_val)
                return str(mem_val)

            # 4. Fallback search across root shared_memory and nested dicts
            target_field = field_key or step_key
            if target_field in shared_memory and not isinstance(shared_memory[target_field], dict):
                return str(shared_memory[target_field])

            for _, dict_obj in shared_memory.items():
                if isinstance(dict_obj, dict):
                    val = dict_obj.get(target_field)
                    if val is None:
                        for k, v in dict_obj.items():
                            if k.lower() == target_field.lower():
                                val = v
                                break
                    if val is None and any(k in target_field.lower() for k in ["link", "url", "meet"]):
                        val = dict_obj.get("meet_link") or dict_obj.get("meetLink") or dict_obj.get("link") or dict_obj.get("url")
                    if val is None and any(k in target_field.lower() for k in ["summary", "text", "content", "desc", "body", "report", "response", "output", "result", "data", "message"]):
                        val = dict_obj.get("summary_text") or dict_obj.get("summary") or dict_obj.get("response_text") or dict_obj.get("response") or dict_obj.get("text")
                    if val is not None:
                        return str(val)

            return full_match

        return re.sub(r"\{{1,2}([\w\.]+)\}{1,2}", replace_match, payload)

    elif isinstance(payload, dict):
        return {k: resolve_placeholders(v, shared_memory) for k, v in payload.items()}
    elif isinstance(payload, list):
        return [resolve_placeholders(item, shared_memory) for item in payload]
    return payload


def get_step_label(agent_name: str, action: Optional[str], step_info: Dict[str, Any]) -> str:
    """Dynamically resolves a clean, concise action label for UI display."""
    if action and action != "general_chat":
        return action.replace("_", " ").title()

    desc = step_info.get("description") or step_info.get("label") or step_info.get("thought")
    if desc and isinstance(desc, str) and len(desc.strip()) < 35:
        return desc.strip()

    agent_clean = (agent_name or "AI").capitalize()
    action_clean = (action or "process").replace("_", " ").title()
    return f"{agent_clean}: {action_clean}"


def get_step_summary(agent_name: str, action: Optional[str], step_output: Dict[str, Any], response_text: str) -> str:
    """Dynamically extracts a concise outcome summary from step output."""
    if not isinstance(step_output, dict):
        return response_text[:80] + ("..." if len(response_text) > 80 else "")

    if "summary" in step_output and isinstance(step_output["summary"], str):
        return step_output["summary"][:90]

    if "message" in step_output and isinstance(step_output["message"], str):
        return step_output["message"]

    if "meet_link" in step_output and step_output["meet_link"]:
        return f"Event scheduled. Link: {step_output['meet_link']}"

    if "tasks" in step_output and isinstance(step_output["tasks"], list):
        return f"Retrieved {len(step_output['tasks'])} items"

    if "task" in step_output and isinstance(step_output["task"], dict):
        task_name = step_output["task"].get("name", "Task")
        task_status = step_output["task"].get("status", "created")
        return f"Task '{task_name}' ({task_status})"

    if "documents" in step_output and isinstance(step_output["documents"], list):
        return f"Retrieved {len(step_output['documents'])} documents"

    first_line = response_text.strip().split("\n")[0] if response_text else "Step completed"
    return first_line[:80] + ("..." if len(first_line) > 80 else "")


class NodeFactory:
    """
    Factory creating LangGraph node functions configured with the registry and AI manager.
    Nodes support event queuing for real-time SSE streaming.
    """
    def __init__(self, registry: AgentRegistry, tool_registry: ToolRegistry, ai_manager: Optional[AIManager] = None):
        self.registry = registry
        self.tool_registry = tool_registry
        self.ai_manager = ai_manager or AIManager()

    def supervisor_node(self, state: EnterpriseGraphState, config: Optional[RunnableConfig] = None) -> Dict[str, Any]:
        """
        Supervisor / Planner node:
        Evaluates the user query against the Agent Manifest, decomposes it into
        an execution plan, and routes to the first agent node.
        """
        event_queue = config.get("configurable", {}).get("event_queue") if config else None

        if event_queue:
            event_queue.put(("thinking", {"message": "Supervisor analyzing request and creating execution plan..."}))

        query = state.get("query", "")
        model = state.get("model", "auto")
        agent_manifest = self.registry.get_manifest()
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S (%A)")

        prompt = f"""
You are a Principal Multi-Agent Supervisor / Planner for an Enterprise AI Assistant.
Analyze the user request and generate a sequential execution plan using the declared capabilities of registered domain agents.

Available Agents Manifest:
{json.dumps(agent_manifest, indent=2)}

Current System Time:
{current_time_str}

User Request:
"{query}"

Rules:
1. Return ONLY a valid JSON object. No Markdown blocks, no extra text.
2. If the request requires multiple steps or agents (e.g. create a meeting AND send an email invitation, or fetch tasks AND email summary), break it down into sequential execution steps under "plan".
3. For single-agent requests, provide a single step in the "plan" array.
4. For each step, set "selected_agent" to the matching agent name, and set "action" to the exact tool "action" name declared under that agent's "tools" in the manifest.
5. In step "payload", extract parameters declared for that tool. For "knowledge" agent ("answer_question"), set "question" in payload to the user question.
6. For ANY factual queries, domain knowledge questions, company/organization information, vision, mission, values, policies, rules, handbooks, guidelines, technical documents, or questions answered by uploaded files, ALWAYS select "knowledge" as "selected_agent" and "answer_question" as "action".
7. Only select "ai" with "general_chat" for generic social conversation, casual chit-chat, or greetings (e.g. "hi", "how are you", "who are you", "tell a joke") that are not asking for factual or organizational knowledge.
8. For email steps, ALWAYS include a "body" field containing the complete email text and reference previous step outputs using placeholders like "{{{{step_1.meet_link}}}}" or "{{{{meeting_details.meet_link}}}}".
9. For each step, ALWAYS include a "description" field containing a concise, natural, user-friendly explanation of what this step is doing.

JSON Schema:
{{
    "is_multi_step": true,
    "plan": [
        {{
            "step_id": 1,
            "selected_agent": "<agent_name>",
            "action": "<action_name from agent's tools>",
            "description": "<natural human-readable explanation of this step>",
            "payload": {{}},
            "output_key": "step_1"
        }}
    ]
}}
"""
        plan = []
        is_multi_step = False
        try:
            res = self.ai_manager.generate(prompt=prompt, model=model)
            raw_text = res.get("response", "") if isinstance(res, dict) else str(res)
            cleaned = raw_text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned)

            plan = parsed.get("plan", [])
            is_multi_step = bool(parsed.get("is_multi_step", len(plan) > 1))
            if not isinstance(plan, list) or len(plan) == 0:
                selected_agent_name = parsed.get("selected_agent", "ai")
                plan = [{
                    "step_id": 1,
                    "selected_agent": selected_agent_name,
                    "action": parsed.get("action"),
                    "payload": parsed.get("payload") or {},
                    "output_key": "step_1"
                }]
        except Exception as e:
            print(f"[LangGraph Supervisor] Planner parsing error: {e}. Defaulting to AI fallback.")
            plan = [{
                "step_id": 1,
                "selected_agent": "ai",
                "action": "general_chat",
                "description": "General AI response",
                "payload": {},
                "output_key": "step_1"
            }]
            is_multi_step = False

        # Format plan steps with labels and initial status
        formatted_plan: List[Dict[str, Any]] = []
        for idx, step in enumerate(plan, start=1):
            agent_name = str(step.get("selected_agent", "ai")).lower()
            action = step.get("action")
            step_id = step.get("step_id", idx)
            label = get_step_label(agent_name, action, step)
            formatted_plan.append({
                "step_id": step_id,
                "selected_agent": agent_name,
                "action": action,
                "description": step.get("description", label),
                "label": label,
                "payload": step.get("payload") or {},
                "output_key": step.get("output_key") or f"step_{step_id}",
                "status": "pending",
                "summary": None,
                "data": None
            })

        if event_queue:
            event_queue.put(("plan_created", {
                "is_multi_step": is_multi_step,
                "steps": [
                    {
                        "step_id": s["step_id"],
                        "agent": s["selected_agent"],
                        "action": s.get("action"),
                        "label": s.get("label"),
                        "status": "pending"
                    }
                    for s in formatted_plan
                ]
            }))

        first_agent = formatted_plan[0]["selected_agent"] if formatted_plan else "ai"
        valid_agents = {"clickup", "calendar", "email", "knowledge", "ai"}
        next_node = first_agent if first_agent in valid_agents else "ai"

        return {
            "plan": formatted_plan,
            "is_multi_step": is_multi_step,
            "current_step_index": 0,
            "shared_memory": dict(state.get("shared_memory") or {}),
            "step_history": list(state.get("step_history") or []),
            "responses": [],
            "next_node": next_node,
            "error": None
        }

    def create_agent_node(self, agent_name: str):
        """Creates a worker node for a specific registered domain agent."""
        def node_fn(state: EnterpriseGraphState, config: Optional[RunnableConfig] = None) -> Dict[str, Any]:
            event_queue = config.get("configurable", {}).get("event_queue") if config else None
            current_idx = state.get("current_step_index", 0)
            plan = list(state.get("plan") or [])
            shared_memory = dict(state.get("shared_memory") or {})
            step_history = list(state.get("step_history") or [])
            responses = list(state.get("responses") or [])
            query = state.get("query", "")
            model = state.get("model", "auto")

            if current_idx >= len(plan):
                return {
                    "next_node": "synthesis",
                    "current_step_index": current_idx
                }

            step = dict(plan[current_idx])
            action = step.get("action")
            raw_payload = dict(step.get("payload") or {})
            step_id = step.get("step_id", current_idx + 1)
            output_key = step.get("output_key") or f"step_{step_id}"
            label = step.get("label") or get_step_label(agent_name, action, step)

            if event_queue:
                event_queue.put(("step_start", {
                    "step_id": step_id,
                    "agent": agent_name,
                    "action": action,
                    "label": label
                }))

            if action:
                raw_payload["action"] = action

            resolved_payload = resolve_placeholders(raw_payload, shared_memory)

            # Build AgentContext and AgentRequest for the domain agent
            context = AgentContext(
                query=query,
                model=model,
                intent=agent_name,
                payload=resolved_payload,
                shared_memory=shared_memory,
                step_history=step_history
            )

            target_agent = self.registry.get(agent_name)
            step_output: Dict[str, Any] = {}
            response_text = ""
            source_name = agent_name

            if target_agent:
                try:
                    request = AgentRequest(
                        message=query,
                        intent=agent_name,
                        payload=resolved_payload,
                        model=model
                    )
                    resp = target_agent.execute(request, context=context)
                    response_text = resp.response_text
                    source_name = resp.source
                    if isinstance(resp.data, dict):
                        step_output.update(resp.data)
                except Exception as ex:
                    print(f"[LangGraph Node: {agent_name}] execution error: {ex}")
                    response_text = f"Error executing {agent_name} action: {str(ex)}"
                    step_output = {"error": str(ex)}
            else:
                response_text = f"Agent '{agent_name}' not found."
                step_output = {"error": response_text}

            step_output["response_text"] = response_text
            if "summary" in step_output:
                step_output["summary_text"] = step_output["summary"]
                step_output["text"] = step_output["summary"]
            elif response_text:
                step_output["summary_text"] = response_text
                step_output["text"] = response_text

            # Update shared memory
            shared_memory[output_key] = step_output
            shared_memory[f"step_{step_id}"] = step_output
            shared_memory[f"step_{current_idx + 1}"] = step_output
            shared_memory[agent_name] = step_output
            for k, v in step_output.items():
                if k not in shared_memory:
                    shared_memory[k] = v

            summary = get_step_summary(agent_name, action, step_output, response_text)

            step_status = "completed" if "error" not in step_output else "error"
            step["status"] = step_status
            step["summary"] = summary
            step["data"] = step_output
            plan[current_idx] = step

            if event_queue:
                event_queue.put(("step_complete", {
                    "step_id": step_id,
                    "agent": agent_name,
                    "action": action,
                    "status": step_status,
                    "summary": summary,
                    "data": step_output
                }))
                if response_text:
                    step_prefix = "\n\n" if len(responses) > 0 else ""
                    event_queue.put(("token", {"token": f"{step_prefix}{response_text}"}))

            step_history.append({
                "agent": agent_name,
                "action": action or "execute",
                "details": step_output
            })
            responses.append(response_text)

            next_idx = current_idx + 1
            if next_idx < len(plan):
                next_agent_name = str(plan[next_idx].get("selected_agent", "ai")).lower()
                valid_agents = {"clickup", "calendar", "email", "knowledge", "ai"}
                next_node = next_agent_name if next_agent_name in valid_agents else "ai"
            else:
                next_node = "synthesis"

            return {
                "plan": plan,
                "shared_memory": shared_memory,
                "step_history": step_history,
                "responses": responses,
                "current_step_index": next_idx,
                "source": source_name,
                "next_node": next_node,
                "last_step_data": step_output
            }

        return node_fn

    def general_ai_node(self, state: EnterpriseGraphState, config: Optional[RunnableConfig] = None) -> Dict[str, Any]:
        """Node for general conversational queries using the LLM directly."""
        event_queue = config.get("configurable", {}).get("event_queue") if config else None
        current_idx = state.get("current_step_index", 0)
        plan = list(state.get("plan") or [])
        shared_memory = dict(state.get("shared_memory") or {})
        step_history = list(state.get("step_history") or [])
        responses = list(state.get("responses") or [])
        query = state.get("query", "")
        model = state.get("model", "auto")

        step_id = current_idx + 1
        label = "Responding directly with AI"
        if current_idx < len(plan):
            step_id = plan[current_idx].get("step_id", step_id)
            label = plan[current_idx].get("label") or label

        if event_queue:
            event_queue.put(("step_start", {
                "step_id": step_id,
                "agent": "ai",
                "action": "general_chat",
                "label": label
            }))

        resp_text = ""
        model_used = model
        try:
            if event_queue:
                for chunk_data in self.ai_manager.generate_stream(prompt=query, model=model):
                    tok = chunk_data.get("token", "")
                    resp_text += tok
                    model_used = chunk_data.get("model", model_used)
                    event_queue.put(("token", {"token": tok}))
            else:
                ai_res = self.ai_manager.generate(prompt=query, model=model)
                resp_text = ai_res.get("response", "") if isinstance(ai_res, dict) else str(ai_res)
                model_used = ai_res.get("model", model) if isinstance(ai_res, dict) else model
        except Exception as e:
            try:
                ai_res = self.ai_manager.generate(prompt=query, model=model)
                resp_text = ai_res.get("response", "") if isinstance(ai_res, dict) else str(ai_res)
                model_used = ai_res.get("model", model) if isinstance(ai_res, dict) else model
                if event_queue:
                    event_queue.put(("token", {"token": resp_text}))
            except Exception as e2:
                resp_text = f"AI Error: {str(e2)}"
                if event_queue:
                    event_queue.put(("token", {"token": resp_text}))

        step_output = {"response_text": resp_text, "summary": resp_text[:90]}
        responses.append(resp_text)

        if current_idx < len(plan):
            step = dict(plan[current_idx])
            step["status"] = "completed"
            step["summary"] = resp_text[:90]
            step["data"] = step_output
            plan[current_idx] = step

        if event_queue:
            event_queue.put(("step_complete", {
                "step_id": step_id,
                "agent": "ai",
                "action": "general_chat",
                "status": "completed",
                "summary": resp_text[:90],
                "data": step_output
            }))

        next_idx = current_idx + 1
        if next_idx < len(plan):
            next_agent_name = str(plan[next_idx].get("selected_agent", "ai")).lower()
            valid_agents = {"clickup", "calendar", "email", "knowledge", "ai"}
            next_node = next_agent_name if next_agent_name in valid_agents else "ai"
        else:
            next_node = "synthesis"

        return {
            "plan": plan,
            "shared_memory": shared_memory,
            "step_history": step_history,
            "responses": responses,
            "current_step_index": next_idx,
            "source": "ai",
            "model": model_used,
            "next_node": next_node,
            "last_step_data": step_output
        }

    def synthesis_node(self, state: EnterpriseGraphState, config: Optional[RunnableConfig] = None) -> Dict[str, Any]:
        """
        Synthesis node:
        Consolidates the responses across plan steps into a coherent final response.
        """
        event_queue = config.get("configurable", {}).get("event_queue") if config else None
        responses = state.get("responses", [])
        plan = state.get("plan", [])
        is_multi_step = state.get("is_multi_step", False) or len(plan) > 1

        if not responses:
            final_text = "Task completed successfully."
        elif len(responses) == 1:
            final_text = responses[0]
        else:
            final_text = "\n\n".join(responses)

        source = "supervisor" if is_multi_step else state.get("source", "ai")
        model = state.get("model", "auto")

        if event_queue:
            formatted_steps = []
            for idx, s in enumerate(plan, start=1):
                formatted_steps.append({
                    "step_id": s.get("step_id", idx),
                    "agent": s.get("selected_agent", "ai"),
                    "action": s.get("action"),
                    "label": s.get("label"),
                    "status": s.get("status", "completed"),
                    "summary": s.get("summary"),
                    "data": s.get("data")
                })

            event_queue.put(("done", {
                "total_steps": len(plan),
                "source": source,
                "response_text": final_text,
                "model": model,
                "steps": formatted_steps
            }))

        return {
            "final_response": final_text,
            "source": source,
            "next_node": "__end__"
        }
