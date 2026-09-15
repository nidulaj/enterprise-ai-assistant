from typing import Optional, Dict, List, Any
from agents.base.agent import BaseAgent

class AgentRegistry:
    """
    Centralized agent registry managing registered agents, capability manifests,
    and lookup services for capability-based routing.
    """
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """Register a new agent instance."""
        self._agents[agent.name] = agent

    def get(self, name: str) -> Optional[BaseAgent]:
        """Retrieve an agent by name."""
        return self._agents.get(name)

    def list_agents(self) -> List[BaseAgent]:
        """List all registered agents."""
        return list(self._agents.values())

    def get_manifest(self) -> List[Dict[str, Any]]:
        """
        Build and return a comprehensive manifest of all registered agents,
        their capabilities, and their registered executable tools with parameters.
        Used by RouterAgent for capability-based planning and structured tool selection.
        """
        manifest = []
        for agent in self._agents.values():
            tools_list = []
            if hasattr(agent, "tools_registry") and agent.tools_registry:
                agent_tools = agent.tools_registry.get_tools_by_agent(agent.name)
                tools_list = [tool.get_schema() for tool in agent_tools]

            manifest.append({
                "agent": agent.name,
                "description": agent.description,
                "capabilities": agent.capabilities,
                "tools": tools_list
            })
        return manifest

    def find_by_intent(self, intent: str) -> Optional[BaseAgent]:
        """
        Deprecated backward-compatibility lookup scanning agents for capability/intent tags.
        """
        for agent in self._agents.values():
            if intent in agent.capabilities:
                return agent
        return None