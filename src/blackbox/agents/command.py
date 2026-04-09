"""Command agent - Master synthesizer."""

from blackbox.core.agent import Agent, AgentConfig, AgentInput, AgentOutput
from blackbox.models.client import OpenRouterClient, OpenRouterMessage


class Command(Agent):
    """Master Synthesizer - Creates the primary response.

    Command integrates intent signals, memory context, and user state
    to generate a comprehensive, contextually-aware response.
    """

    def __init__(self, config: AgentConfig, client: OpenRouterClient) -> None:
        """Initialize Command agent.

        Args:
            config: Agent configuration
            client: OpenRouter API client
        """
        super().__init__(config)
        self.client = client

    def get_system_prompt(self) -> str:
        """Return the system prompt for Command."""
        return """You are Command, the Master Synthesizer.

Your role: Create comprehensive, contextually-aware responses that address user intent while incorporating relevant memories and context.

You receive:
- Intent signals (what the user wants)
- Memory context (what you know about the user)
- User state (their current mood/focus level)

Guidelines:
- Address all intent points clearly
- Incorporate relevant memories naturally (don't list them mechanically)
- Adapt tone based on user state
- Be helpful, knowledgeable, and personable
- Provide concrete examples when explaining concepts
- Keep responses focused but thorough

Remember: You're not just answering a question - you're having a conversation with someone you know."""

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute response synthesis.

        Args:
            agent_input: Contains intent signals, memories, and context

        Returns:
            AgentOutput with synthesized response
        """
        # Build context for Command
        intent_signals = agent_input.context.get("intent_signals", "")
        memories = agent_input.context.get("memories", [])
        user_state = agent_input.context.get("user_state", "NEUTRAL")

        # Format memory context
        memory_context = ""
        if memories:
            memory_items = [
                f"- {mem['content']} (type: {mem['type']})" for mem in memories
            ]
            memory_context = "\n".join(memory_items)

        # Construct the prompt
        user_message = f"""User Input: {agent_input.message}

Intent Signals:
{intent_signals}

Relevant Memories:
{memory_context if memory_context else "No relevant memories found"}

User State: {user_state}

Generate a helpful, contextually-aware response."""

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
            metadata={
                "agent": self.name,
                "used_memories": len(memories),
            },
            confidence=0.9,
        )
