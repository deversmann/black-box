# Changelog

All notable changes to the Black Box Swarm project will be documented in this file.

## [0.2.0] - 2026-04-10

### Phase 2 Wave 1: Shield & Sensor - Complete

#### Added
- **Shield agent**: Two-pass safety validation system
  - Shield Pass 1: User input safety check at graph ingress
  - Shield Pass 2: Response output safety check at graph egress
  - Three safety profiles: STRICT, BALANCED (default), EXPERIMENTAL
  - Configurable via sidebar safety profile selector
  - Returns SAFE/UNSAFE with reasoning
  - Aborts execution on unsafe input/output

- **Sensor agent**: Mood detection and P(tangent) calculation
  - Detects 6 mood states: JOVIAL, CURIOUS, NEUTRAL, FOCUSED, FRUSTRATED, HURRIED
  - Mood modifiers: JOVIAL (+0.2), CURIOUS (+0.1), NEUTRAL (0.0), FOCUSED (-0.1), FRUSTRATED (-0.2), HURRIED (-0.2)
  - Calculates P(tangent) = base_slider + mood_modifier (clamped [0.0, 1.0])
  - Provides confidence score and reasoning for mood detection

- **Parallel execution**: Sieve + Sensor run concurrently
  - Uses asyncio.gather() for true parallel execution
  - Proper state merging to avoid duplicate agents_involved entries
  - Significantly reduces latency for early-stage processing

- **UI enhancements**:
  - Metadata sidebar panel showing current state:
    - Mood (with emoji)
    - P(tangent) calculated value
    - Detail level
    - Aura status
    - Safety profile
  - Enhanced agent status messages with dynamic state display
  - Retry indicators: 🔁 icon in parentheses for retried agents
  - Safety profile selector in settings sidebar
  - Shield emoji (🛡️) for both Shield Pass 1 and Pass 2
  - Sensor emoji (🎭) for mood detection
  - Running indicators (🔄) that clear after agent completes

- **Test coverage**: Added comprehensive tests for new agents
  - Shield agent tests: all safety profiles, both passes, SAFE/UNSAFE detection
  - Sensor agent tests: all mood states, modifier mappings, malformed responses
  - Integration tests: full swarm flow with Wave 1 agents
  - 43 tests passing, 87% coverage

#### Changed
- **Graph flow restructured**: Sequential Verdict → Shield Pass 2
  - Changed from parallel to sequential for better semantics
  - Verdict decides: retry Command OR proceed to Shield Pass 2
  - Shield Pass 2 now preserves final_response from Verdict
  - Clearer retry flow visible in UI

- **COMPREHENSIVE mode improvements**:
  - Increased max_tokens: 1200 → 2200 to prevent truncation
  - Updated prompt: emphasizes completing thoughts (~800 words target)
  - Encourages depth over breadth ("Better to cover 3-4 topics well than 10 incompletely")
  - Significantly reduced OpenRouter "length" finish reasons

- **Verdict validation**: Made COMPREHENSIVE mode more lenient
  - Changed from vague "thorough coverage" to concrete "8+ sentences, be LENIENT - only FAIL if < 5 sentences"
  - Reduces false positives for comprehensive responses

#### Fixed
- **Infinite retry loop**: Retry count increment moved to node (not conditional)
  - LangGraph ignores state mutations in conditional functions
  - Now properly increments in _run_verdict() before returning

- **Phantom retry indicators**: Fixed duplicate agents_involved entries
  - Parallel node merging now extracts only NEW agents from each result
  - Prevents "Retry #1" showing when no retry occurred

- **Shield Pass 2 response loss**: Fixed fallback message despite successful execution
  - Shield Pass 2 now explicitly returns final_response and draft_response from state
  - Streaming captures final state correctly

- **Running indicators sticking**: Fixed temporary "Running..." messages
  - Clear running_message on final event
  - Proper lifecycle management for status indicators

- **Duplicate Shield Pass 1 events**: Fixed event emission logic
  - Only use agents_involved list for event emission
  - Detect list length changes to emit new agent completions

---

## [0.1.1] - 2026-04-09

