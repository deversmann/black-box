# Claude Code Context

This file helps Claude Code understand the project context when you return.

## Project: Black Box Swarm
**Status:** Phase 2 Wave 1 Complete - Shield & Sensor Added  
**Date:** 2026-04-10

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

### Next Steps
**Phase 2 Wave 2: Vault + Probe**
Add remaining validation and data agents:
1. Vault (DB queries - mock initially) - [Issue #1](https://github.com/deversmann/black-box/issues/1)
2. Probe (logic validation) - [Issue #2](https://github.com/deversmann/black-box/issues/2)

## GitHub Project Management

**Repository:** https://github.com/deversmann/black-box

**Milestones:**
- [Phase 2: Complete Agent Suite](https://github.com/deversmann/black-box/milestone/2) (In Progress)
- [Phase 3: The Ledger - Memory System](https://github.com/deversmann/black-box/milestone/3)
- [Phase 4: Production Readiness](https://github.com/deversmann/black-box/milestone/4)
- [Phase 5: Advanced Features](https://github.com/deversmann/black-box/milestone/5)

**Wave Labels:**
- `phase-2-wave-1` - Shield & Sensor (COMPLETE)
- `phase-2-wave-2` - Vault & Probe (NEXT)
- `phase-2-wave-3` - Aura & Parser

**Open Issues:**
- [#1 Add Vault agent](https://github.com/deversmann/black-box/issues/1) - Wave 2
- [#2 Add Probe agent](https://github.com/deversmann/black-box/issues/2) - Wave 2
- [#3 Add Aura agent](https://github.com/deversmann/black-box/issues/3) - Wave 3
- [#4 Add Parser agent](https://github.com/deversmann/black-box/issues/4) - Wave 3

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

7. **Vault** - Relational DB queries (Planned)
8. **Probe** - Logic validation, can veto (Planned)
9. **Aura** - Narrative enhancement (P(tangent) ≥ 0.7) (Planned)
10. **Parser** - Memory extraction & storage (Planned)

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

### Future Implementation (Phase 2+)

**Atomic Memory Rewriting:**
Parser must make memories self-contained:
```
Input: "It broke yesterday"
Context: Previous mention of "Honda Shadow"
Output: "The user's Honda Shadow motorcycle broke yesterday"
```
Solution: Few-shot prompting + entity tracking + context injection

**Cooldown Filter:**
In-memory cache → DB check → background cleanup
Prevents mentioning same memory twice in 24 hours (configurable)

**Parallelization via LangGraph:**
- Sieve + Sensor run in parallel
- Verdict + Shield Pass 2 run in parallel
- Conditional: Aura only if P(tangent) ≥ 0.7

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

**Phase 2 Wave 1 is complete!** Recent session (2026-04-10):
- ✅ Fixed all UI/UX bugs (sidebar updates, ghost messages, p_tangent slider)
- ✅ Added Sieve expansion continuation detection
- ✅ Created GitHub milestones and issues for remaining work
- ✅ Committed UI/UX fixes (commit 387f2af)

**They'll likely want to:**
1. Continue Phase 2 Wave 2: Vault + Probe agents
   - [Issue #1: Add Vault agent](https://github.com/deversmann/black-box/issues/1)
   - [Issue #2: Add Probe agent](https://github.com/deversmann/black-box/issues/2)
2. Test the system with various conversation patterns
3. Eventually: Wave 3 (Aura + Parser), then Phase 3 (The Ledger)

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

**Last Session:** Phase 2 Wave 1 UI/UX bug fixes + GitHub project setup (2026-04-10)
**Next Session:** Begin Phase 2 Wave 2 - Vault + Probe agents ([view issues](https://github.com/deversmann/black-box/milestone/2))
