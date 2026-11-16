from typing import Optional, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from agents.base.registry import AgentRegistry
from agents.base.tool import ToolRegistry
from agents.graph.state import EnterpriseGraphState
from agents.graph.nodes import NodeFactory
from services.llm.ai_manager import AIManager


def route_next(state: EnterpriseGraphState) -> str:
    """
    Evaluates state['next_node'] to route execution dynamically to the next agent node,
    synthesis, or completion.
    """
    next_node = state.get("next_node")
    if not next_node or next_node in ("__end__", "end"):
        return END
    return next_node


def build_enterprise_graph(
    registry: AgentRegistry,
    tool_registry: ToolRegistry,
    ai_manager: Optional[AIManager] = None,
    checkpointer: Optional[Any] = None
):
    """
    Constructs and compiles the Enterprise Multi-Agent StateGraph.
    """
    factory = NodeFactory(registry=registry, tool_registry=tool_registry, ai_manager=ai_manager)
    workflow = StateGraph(EnterpriseGraphState)

    # 1. Add Planner / Supervisor Node
    workflow.add_node("supervisor", factory.supervisor_node)

    # 2. Add Worker Nodes for Domain Agents
    workflow.add_node("clickup", factory.create_agent_node("clickup"))
    workflow.add_node("calendar", factory.create_agent_node("calendar"))
    workflow.add_node("email", factory.create_agent_node("email"))
    workflow.add_node("knowledge", factory.create_agent_node("knowledge"))
    workflow.add_node("ai", factory.general_ai_node)

    # 3. Add Synthesis Node
    workflow.add_node("synthesis", factory.synthesis_node)

    # 4. Set Entry Point
    workflow.set_entry_point("supervisor")

    routing_destinations = {
        "clickup": "clickup",
        "calendar": "calendar",
        "email": "email",
        "knowledge": "knowledge",
        "ai": "ai",
        "synthesis": "synthesis",
        END: END
    }

    # 5. Add Conditional Edges from Supervisor
    workflow.add_conditional_edges("supervisor", route_next, routing_destinations)

    # 6. Add Conditional Edges from Worker Nodes (enabling multi-step chaining and loops)
    for worker in ["clickup", "calendar", "email", "knowledge", "ai"]:
        workflow.add_conditional_edges(worker, route_next, routing_destinations)

    # 7. Add Final Edge from Synthesis to END
    workflow.add_edge("synthesis", END)

    # 8. Compile with MemorySaver checkpointer for stateful conversation threads
    saver = checkpointer if checkpointer is not None else MemorySaver()
    compiled_app = workflow.compile(checkpointer=saver)

    return compiled_app
