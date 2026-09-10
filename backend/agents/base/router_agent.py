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
4. If no specialized domain agent matches the request, set "selected_agent" to "ai".
5. In step payloads, extract parameters. For email steps, ALWAYS include a "body" field containing the complete email text and reference previous step outputs using placeholders like "{{step_1.meet_link}}" or "{{meeting_details.meet_link}}".

JSON Schema:
{{
    "is_multi_step": true,
    "plan": [
        {{
            "step_id": 1,
            "selected_agent": "<agent_name>",
            "action": "<action_name>",
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
        or '{meet_link}' using values stored in context.shared_memory.
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
                    if val is None and field_key.lower() in ["link", "url", "meeting_link", "google_meet", "meet_link", "meetlink"]:
                        val = memory_val.get("meet_link") or memory_val.get("meetLink") or memory_val.get("link") or memory_val.get("url")
                    if val is not None:
                        return str(val)

                # 3. If memory_val is found and no field_key was requested
                elif memory_val is not None and not field_key:
                    if isinstance(memory_val, dict):
                        return memory_val.get("response_text") or str(memory_val)
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
                        if val is None and target_field.lower() in ["link", "url", "meeting_link", "google_meet", "meet_link", "meetlink"]:
                            val = dict_obj.get("meet_link") or dict_obj.get("meetLink") or dict_obj.get("link") or dict_obj.get("url")
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
