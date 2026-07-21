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


class RouterAgent:
    """
    Capability-based Router Agent that dynamically inspects registered agent
    capabilities and routes incoming requests using LLM evaluation without rigid intent schemas.
    """
    def __init__(self, registry: Optional[AgentRegistry] = None, tool_registry: Optional[ToolRegistry] = None):
        self.tool_registry = tool_registry or ToolRegistry()
        self.registry = registry or AgentRegistry()
        self.ai_manager = AIManager()

        # Register default enterprise agents using the central tool registry
        self.registry.register(ClickUpAgent(tool_registry=self.tool_registry))
        self.registry.register(CalendarAgent(tool_registry=self.tool_registry))
        self.registry.register(KnowledgeAgent(tool_registry=self.tool_registry))

    def route(self, message: str, model: str = "auto") -> AgentResponse:
        """
        Evaluates user prompt against dynamic agent capabilities and routes execution.
        """
        context = AgentContext(query=message, model=model)

        # 1. Retrieve current capability manifest from registry
        agent_manifest = self.registry.get_manifest()

        # 2. Construct capability evaluation prompt
        prompt = f"""
You are a Principal Router Agent for an Enterprise AI Assistant.
Analyze the user request and select the single best matching agent based on their declared capabilities.

Available Agents Manifest:
{json.dumps(agent_manifest, indent=2)}

User Request:
"{message}"

Rules:
1. Return ONLY a valid JSON object. No Markdown block, no extra text.
2. Select an agent name from the manifest ("clickup", "calendar", "knowledge") if the request matches its capabilities.
3. If the request does NOT match any agent's specialized capabilities, set "selected_agent" to "ai".
4. Extract relevant parameters into "payload" (e.g. title, status, task_name, summary, start_time, end_time, query).

JSON Format:
{{
    "selected_agent": "<agent_name or 'ai'>",
    "action": "<optional action name>",
    "payload": {{}}
}}
"""

        try:
            res = self.ai_manager.generate(prompt=prompt, model=model)
            raw_text = res.get("response", "") if isinstance(res, dict) else str(res)

            # Clean markdown JSON wrappers if present
            cleaned_text = raw_text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned_text)

            selected_agent_name = parsed.get("selected_agent", "ai")
            action = parsed.get("action")
            payload = parsed.get("payload") or {}

            if action:
                payload["action"] = action

        except Exception as e:
            print(f"RouterAgent capability evaluation warning: {e}. Falling back to knowledge/general AI.")
            selected_agent_name = "knowledge"
            payload = {}

        # 3. Dispatch to selected agent
        target_agent = self.registry.get(selected_agent_name)
        if target_agent:
            request = AgentRequest(
                message=message,
                intent=selected_agent_name,
                payload=payload,
                model=model
            )
            response = target_agent.execute(request, context=context)

            # RAG fallback check: if knowledge agent has no matching context, fallback to general AI
            if response.source == "documents" and response.response_text == "I could not find that information in the uploaded documents.":
                return self._fallback_to_general_ai(message, model, context)

            return response

        # 4. Fallback to Knowledge Base if available before general AI
        knowledge_agent = self.registry.get("knowledge")
        if knowledge_agent:
            request = AgentRequest(message=message, intent="knowledge", payload=payload, model=model)
            response = knowledge_agent.execute(request, context=context)
            if response.response_text != "I could not find that information in the uploaded documents.":
                return response

        # 5. Final General LLM Fallback
        return self._fallback_to_general_ai(message, model, context)

    def _fallback_to_general_ai(self, message: str, model: str, context: Optional[AgentContext] = None) -> AgentResponse:
        """Fallback helper for general conversational LLM requests."""
        ai_res = self.ai_manager.generate(prompt=message, model=model)
        resp_text = ai_res.get("response", "") if isinstance(ai_res, dict) else str(ai_res)
        model_used = ai_res.get("model", "gemini") if isinstance(ai_res, dict) else "gemini"

        return AgentResponse(
            source="ai",
            response_text=resp_text,
            model=model_used
        )
