import json
from typing import Optional, Dict, Any

from agents.base.agent import BaseAgent
from agents.base.registry import AgentRegistry
from agents.base.tool import ToolRegistry
from agents.base.context import AgentContext
from agents.base.models import AgentRequest, AgentResponse
from services.llm.ai_manager import AIManager

from agents.clickup.agent import ClickUpAgent
from agents.calendar.agent import CalendarAgent
from agents.knowledge.agent import KnowledgeAgent
from agents.email.agent import EmailAgent


class RouterAgent:
    """
    Supervisor / Planner Agent that dynamically inspects registered agent capabilities,
    constructs multi-step execution plans for complex or single-agent requests,
    and orchestrates execution passing state via AgentContext.
    """
    def __init__(self, registry: Optional[AgentRegistry] = None, tool_registry: Optional[ToolRegistry] = None):
        self.tool_registry = tool_registry or ToolRegistry()
        self.registry = registry or AgentRegistry()
        self.ai_manager = AIManager()

        # Register default enterprise agents using the central tool registry
        self.registry.register(ClickUpAgent(tool_registry=self.tool_registry))
        self.registry.register(CalendarAgent(tool_registry=self.tool_registry))
        self.registry.register(KnowledgeAgent(tool_registry=self.tool_registry))
        self.registry.register(EmailAgent(tool_registry=self.tool_registry))

    def route(self, message: str, model: str = "auto") -> AgentResponse:
        """
        Supervisor / Planner workflow:
        1. Evaluates user request against agent capabilities.
        2. Generates a single-step or multi-step execution plan.
        3. Sequentially executes plan steps, resolving dynamic output placeholders via AgentContext.
        """
        context = AgentContext(query=message, model=model)
        agent_manifest = self.registry.get_manifest()

        prompt = f"""
You are a Principal Multi-Agent Supervisor / Planner for an Enterprise AI Assistant.
Analyze the user request and generate a sequential execution plan using the declared capabilities of registered domain agents.

Available Agents Manifest:
{json.dumps(agent_manifest, indent=2)}

User Request:
"{message}"

Rules:
1. Return ONLY a valid JSON object. No Markdown blocks, no extra text.
2. If the request requires multiple steps or agents (e.g. create a meeting AND send an email invitation, or fetch tasks AND email summary), break it down into sequential execution steps under "plan".
3. For single-agent requests, provide a single step in the "plan" array.
4. For each step, set "selected_agent" to the matching agent name, and set "action" to the exact tool "action" name declared under that agent's "tools" in the manifest.
5. In step "payload", extract parameters declared for that tool.
6. If no specialized domain agent matches the request, set "selected_agent" to "ai" and "action" to "general_chat".
7. For email steps, ALWAYS include a "body" field containing the complete email text and reference previous step outputs using placeholders like "{{step_1.meet_link}}" or "{{meeting_details.meet_link}}".
8. For each step, ALWAYS include a "description" field containing a concise, natural, user-friendly explanation of what this step is doing (e.g. "Fetching active sprint tasks from ClickUp", "Scheduling 1-hour Sprint Review on Google Calendar", "Sending invitation email").

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

        try:
            res = self.ai_manager.generate(prompt=prompt, model=model)
            raw_text = res.get("response", "") if isinstance(res, dict) else str(res)

            cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned_text)
            print(parsed)

            plan = parsed.get("plan", [])
            if not isinstance(plan, list) or len(plan) == 0:
                # Handle direct single selection format backward compatibility
                selected_agent_name = parsed.get("selected_agent", "ai")
                plan = [{
                    "step_id": 1,
                    "selected_agent": selected_agent_name,
                    "action": parsed.get("action"),
                    "payload": parsed.get("payload") or {},
                    "output_key": "step_1"
                }]

        except Exception as e:
            print(f"Supervisor/Planner evaluation warning: {e}. Falling back to knowledge/general AI.")
            return self._fallback_to_general_ai(message, model, context)

        # Execute Plan Sequentially
        responses = []
        last_source = "ai"
        
        for idx, step in enumerate(plan, start=1):
            agent_name = str(step.get("selected_agent", "ai")).lower()
            action = step.get("action")
            raw_payload = step.get("payload") or {}
            step_id = step.get("step_id", idx)
            output_key = step.get("output_key") or f"step_{step_id}"

            if action:
                raw_payload["action"] = action

            # Resolve template placeholders from shared_memory
            resolved_payload = self._resolve_placeholders(raw_payload, context)
            print("RAW PAYLOAD:", raw_payload)
            print("RESOLVED PAYLOAD:", resolved_payload)

            if agent_name == "ai":
                fallback_resp = self._fallback_to_general_ai(message, model, context)
                responses.append(fallback_resp.response_text)
                last_source = fallback_resp.source
                continue

            target_agent = self.registry.get(agent_name)
            if target_agent:
                request = AgentRequest(
                    message=message,
                    intent=agent_name,
                    payload=resolved_payload,
                    model=model
                )
                response = target_agent.execute(request, context=context)

                # Store output data in shared_memory under output_key, step_N, agent_name, and global fields
                step_output = {}
                if isinstance(response.data, dict):
                    step_output.update(response.data)
                step_output["response_text"] = response.response_text

                # Store convenient aliases for summaries and textual outputs
                if "summary" in step_output:
                    step_output["summary_text"] = step_output["summary"]
                    step_output["text"] = step_output["summary"]
                elif response.response_text:
                    step_output["summary_text"] = response.response_text
                    step_output["text"] = response.response_text

                # Store under multiple keys for bulletproof placeholder lookup
                context.set_memory(output_key, step_output)
                context.set_memory(f"step_{step_id}", step_output)
                context.set_memory(f"step_{idx}", step_output)
                context.set_memory(agent_name, step_output)

                # Also store individual top-level fields globally in shared_memory
                for k, v in step_output.items():
                    if k not in context.shared_memory:
                        context.set_memory(k, v)

                print("Context Memory set for:", [output_key, f"step_{step_id}", agent_name], "Data:", step_output)
                context.add_step(agent_name, action or "execute", details=step_output)

                responses.append(response.response_text)
                last_source = response.source
            else:
                # Fallback if specified agent isn't found
                fallback_resp = self._fallback_to_general_ai(message, model, context)
                responses.append(fallback_resp.response_text)

        combined_text = "\n\n".join(responses) if responses else "Execution completed."

        return AgentResponse(
            source=last_source if len(plan) == 1 else "supervisor",
            response_text=combined_text,
            model=model
        )

    def _resolve_placeholders(self, payload: Any, context: AgentContext) -> Any:
        """
        Recursively resolves placeholder strings like '{step_1.meet_link}', '{{meeting_details.meet_link}}',
        or '{sprint_summary.summary_text}' using values stored in context.shared_memory.
        """
        if isinstance(payload, str):
            import re
            def replace_match(match):
                full_match = match.group(0)
                path_str = match.group(1).strip()
                path = path_str.split(".")
                step_key = path[0]
                field_key = path[1] if len(path) > 1 else None

                # 1. Look up step_key in shared_memory (exact or case-insensitive)
                memory_val = context.get_memory(step_key)
                if memory_val is None:
                    for k, v in context.shared_memory.items():
                        if k.lower() == step_key.lower():
                            memory_val = v
                            break

                # 2. If memory_val is a dict and a field_key is specified
                if isinstance(memory_val, dict) and field_key:
                    val = memory_val.get(field_key)
                    if val is None:
                        for k, v in memory_val.items():
                            if k.lower() == field_key.lower():
                                val = v
                                break
                    if val is None and any(k in field_key.lower() for k in ["link", "url", "meet"]):
                        val = memory_val.get("meet_link") or memory_val.get("meetLink") or memory_val.get("link") or memory_val.get("url")
                    if val is None and any(k in field_key.lower() for k in ["summary", "text", "content", "desc", "body", "report", "response", "output", "result", "data", "message", "info"]):
                        val = memory_val.get("summary_text") or memory_val.get("summary") or memory_val.get("response_text") or memory_val.get("response") or memory_val.get("text")
                    # Fallback to response_text or summary if specific field not matched
                    if val is None:
                        val = memory_val.get("summary_text") or memory_val.get("summary") or memory_val.get("response_text")
                    if val is not None:
                        return str(val)

                # 3. If memory_val is found and no field_key was requested
                elif memory_val is not None and not field_key:
                    if isinstance(memory_val, dict):
                        return memory_val.get("summary_text") or memory_val.get("summary") or memory_val.get("response_text") or str(memory_val)
                    return str(memory_val)

                # 4. Fallback search across root shared_memory and all stored step dictionaries
                target_field = field_key or step_key
                global_val = context.get_memory(target_field)
                if global_val is not None and not isinstance(global_val, dict):
                    return str(global_val)

                for dict_key, dict_obj in context.shared_memory.items():
                    if isinstance(dict_obj, dict):
                        val = dict_obj.get(target_field)
                        if val is None:
                            for k, v in dict_obj.items():
                                if k.lower() == target_field.lower():
                                    val = v
                                    break
                        if val is None and any(k in target_field.lower() for k in ["link", "url", "meet"]):
                            val = dict_obj.get("meet_link") or dict_obj.get("meetLink") or dict_obj.get("link") or dict_obj.get("url")
                        if val is None and any(k in target_field.lower() for k in ["summary", "text", "content", "desc", "body", "report", "response", "output", "result", "data", "message", "info"]):
                            val = dict_obj.get("summary_text") or dict_obj.get("summary") or dict_obj.get("response_text") or dict_obj.get("response") or dict_obj.get("text")
                        if val is not None:
                            return str(val)

                return full_match

            # Match both single {step_1.meet_link} and double {{step_1.meet_link}} braces
            return re.sub(r"\{{1,2}([\w\.]+)\}{1,2}", replace_match, payload)
        
        elif isinstance(payload, dict):
            return {k: self._resolve_placeholders(v, context) for k, v in payload.items()}
        elif isinstance(payload, list):
            return [self._resolve_placeholders(item, context) for item in payload]
        
        return payload

    def _fallback_to_general_ai(self, message: str, model: str, context: Optional[AgentContext] = None) -> AgentResponse:
        """Fallback helper for general conversational LLM requests."""
        ai_res = self.ai_manager.generate(prompt=message, model=model)
        resp_text = ai_res.get("response", "") if isinstance(ai_res, dict) else str(ai_res)
        
        model_used = "gemini"
        if isinstance(ai_res, dict) and ai_res.get("model"):
            model_used = ai_res.get("model")
        elif model and model != "auto":
            model_used = model

        return AgentResponse(
            source="ai",
            response_text=resp_text,
            model=model_used
        )

    def _get_step_label(self, agent_name: str, action: Optional[str], step_info: Dict[str, Any]) -> str:
        """Dynamically resolves a clean, concise action name for the step."""
        if action and action != "general_chat":
            return action.replace("_", " ").title()

        desc = step_info.get("description") or step_info.get("label") or step_info.get("thought")
        if desc and isinstance(desc, str) and len(desc.strip()) < 35:
            return desc.strip()

        agent_clean = (agent_name or "AI").capitalize()
        action_clean = (action or "process").replace("_", " ").title()
        return f"{agent_clean}: {action_clean}"


    def _get_step_summary(self, agent_name: str, action: Optional[str], step_output: Dict[str, Any], response_text: str) -> str:
        """Dynamically extracts a concise outcome summary from step output without hardcoding."""
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


    def route_stream(self, message: str, model: str = "auto"):
        """
        Streaming Supervisor / Planner workflow yielding structured event dicts:
        - thinking: initial signal
        - plan_created: decomposed execution plan with labels
        - step_start: start of an agent step
        - token: token chunks
        - step_complete: completion of an agent step with summary/data
        - done: completion of the entire run
        """
        context = AgentContext(query=message, model=model)
        agent_manifest = self.registry.get_manifest()

        yield {
            "event": "thinking",
            "data": {"message": "Supervisor analyzing request and creating execution plan..."}
        }

        prompt = f"""
