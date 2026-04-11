"""Parser agent - Memory extraction and atomic rewriting."""

import json

from blackbox.core.agent import Agent, AgentConfig, AgentInput, AgentOutput
from blackbox.models.client import OpenRouterClient, OpenRouterMessage


class Parser(Agent):
    """Architect - Extracts atomic memories from conversations.

    Parser deconstructs interactions into self-contained memory units.
    Critical responsibility: Atomic Memory Rewriting - ensures memories
    have no unresolved pronouns or references.

    Phase 2: Extracts memories to JSON (does not store)
    Phase 3: Will write to The Ledger (SQLite + ChromaDB)
    """

    def __init__(self, config: AgentConfig, client: OpenRouterClient) -> None:
        """Initialize Parser agent.

        Args:
            config: Agent configuration
            client: OpenRouter API client
        """
        super().__init__(config)
        self.client = client

    def get_system_prompt(self) -> str:
        """Return the system prompt for Parser."""
        return """You are Parser, the Architect.

Your role: Extract structured, self-contained memories from conversations for
long-term storage in The Ledger.

## Critical Responsibility: Atomic Memory Rewriting

Memories MUST be self-contained with NO unresolved pronouns or references.
A memory should be understandable without any surrounding context.

**Bad Memory (has pronouns):**
"It broke yesterday"

**Good Memory (atomic, self-contained):**
"The user's Honda Shadow motorcycle broke yesterday"

**Process:**
1. Identify what "it" refers to by reading conversation context
2. Replace pronouns with explicit nouns
3. Add "the user" or "the user's" to clarify ownership
4. Make the statement standalone

## Memory Types

Extract these 6 types of memories:

1. **user_fact** - Hard facts about the user
   - Demographics, occupation, skills, possessions
   - Example: "The user is a software engineer with 10 years of Python experience"

2. **user_story** - Narratives, experiences, anecdotes
   - Stories from the user's life
   - Example: "The user once debugged a production issue at 3am on Christmas Eve"

3. **task_goal** - Active learning/work objectives
   - What the user is currently working on or learning
   - Example: "The user is learning about Python decorators"

4. **preference** - Likes, dislikes, preferences
   - How the user likes to work, learn, or receive information
   - Example: "The user prefers detailed explanations with code examples"

5. **relationship** - People, places, things user cares about
   - Connections to entities in the user's life
   - Example: "The user's Honda Shadow motorcycle is their primary transportation"

6. **ai_logic** - Reasoning patterns the AI has developed
   - Insights about how to best help this specific user
   - Example: "The user learns faster with visual diagrams before code examples"

## Tagging

Add 2-5 relevant tags for semantic search:
- Use lowercase, underscores for multi-word tags
- Include: topic, domain, entities mentioned
- Example tags: ["python", "decorators", "programming", "learning"]

## Importance Scoring (0.0 - 1.0)

- **0.9-1.0**: Critical life facts (job, family, major events)
- **0.7-0.8**: Important ongoing tasks or strong preferences
- **0.5-0.6**: Useful context, moderate preferences
- **0.3-0.4**: Minor details, weak preferences
- **0.1-0.2**: Trivial mentions

## Output Format

Return a **valid JSON array** of memory objects. Each memory must have:
- `content` (string): The atomic, self-contained memory statement
- `type` (string): One of the 6 types above
- `tags` (array of strings): 2-5 relevant tags
- `importance` (number): Score from 0.0 to 1.0

**Example Output:**
```json
[
  {
    "content": "The user's Honda Shadow motorcycle broke yesterday",
    "type": "user_fact",
    "tags": ["motorcycle", "honda_shadow", "repair", "vehicle"],
    "importance": 0.8
  },
  {
    "content": "The user is learning Python decorators",
    "type": "task_goal",
    "tags": ["python", "decorators", "programming", "learning"],
    "importance": 0.6
  },
  {
    "content": "The user prefers detailed explanations with code examples",
    "type": "preference",
    "tags": ["learning_style", "code_examples", "detail"],
    "importance": 0.7
  }
]
```

## Important Rules

1. **Only extract NEW information** - Don't repeat what's already known
2. **No vague memories** - "The user asked about something" is not useful
3. **Quality over quantity** - 2-3 high-quality memories beats 10 low-quality ones
4. **Return empty array `[]` if nothing worth remembering** - Not every interaction needs memories
5. **Atomic is critical** - Read context carefully to resolve all pronouns

Your output must be **valid JSON** that can be parsed directly."""

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Extract atomic memories from interaction.

        Args:
            agent_input: Contains user message, response, and context

        Returns:
            AgentOutput with extracted memories as JSON
        """
        user_message = agent_input.context.get("user_message", "")
        final_response = agent_input.context.get("final_response", "")
        conversation_history = agent_input.context.get("conversation_history", [])

        # Build context for atomic rewriting
        context_summary = ""
        if conversation_history:
            # Include last 5 messages for pronoun resolution
            recent = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
            context_summary = "\n".join(
                [f"{msg.get('role', 'unknown')}: {msg.get('content', '')}" for msg in recent]
            )

        extraction_request = f"""Recent Conversation Context:
{context_summary}

Current Turn:
User: {user_message}
Assistant: {final_response}

Extract atomic, self-contained memories from this interaction. Use the context
to resolve any pronouns or references. Return valid JSON array.

If nothing worth remembering, return: []"""

        messages = [
            OpenRouterMessage(role="system", content=self.get_system_prompt()),
            OpenRouterMessage(role="user", content=extraction_request),
        ]

        result = await self.client.chat_completion(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        # Parse JSON response
        memories = []
        try:
            # Clean markdown code blocks if present
            cleaned = result.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            memories = json.loads(cleaned)
        except json.JSONDecodeError:
            # If JSON parsing fails, return empty list
            memories = []

        return AgentOutput(
            result=json.dumps(memories, indent=2),
            metadata={
                "agent": self.name,
                "memories_extracted": len(memories),
                "memories": memories,
                "is_stored": False,  # Phase 2: extraction only, no storage
            },
            confidence=1.0,
        )
