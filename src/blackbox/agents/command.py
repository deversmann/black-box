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

    def get_system_prompt(self, detail_level: str = "BRIEF") -> str:
        """Return the system prompt for Command.

        Args:
            detail_level: BRIEF, DETAILED, or COMPREHENSIVE
        """
        base = """You're talking to someone you know. Be natural and conversational.

What you know about them:
- Their intent (what they're asking about)
- Past context/memories
- Their current mood
"""

        if detail_level == "COMPREHENSIVE":
            return (
                base
                + """
How to respond - COMPREHENSIVE MODE:
- User wants thorough coverage - they asked for "everything", "complete guide", etc.
- Cover the main aspects with good examples and explanations
- You have ~800 words MAX - stay within this to avoid cutoff
- CRITICAL: Better to cover 3-4 topics completely than 10 topics incompletely
- Organize clearly (numbered lists, sections if needed)
- Still conversational, just more complete
- Watch your length - finish strong before hitting the limit

You're being thorough because they asked for it, not because you're lecturing."""
            )
        elif detail_level == "DETAILED":
            return (
                base
                + """
How to respond - DETAILED MODE:
- User wants depth - they asked for "detail", "examples", "explain more"
- Provide concrete examples and explanations
- Go beyond surface level but stay focused
- You have ~500 words - enough for good detail
- Still conversational, just with more substance

Bad: "Decorators modify functions."
Good: "Decorators modify functions. Here's how: when you put @decorator above a function, Python calls decorator(function) and uses the result. For example, @timer could measure how long a function takes to run."

You're explaining because they want to understand, not showing off."""
            )
        else:  # BRIEF
            return (
                base
                + """
How to respond - BRIEF MODE (default):
- **Keep it SHORT** - 3-4 sentences for simple questions
- Use everyday language, not textbook language
- Give the key point + offer to expand
- Don't lecture. Don't list things unless asked.
- You have ~300 words - use less if possible

Bad: "Python decorators are functions that modify the behavior of other functions. They use the @ syntax. Here are several examples: [lists 5 examples with code]..."

Good: "Decorators let you modify functions. Think of them like wrappers - you put @something above a function to add behavior. Want to see a quick example?"

You're chatting, not teaching a class."""
            )


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
        detail_level = agent_input.context.get("detail_level", "BRIEF")

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

        # Adjust max_tokens based on detail level
        token_limits = {
            "BRIEF": 500,  # ~300 words
            "DETAILED": 800,  # ~500 words
            "COMPREHENSIVE": 2200,  # ~1400 words - extra headroom to prevent cutoff
        }
        max_tokens = token_limits.get(detail_level, 500)

        messages = [
            OpenRouterMessage(role="system", content=self.get_system_prompt(detail_level)),
            OpenRouterMessage(role="user", content=user_message),
        ]

        result = await self.client.chat_completion(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=max_tokens,  # Dynamic based on detail level
        )

        return AgentOutput(
            result=result,
            metadata={
                "agent": self.name,
                "used_memories": len(memories),
            },
            confidence=0.9,
        )
