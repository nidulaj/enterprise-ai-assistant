from abc import ABC, abstractmethod
from typing import List, Optional
from agents.base.models import AgentRequest, AgentResponse
from agents.base.context import AgentContext
from agents.base.tool import ToolRegistry

class BaseAgent(ABC):
    """
    Abstract base class for all enterprise assistant agents.
    Declares capabilities, accepts a central ToolRegistry, and executes with AgentContext.
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

    @abstractmethod
    def execute(self, request: AgentRequest, context: Optional[AgentContext] = None) -> AgentResponse:
        """
        Execute agent logic using the standardized request and execution context.
        """
        pass