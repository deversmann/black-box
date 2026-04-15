# Black Box Swarm - Development Guide

Core abstractions, testing strategy, and implementation rules for developers.

---

## Core Abstractions

### Base Agent Interface (`src/blackbox/core/agent.py`)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel

class AgentConfig(BaseModel):
    """Configuration for an individual agent"""
    name: str
    model: str              # e.g., "openai/gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 500
    timeout: int = 30       # seconds

class AgentInput(BaseModel):
    """Standardized input to agents"""
    message: str
    context: Dict[str, Any] = {}

class AgentOutput(BaseModel):
    """Standardized output from agents"""
    result: str
    metadata: Dict[str, Any] = {}
    confidence: float = 1.0

class Agent(ABC):
    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.name
    
    @abstractmethod
    async def execute(self, input: AgentInput) -> AgentOutput:
        """Execute the agent's primary function"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
```

### Shared State (`src/blackbox/core/state.py`)

```python
from typing import TypedDict, List, Optional, Dict
from langgraph.graph import add_messages

class SwarmState(TypedDict):
    """The state passed between agents in the swarm"""
    # Input
    user_input: str
    session_id: str
    conversation_history: Optional[List[Dict]]  # Last 10 turns (20 messages)
    
    # Ingress outputs
    intent_signals: Optional[str]
    detail_level: Optional[str]         # BRIEF, DETAILED, COMPREHENSIVE
    user_state: Optional[str]           # JOVIAL, FRUSTRATED, etc.
    
    # Context outputs
    memory_hits: Optional[List[Dict]]   # From Flash
    facts: Optional[List[str]]          # From Vault
    
    # Synthesis outputs
    draft_response: Optional[str]       # From Command
    enhanced_response: Optional[str]    # From Aura (if activated)
    
    # Egress outputs
    final_response: Optional[str]
    validation_passed: bool
    safety_passed: bool
    verdict_feedback: Optional[str]     # Feedback for retry
    
    # Metadata
    p_tangent: float                    # Slider + mood modifier
    aura_activated: bool
    retry_count: int
    agents_involved: List[str]
```

---

## Testing & Validation

### Testing Strategy

#### Unit Tests
- Each agent in isolation with mocked LLM responses
- Memory Manager CRUD operations
- Vector store search accuracy
- Cooldown filter logic

**Example:**
```python
@pytest.mark.asyncio
async def test_sieve_extracts_intent():
    config = AgentConfig(name="Sieve", model="openai/gpt-4o-mini", ...)
    agent = SieveAgent(config)
    
    result = await agent.execute(AgentInput(
        message="I'm trying to learn Python but I'm confused about decorators"
    ))
    
    assert "python" in result.result.lower()
    assert "decorator" in result.result.lower()
```

#### Integration Tests
- Full swarm execution
- Memory persistence across sessions
- Cooldown filter integration
- Safety profile enforcement

#### End-to-End Tests
- Streamlit UI interaction
- WebSocket streaming
- Multi-turn conversations
- Memory accumulation over time

#### Load Tests
- Concurrent sessions
- Large memory databases (10k+ memories)
- Vector search performance

### Validation Checklists

**Phase 1 (MVP):**
- [ ] Can send message through Streamlit UI
- [ ] Receives coherent response
- [ ] LangGraph visualization shows execution flow
- [ ] Response time < 5 seconds

**Phase 2 (Full Swarm):**
- [ ] All 11 agents execute in correct order
- [ ] Aura activates when slider > 0.7
- [ ] Sensor detects mood correctly
- [ ] Probe vetoes incoherent responses
- [ ] Parser outputs structured JSON

**Phase 3 (Memory):**
- [ ] Memories persist across app restarts
- [ ] Vector search returns relevant results
- [ ] Cooldown prevents repetition within 24 hours
- [ ] Parser creates atomic memories (no unresolved pronouns)

**Phase 4 (Production):**
- [ ] 80%+ test coverage
- [ ] Docker: `docker-compose up` works
- [ ] Metrics visible via Prometheus
- [ ] All tests passing

**Phase 5 (Advanced):**
- [ ] Response time < 2s for 80% of queries
- [ ] Memory consolidation removes duplicates
- [ ] Plugin system functional
- [ ] Preference learning works

---

## Implementation Rules

### For Developers

1. **Model Tiering:** Use high-reasoning models (GPT-4o/Claude Opus) for Command, Aura, and Probe. Use small, fast models (GPT-4o-mini/Claude Haiku) for Sieve, Sensor, Vault, and Parser.

2. **Parallelization:** Agents in the Perception and Verification phases must run concurrently to minimize latency.

3. **The Associative Slider:** Implement as:
   ```python
   P(tangent) = base_slider + mood_modifier
   # Where:
   # base_slider: 0.0-1.0 (user-controlled)
   # mood_modifier: ±0.2 based on user state
   ```

4. **Atomic Memory:** Ensure Parser rewrites memories to be self-contained (e.g., replacing "It is broken" with "The user's Honda Shadow is broken") before storing in the Ledger.

5. **Cooldown Filter:** Any memory ID used must be added to a "Recently Used" queue in Flash to prevent the AI from harping on the same story in a single session.

6. **Safety First:** Shield runs twice—once on input, once on output. If either fails, the swarm must abort gracefully.

7. **State Immutability:** SwarmState should be treated as immutable within agents. Create new state objects rather than mutating existing ones.

8. **Error Handling:** Each agent must handle LLM failures gracefully. Retry up to 3 times with exponential backoff.

9. **Logging:** Every agent execution must be logged with:
   - Agent name
   - Input/output lengths
   - Duration (ms)
   - Success/failure status
   - Metadata (model used, tokens consumed)

10. **Configuration:** All magic numbers (thresholds, timeouts, cooldown periods) must be configurable via YAML.

---

## Development Workflow

### Adding a New Agent (Future Phases)

1. Create agent file: `src/blackbox/agents/new_agent.py`
2. Implement Agent ABC with `execute()` and `get_system_prompt()`
3. Add config to `config/default.yaml`
4. Update orchestrator: `src/blackbox/core/orchestrator.py`
5. Write tests: `tests/unit/test_agents/test_new_agent.py`

### Code Quality

```bash
# Type checking
mypy src/

# Linting
ruff check src/

# Auto-format
ruff format src/
```

---

## Related Documentation

- [Configuration Guide](CONFIGURATION.md) - Tech stack, setup, and configuration
- [Technical Challenges](CHALLENGES.md) - Implementation challenges and solutions
- [Architecture Overview](../architecture/OVERVIEW.md) - System design philosophy
