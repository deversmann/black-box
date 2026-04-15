# Changelog

All notable changes to the Black Box Swarm project will be documented in this file.

## [0.3.0] - 2026-04-15

### UI/UX Bug Fixes & Logging System

#### Added
- **Structured JSON logging system** (Issue #8)
  - Created `src/blackbox/core/logging.py` with JSONFormatter, configure_logging, get_logger
  - JSONFormatter outputs structured logs with event_type, data, correlation_id fields
  - Automatic sensitive data redaction (API keys, passwords, tokens)
  - Log rotation (10MB files, 5 backups = ~50MB max)
  - Dual output: stdout + file (`./logs/swarm.log`)
  - <2% performance overhead on typical execution times

- **Agent execution logging**
  - Refactored Agent base class with execute() wrapper for automatic timing
  - All agents now implement `_execute_impl()` instead of `execute()`
  - Logs `agent_execution_start` and `agent_execution_complete` with duration_ms
  - Mechanical rename across all 10 agent files

- **API client logging**
  - Logs `api_call_start` with model, temperature, max_tokens, attempt
  - Logs `api_call_complete` with latency_ms, token counts
  - Logs `api_call_error` with error type, will_retry flag
  - Logs exponential backoff delays

- **Orchestrator flow logging**
  - Logs `orchestrator_initialized` with agent roster and safety profile
  - Logs `orchestrator_process_start`/`complete` with correlation_id (session_id)
  - Logs routing decisions (probe veto, aura activation, verdict retry)
  - Logs retry triggers with reasoning

- **Configuration enhancements**
  - Updated `config/default.yaml` with logging.rotation settings
  - Modified `config.py` to call `configure_logging()` on load

#### Fixed
- **Metadata panel not updating** (Issue #5)
  - Fixed one-turn delay in sidebar metadata display
  - Used `st.empty()` placeholder pattern for dynamic updates
  - Metadata now updates immediately after processing completes

- **State accumulation bug** (Issue #5)
  - Fixed bug where Parser's partial state overwrote Sensor's user_mood
  - Changed from `final_state = node_output` to accumulated merge pattern
  - LangGraph `astream()` yields partial updates, must be accumulated
  - All state fields now preserved through full execution flow

- **Agent status bubble positioning** (Issue #6)
  - Moved status bubbles to appear BEFORE responses (not after)
  - Made status bubbles persistent in chat history
  - Displays as collapsed by default for clean history view
  - Works like "thinking" streams in other chat UIs

- **Agent status messages** (Issue #7)
  - Removed Probe reasoning truncation (show full text)
  - Added Verdict failure reason to status display
  - Verdict now shows "✗ Fail: [specific reason]" instead of just "✗ Fail"

#### Changed
- **Agent base class API**: Agents implement `_execute_impl()` instead of `execute()`
  - `execute()` is now a wrapper method that handles timing and logging
  - Breaking change for agent implementations (but easy mechanical refactor)

---

## [0.2.0] - 2026-04-11

### Phase 2 Complete: All 10 Agents Implemented

All three waves of Phase 2 are now complete, implementing all 10 agents in the swarm.

---

### Phase 2 Wave 3: Aura & Parser - Complete (2026-04-11)

#### Added
- **Aura agent**: Narrative enhancement for high P(tangent) scenarios
  - Only activates when P(tangent) ≥ 0.7 (configurable threshold)
  - Temperature 0.9 for creative, narrative-rich responses
  - Adds metaphors, sensory details, emotional language
  - Maintains factual accuracy (decorates without distorting)
  - Mood-aware enhancement (adjusts style based on user mood)

- **Parser agent**: Memory extraction with atomic rewriting
  - Extracts 6 memory types: user_fact, user_story, task_goal, preference, relationship, ai_logic
  - Atomic memory rewriting: resolves pronouns using conversation context
  - Makes memories self-contained (e.g., "It broke" → "The user's Honda Shadow motorcycle broke")
  - Tags: 2-5 relevant tags per memory for semantic search
  - Importance scoring: 0.0-1.0 scale for memory prioritization
  - Phase 2: JSON extraction only (no storage)
  - Phase 3: Will write to The Ledger (SQLite + ChromaDB)

- **Conditional routing**: Enhanced graph flow
  - Probe → (retry Command OR Aura OR Verdict)
  - Aura only runs when P(tangent) ≥ 0.7
  - Verdict validates enhanced_response when Aura activated

- **UI enhancements**:
  - Parser displays "Extracted N memories" in status bubble
  - Debug Info panel shows extracted memories JSON
  - Agent flow includes: 🛡️₁ → 🔍 → 🎭 → 💾 → 📚 → 🧠 → 🔬 → (✨) → ✅ → 🛡️₂ → 🗂️
  - Aura emoji (✨) shows conditionally based on P(tangent)
  - Parser emoji (🗂️) always appears as final step

- **Test coverage**: Added comprehensive tests for new agents
  - Aura agent tests: 7 tests covering activation, enhancement, mood awareness
  - Parser agent tests: 8 tests covering memory extraction, atomic rewriting, JSON handling
  - 70 tests passing, 85% coverage

#### Fixed
- **Aura P(tangent) display**: Aura now includes p_tangent in return dict for UI display
- **Verdict using wrong response**: Verdict now checks enhanced_response when Aura activated
- **Parser response loss**: Parser now preserves final_response from previous agents
- **State propagation bug**: Added memories_count and extracted_memories to SwarmState TypedDict
  - LangGraph only merges fields defined in state schema
  - Critical fix for UI displaying "Extracted 0 memories" despite successful extraction

#### Changed
- **Graph flow**: Updated to Shield Pass 1 → [Sieve + Sensor] → Flash → Vault → Command → Probe → (retry OR Aura OR Verdict) → (retry OR Shield Pass 2) → Parser → END

---

### Phase 2 Wave 2: Vault & Probe - Complete (2026-04-11)

#### Added
- **Vault agent**: Relational database fact retrieval
  - Returns 5 hardcoded facts for Phase 2 testing
  - Phase 3 will query real SQLite database
  - Provides factual knowledge context to Command
  - Facts include: project history, domain expertise, activity patterns

- **Probe agent**: Logic validation with veto power
  - Three validation criteria: logical coherence, relevance to intent, tangent appropriateness
  - Three decision types: APPROVE, VETO, SUGGEST
  - Can veto responses and trigger Command retry (up to 2 retries)
  - Mood-aware validation:
    - Strict with HURRIED/FRUSTRATED users (precision over creativity)
    - Lenient with JOVIAL users (allows more tangents)
  - Reasoning transparency: explains validation decision

- **Conditional routing**: Enhanced retry logic
  - Probe → retry Command (if VETO and retries remain)
  - Probe → Aura (if APPROVE and P(tangent) ≥ 0.7)
  - Probe → Verdict (if APPROVE and P(tangent) < 0.7)

- **UI enhancements**:
  - Vault emoji (📚) in agent flow display
  - Probe emoji (🔬) in agent flow display
  - Probe shows decision and reasoning in status bubble

- **Test coverage**: Added comprehensive tests for new agents
  - Vault agent tests: 4 tests covering initialization and fact retrieval
  - Probe agent tests: 8 tests covering all decision types, mood awareness, criteria validation
  - 62 tests passing, 85% coverage

#### Changed
- **Graph flow**: Updated to include Vault after Flash and Probe after Command

---

### Phase 2 Wave 1: Shield & Sensor - Complete (2026-04-10)

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

### UI/UX Fixes - 2026-04-10

#### Fixed
- **Sidebar metadata one-turn delay**: Metadata panel now updates with current turn, not previous
  - Session state updated immediately after async processing completes
  - Sidebar shows live mood, P(tangent), detail level, etc. from current response

- **P(tangent) slider not connected**: Associative slider now properly passed to swarm
  - Added p_tangent parameter to process_stream()
  - Sensor now calculates based on slider value + mood modifier
  - Previously always used config default (0.5)

- **Debug info text wrapping**: Agent flow display now uses compact emoji format
  - Changed from vertical list to horizontal flow: 🛡️₁ → 🔍 → 🎭 → 💾 → 🧠 → ✅ → 🛡️₂
  - Fits cleanly in narrow sidebar
  - Makes retry patterns obvious (duplicate emojis)

- **Sieve expansion detection**: Added continuation pattern recognition
  - Sieve now detects when assistant offers expansion and user affirms
  - Example: Assistant says "Would you like more detail?" → User says "yes" → DETAILED mode
  - Prevents Command/Verdict conflict where Command expands but Sieve detects BRIEF
  - Added example pattern to Sieve prompt

- **Greyed-out duplicate message**: Fixed ghost message appearing during processing
  - Root cause: Empty assistant message bubble during async streaming
  - Solution: Create response placeholder at start, populate on completion
  - Eliminated partial rerender artifacts

#### Changed
- **Status bubble default state**: Now starts expanded (was collapsed)
  - Shows live agent progress updates during execution
  - Better visibility for debugging and user awareness

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
