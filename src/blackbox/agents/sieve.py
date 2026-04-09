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

You receive:
- Recent conversation (last 2-3 messages for context)
- Current user message

Output format:
- List 2-5 bullet points capturing what the user wants
- Be specific and actionable
- If current message refers to previous context ("it", "that", "what about X"), incorporate that context
- Note any relevant context (e.g., "user has some background knowledge", "follow-up to previous question")
- Strip filler words, pleasantries, and ambiguity

Example with context:
Recent: User asked about "How do decorators work?"
Current: "What about error handling?"

Output:
- Explain error handling for Python decorators
- Follow-up to previous decorator question

Keep it concise. Do not elaborate or answer the question - just distill the intent."""

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute intent distillation.

        Args:
            agent_input: Contains user message and optional recent conversation

        Returns:
            AgentOutput with distilled intent signals
        """
        # Format recent conversation context if provided
        recent_conversation = agent_input.context.get("recent_conversation", [])
        context_str = ""

        if recent_conversation:
            context_lines = []
            for msg in recent_conversation:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                # Truncate long messages
                if len(content) > 100:
                    content = content[:100] + "..."
                context_lines.append(f"{role.capitalize()}: {content}")
            context_str = f"\nRecent conversation:\n" + "\n".join(context_lines) + "\n"

        user_message = f"""{context_str}
Current message: {agent_input.message}

Distill the intent."""

        messages = [
            OpenRouterMessage(role="system", content=self.get_system_prompt()),
            OpenRouterMessage(role="user", content=user_message),
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
