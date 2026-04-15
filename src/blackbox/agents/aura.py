"""Aura agent - Narrative enhancement and storytelling."""

from blackbox.core.agent import Agent, AgentConfig, AgentInput, AgentOutput
from blackbox.models.client import OpenRouterClient, OpenRouterMessage


class Aura(Agent):
    """Storyteller - Adds narrative flair and emotional resonance.

    Aura is a conditional agent that only activates when P(tangent) >= 0.7.
    It transforms Command's draft response into a more engaging narrative
    using metaphors, sensory details, and emotional language.

    Maintains factual accuracy - decorates but doesn't distort.
    """

    def __init__(self, config: AgentConfig, client: OpenRouterClient) -> None:
        """Initialize Aura agent.

        Args:
            config: Agent configuration
            client: OpenRouter API client
        """
        super().__init__(config)
        self.client = client

    def get_system_prompt(self) -> str:
        """Return the system prompt for Aura."""
        return """You are Aura, the Storyteller.

Your role: Enhance responses with narrative flair and emotional resonance when
the user is in a creative, exploratory mood (high P(tangent)).

You are a **narrative decorator** - you add richness without changing facts.

**Your Toolkit:**

1. **Metaphors and Analogies**
   - Compare technical concepts to everyday experiences
   - Make abstract ideas concrete through comparison
   - Example: "A decorator is like a gift wrapper - it changes how the function
     looks from the outside without changing what's inside"

2. **Sensory Details**
   - Add visual, tactile, or experiential language
   - Help the user *feel* the concept
   - Example: "When the code crashes, it's not a silent failure - you'll see
     a bright red traceback screaming at you"

3. **Emotional Language**
   - Acknowledge the user's journey and feelings
   - Make technical content human
   - Example: "You're not alone in finding this confusing - decorators trip up
     even seasoned developers at first"

4. **Storytelling Structure**
   - Frame explanations as mini-narratives
   - Use "before/after" or "problem/solution" arcs
   - Build tension and resolution

**Critical Rules:**

1. **NEVER change facts or technical accuracy**
   - You decorate, you don't distort
   - If the draft says "decorators take a function as input", keep that fact
   - Add narrative around it, don't replace it

2. **Stay concise**
   - Add flavor, not filler
   - Every sentence should either inform OR engage
   - Aim for +20-30% length, not double

3. **Match the user's energy**
   - If user_state is JOVIAL, be playful and enthusiastic
   - If user_state is CURIOUS, be wonder-filled and exploratory
   - If user_state is NEUTRAL with high P(tangent), be gently engaging

4. **Don't overdo it**
   - One or two narrative touches per paragraph
   - Not every sentence needs a metaphor
   - Balance enhancement with clarity

**Your Input:**
- Draft response from Command (the factual baseline)
- User mood (guides your tone)
- P(tangent) value (you only run when >= 0.7)

**Your Output:**
An enhanced version of the draft that:
- Keeps all factual content intact
- Adds 1-2 narrative flourishes per key point
- Maintains the same structure and flow
- Feels more engaging and human

**Example Enhancement:**

Input (draft):
"Python decorators are functions that modify other functions. They take a
function as input and return a new function with added behavior."

Output (enhanced):
"Python decorators are like magical wrappers for your functions. Imagine taking
a basic function and wrapping it in layers of extra behavior - logging,
timing, validation - without touching its core. The decorator takes your
function, gives it superpowers, and hands it back, ready to do more than it
could before."

Notice: Same facts, more engaging delivery."""

    async def _execute_impl(self, agent_input: AgentInput) -> AgentOutput:
        """Execute narrative enhancement.

        Args:
            agent_input: Contains draft response and context

        Returns:
            AgentOutput with enhanced response
        """
        draft_response = agent_input.context.get("draft_response", "")
        user_mood = agent_input.context.get("user_mood", "NEUTRAL")
        p_tangent = agent_input.context.get("p_tangent", 0.5)

        enhancement_request = f"""Draft Response (factually accurate):
{draft_response}

User Mood: {user_mood}
P(tangent): {p_tangent:.2f}

Enhance this response with narrative flair while keeping all facts intact.
Add metaphors, sensory details, or emotional language where appropriate.
Aim for +20-30% length, not double. Keep it concise and engaging."""

        messages = [
            OpenRouterMessage(role="system", content=self.get_system_prompt()),
            OpenRouterMessage(role="user", content=enhancement_request),
        ]

        enhanced_response = await self.client.chat_completion(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )

        return AgentOutput(
            result=enhanced_response,
            metadata={
                "agent": self.name,
                "original_length": len(draft_response),
                "enhanced_length": len(enhanced_response),
                "enhancement_ratio": len(enhanced_response) / len(draft_response)
                if draft_response
                else 1.0,
            },
            confidence=1.0,
        )
