import queue
import threading
from typing import Any, Dict, Generator, Optional

from agents.base.models import AgentResponse
from agents.base.registry import AgentRegistry
from agents.base.tool import ToolRegistry
from agents.calendar.agent import CalendarAgent
from agents.clickup.agent import ClickUpAgent
from agents.email.agent import EmailAgent
from agents.knowledge.agent import KnowledgeAgent
from agents.graph.graph import build_enterprise_graph
from services.llm.ai_manager import AIManager


class LangGraphOrchestrator:
    """
    Production-grade multi-agent orchestrator driven by LangGraph.
    Provides stateful graph execution, checkpointer-backed session persistence,
    and real-time Server-Sent Events (SSE) streaming for the Next.js ThoughtStream UI.
    """
    def __init__(
        self,
        registry: Optional[AgentRegistry] = None,
        tool_registry: Optional[ToolRegistry] = None,
        ai_manager: Optional[AIManager] = None
    ):
        self.tool_registry = tool_registry or ToolRegistry()
        self.registry = registry or AgentRegistry()
        self.ai_manager = ai_manager or AIManager()

        # Register default enterprise agents
        self.registry.register(ClickUpAgent(tool_registry=self.tool_registry))
        self.registry.register(CalendarAgent(tool_registry=self.tool_registry))
        self.registry.register(KnowledgeAgent(tool_registry=self.tool_registry))
        self.registry.register(EmailAgent(tool_registry=self.tool_registry))

        # Build and compile LangGraph state graph
        self.app = build_enterprise_graph(
            registry=self.registry,
            tool_registry=self.tool_registry,
            ai_manager=self.ai_manager
        )

    def route(self, message: str, model: str = "auto", thread_id: Optional[str] = None) -> AgentResponse:
        """
        Synchronous graph execution.
        Runs the full LangGraph pipeline to completion and returns standard AgentResponse.
        """
        initial_state = {
            "query": message,
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "shared_memory": {},
            "step_history": [],
            "responses": [],
            "current_step_index": 0
        }

        config = {
            "configurable": {
                "thread_id": thread_id or "default_session"
            }
        }

        final_state = self.app.invoke(initial_state, config=config)

        source = final_state.get("source", "ai")
        response_text = final_state.get("final_response", "Execution completed.")
        last_step_data = final_state.get("last_step_data")

        # For single agent runs that returned structured data, preserve it in response.data
        data = None
        if isinstance(last_step_data, dict):
            data = last_step_data
        elif final_state.get("shared_memory"):
            # Provide root shared memory if present
            data = final_state.get("shared_memory")

        return AgentResponse(
            source=source,
            response_text=response_text,
            data=data,
            model=final_state.get("model", model)
        )

    def route_stream(
        self,
        message: str,
        model: str = "auto",
        thread_id: Optional[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Streaming graph execution generator yielding structured event dicts:
        - thinking: initial signal
        - plan_created: decomposed execution plan
        - step_start: start of an agent step
        - token: token chunks for direct LLM completions
        - step_complete: completion of an agent step with summary/data
        - done: completion of the entire run
        """
        event_queue = queue.Queue()
        execution_error: Dict[str, Any] = {}

        config = {
            "configurable": {
                "thread_id": thread_id or "default_session",
                "event_queue": event_queue
            }
        }

        initial_state = {
            "query": message,
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "shared_memory": {},
            "step_history": [],
            "responses": [],
            "current_step_index": 0
        }

        def run_graph():
            try:
                self.app.invoke(initial_state, config=config)
            except Exception as e:
                execution_error["error"] = e
            finally:
                event_queue.put(None)

        worker_thread = threading.Thread(target=run_graph, daemon=True)
        worker_thread.start()

        # Yield events as they are produced by nodes in real time
        has_emitted_done = False
        while True:
            try:
                item = event_queue.get(timeout=0.1)
                if item is None:
                    break
                event_name, event_data = item
                if event_name == "done":
                    has_emitted_done = True
                yield {
                    "event": event_name,
                    "data": event_data
                }
            except queue.Empty:
                if not worker_thread.is_alive():
                    # Check if there are any remaining items in queue
                    try:
                        while True:
                            remaining = event_queue.get_nowait()
                            if remaining is None:
                                break
                            event_name, event_data = remaining
                            if event_name == "done":
                                has_emitted_done = True
                            yield {
                                "event": event_name,
                                "data": event_data
                            }
                    except queue.Empty:
                        break
                    break

        worker_thread.join()

        if "error" in execution_error:
            err = execution_error["error"]
            print(f"[LangGraph Stream] Execution exception: {err}")
            yield {
                "event": "error",
                "data": {"error": str(err)}
            }
            if not has_emitted_done:
                yield {
                    "event": "done",
                    "data": {"total_steps": 1, "source": "ai", "response_text": str(err), "model": model}
                }
        elif not has_emitted_done:
            yield {
                "event": "done",
                "data": {"total_steps": 1, "source": "supervisor", "response_text": "Completed.", "model": model}
            }

