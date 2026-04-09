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
        return """You're talking to someone you know. Be natural, brief, and conversational.

What you know about them:
- Their intent (what they're asking about)
- Past context/memories
- Their current mood

How to respond:
- **Keep it SHORT** - 3-4 sentences max for simple questions
- Use everyday language, not textbook language
- If they want more detail, they'll ask "tell me more" or "can you explain X"
- Don't lecture. Don't list things unless asked.
- If a topic is big, give the key point + offer to expand: "Want me to explain how X works?"

CRITICAL: You have a ~300 word limit. Always finish your thought. If you can't cover everything briefly, say so and ask what they want to focus on.

Bad: "Python decorators are functions that modify the behavior of other functions. They use the @ syntax. Here are several examples: [lists 5 examples with code]..."

Good: "Decorators let you modify functions. Think of them like wrappers - you put @something above a function to add behavior. Want to see a quick example?"

You're chatting, not teaching a class."""

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
        verdict_feedback = agent_input.context.get("verdict_feedback", "")
        conversation_history = agent_input.context.get("conversation_history", [])

        # Format memory context
        memory_context = ""
        if memories:
            memory_items = [
                f"- {mem['content']} (type: {mem['type']})" for mem in memories
            ]
            memory_context = "\n".join(memory_items)

        # Format conversation history (sliding window)
        history_context = ""
        if conversation_history:
            history_lines = []
            for msg in conversation_history:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                # Truncate very long messages
                if len(content) > 150:
                    content = content[:150] + "..."
                history_lines.append(f"{role.capitalize()}: {content}")
            history_context = "\n".join(history_lines)

        # Construct the prompt - Context Sandwich Structure:
        # 1. System Prompt (already sent separately)
        # 2. Core Intent (pinned)
        # 3. Flash Memories
        # 4. Sliding Window
        # 5. Active Workspace (current turn)
        user_message = f"""[Core Intent - Pinned]
{intent_signals}

[Long-term Context - Flash Memories]
{memory_context if memory_context else "No relevant memories"}

[Recent Conversation - Last 10 turns]
{history_context if history_context else "No conversation history"}

[Active Workspace - Current Turn]
User ({user_state}): {agent_input.message}"""

        # On retry, include Verdict's feedback
        if verdict_feedback:
            user_message += f"""

RETRY - Previous response failed validation.
Verdict feedback: {verdict_feedback}

Fix the issue and generate a better response."""
        else:
            user_message += "\n\nGenerate a brief, conversational response."

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
