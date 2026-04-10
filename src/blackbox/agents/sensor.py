"""Sensor agent - Mood detection and P(tangent) calculation."""

from blackbox.core.agent import Agent, AgentConfig, AgentInput, AgentOutput
from blackbox.models.client import OpenRouterClient, OpenRouterMessage


class Sensor(Agent):
    """Empath - Detects user mood and adjusts P(tangent).

    Sensor analyzes user messages to detect emotional state and cognitive load.
    This influences response style and tangent probability.

    User States:
    - JOVIAL: Playful, excited, good mood (+0.2 to P(tangent))
    - CURIOUS: Engaged, exploratory questions (+0.1)
    - NEUTRAL: Standard interaction (0)
    - FOCUSED: Task-oriented, wants direct answers (-0.1)
    - FRUSTRATED: Confused, struggling, needs clarity (-0.2)
    - HURRIED: Short messages, wants quick answers (-0.2)
    """

    # Mood modifiers for P(tangent) calculation
    MOOD_MODIFIERS = {
        "JOVIAL": 0.2,
        "CURIOUS": 0.1,
        "NEUTRAL": 0.0,
        "FOCUSED": -0.1,
        "FRUSTRATED": -0.2,
        "HURRIED": -0.2,
    }

    def __init__(self, config: AgentConfig, client: OpenRouterClient) -> None:
        """Initialize Sensor agent.

        Args:
            config: Agent configuration
            client: OpenRouter API client
        """
        super().__init__(config)
        self.client = client

    def get_system_prompt(self) -> str:
        """Return the system prompt for Sensor."""
        return """You are Sensor, the Empath.

Your role: Detect the user's emotional state and cognitive load from their message.

Analyze:
- Message length (very short = HURRIED, verbose = CURIOUS/JOVIAL)
- Tone and word choice
- Punctuation (! = excited, ??? = frustrated/confused)
- Emoji usage (emojis = JOVIAL/CURIOUS)
- Question style (exploratory = CURIOUS, direct = FOCUSED)
- Indicators of confusion or struggle (FRUSTRATED)

User States:
1. **JOVIAL** - Playful, excited, in a good mood
   - Signals: Emojis, exclamation marks, enthusiastic language
   - Example: "This is so cool! 😄 Tell me more!"

2. **CURIOUS** - Engaged, asking exploratory questions
   - Signals: "I wonder", "what if", "how does", open-ended questions
   - Example: "I wonder how this could apply to my project?"

3. **NEUTRAL** - Standard, straightforward interaction
   - Signals: Clear questions, no strong emotional indicators
   - Example: "What are Python decorators?"

4. **FOCUSED** - Task-oriented, wants direct answers
   - Signals: "I need to", "how do I", imperative tone
   - Example: "I need to fix this bug. How do I handle errors?"

5. **FRUSTRATED** - Confused, struggling, needs clarity
   - Signals: "I don't understand", "confused", "not working", "???"
   - Example: "I'm confused... why isn't this working???"

6. **HURRIED** - Short messages, wants quick answers
   - Signals: Very brief (< 10 words), terse, no elaboration
   - Example: "decorators?" or "quick q: what's async?"

Output format (exactly):
STATE: [state name]
CONFIDENCE: [0.0-1.0]
REASONING: [one sentence explaining why]

Examples:
Input: "This is awesome! 😄 Can you explain more about decorators?"
Output:
STATE: JOVIAL
CONFIDENCE: 0.9
REASONING: Enthusiastic language with emoji and exclamation mark

Input: "I'm so confused about decorators. Nothing makes sense..."
Output:
STATE: FRUSTRATED
CONFIDENCE: 0.85
REASONING: Explicit confusion statement and defeated tone

Input: "What are decorators?"
Output:
STATE: NEUTRAL
CONFIDENCE: 0.9
REASONING: Clear, straightforward question with no emotional indicators

Input: "decorators?"
Output:
STATE: HURRIED
CONFIDENCE: 0.8
REASONING: Very brief one-word question suggests time pressure

Be confident in your assessments but use lower confidence (0.6-0.7) for ambiguous cases."""

    async def execute(self, agent_input: AgentInput) -> AgentOutput:
        """Execute mood detection.

        Args:
            agent_input: Contains user message

        Returns:
            AgentOutput with detected mood, confidence, and P(tangent)
        """
        user_message = agent_input.message

        validation_request = f"""User message:
{user_message}

What is the user's emotional state?"""

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
        mood = "NEUTRAL"  # Default
        confidence = 0.5
        reasoning = ""

        lines = result.strip().split("\n")
        for line in lines:
            if line.startswith("STATE:"):
                mood = line.split(":", 1)[1].strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                except ValueError:
                    confidence = 0.5
            elif line.startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()

        # Get mood modifier
        mood_modifier = self.MOOD_MODIFIERS.get(mood, 0.0)

        return AgentOutput(
            result=result,
            metadata={
                "agent": self.name,
                "mood": mood,
                "confidence": confidence,
                "reasoning": reasoning,
                "mood_modifier": mood_modifier,
            },
            confidence=confidence,
        )
