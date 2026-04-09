"""Sieve agent - Intent distillation."""

from blackbox.core.agent import Agent, AgentConfig, AgentInput, AgentOutput
from blackbox.models.client import OpenRouterClient, OpenRouterMessage


class Sieve(Agent):
    """Intent Distiller - Extracts core intent signals from user input.

    The Sieve analyzes user messages and distills them into high-density
    intent signals, stripping away fluff and ambiguity. This reduces cognitive
    load for downstream agents.
    """

    def __init__(self, config: AgentConfig, client: OpenRouterClient) -> None:
        """Initialize Sieve agent.

        Args:
            config: Agent configuration
            client: OpenRouter API client
        """
        super().__init__(config)
        self.client = client

    def get_system_prompt(self) -> str:
        """Return the system prompt for Sieve."""
        return """You are Sieve, the Intent Distiller.

Your role: Extract the core intent from user messages with maximum clarity and minimum words.

Output format:
- List 2-5 bullet points capturing what the user wants
- Be specific and actionable
- Note any relevant context (e.g., "user has some background knowledge")
- Strip filler words, pleasantries, and ambiguity

Example:
Input: "Hey, I was wondering if you could help me understand how neural networks work? I've been reading about them but I'm confused about backpropagation."

Output:
- Explain neural networks fundamentals
- Clarify backpropagation mechanism
- User has some background knowledge

Keep it concise. Do not elaborate or answer the question - just distill the intent."""

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute intent distillation.

        Args:
            agent_input: Contains user message

        Returns:
            AgentOutput with distilled intent signals
        """
        messages = [
            OpenRouterMessage(role="system", content=self.get_system_prompt()),
            OpenRouterMessage(role="user", content=agent_input.message),
        ]

        result = await self.client.chat_completion(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        return AgentOutput(
            result=result,
            metadata={"agent": self.name},
            confidence=0.95,
        )
