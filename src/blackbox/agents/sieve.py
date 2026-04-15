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

Output format - TWO PARTS:

1. DETAIL_LEVEL: [one word only]
   - BRIEF: Default, conversational answer (3-5 sentences)
   - DETAILED: User wants more depth (examples, explanations, code)
     Triggers: "explain in detail", "comprehensive", "tell me more", "can you elaborate", "with examples"
     Continuation: If assistant offered to expand/explain more in previous message, and user affirms ("yes", "please", "sure", "go ahead"), treat as DETAILED even if current message is short
   - COMPREHENSIVE: User wants thorough coverage (multiple aspects, edge cases)
     Triggers: "everything about", "complete guide", "all the details", "step by step"

2. INTENT: [bullet points]
   - List 2-5 bullet points capturing what the user wants
   - Be specific and actionable
   - If current message refers to previous context ("it", "that", "what about X"), incorporate that context
   - Note any relevant context (e.g., "user has some background knowledge", "follow-up to previous question")

Examples:

Example 1 - Explicit request:
Recent: User asked about "How do decorators work?"
Current: "Can you explain error handling in detail with examples?"

Output:
DETAIL_LEVEL: DETAILED
INTENT:
- Explain error handling for Python decorators
- Include code examples
- Follow-up to previous decorator question

Example 2 - Continuation pattern:
Recent: Assistant said "...Would you like me to explain the implementation details?"
Current: "Yes please"

Output:
DETAIL_LEVEL: DETAILED
INTENT:
- User accepts offer to expand on previous topic
- Provide implementation details as offered

Keep it concise. Do not elaborate or answer the question - just distill the intent and detect detail level."""

    async def _execute_impl(self, agent_input: AgentInput) -> AgentOutput:
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

        # Parse DETAIL_LEVEL from response
        detail_level = "BRIEF"  # Default
        if "DETAIL_LEVEL: DETAILED" in result:
            detail_level = "DETAILED"
        elif "DETAIL_LEVEL: COMPREHENSIVE" in result:
            detail_level = "COMPREHENSIVE"

        # Extract just the INTENT part for downstream agents
        intent_only = result
        if "INTENT:" in result:
            intent_only = result.split("INTENT:")[1].strip()

        return AgentOutput(
            result=intent_only,
            metadata={
                "agent": self.name,
                "detail_level": detail_level,
            },
            confidence=0.95,
        )
