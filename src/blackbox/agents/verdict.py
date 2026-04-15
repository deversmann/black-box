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
   - FAIL if response ends mid-word or without proper punctuation (. ? ! " etc.)
   - OK to end with "..." if used intentionally for effect
   - FAIL if last sentence is clearly incomplete (e.g., "This is because" with nothing after)
   - Tell Command: "Response truncated mid-sentence. Use fewer words to complete the thought."

2. Coherence: Does the response make logical sense?

3. Completeness: Does it address the core intent?
   - Don't require covering EVERYTHING - just the main point

4. Tone: Is it conversational (like chatting) or formal (like a textbook)?
   - FAIL if it sounds like a manual or lecture
   - Tell Command: "Too formal. Talk naturally, like explaining to a friend."

5. Length: Is it appropriately sized for the DETAIL_LEVEL?
   - BRIEF: PASS if 3-5 sentences, FAIL if multi-paragraph or just 1-2 sentences
   - DETAILED: PASS if includes examples/explanations (5+ sentences), FAIL if too brief (< 3 sentences)
   - COMPREHENSIVE: PASS if multi-paragraph with depth (8+ sentences), be LENIENT - only FAIL if very short (< 5 sentences)
   - Tell Command: "Too long for BRIEF mode" or "Too short for DETAILED request"

Output format (exactly):
PASS: [brief reason]
or
FAIL: [what's wrong - be specific]

Priority order: Truncation > Length > Tone > Completeness"""

    async def _execute_impl(self, agent_input: AgentInput) -> AgentOutput:
        """Execute response validation.

        Args:
            agent_input: Contains draft response and context

        Returns:
            AgentOutput with validation result (PASS/FAIL)
        """
        draft_response = agent_input.context.get("draft_response", "")
        intent_signals = agent_input.context.get("intent_signals", "")
        detail_level = agent_input.context.get("detail_level", "BRIEF")
        original_message = agent_input.message

        user_message = f"""Original User Message:
{original_message}

Intent Signals:
{intent_signals}

Detail Level Expected: {detail_level}
(BRIEF = 3-5 sentences, DETAILED = examples/depth, COMPREHENSIVE = thorough)

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
