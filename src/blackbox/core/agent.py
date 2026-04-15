"""Base agent abstraction for Black Box Swarm."""

import time
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field

from blackbox.core.logging import get_logger


class AgentConfig(BaseModel):
    """Configuration for an individual agent."""

    name: str
    model: str  # e.g., "openai/gpt-5.4-nano"
    temperature: float = 0.7
    max_tokens: int = 500
    timeout: int = 30  # seconds


class AgentInput(BaseModel):
    """Standardized input to agents."""

    message: str
    context: dict[str, Any] = Field(default_factory=dict)


class AgentOutput(BaseModel):
    """Standardized output from agents."""

    result: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0


class Agent(ABC):
    """Base class for all swarm agents."""

    def __init__(self, config: AgentConfig) -> None:
        """Initialize the agent with configuration.

        Args:
            config: Agent configuration parameters
        """
        self.config = config
        self.name = config.name
        self.logger = get_logger(f"blackbox.agents.{self.name.lower()}")

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute the agent's primary function with logging.

        This wrapper method handles timing and logging. Agents should
        implement _execute_impl() instead of overriding this method.

        Args:
            agent_input: Standardized input containing message and context

        Returns:
            AgentOutput containing result, metadata, and confidence
        """
        start_time = time.perf_counter()

        # Log agent execution start
        self.logger.info(
            f"{self.name} agent execution started",
            extra={
                "event_type": "agent_execution_start",
                "data": {
                    "agent": self.name,
                    "input_length": len(agent_input.message),
                    "context_keys": list(agent_input.context.keys()),
                },
            },
        )

        # Execute agent-specific logic
        output = await self._execute_impl(agent_input)

        # Calculate execution time
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Log agent execution completion
        self.logger.info(
            f"{self.name} agent execution completed",
            extra={
                "event_type": "agent_execution_complete",
                "data": {
                    "agent": self.name,
                    "duration_ms": round(duration_ms, 2),
                    "output_length": len(output.result),
                    "confidence": output.confidence,
                    "metadata_keys": list(output.metadata.keys()),
                },
            },
        )

        return output

    @abstractmethod
    async def _execute_impl(self, agent_input: AgentInput) -> AgentOutput:
        """Execute the agent's primary function (implementation).

        Agents should implement this method instead of execute().

        Args:
            agent_input: Standardized input containing message and context

        Returns:
            AgentOutput containing result, metadata, and confidence
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent.

        Returns:
            System prompt string defining the agent's role and behavior
        """
        pass
