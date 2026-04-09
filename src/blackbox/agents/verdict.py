"""Verdict agent - Response validation."""

from blackbox.core.agent import Agent, AgentConfig, AgentInput, AgentOutput
from blackbox.models.client import OpenRouterClient, OpenRouterMessage


class Verdict(Agent):
    """Response Validator - Quality control for final responses.

    Verdict checks that responses are coherent, accurate, complete,
    and appropriately address the user's intent.
    """

    def __init__(self, config: AgentConfig, client: OpenRouterClient) -> None:
        """Initialize Verdict agent.

        Args:
            config: Agent configuration
            client: OpenRouter API client
        """
        super().__init__(config)
        self.client = client

    def get_system_prompt(self) -> str:
        """Return the system prompt for Verdict."""
        return """You are Verdict, the Response Validator.

Your role: Quality control. Validate that responses meet quality standards before delivery.

Check for:
1. **Truncation** (CRITICAL): Does the response end mid-sentence or mid-word?
   - FAIL immediately if it doesn't end with punctuation (. ? ! " etc.)
   - FAIL if last sentence is incomplete
   - Tell Command: "Response truncated mid-sentence. Make it shorter to finish the thought."

2. Coherence: Does the response make logical sense?

3. Completeness: Does it address the core intent?
   - Don't require covering EVERYTHING - just the main point

4. Tone: Is it conversational (like chatting) or formal (like a textbook)?
   - FAIL if it sounds like a manual or lecture
   - Tell Command: "Too formal. Talk naturally, like explaining to a friend."

5. Length: Is it brief?
   - PASS if 3-5 sentences for simple questions
   - FAIL if multi-paragraph unless user asked for detail
   - Tell Command: "Too long. Give the key point in 3-4 sentences."

Output format (exactly):
PASS: [brief reason]
or
FAIL: [what's wrong - be specific]

Priority order: Truncation > Length > Tone > Completeness"""

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute response validation.

        Args:
            agent_input: Contains draft response and context

        Returns:
            AgentOutput with validation result (PASS/FAIL)
        """
        draft_response = agent_input.context.get("draft_response", "")
        intent_signals = agent_input.context.get("intent_signals", "")
        original_message = agent_input.message

        user_message = f"""Original User Message:
{original_message}

Intent Signals:
{intent_signals}

Draft Response:
{draft_response}

Validate this response."""

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

        # Parse PASS/FAIL from result
        passed = result.strip().startswith("PASS")

        return AgentOutput(
            result=result,
            metadata={
                "agent": self.name,
                "validation_passed": passed,
            },
            confidence=0.95,
        )
