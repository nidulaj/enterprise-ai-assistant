from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from agents.base.models import AgentRequest, AgentResponse
from agents.base.context import AgentContext
from agents.base.tool import Tool, ToolRegistry

class BaseAgent(ABC):
    """
    Abstract base class for all enterprise assistant agents.
    Declares capabilities, accepts a central ToolRegistry, and executes with AgentContext.
    Provides dynamic tool resolution and automated schema binding.
    """
    name: str
    description: str
    capabilities: List[str] = []

    def __init__(self, tool_registry: Optional[ToolRegistry] = None):
        self.tools_registry = tool_registry or ToolRegistry()
        self.register_tools()

    @abstractmethod
    def register_tools(self) -> None:
        """
        Abstract method where child agents register tools into `self.tools_registry`
        using `self.tools_registry.register(Tool(...), agent_name=self.name)`.
        """
        pass

    def get_my_tools(self) -> List[Tool]:
        """Return all tools registered under this agent's name."""
        return self.tools_registry.get_tools_by_agent(self.name)

    def resolve_tool(self, action_name: Optional[str] = None, message_hint: Optional[str] = None) -> Optional[Tool]:
        """
        Dynamically resolve an action string or message hint to one of this agent's registered tools.
        Supports exact match, normalized slug match, substring match, and rapidfuzz semantic matching.
        """
        agent_tools = self.get_my_tools()
        if not agent_tools:
            return None

        # 1. Exact match on tool name
        if action_name:
            clean_action = str(action_name).strip()
            for tool in agent_tools:
                if tool.name.lower() == clean_action.lower():
                    return tool

            # 2. Normalized slug match (e.g. "Create Task" or "create-task" -> "create_task")
            norm_action = clean_action.lower().replace("-", "_").replace(" ", "_")
            for tool in agent_tools:
                if tool.name.lower() == norm_action:
                    return tool

            # 3. Substring match (e.g. "Create new project tasks" contains "create_task" concepts)
            for tool in agent_tools:
                t_lower = tool.name.lower()
                if t_lower in norm_action or norm_action in t_lower:
                    return tool

            # 4. Fuzzy match against tool names and descriptions
            try:
                from rapidfuzz import process, fuzz
                tool_candidates = {t.name: t for t in agent_tools}
                # Check match against tool names
                best_match = process.extractOne(
                    clean_action,
                    list(tool_candidates.keys()),
                    scorer=fuzz.WRatio,
                    score_cutoff=60
                )
                if best_match:
                    return tool_candidates[best_match[0]]
            except Exception:
                pass

        # 5. Fallback: inspect user message against tool names
        if message_hint:
            try:
                from rapidfuzz import process, fuzz
                tool_candidates = {t.name: t for t in agent_tools}
                best_match = process.extractOne(
                    message_hint,
                    list(tool_candidates.keys()),
                    scorer=fuzz.partial_ratio,
                    score_cutoff=70
                )
                if best_match:
                    return tool_candidates[best_match[0]]
            except Exception:
                pass

        return None

    def execute_dynamic_tool(self, tool_name: str, payload: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """
        Dynamically call a registered tool, filtering payload and kwargs to match
        the tool function's accepted parameters.
        """
        tool = self.tools_registry.get(tool_name)
        if not tool:
            raise KeyError(f"Tool '{tool_name}' not found for agent '{self.name}'.")

        accepted_params = set(tool.get_parameters())
        combined_args = dict(payload or {})
        combined_args.update(kwargs)

        # Filter to accepted parameters
        filtered_args = {k: v for k, v in combined_args.items() if k in accepted_params}

        return self.tools_registry.execute_tool(tool.name, **filtered_args)

    @abstractmethod
    def execute(self, request: AgentRequest, context: Optional[AgentContext] = None) -> AgentResponse:
        """
        Execute agent logic using the standardized request and execution context.
        """
        pass