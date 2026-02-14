import logging
from typing import Dict, Optional, Type
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Central registry for agent discovery and management."""

    def __init__(self):
        """Initialize the agent registry."""
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_types: Dict[str, Type[BaseAgent]] = {}

    def register(self, agent: BaseAgent) -> None:
        """Register an agent instance.

        Args:
            agent: The agent to register
        """
        if agent.agent_name in self._agents:
            logger.warning(f"Overwriting agent {agent.agent_name}")

        self._agents[agent.agent_name] = agent
        logger.info(f"Registered agent: {agent.agent_name}")

    def register_type(self, agent_name: str, agent_class: Type[BaseAgent]) -> None:
        """Register an agent type for later instantiation.

        Args:
            agent_name: Name of the agent
            agent_class: Agent class
        """
        if agent_name in self._agent_types:
            logger.warning(f"Overwriting agent type {agent_name}")

        self._agent_types[agent_name] = agent_class
        logger.info(f"Registered agent type: {agent_name}")

    def get(self, agent_name: str) -> Optional[BaseAgent]:
        """Get a registered agent by name.

        Args:
            agent_name: Name of the agent

        Returns:
            The agent instance or None if not found
        """
        return self._agents.get(agent_name)

    def get_type(self, agent_name: str) -> Optional[Type[BaseAgent]]:
        """Get a registered agent type by name.

        Args:
            agent_name: Name of the agent type

        Returns:
            The agent class or None if not found
        """
        return self._agent_types.get(agent_name)

    def list_agents(self) -> list[str]:
        """List all registered agents.

        Returns:
            List of agent names
        """
        return list(self._agents.keys())

    def list_agent_types(self) -> list[str]:
        """List all registered agent types.

        Returns:
            List of agent type names
        """
        return list(self._agent_types.keys())

    async def initialize_all(self) -> None:
        """Initialize all registered agents."""
        for agent in self._agents.values():
            try:
                await agent.initialize()
            except Exception as e:
                logger.error(f"Failed to initialize agent {agent.agent_name}: {str(e)}")

    async def shutdown_all(self) -> None:
        """Shutdown all registered agents."""
        for agent in self._agents.values():
            try:
                await agent.shutdown()
            except Exception as e:
                logger.error(f"Failed to shutdown agent {agent.agent_name}: {str(e)}")

    async def health_check_all(self) -> Dict[str, dict]:
        """Perform health check on all agents.

        Returns:
            Dictionary mapping agent names to health check results
        """
        results = {}

        for name, agent in self._agents.items():
            try:
                results[name] = await agent.health_check()
            except Exception as e:
                results[name] = {
                    "agent_name": name,
                    "status": "error",
                    "error": str(e),
                }

        return results

    def unregister(self, agent_name: str) -> Optional[BaseAgent]:
        """Unregister an agent.

        Args:
            agent_name: Name of the agent to unregister

        Returns:
            The unregistered agent or None if not found
        """
        agent = self._agents.pop(agent_name, None)

        if agent:
            logger.info(f"Unregistered agent: {agent_name}")

        return agent

    def unregister_type(self, agent_name: str) -> Optional[Type[BaseAgent]]:
        """Unregister an agent type.

        Args:
            agent_name: Name of the agent type to unregister

        Returns:
            The unregistered agent class or None if not found
        """
        agent_type = self._agent_types.pop(agent_name, None)

        if agent_type:
            logger.info(f"Unregistered agent type: {agent_name}")

        return agent_type
