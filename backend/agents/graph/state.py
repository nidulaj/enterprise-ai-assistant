from typing import Annotated, Any, Dict, List, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class PlanStep(TypedDict, total=False):
    step_id: int
    selected_agent: str
    action: Optional[str]
    description: Optional[str]
    label: Optional[str]
    payload: Dict[str, Any]
    output_key: str
    status: str  # "pending" | "running" | "completed" | "error"
    summary: Optional[str]
    data: Optional[Dict[str, Any]]
    error: Optional[str]

class EnterpriseGraphState(TypedDict, total=False):
    """
    Core state for the Enterprise Multi-Agent LangGraph workflow.
    Tracks query, conversation messages, decomposed plan, execution steps,
    shared memory layer, and synthesis responses.
    """
    messages: Annotated[list, add_messages]
    query: str
    model: str
    is_multi_step: bool
    plan: List[Dict[str, Any]]
    current_step_index: int
    shared_memory: Dict[str, Any]
    step_history: List[Dict[str, Any]]
    responses: List[str]
    final_response: str
    source: str
    error: Optional[str]
    next_node: Optional[str]

