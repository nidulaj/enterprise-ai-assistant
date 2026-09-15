import inspect
from typing import Callable, Any, Optional, List, Dict
from pydantic import BaseModel, Field

def extract_callable_parameters(func: Callable[..., Any]) -> List[str]:
    """Dynamically inspect a callable to extract argument names."""
    try:
        sig = inspect.signature(func)
        return [
            p.name for p in sig.parameters.values()
            if p.name not in ("self", "cls") and p.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY
            )
        ]
    except Exception:
        return []

class Tool(BaseModel):
    """
    Standardized tool wrapper containing function callable, metadata descriptions,
    parameter schemas, and agent ownership attributes.
    """
    name: str = Field(description="Unique identifier name of the tool.")
    description: str = Field(description="Detailed description of tool capability for planners and routers.")
    func: Callable[..., Any] = Field(description="Python executable function implementation.")
    parameters: Optional[List[str]] = Field(default=None, description="Explicit parameter names accepted by the tool.")
    args_schema: Optional[Any] = Field(default=None, description="Pydantic parameter validation model.")
    agent_name: Optional[str] = Field(default=None, description="Owner agent name registered with this tool.")

    def get_parameters(self) -> List[str]:
        """Return parameters list either explicitly provided or dynamically inspected."""
        if self.parameters is not None:
            return self.parameters
        return extract_callable_parameters(self.func)

    def get_schema(self) -> Dict[str, Any]:
        """Export clean structured metadata for planner models."""
        return {
            "action": self.name,
            "description": self.description,
            "parameters": self.get_parameters()
        }

class ToolRegistry:
    """
    Production-grade centralized tool registry enabling global tool discovery,
    agent-scoped retrieval, schema exports, and dynamic tool invocation.
    """
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool, agent_name: Optional[str] = None) -> None:
        """Register a tool into the global registry with optional agent ownership."""
        if agent_name:
            tool.agent_name = agent_name
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        """Retrieve a registered tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        """List all tools currently registered."""
        return list(self._tools.values())

    def get_tools_by_agent(self, agent_name: str) -> List[Tool]:
        """Retrieve all tools owned by a specific agent."""
        return [tool for tool in self._tools.values() if tool.agent_name == agent_name]

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name with keyword arguments."""
        tool = self.get(tool_name)
        if not tool:
            raise KeyError(f"Tool '{tool_name}' is not registered in ToolRegistry.")
        return tool.func(**kwargs)

    def get_manifest(self) -> List[Dict[str, Any]]:
        """Export tool descriptions as a structured manifest for Planner agents."""
        return [tool.get_schema() for tool in self._tools.values()]

