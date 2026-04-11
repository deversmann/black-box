"""Vault agent - Relational database queries (mock implementation for Phase 2)."""

from blackbox.core.agent import Agent, AgentConfig, AgentInput, AgentOutput


class Vault(Agent):
    """Librarian - Retrieves raw relational facts based on memory hits.

    Phase 2 Mock: Returns hardcoded example facts.
    Phase 3: Will perform real database queries against The Ledger.

    Purpose:
    Separates factual retrieval from creative synthesis. Vault provides
    raw ingredients; Command cooks the meal.
    """

    # Hardcoded facts for Phase 2 testing
    MOCK_FACTS = [
        "User has completed 47 projects in Python over the past 5 years",
        "User's most frequent topics: AI/ML, web development, system design",
        "User prefers code examples with inline comments explaining the logic",
        "User has asked about decorators 3 times in the past month",
        "User's learning pattern: deep-dive sessions on weekends, quick questions on weekdays",
    ]

    def __init__(self, config: AgentConfig) -> None:
        """Initialize Vault agent.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

    def get_system_prompt(self) -> str:
        """Return the system prompt for Vault."""
        return """You are Vault, the Librarian.

Your role: Retrieve raw relational facts from The Ledger database based on
memory context provided by Flash.

In Phase 2, you return mock hardcoded facts for testing.
In Phase 3, you will perform SQL queries against the relational database."""

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute fact retrieval (mock).

        Args:
            agent_input: Contains memory hits from Flash

        Returns:
            AgentOutput with mock relational facts
        """
        # Phase 2: Return all mock facts
        # Phase 3: Will query database based on memory_hits context
        memory_hits = agent_input.context.get("memory_hits", [])

        # In Phase 3, we'd use memory_hits to construct SQL queries
        # For now, just return mock facts
        return AgentOutput(
            result=f"Retrieved {len(self.MOCK_FACTS)} facts from relational database",
            metadata={
                "agent": self.name,
                "facts": self.MOCK_FACTS,
                "is_mock": True,
                "memory_context_count": len(memory_hits),
            },
            confidence=1.0,
        )
