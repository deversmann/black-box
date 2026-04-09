# Claude Code Context

This file helps Claude Code understand the project context when you return.

## Project: Black Box Swarm
**Status:** Design phase complete, ready for Phase 1 implementation  
**Date:** 2026-04-09

## What This Is
Multi-agent AI system for a personal learning assistant that learns, remembers, and develops personality through 11 specialized agents coordinated via LangGraph.

## Current State

### Completed
- ✅ Comprehensive technical specification (SPEC.md)
- ✅ Project structure defined
- ✅ Technology stack chosen
- ✅ Database schemas designed
- ✅ All architectural decisions documented
- ✅ 5-phase implementation roadmap
- ✅ README.md for public consumption
- ✅ MIT LICENSE

### Next Steps
**Phase 1: Core Swarm MVP (Week 1-2)**
Implement 4 core agents to prove the swarm pattern:
1. Sieve (Intent Distiller)
2. Flash (Memory Retrieval - mock initially)
3. Command (Master Synthesizer)
4. Verdict (Validator)

Plus: LangGraph orchestration, OpenRouter integration, Streamlit UI

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

### The 11 Agents
1. **Shield** - Safety (2-pass: input + output)
2. **Sieve** - Intent distillation
3. **Sensor** - Mood detection (JOVIAL, FRUSTRATED, etc.)
4. **Flash** - Semantic memory search
5. **Vault** - Relational DB queries
6. **Probe** - Logic validation, can veto
7. **Aura** - Narrative enhancement (P(tangent) ≥ 0.7)
8. **Command** - Master synthesizer
9. **Verdict** - Response validation
10. **Shield Pass 2** - Output safety
11. **Parser** - Memory extraction & storage

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

### Atomic Memory Rewriting
Parser must make memories self-contained:
```
Input: "It broke yesterday"
Context: Previous mention of "Honda Shadow"
Output: "The user's Honda Shadow motorcycle broke yesterday"
```
Solution: Few-shot prompting + entity tracking + context injection

### Cooldown Filter
In-memory cache → DB check → background cleanup
Prevents mentioning same memory twice in 24 hours (configurable)

### Model Tiering
- Fast/cheap (gpt-4o-mini): Shield, Sieve, Sensor, Vault, Parser
- Powerful (gpt-4o): Command, Aura, Probe
Target: < 2s for simple queries

### Parallelization via LangGraph
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

## Files to Reference

- **SPEC.md** - Comprehensive technical specification (500+ lines)
- **README.md** - Public-facing documentation
- **LICENSE** - MIT open source license
- **config/default.yaml** - Configuration reference (in SPEC.md)

## When User Returns

They'll likely want to:
1. Begin Phase 1 implementation (4-agent MVP)
2. Set up project structure (pyproject.toml, src/, tests/)
3. Implement base abstractions (Agent ABC, SwarmState, Orchestrator)
4. Create first 4 agents
5. Build Streamlit UI

**Remember:** User chose this architecture deliberately. Don't suggest simplifications unless there's a blocking issue. They understand the complexity and want the full vision built incrementally.

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

**Last Session:** Completed comprehensive specification and documentation  
**Next Session:** Begin Phase 1 implementation (Core Swarm MVP)
