# Claude Code Context - Black Box Swarm

Multi-agent AI learning assistant | Phase 2.5 Complete | 10 agents + logging | 70 tests, 85% coverage

**Repo:** https://github.com/deversmann/black-box  
**Docs:** docs/STATUS.md (roadmap), docs/architecture/ (design), docs/guides/ (development)

## Current State

**Phase 2.5 Complete** (2026-04-15) - All 10 agents operational, logging system implemented, UI/UX polished
- Recent: Structured JSON logging (issue #8), UI bug fixes (issues #5-7)
- Next: Phase 3 - The Ledger (persistent memory with SQLite + ChromaDB)

**Phases:**
- ✅ 0: Design complete
- ✅ 1: Core 4-agent MVP (Sieve, Flash-mock, Command, Verdict) - conversational intelligence, truncation detection
- ✅ 1.5: Real-time agent visualization (st.status, astream)
- ✅ 2.1: Shield (2-pass safety) + Sensor (mood → P(tangent))
- ✅ 2.2: Vault (mock DB) + Probe (logic veto)
- ✅ 2.3: Aura (narrative @P≥0.7) + Parser (memory extraction)
- ✅ 2.5: JSON logging system + UI fixes
- 📋 3: The Ledger (persistent memory)

**Recent Commits:**
- e384e2b: Update documentation: Phase 2.5 complete
- 79ad072: Implement JSON logging system
- a9b06d9: Fix metadata panel + state accumulation bug
- 0c51af4: Move status bubbles before responses

## Stack

Python 3.11+ | LangGraph | OpenRouter (gpt-4o / gpt-4o-mini) | SQLite + ChromaDB | Streamlit | FastAPI

**Model Tier:**
- High-reasoning (gpt-4o): Command, Aura, Probe
- Fast (gpt-4o-mini): Shield, Sieve, Sensor, Flash, Vault, Verdict, Parser

## Agent Roster

**Ingress (Input):**
- 🛡️ Shield: 2-pass safety (Pass 1 input, Pass 2 output) | 3 profiles: STRICT/BALANCED/EXPERIMENTAL
- 🔍 Sieve: Intent distillation + detail level (BRIEF/DETAILED/COMPREHENSIVE) + pronoun resolution
- 🎭 Sensor: Mood detection (JOVIAL/CURIOUS/NEUTRAL/FOCUSED/FRUSTRATED/HURRIED) | calculates P(tangent) = slider + mood_modifier

**Context (Memory):**
- 💾 Flash: Vector search in The Ledger (Phase 2: mock, Phase 3: real ChromaDB)
- 📚 Vault: Relational DB queries (Phase 2: mock, Phase 3: real SQLite)

**Synthesis (Creation):**
- 🧠 Command: Master synthesizer | receives 5-layer context sandwich (Intent → Memories → History → Current)
- 🔬 Probe: Logic validator | can APPROVE/VETO/SUGGEST | triggers Command retry on VETO
- ✨ Aura: Narrative enhancer | activates when P(tangent) ≥ 0.7 | temp 0.9 for creative flair

**Egress (Validation):**
- ✅ Verdict: Response validator | checks intent satisfaction + truncation + completeness | passes feedback to Command on fail
- 🛡️ Shield Pass 2: Output safety check
- 🗂️ Parser: Memory extractor | 6 types (user_fact, user_story, task_goal, preference, relationship, ai_logic) | Phase 2: JSON only, Phase 3: write to DB

**Flow:** Shield₁ → (Sieve ∥ Sensor) → Flash → Vault → Command → Probe → (Aura if P≥0.7) → Verdict → Shield₂ → Parser

## Critical Patterns

**Context Sandwich** (Command receives in priority order):
1. System prompt (adapted to detail_level)
2. Core intent (from Sieve, pinned)
3. Flash memories (long-term semantic)
4. Sliding window (last 10 turns)
5. Active workspace (current message + state)

**Atomic Rewriting** (Parser):
```python
# Input: "It broke yesterday"
# Context: Previous mention "Honda Shadow motorcycle"
# Output: "The user's Honda Shadow motorcycle broke yesterday"
# Implementation: Conversation context injection + pronoun resolution prompting
```

**Parallelization:**
```python
# Sieve + Sensor run concurrently
sieve_result, sensor_result = await asyncio.gather(
    self._run_sieve(state),
    self._run_sensor(state)
)
# Verdict + Shield Pass 2 run sequentially (semantics matter)
```

**State Management:**
- SwarmState is TypedDict (immutable by convention)
- Create new objects, don't mutate
- All agents receive + return state

## File Reference

```
src/blackbox/
├── core/
│   ├── agent.py          # Base Agent ABC with execute() wrapper (logging)
│   ├── state.py          # SwarmState TypedDict
│   ├── orchestrator.py   # LangGraph graph + flow logging
│   ├── logging.py        # JSONFormatter, configure_logging, get_logger
│   └── config.py         # Config loader (initializes logging)
├── agents/               # All agents implement _execute_impl()
│   ├── {sieve,flash,command,verdict,shield,sensor,vault,probe,aura,parser}.py
└── models/
    └── client.py         # OpenRouter client + API logging

frontend/app.py           # Streamlit UI with status bubbles
config/default.yaml       # All configs (agents, memory, safety, logging)
logs/swarm.log            # JSON logs (rotated, 10MB × 5 backups)
```

## Commands

```bash
# Run
streamlit run frontend/app.py

# Test
pytest                                    # All
pytest tests/unit/test_agents/           # Agents only
pytest --cov=blackbox --cov-report=html  # With coverage

# Logs
tail -f logs/swarm.log | jq              # Pretty JSON
jq 'select(.event_type == "agent_execution_complete" and .data.duration_ms > 1000)' logs/swarm.log  # Slow agents

# Issues
gh issue list
gh issue view 9
gh issue create --milestone 3 --label "phase-3"
```

## Documentation Rules

**Root:** README.md (concise + QuickStart), CLAUDE.md (this file, minimal), LICENSE  
**docs/:** All detail organized max 1-level deep  
- STATUS.md: Roadmap + completion (update after sessions)
- architecture/: OVERVIEW.md, AGENTS.md, MEMORY.md
- guides/: CONFIGURATION.md, DEVELOPMENT.md, CHALLENGES.md

**Rules:**
- 250-line limit per file (split if needed)
- All docs reachable via link chain from README
- Markdown only
- Update STATUS.md after phase changes/feature completions
- Keep CLAUDE.md compressed (this file: AI context only, no human prose)