You are a Principal Multi-Agent Supervisor / Planner for an Enterprise AI Assistant.
Analyze the user request and generate a sequential execution plan using the declared capabilities of registered domain agents.

Available Agents Manifest:
{json.dumps(agent_manifest, indent=2)}

User Request:
"{message}"

Rules:
1. Return ONLY a valid JSON object. No Markdown blocks, no extra text.
2. If the request requires multiple steps or agents (e.g. create a meeting AND send an email invitation, or fetch tasks AND email summary), break it down into sequential execution steps under "plan".
3. For single-agent requests, provide a single step in the "plan" array.
4. For each step, set "selected_agent" to the matching agent name, and set "action" to the exact tool "action" name declared under that agent's "tools" in the manifest.
5. In step "payload", extract parameters declared for that tool.
6. If no specialized domain agent matches the request, set "selected_agent" to "ai" and "action" to "general_chat".
7. For email steps, ALWAYS include a "body" field containing the complete email text and reference previous step outputs using placeholders like "{{step_1.meet_link}}" or "{{meeting_details.meet_link}}".
8. For each step, ALWAYS include a "description" field containing a concise, natural, user-friendly explanation of what this step is doing (e.g. "Fetching active sprint tasks from ClickUp", "Scheduling 1-hour Sprint Review on Google Calendar", "Sending invitation email").

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

        try:
            res = self.ai_manager.generate(prompt=prompt, model=model)
            raw_text = res.get("response", "") if isinstance(res, dict) else str(res)
            cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned_text)

            plan = parsed.get("plan", [])
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
            print(f"Supervisor/Planner evaluation warning: {e}. Streaming fallback.")
            yield {
                "event": "plan_created",
                "data": {
                    "is_multi_step": False,
                    "steps": [{
                        "step_id": 1,
                        "agent": "ai",
                        "action": "general_chat",
                        "label": "Responding directly with AI",
                        "status": "running"
                    }]
                }
            }
            yield {
                "event": "step_start",
                "data": {
                    "step_id": 1,
                    "agent": "ai",
                    "action": "general_chat",
                    "label": "Responding directly with AI"
                }
            }
            full_content = ""
            try:
                for chunk_data in self.ai_manager.generate_stream(prompt=message, model=model):
                    token = chunk_data.get("token", "")
                    full_content += token
                    yield {
                        "event": "token",
                        "data": {"token": token}
                    }
            except Exception:
                fallback_resp = self._fallback_to_general_ai(message, model, context)
                full_content = fallback_resp.response_text
                yield {
                    "event": "token",
                    "data": {"token": full_content}
                }

            yield {
                "event": "step_complete",
                "data": {
                    "step_id": 1,
                    "agent": "ai",
                    "action": "general_chat",
                    "status": "completed",
                    "summary": "Generated response"
                }
            }
            yield {
                "event": "done",
                "data": {
                    "source": "ai",
                    "response_text": full_content,
                    "model": model,
                    "steps": [{
                        "step_id": 1,
                        "agent": "ai",
                        "action": "general_chat",
                        "status": "completed",
                        "summary": "Generated response"
                    }]
                }
            }
            return

        formatted_steps = []
        for idx, step in enumerate(plan, start=1):
            agent_name = str(step.get("selected_agent", "ai")).lower()
            action = step.get("action")
            raw_payload = step.get("payload") or {}
            step_id = step.get("step_id", idx)
            label = self._get_step_label(agent_name, action, step)
            formatted_steps.append({
                "step_id": step_id,
                "agent": agent_name,
                "action": action,
                "label": label,
                "status": "pending"
            })

        yield {
            "event": "plan_created",
            "data": {
                "is_multi_step": len(plan) > 1,
                "steps": formatted_steps
            }
        }

        responses = []
        completed_steps_meta = []
        last_source = "ai"

        for idx, step in enumerate(plan, start=1):
            agent_name = str(step.get("selected_agent", "ai")).lower()
            action = step.get("action")
            raw_payload = step.get("payload") or {}
            step_id = step.get("step_id", idx)
            output_key = step.get("output_key") or f"step_{step_id}"
            label = self._get_step_label(agent_name, action, step)

            if action:
                raw_payload["action"] = action

            yield {
                "event": "step_start",
                "data": {
                    "step_id": step_id,
                    "agent": agent_name,
                    "action": action,
                    "label": label
                }
            }

            resolved_payload = self._resolve_placeholders(raw_payload, context)

            if agent_name == "ai":
                step_text = ""
                try:
                    for chunk_data in self.ai_manager.generate_stream(prompt=message, model=model):
                        token = chunk_data.get("token", "")
                        step_text += token
                        yield {
                            "event": "token",
                            "data": {"token": token}
                        }
                except Exception:
                    fallback_resp = self._fallback_to_general_ai(message, model, context)
                    step_text = fallback_resp.response_text
                    yield {
                        "event": "token",
                        "data": {"token": step_text}
                    }

                responses.append(step_text)
                last_source = "ai"
                step_meta = {
                    "step_id": step_id,
                    "agent": "ai",
                    "action": action or "general_chat",
                    "status": "completed",
                    "summary": "Generated response",
                    "label": label
                }
                completed_steps_meta.append(step_meta)
                yield {
                    "event": "step_complete",
                    "data": step_meta
                }
                continue

            target_agent = self.registry.get(agent_name)
            if target_agent:
                request = AgentRequest(
                    message=message,
                    intent=agent_name,
                    payload=resolved_payload,
                    model=model
                )
                try:
                    response = target_agent.execute(request, context=context)
                except Exception as step_err:
                    err_msg = f"Failed to execute {agent_name}: {str(step_err)}"
                    step_meta = {
                        "step_id": step_id,
                        "agent": agent_name,
                        "action": action,
                        "status": "error",
                        "summary": err_msg,
                        "label": label
                    }
                    completed_steps_meta.append(step_meta)
                    yield {
                        "event": "step_complete",
                        "data": step_meta
                    }
                    responses.append(err_msg)
                    continue

                step_output = {}
                if isinstance(response.data, dict):
                    step_output.update(response.data)
                step_output["response_text"] = response.response_text

                if "summary" in step_output:
                    step_output["summary_text"] = step_output["summary"]
                    step_output["text"] = step_output["summary"]
                elif response.response_text:
                    step_output["summary_text"] = response.response_text
                    step_output["text"] = response.response_text

                context.set_memory(output_key, step_output)
                context.set_memory(f"step_{step_id}", step_output)
                context.set_memory(f"step_{idx}", step_output)
                context.set_memory(agent_name, step_output)

                for k, v in step_output.items():
                    if k not in context.shared_memory:
                        context.set_memory(k, v)

                context.add_step(agent_name, action or "execute", details=step_output)
                responses.append(response.response_text)
                last_source = response.source

                summary_line = self._get_step_summary(agent_name, action, step_output, response.response_text)
                step_meta = {
                    "step_id": step_id,
                    "agent": agent_name,
                    "action": action,
                    "status": "completed",
                    "summary": summary_line,
                    "label": label,
                    "data": step_output
                }
                completed_steps_meta.append(step_meta)

                yield {
                    "event": "step_complete",
                    "data": step_meta
                }

                # Yield this step's output text as a token event so user sees progress
                if response.response_text:
                    step_prefix = "\n\n" if len(responses) > 1 else ""
                    yield {
                        "event": "token",
                        "data": {"token": f"{step_prefix}{response.response_text}"}
                    }

            else:
                fallback_resp = self._fallback_to_general_ai(message, model, context)
                responses.append(fallback_resp.response_text)
                step_meta = {
                    "step_id": step_id,
                    "agent": agent_name,
                    "action": action,
                    "status": "completed",
                    "summary": "Handled with AI fallback",
                    "label": label
                }
                completed_steps_meta.append(step_meta)
                yield {
                    "event": "step_complete",
                    "data": step_meta
                }
                yield {
                    "event": "token",
                    "data": {"token": fallback_resp.response_text}
                }

        combined_text = "\n\n".join(responses) if responses else "Execution completed."
        final_source = last_source if len(plan) == 1 else "supervisor"

        yield {
            "event": "done",
            "data": {
                "source": final_source,
                "response_text": combined_text,
                "model": model,
                "steps": completed_steps_meta
            }
        }

