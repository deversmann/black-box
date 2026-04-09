"""Base agent abstraction for Black Box Swarm."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


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

    @abstractmethod
    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute the agent's primary function.

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
