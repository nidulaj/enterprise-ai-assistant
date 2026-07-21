from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AgentContext(BaseModel):
    """
    State-conscious execution context for agent interactions, multi-agent workflows,
    shared memory, and graph execution (LangGraph readiness).
    """
    query: str = Field(description="The original user query or prompt.")
    model: str = Field(default="auto", description="The requested LLM model provider.")
    intent: Optional[str] = Field(default=None, description="Optional detected intent or action tag.")
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Extracted payload or parameters.")
    shared_memory: Dict[str, Any] = Field(default_factory=dict, description="Shared memory layer across agents and tools.")
    step_history: List[Dict[str, Any]] = Field(default_factory=list, description="Audit log of agent execution steps.")

    def get_memory(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the shared memory layer."""
        return self.shared_memory.get(key, default)

    def set_memory(self, key: str, value: Any) -> None:
        """Store a value in the shared memory layer."""
        self.shared_memory[key] = value

    def add_step(self, agent_name: str, action: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Record an execution step in step_history."""
        self.step_history.append({
            "agent": agent_name,
            "action": action,
            "details": details or {}
        })
