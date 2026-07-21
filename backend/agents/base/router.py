from agents.base.router_agent import RouterAgent
from agents.base.models import AgentResponse

class AgentRouter:
    """
    Backward-compatible wrapper around capability-based RouterAgent.
    """
    def __init__(self):
        self._router_agent = RouterAgent()

    def route(self, message: str, model: str = "auto") -> AgentResponse:
        return self._router_agent.route(message=message, model=model)