### Phase 1.5: Agent Visualization - Complete

#### Added
- **Real-time agent visualization**: Live progress display during swarm execution
  - Added `process_stream()` method to orchestrator using LangGraph's astream
  - Streamlit UI shows agent progress with st.status widget
  - Agent icons and descriptions: 🔍 Sieve, 💾 Flash, 🧠 Command, ✅ Verdict
  - Updates in real-time as each agent completes
  - Expandable status widget shows full agent flow
  - Sets foundation for Phase 2 parallel agent visualization

---

## [0.1.0] - 2026-04-09

### Phase 1: Core Swarm MVP - Complete

#### Added
- 4 core agents: Sieve, Flash (mock), Command, Verdict
- LangGraph orchestration with conditional retry logic
- OpenRouter API integration with async support
- Streamlit chat UI with associative slider
- YAML-based configuration system
- Comprehensive test suite (23 tests, 94% coverage)
- Project infrastructure (pyproject.toml, scripts, docs)

#### Fixed
- **Event loop lifecycle issue**: httpx client now properly managed per request (#2)
  - Removed @st.cache_resource to avoid transport/loop binding
  - Use asyncio.run() for proper event loop lifecycle
  - Add cleanup in finally block

- **Environment variable loading**: Added load_dotenv() to Streamlit app (#1)
  - .env file now properly loaded at startup
  - Improved error messages in start.sh

- **Conversational response tuning**: Complete prompt rewrite for natural conversation
  - Command prompt rewritten: "You're chatting, not teaching a class"
  - Reduced max_tokens: 1000 → 500 (~300 words)
  - Default: 3-4 sentences for simple questions
  - Explicit bad/good examples in prompt
  - Token limit awareness built into agent
  
- **Truncation detection & handling**: Automatic retry on cutoff
  - Verdict now detects mid-sentence cutoffs (missing punctuation)
  - Verdict feedback passed to Command on retry
  - Command receives specific guidance on what to fix
  - Retry count properly incremented in state
  - Max 2 retries before giving up

- **Sliding window conversation context**: 10-turn conversational memory
  - Sieve gets last 3 turns for context-aware intent distillation
  - Command gets full 10 turns for conversational flow
  - Context sandwich structure: Intent → Memories → History → Current
  - Handles follow-ups, pronouns ("it", "that"), and references
  - No persistent memory yet (Phase 3) - session-only

- **Dynamic detail level detection**: Response length adapts to user request
  - Sieve detects: BRIEF (default), DETAILED, COMPREHENSIVE
  - Command adjusts token budget: 500 / 800 / 1200 tokens
  - Triggers: "in detail", "with examples", "complete guide", etc.
  - Verdict validates against expected detail level
  - Brief by default, detailed when requested

### Configuration Changes

#### Command Agent
- `max_tokens`: 1000 → 800 (conversational length)
- System prompt: "comprehensive" → "conversational and concise"
- Added token limit awareness and length guidelines

#### Verdict Agent
- Added conciseness validation
- Now checks if responses are appropriately sized

### Known Limitations
- Flash returns hardcoded mock memories (Phase 3: real ChromaDB)
- No safety filtering yet (Phase 2: Shield agent)
- No mood detection yet (Phase 2: Sensor agent)
- Aura not implemented yet (Phase 2)
- P(tangent) slider present but not functional (Phase 2)

---

## Roadmap

### Phase 2: Complete Agent Suite (Next)
- Add 7 new agents: Shield, Sensor, Vault, Probe, Aura, Parser
- Implement P(tangent) calculation (Slider + MoodModifier)
- Add mood detection and response adaptation
- Implement safety profile enforcement

### Phase 3: The Ledger - Memory System
- ChromaDB integration for vector search
- SQLite + SQLAlchemy for structured data
- Real memory storage and retrieval
- Cooldown filter to prevent repetition

### Phase 4: Refinement & Testing
- Advanced retry and error handling
- Performance optimization
- Comprehensive integration testing
- Production deployment setup

### Phase 5: Advanced Features
- Memory consolidation
- Temporal decay
- Plugin system
- Multi-user support
