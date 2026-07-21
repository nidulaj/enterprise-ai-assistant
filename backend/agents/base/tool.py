from typing import Callable, Any, Optional, List, Dict
from pydantic import BaseModel, Field

class Tool(BaseModel):
    """
    Standardized tool wrapper containing function callable, metadata descriptions,
    and agent ownership attributes.
    """
    name: str = Field(description="Unique identifier name of the tool.")
    description: str = Field(description="Detailed description of tool capability for planners and routers.")
    func: Callable[..., Any] = Field(description="Python executable function implementation.")
    args_schema: Optional[Any] = Field(default=None, description="Pydantic parameter validation model.")
    agent_name: Optional[str] = Field(default=None, description="Owner agent name registered with this tool.")

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
        manifest = []
        for tool in self._tools.values():
            manifest.append({
                "name": tool.name,
                "description": tool.description,
                "agent_name": tool.agent_name
            })
        return manifest
