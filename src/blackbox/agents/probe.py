"""Probe agent - Logic validation and Devil's Advocate."""

from blackbox.core.agent import Agent, AgentConfig, AgentInput, AgentOutput
from blackbox.models.client import OpenRouterClient, OpenRouterMessage


class Probe(Agent):
    """Devil's Advocate - Validates draft response logic and appropriateness.

    Probe stress-tests Command's draft response against three criteria:
    1. Logical coherence - Does it make sense?
    2. Relevance to intent - Does it answer what the user asked?
    3. Appropriateness of tangents - Are creative tangents justified?

    Can APPROVE, VETO, or SUGGEST improvements.
    """

    def __init__(self, config: AgentConfig, client: OpenRouterClient) -> None:
        """Initialize Probe agent.

        Args:
            config: Agent configuration
            client: OpenRouter API client
        """
        super().__init__(config)
        self.client = client

    def get_system_prompt(self) -> str:
        """Return the system prompt for Probe."""
        return """You are Probe, the Devil's Advocate.

Your role: Validate Command's draft response for logic, relevance, and appropriateness.

You perform THREE critical checks:

1. **Logical Coherence**
   - Does the response make internal sense?
   - Are there contradictions or logical gaps?
   - Is the reasoning sound?

2. **Relevance to Intent**
   - Does the response actually answer what the user asked?
   - Is it on-topic or does it drift without justification?
   - Does it address the core intent signals?

3. **Appropriateness of Tangents**
   - If the response includes creative tangents or associative leaps:
     * Are they justified given the user's state?
     * HURRIED/FRUSTRATED users need direct answers, not tangents
     * JOVIAL/CURIOUS users may enjoy creative tangents
     * Does the tangent add value or just add noise?

**Output format (exactly):**
DECISION: [APPROVE | VETO | SUGGEST]
REASONING: [one-sentence explanation]

**Decision Types:**

- **APPROVE**: Response passes all checks. Continue to quality validation.
  Example:
  DECISION: APPROVE
  REASONING: Logically sound, directly addresses user's question about decorators

- **VETO**: Response has critical flaws. Must retry.
  Example:
  DECISION: VETO
  REASONING: User is HURRIED but response includes unnecessary tangents about metaclasses

- **SUGGEST**: Response is acceptable but could be improved (treat as APPROVE with feedback).
  Example:
  DECISION: SUGGEST
  REASONING: Could mention context managers as a related concept, but core answer is solid

**Special Rules:**

1. If user_state is HURRIED or FRUSTRATED:
   - Veto ANY tangents that don't directly serve the answer
   - Demand clarity and brevity
   - No creative flourishes

2. If user_state is JOVIAL or CURIOUS:
   - Be lenient with well-motivated tangents
   - Allow associative connections if they add value
   - Creative tangents are acceptable

3. If user_state is NEUTRAL or FOCUSED:
   - Apply balanced judgment
   - Minor tangents OK if relevant
   - Prioritize answering the question

Be a constructive critic. Your goal is quality control, not perfection.
If the response accomplishes its purpose, APPROVE it."""

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute logic validation.

        Args:
            agent_input: Contains draft response and validation context

        Returns:
            AgentOutput with validation decision and reasoning
        """
        draft_response = agent_input.context.get("draft_response", "")
        intent_signals = agent_input.context.get("intent_signals", "")
        user_state = agent_input.context.get("user_state", "NEUTRAL")
        p_tangent = agent_input.context.get("p_tangent", 0.5)

        validation_request = f"""Draft Response:
{draft_response}

User Intent:
{intent_signals}

User State: {user_state}
P(tangent): {p_tangent:.2f}

Validate this response against the three criteria. Should I approve, veto, or suggest improvements?"""

        messages = [
            OpenRouterMessage(role="system", content=self.get_system_prompt()),
            OpenRouterMessage(role="user", content=validation_request),
        ]

        result = await self.client.chat_completion(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        # Parse the response
        decision = "APPROVE"  # Default to approve
        reasoning = ""

        lines = result.strip().split("\n")
        for line in lines:
            if line.startswith("DECISION:"):
                decision = line.split(":", 1)[1].strip()
            elif line.startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()

        # SUGGEST is treated as APPROVE with feedback
        approved = decision in ["APPROVE", "SUGGEST"]

        return AgentOutput(
            result=result,
            metadata={
                "agent": self.name,
                "decision": decision,
                "reasoning": reasoning,
                "approved": approved,
            },
            confidence=1.0 if approved else 0.0,
        )
