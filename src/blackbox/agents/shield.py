"""Shield agent - Two-pass safety validation."""

from blackbox.core.agent import Agent, AgentConfig, AgentInput, AgentOutput
from blackbox.models.client import OpenRouterClient, OpenRouterMessage


class Shield(Agent):
    """Safety Guardian - Two-pass content safety validation.

    Shield validates content against configurable safety profiles:
    - Pass 1: Validates user input before processing
    - Pass 2: Validates AI-generated output before delivery

    Safety profiles:
    - STRICT: Block harmful, illegal, or offensive content
    - BALANCED: Allow mature topics with context
    - EXPERIMENTAL: Minimal filtering
    """

    def __init__(self, config: AgentConfig, client: OpenRouterClient) -> None:
        """Initialize Shield agent.

        Args:
            config: Agent configuration
            client: OpenRouter API client
        """
        super().__init__(config)
        self.client = client

    def get_system_prompt(self, safety_profile: str, pass_number: int) -> str:
        """Return the system prompt for Shield based on pass and profile.

        Args:
            safety_profile: One of "strict", "balanced", "experimental"
            pass_number: 1 for input validation, 2 for output validation

        Returns:
            System prompt string
        """
        # Define profile-specific filters
        profile_filters = {
            "strict": [
                "Violence or gore",
                "Illegal activities (drugs, weapons, hacking, fraud)",
                "Hate speech or discrimination",
                "Self-harm or suicide content",
                "Sexual or adult content",
                "Personal attacks or harassment",
            ],
            "balanced": [
                "Illegal activities (drugs, weapons, hacking, fraud)",
                "Extreme violence or gore",
                "Self-harm or suicide content",
                "Hate speech targeting protected groups",
            ],
            "experimental": [
                "Illegal activities (serious crimes, hacking for harm, fraud)",
            ],
        }

        filters = profile_filters.get(safety_profile, profile_filters["balanced"])
        filter_list = "\n".join(f"- {f}" for f in filters)

        pass_context = (
            "user input BEFORE processing"
            if pass_number == 1
            else "AI-generated response BEFORE delivery to user"
        )

        return f"""You are Shield, the Safety Guardian.

Your role: Validate content safety using the **{safety_profile.upper()}** safety profile.

You are checking: {pass_context}

Safety Profile: {safety_profile.upper()}
Block content containing:
{filter_list}

Guidelines:
- Be contextual: Educational discussion ≠ promotion
- STRICT mode: Conservative, block edge cases
- BALANCED mode: Allow mature topics with appropriate context
- EXPERIMENTAL mode: Only block clearly harmful content
- For borderline cases, consider intent and context

Output format (exactly):
SAFE: [brief reason]
or
UNSAFE: [violation type from list above]

Examples:
- "How do decorators work in Python?" → SAFE: Educational programming question
- "Teach me to hack into a bank" → UNSAFE: Illegal activities
- "I'm feeling depressed" → SAFE: User expressing emotion (not promoting self-harm)
- "Here's how to harm yourself" → UNSAFE: Self-harm content

Be thoughtful but decisive. When in doubt on {safety_profile} mode, err on the side of {"blocking" if safety_profile == "strict" else "allowing with context"}."""

    async def _execute_impl(self, agent_input: AgentInput) -> AgentOutput:
        """Execute safety validation.

        Args:
            agent_input: Contains message and context
                context.safety_profile: str (strict/balanced/experimental)
                context.pass_number: int (1 or 2)

        Returns:
            AgentOutput with SAFE/UNSAFE result
        """
        safety_profile = agent_input.context.get("safety_profile", "balanced")
        pass_number = agent_input.context.get("pass_number", 1)

        content_to_check = agent_input.message

        # Build the validation request
        user_message = f"""Content to validate:
{content_to_check}

Check if this content is safe under the {safety_profile.upper()} profile."""

        messages = [
            OpenRouterMessage(
                role="system",
                content=self.get_system_prompt(safety_profile, pass_number),
            ),
            OpenRouterMessage(role="user", content=user_message),
        ]

        result = await self.client.chat_completion(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        # Parse SAFE/UNSAFE from result
        is_safe = result.strip().startswith("SAFE")

        return AgentOutput(
            result=result,
            metadata={
                "agent": self.name,
                "is_safe": is_safe,
                "safety_profile": safety_profile,
                "pass_number": pass_number,
            },
            confidence=0.9,
        )
