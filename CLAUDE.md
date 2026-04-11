# Claude Code Context

This file helps Claude Code understand the project context when you return.

## Project: Black Box Swarm
**Status:** Phase 2 Complete - All 10 Agents Implemented  
**Date:** 2026-04-11

## What This Is
Multi-agent AI system for a personal learning assistant that learns, remembers, and develops personality through specialized agents coordinated via LangGraph.

## Current State

### Phase 1: COMPLETE ✅
- ✅ 4 core agents fully implemented and tested
- ✅ LangGraph orchestration with conditional retry
- ✅ OpenRouter integration (gpt-5.4 / gpt-5.4-nano)
- ✅ Streamlit chat UI with session tracking
- ✅ **Sliding window context** - Last 10 turns for conversational flow
- ✅ **Detail level detection** - BRIEF/DETAILED/COMPREHENSIVE modes
- ✅ **Truncation handling** - Auto-detects cutoffs, retries with feedback
- ✅ **Conversational tuning** - Brief by default, detailed on request
- ✅ 23 tests passing, 87% coverage
- ✅ Complete documentation (SPEC.md, README.md, CHANGELOG.md, QUICKSTART.md)

### Phase 1.5: COMPLETE ✅
- ✅ **Real-time agent visualization** - Live progress display using st.status
- ✅ Event streaming from LangGraph via astream()
- ✅ Agent icons and descriptions in UI
- ✅ Foundation for Phase 2 parallel agent visualization

### Phase 2 Wave 1: COMPLETE ✅
- ✅ **Shield agent** - Two-pass safety validation (input + output)
  - Three safety profiles: STRICT, BALANCED, EXPERIMENTAL
  - Integrated at graph ingress (Pass 1) and egress (Pass 2)
- ✅ **Sensor agent** - Mood detection and P(tangent) calculation
  - 6 mood states: JOVIAL, CURIOUS, NEUTRAL, FOCUSED, FRUSTRATED, HURRIED
  - Calculates P(tangent) = slider + mood_modifier, clamped [0.0, 1.0]
- ✅ **Parallel execution** - Sieve + Sensor run concurrently via asyncio.gather()
- ✅ **Sequential validation** - Verdict → (retry OR Shield Pass 2)
- ✅ **UI enhancements**
  - Metadata sidebar panel (mood, P(tangent), detail level, Aura status, safety profile)
  - Real-time sidebar updates (current turn, not delayed)
  - P(tangent) slider properly connected to swarm
  - Compact emoji flow in Debug Info panel (🛡️₁ → 🔍 → 🎭 → ...)
  - Enhanced agent status messages with dynamic state display
  - Retry indicators (🔁) for Command/Verdict retries
  - Safety profile selector in settings
  - Status bubble expanded by default for visibility
  - Fixed ghost message duplication during processing
- ✅ **Sieve expansion detection**
  - Detects continuation patterns (assistant offers → user affirms)
  - Prevents Command/Verdict conflicts on expansion requests
- ✅ **COMPREHENSIVE mode improvements**
  - Increased token budget (500→2200) with prompt guardrails
  - Prevents truncation while encouraging concise responses
- ✅ 43 tests passing, 87% coverage

### Phase 2 Wave 2: COMPLETE ✅
- ✅ **Vault agent** - Relational database queries (mock)
  - Returns 5 hardcoded facts for Phase 2 testing
  - Phase 3 will query real SQLite database
  - Provides factual knowledge context to Command
- ✅ **Probe agent** - Logic validation with veto power
  - Three validation criteria: logical coherence, relevance to intent, tangent appropriateness
  - Can APPROVE, VETO, or SUGGEST improvements
  - Mood-aware: strict with HURRIED/FRUSTRATED users, lenient with JOVIAL
  - Triggers Command retry on VETO (up to 2 retries)
- ✅ **Conditional routing** - Probe → (retry OR Aura OR Verdict)
- ✅ 62 tests passing, 85% coverage

