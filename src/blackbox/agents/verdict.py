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
1. Coherence: Does the response make logical sense?
2. Completeness: Does it address all intent points?
3. Accuracy: Are there obvious factual errors or contradictions?
4. Appropriateness: Is the tone and detail level suitable?

Output format (exactly):
PASS: [brief reason]
or
FAIL: [what's wrong and how to fix it]

Be strict but fair. A response doesn't need to be perfect - just good enough to be helpful."""

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
