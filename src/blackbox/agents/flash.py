"""Flash agent - Memory retrieval (mock implementation for Phase 1)."""

from blackbox.core.agent import Agent, AgentConfig, AgentInput, AgentOutput


class Flash(Agent):
    """Memory Retrieval - Semantic search over The Ledger.

    Phase 1 Mock: Returns hardcoded example memories.
    Phase 3: Will perform real vector search using ChromaDB.
    """

    # Hardcoded memories for Phase 1 testing
    MOCK_MEMORIES = [
        {
            "id": "mem_001",
            "type": "USER_FACT",
            "content": "User is a software engineer with 10 years of Python experience",
            "similarity": 0.92,
            "last_referenced": "2026-03-15",
        },
        {
            "id": "mem_002",
            "type": "USER_STORY",
            "content": "User recently started learning about AI/ML and neural networks",
            "similarity": 0.85,
            "last_referenced": "2026-04-01",
        },
        {
            "id": "mem_003",
            "type": "PREFERENCE",
            "content": "User prefers detailed technical explanations with code examples",
            "similarity": 0.88,
            "last_referenced": "2026-03-20",
        },
    ]

    def __init__(self, config: AgentConfig) -> None:
        """Initialize Flash agent.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

    def get_system_prompt(self) -> str:
        """Return the system prompt for Flash."""
        return """You are Flash, the Memory Retrieval agent.

Your role: Search The Ledger (persistent memory) for relevant context.

In Phase 1, you return mock hardcoded memories for testing.
In Phase 3, you will perform semantic vector search."""

    async def _execute_impl(self, agent_input: AgentInput) -> AgentOutput:
        """Execute memory retrieval (mock).

        Args:
            agent_input: Contains intent signals and context

        Returns:
            AgentOutput with mock memory hits
        """
        # Phase 1: Return all mock memories
        # Phase 3: Will perform semantic search based on intent_signals
        return AgentOutput(
            result=f"Retrieved {len(self.MOCK_MEMORIES)} memories",
            metadata={
                "agent": self.name,
                "memories": self.MOCK_MEMORIES,
                "is_mock": True,
            },
            confidence=1.0,
        )