### Phase 2 Wave 3: COMPLETE ✅
- ✅ **Aura agent** - Narrative enhancement (P(tangent) ≥ 0.7)
  - Temperature 0.9 for creative flair
  - Adds metaphors, sensory details, emotional language
  - Maintains factual accuracy (decorates, doesn't distort)
  - Only activates when P(tangent) crosses threshold
- ✅ **Parser agent** - Memory extraction with atomic rewriting
  - Extracts 6 memory types: user_fact, user_story, task_goal, preference, relationship, ai_logic
  - Resolves pronouns using conversation context for self-contained memories
  - Tags and importance scoring (0.0-1.0)
  - Phase 2: extraction to JSON only (no storage)
  - Phase 3: will write to The Ledger (SQLite + ChromaDB)
- ✅ **UI enhancements**
  - Extracted memories displayed in Debug Info panel
  - Parser shows "Extracted N memories" in status bubble
  - Agent flow includes all 10 agents: 🛡️₁ → 🔍 → 🎭 → 💾 → 📚 → 🧠 → 🔬 → (✨) → ✅ → 🛡️₂ → 🗂️
- ✅ **Fixed state propagation** - memories_count and extracted_memories added to SwarmState
- ✅ 70 tests passing, 85% coverage

### Next Steps
**Phase 3: The Ledger - Memory System**
Persistent long-term memory with semantic search:
1. SQLite database schema implementation
2. ChromaDB vector store integration
3. Flash agent real memory retrieval (replace mock)
4. Parser agent write to database
5. Cooldown filter (24hr default)
6. Memory consolidation and importance decay

## GitHub Project Management

**Repository:** https://github.com/deversmann/black-box

**Milestones:**
- [Phase 2: Complete Agent Suite](https://github.com/deversmann/black-box/milestone/2) (In Progress)
- [Phase 3: The Ledger - Memory System](https://github.com/deversmann/black-box/milestone/3)
- [Phase 4: Production Readiness](https://github.com/deversmann/black-box/milestone/4)
- [Phase 5: Advanced Features](https://github.com/deversmann/black-box/milestone/5)

**Wave Labels:**
- `phase-2-wave-1` - Shield & Sensor (COMPLETE ✅)
- `phase-2-wave-2` - Vault & Probe (COMPLETE ✅)
- `phase-2-wave-3` - Aura & Parser (COMPLETE ✅)

**Closed Issues (Phase 2):**
- [#1 Add Vault agent](https://github.com/deversmann/black-box/issues/1) - Wave 2 ✅
- [#2 Add Probe agent](https://github.com/deversmann/black-box/issues/2) - Wave 2 ✅
- [#3 Add Aura agent](https://github.com/deversmann/black-box/issues/3) - Wave 3 ✅
- [#4 Add Parser agent](https://github.com/deversmann/black-box/issues/4) - Wave 3 ✅

**Open Bug Issues:**
- [#5 Associative Slider: Investigate behavior](https://github.com/deversmann/black-box/issues/5)
- [#6 Double counting in retry scenarios](https://github.com/deversmann/black-box/issues/6)
- [#7 Extract "Running..." logic](https://github.com/deversmann/black-box/issues/7)
- [#8 Implement application-wide logging system](https://github.com/deversmann/black-box/issues/8)

**Access via gh CLI:**
- List issues: `gh issue list --milestone "Phase 2: Complete Agent Suite"`
- View issue: `gh issue view 1`
- Create issue: `gh issue create --milestone 2 --label "phase-2-wave-2,agent"`

## Technology Stack (Final Decisions)
- **Language:** Python 3.11+
- **Orchestration:** LangGraph (type-safe state, DAG viz, conditional branching)
- **AI Provider:** OpenRouter.ai (OpenAI API compatible)
- **Models:** gpt-4o (Command, Aura, Probe), gpt-4o-mini (others)
- **Database:** SQLite + SQLAlchemy
- **Vector Store:** ChromaDB (embedded)
- **API:** FastAPI
- **Frontend:** Streamlit (MVP), React (future)
- **Deployment:** Docker + Docker Compose

## Key Architecture Concepts

### Phase 1 Agents (Implemented)

1. **Sieve** - Intent distillation + detail level detection
   - Parses user intent into bullet points
   - Detects BRIEF/DETAILED/COMPREHENSIVE request
   - Resolves pronouns using last 3 turns of context
   - Output: `DETAIL_LEVEL: X\nINTENT: bullets`

2. **Flash** - Memory retrieval (mock)
   - Returns 3 hardcoded memories for testing
   - Phase 3 will use real ChromaDB vector search

3. **Command** - Master synthesizer with context sandwich
   - Receives 5-layer context: Intent → Memories → History → Current
   - 3 modes: BRIEF (500 tokens), DETAILED (800), COMPREHENSIVE (2200)
   - Conversational by default, detailed on request
   - Receives Verdict feedback on retry

4. **Verdict** - Response validation with truncation detection
   - Priority checks: Truncation → Length → Tone → Completeness
   - Passes specific feedback to Command on failure
   - Validates against expected detail_level

### Phase 2 Agents

5. **Shield** - Safety validation (2-pass: input + output) ✅
   - Pass 1: User input safety check (blocks unsafe input)
   - Pass 2: Response output safety check (blocks unsafe output)
   - Three profiles: STRICT (strict filtering), BALANCED (default), EXPERIMENTAL (minimal)
   - Returns SAFE/UNSAFE with reasoning

6. **Sensor** - Mood detection and P(tangent) calculation ✅
   - Detects 6 mood states: JOVIAL (+0.2), CURIOUS (+0.1), NEUTRAL (0.0), FOCUSED (-0.1), FRUSTRATED (-0.2), HURRIED (-0.2)
   - Calculates P(tangent) = base_slider + mood_modifier (clamped [0.0, 1.0])
   - Runs in parallel with Sieve for efficiency

7. **Vault** - Relational DB queries ✅
   - Returns 5 mock facts for Phase 2
   - Phase 3 will query real SQLite database
   - Provides factual context to Command

8. **Probe** - Logic validation with veto power ✅
   - Validates logical coherence, relevance, tangent appropriateness
   - Can APPROVE, VETO, or SUGGEST
   - Triggers Command retry on VETO

9. **Aura** - Narrative enhancement (P(tangent) ≥ 0.7) ✅
   - Adds creative flair, metaphors, sensory details
   - Only activates when P(tangent) crosses 0.7 threshold
   - Maintains factual accuracy

10. **Parser** - Memory extraction with atomic rewriting ✅
    - Extracts 6 memory types with tags and importance
    - Resolves pronouns for self-contained memories
    - Phase 2: JSON extraction only (no storage)
    - Phase 3: will write to The Ledger

### The Ledger (Memory System)
Hybrid database:
- SQLite for structure (memories, tags, sessions, interactions)
- ChromaDB for semantic vector search
- 6 memory types: USER_FACT, USER_STORY, AI_LOGIC, TASK/GOAL, PREFERENCE, RELATIONSHIP
- Cooldown filter (24hr default) prevents repetition
- Atomic memories (self-contained, no unresolved pronouns)

### Associative Personality
```
P(tangent) = Slider (0.0-1.0) + MoodModifier (±0.2)
```
- At P(tangent) ≥ 0.7, Aura activates for narrative flair
- Sensor detects mood: JOVIAL (+0.2), FRUSTRATED (-0.2), etc.
- Thresholds adjust based on tangent probability

## Critical Implementation Details

### Context Sandwich Structure (Implemented)
Command receives context in priority order:
1. **System Prompt** - Adapted to detail_level (BRIEF/DETAILED/COMPREHENSIVE)
2. **Core Intent** (pinned) - From Sieve, prevents conversational drift
3. **Flash Memories** - Long-term semantic context (mock in Phase 1)
4. **Sliding Window** - Last 10 turns (20 messages) for conversational flow
5. **Active Workspace** - Current user message + state

This structure ensures agents have the right context at the right priority.

### Detail Level Detection (Implemented)
Sieve detects user's desired response length:
- **BRIEF** (default): "What are decorators?" → 500 tokens (~300 words)
- **DETAILED**: "Explain decorators in detail with examples" → 800 tokens
- **COMPREHENSIVE**: "Give me everything about decorators" → 1200 tokens

Triggers passed through state, Command adjusts prompt + token budget.

### Truncation Handling (Implemented)
Verdict detects mid-sentence cutoffs:
1. Check if response ends with punctuation (. ? ! " etc.)
2. If not → FAIL with specific feedback
3. Command receives feedback on retry
4. Max 2 retries before giving up

Prevents user from seeing incomplete responses.

### Model Tiering (Phase 1)
- **Fast** (gpt-5.4-nano): Sieve, Flash, Verdict
- **High-reasoning** (gpt-5.4): Command
Target: < 2s for simple queries (achieved with mocks)

### Conversational Tone (Implemented)
All prompts emphasize:
- "You're chatting, not teaching a class"
- Brief by default, detailed on request
- Everyday language, not textbook language
- Offer to expand rather than dumping everything

### Implemented Features (Phase 2)

**Atomic Memory Rewriting:** ✅
Parser makes memories self-contained:
```
Input: "It broke yesterday"
Context: Previous mention of "Honda Shadow"
Output: "The user's Honda Shadow motorcycle broke yesterday"
```
Implementation: Conversation context injection + pronoun resolution prompting

**Parallelization via LangGraph:** ✅
- Sieve + Sensor run in parallel (asyncio.gather)
- Conditional: Aura only if P(tangent) ≥ 0.7
- Verdict → Shield Pass 2 (sequential for semantics)

### Future Implementation (Phase 3+)

**Cooldown Filter:**
In-memory cache → DB check → background cleanup
Prevents mentioning same memory twice in 24 hours (configurable)

**The Ledger Storage:**
- Parser writes extracted memories to SQLite + ChromaDB
- Flash retrieves real memories via semantic search
- Memory importance decay over time
- Memory consolidation (merge similar memories)

## User Preferences

The user (project creator):
- Values **detailed planning** and documentation before coding
- Wants **phased approach** with MVP first
- Chose **full 11-agent system** (not simplified)
- Emphasizes **maintainability and extensibility**
- Plans to **open source** (MIT license)
- Building **personal assistant** for general use across domains
- Wants assistant to **get to know them** like a friend would
- **UI preferences:**
  - Likes real-time agent visualization during execution
  - Wants both in-chat status updates AND sidebar metadata panel
  - Interested in graphical DAG visualization (start with LangGraph built-in)

## Files to Reference

- **SPEC.md** - Comprehensive technical specification (500+ lines)
- **README.md** - Public-facing documentation
- **LICENSE** - MIT open source license
- **config/default.yaml** - Configuration reference (in SPEC.md)

## Phase 1 Session Summary (2026-04-09)

**What We Built:**
- Complete 4-agent MVP with conversational intelligence
- Sliding window context (10 turns) for natural conversation flow
- Detail level detection (BRIEF/DETAILED/COMPREHENSIVE)
- Truncation detection and automatic retry with feedback
- Conversational tone tuning - brief by default, detailed on request
- 23 tests passing, 87% coverage

**Key Decisions Made:**
- **Context sandwich** structure for agent prompts (user's idea ✨)
- Brief responses by default (~300 words) with auto-expansion on request
- Truncation detection as #1 priority in Verdict
- Feedback loop between Verdict and Command
- Two types of tangents identified: USER_TANGENT vs AI_TANGENT (for Phase 2)

**Ready for Phase 2:**
- Intent lifecycle tracking (CONTINUATION, USER_TANGENT, AI_TANGENT, SATISFIED_NEW, NEW)
- 7 additional agents (Shield, Sensor, Vault, Probe, Aura, Parser)
- P(tangent) calculation with mood modifiers
- Safety profile enforcement
- **UI enhancements:**
  - Metadata sidebar panel (mood, P(tangent), detail level, Aura status, safety profile)
  - Enhanced agent status messages showing metadata details

## When User Returns

**Phase 2 is COMPLETE! 🎉** Recent sessions (2026-04-10 to 2026-04-11):
- ✅ All 10 agents implemented and tested (70 tests passing)
- ✅ Wave 1: Shield + Sensor (safety + mood detection)
- ✅ Wave 2: Vault + Probe (facts + logic validation)
- ✅ Wave 3: Aura + Parser (narrative enhancement + memory extraction)
- ✅ Fixed state propagation bug (memories_count in SwarmState)
- ✅ All GitHub issues closed for Phase 2

**Commits:**
- efe020a: Update documentation (Phase 2 Wave 1 status)
- 387f2af: Fix UI/UX issues (sidebar, p_tangent, ghost messages)
- 0e2396c: Add Shield and Sensor agents (Wave 1)
- 6c8c26b: Add Vault and Probe agents (Wave 2)
- b5f2a3d: Add Aura agent (Wave 3)
- ece4791: Add Parser agent (Wave 3)

**They'll likely want to:**
1. **Test the complete system** - All 10 agents working together
2. **Address open bugs:**
   - [#5 Associative Slider behavior](https://github.com/deversmann/black-box/issues/5)
   - [#6 Double counting in retries](https://github.com/deversmann/black-box/issues/6)
   - [#7 Extract "Running..." logic](https://github.com/deversmann/black-box/issues/7)
   - [#8 Implement logging system](https://github.com/deversmann/black-box/issues/8)
3. **Begin Phase 3: The Ledger** - Persistent memory with SQLite + ChromaDB
   - Database schema implementation
   - Flash agent real memory retrieval
   - Parser agent write to database
   - Cooldown filter

**Remember:** 
- User values detailed planning before coding
- Chose full 11-agent system (not simplified)
- Emphasizes maintainability and extensibility
- Building for personal use but plans to open source
- Wants assistant to "get to know them" like a friend would
- **Uses GitHub issues** for task tracking - check open issues before planning work

## Quick Reference: Phase 1 Critical Files

```
/black-box/
├── pyproject.toml              # Dependencies: langgraph, chromadb, fastapi, streamlit, sqlalchemy
├── .env.example                # OPENROUTER_API_KEY
├── config/default.yaml         # Agent configs, models, thresholds
├── src/blackbox/
│   ├── core/
│   │   ├── agent.py           # Base Agent ABC
│   │   ├── state.py           # SwarmState TypedDict
│   │   └── orchestrator.py    # LangGraph graph
│   ├── agents/
│   │   ├── sieve.py
│   │   ├── flash.py           # Mock version for Phase 1
│   │   ├── command.py
│   │   └── verdict.py
│   └── models/
│       └── client.py          # OpenRouter client
└── frontend/
    └── app.py                 # Streamlit UI
```

---

**Last Session:** Phase 2 Complete - All 10 agents implemented (Wave 1, 2, 3) (2026-04-11)
**Next Session:** Address open bugs or begin Phase 3 - The Ledger ([view issues](https://github.com/deversmann/black-box/issues))
