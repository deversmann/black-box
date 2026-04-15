# Black Box Swarm 🧠

A sophisticated multi-agent AI system designed as a personal learning assistant that builds deep familiarity with you over time.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Version 0.3.0](https://img.shields.io/badge/version-0.3.0-brightgreen.svg)](https://github.com/deversmann/black-box/releases)
[![Issues](https://img.shields.io/github/issues/deversmann/black-box)](https://github.com/deversmann/black-box/issues)

## What is Black Box Swarm?

Unlike traditional chatbots that treat every conversation as new, Black Box Swarm **learns, remembers, and develops personality** through an architecture of 11 specialized AI agents working in coordination.

Think of it as a personal assistant that:
- 📚 **Remembers your life** - facts, stories, preferences, relationships, goals
- 🎭 **Adapts to your mood** - detects if you're jovial, frustrated, or hurried
- 🎨 **Balances creativity and precision** - you control how tangential or focused it gets
- 🛡️ **Stays safe** - multi-layer safety validation
- 🧩 **Grows with you** - learns from every conversation

## The Swarm Architecture

The system uses a **Decoupled Swarm** pattern where specialized agents handle distinct responsibilities:

### 🔍 Ingress Layer (Input Processing)
- **Shield** - Safety validation (input & output)
- **Sieve** - Distills your intent from noise
- **Sensor** - Detects your emotional state

### 🧠 Context Layer (Memory Retrieval)
- **Flash** - Lightning-fast semantic memory search
- **Vault** - Queries factual knowledge database

### ✨ Synthesis Layer (Creation)
- **Probe** - Stress-tests logic, vetoes nonsense
- **Aura** - Adds narrative flair (when you want it)
- **Command** - Master synthesizer, weaves everything together

### ✅ Egress Layer (Validation & Learning)
- **Verdict** - Final quality check
- **Shield (Pass 2)** - Output safety sweep
- **Parser** - Extracts memories for The Ledger

## The Ledger: Your Personal Memory System

All memories are stored in **The Ledger**, a hybrid database that combines:
- **Relational data** (SQLite) - Facts, tags, relationships
- **Vector embeddings** (ChromaDB) - Semantic similarity search

**Memory Types:**
- `USER_FACT` - Factual information about you
- `USER_STORY` - Your anecdotes and narratives
- `AI_LOGIC` - Reasoning patterns that work well for you
- `TASK/GOAL` - Your ongoing projects and objectives
- `PREFERENCE` - Your likes, dislikes, communication style
- `RELATIONSHIP` - People in your life and their context

**Smart Features:**
- ⏰ **Cooldown filter** - Won't mention the same thing repeatedly
- 🔍 **Semantic search** - Finds relevant memories by meaning, not keywords
- 🧬 **Atomic memories** - Self-contained, no confusing pronouns

## The Associative Slider

Control how creative and tangential the assistant gets:

```
P(tangent) = Your Slider (0.0-1.0) + Mood Modifier (±0.2)
```

- **Low (0.0-0.3)**: Precise, factual, straight to the point
- **Medium (0.4-0.6)**: Balanced, some context and color
- **High (0.7-1.0)**: Creative, narrative-rich, tangential stories

The **Aura** agent (storyteller) activates when `P(tangent) ≥ 0.7`, transforming dry facts into vivid narratives.

## Technology Stack

- **Language:** Python 3.11+
- **Orchestration:** [LangGraph](https://github.com/langchain-ai/langgraph) - Type-safe agent coordination with DAG visualization
- **AI Provider:** [OpenRouter.ai](https://openrouter.ai) - Single endpoint for multiple LLM providers
- **Database:** SQLite + SQLAlchemy (relational) + ChromaDB (vector)
- **API:** FastAPI (async, WebSocket support)
- **Frontend:** Streamlit (Phase 1), React (future)
- **Deployment:** Docker + Docker Compose

### Model Tiering for Cost Optimization

- **High-reasoning agents** (Command, Aura, Probe): GPT-4o
- **Fast agents** (Shield, Sieve, Sensor, Vault, Parser): GPT-4o-mini

## Implementation Roadmap

### ✅ Phase 0: Design (Complete)
- [x] Conceptual architecture
- [x] Technical specification (SPEC.md)
- [x] Database schemas
- [x] Configuration design

### ✅ Phase 1: Core Swarm MVP (COMPLETE - 2026-04-09)
**Goal:** Prove the swarm pattern works end-to-end with conversational intelligence

**Agents:** Sieve → Flash (mock) → Command → Verdict

**Delivered:**
- ✅ LangGraph orchestration with conditional retry
- ✅ OpenRouter integration (gpt-4o / gpt-4o-mini)  
- ✅ Streamlit chat interface with session tracking
- ✅ Sliding window context (10 turns)
- ✅ Detail level detection (BRIEF/DETAILED/COMPREHENSIVE)
- ✅ Truncation handling with auto-retry
- ✅ Real-time agent visualization with st.status
- ✅ 23 tests passing, 87% coverage

### ✅ Phase 1.5: Agent Visualization (COMPLETE - 2026-04-09)
**Delivered:**
- ✅ Live progress display using LangGraph's astream()
- ✅ Agent icons and descriptions in UI
- ✅ Foundation for parallel agent visualization

### ✅ Phase 2: Complete Agent Suite (COMPLETE - 2026-04-11)
**Goal:** All 10 agents implemented with full personality system

#### ✅ Wave 1: Shield + Sensor (COMPLETE - 2026-04-10)
- ✅ **Shield agent** - Two-pass safety validation (input + output)
- ✅ **Sensor agent** - Mood detection and P(tangent) calculation
- ✅ Parallel execution (Sieve + Sensor run concurrently)
- ✅ Metadata sidebar panel (mood, P(tangent), detail level, safety profile)
- ✅ P(tangent) slider integration
- ✅ Sieve expansion continuation pattern detection
- ✅ 43 tests passing, 87% coverage

#### ✅ Wave 2: Vault + Probe (COMPLETE - 2026-04-11)
- ✅ **Vault agent** - Relational database queries (mock for Phase 2)
- ✅ **Probe agent** - Logic validation with veto power
- ✅ Conditional routing (Probe → retry OR Aura OR Verdict)
- ✅ Mood-aware validation (strict with HURRIED, lenient with JOVIAL)
- ✅ 62 tests passing, 85% coverage

#### ✅ Wave 3: Aura + Parser (COMPLETE - 2026-04-11)
- ✅ **Aura agent** - Narrative enhancement (activates at P(tangent) ≥ 0.7)
- ✅ **Parser agent** - Memory extraction with atomic rewriting
- ✅ 6 memory types with tags and importance scores
- ✅ Extracted memories displayed in Debug Info panel
- ✅ Fixed state propagation bug (memories_count in SwarmState)
- ✅ 70 tests passing, 85% coverage

### ✅ Phase 2.5: Infrastructure & Bug Fixes (COMPLETE - 2026-04-15)
**Goal:** Production-ready logging and UI polish

**UI/UX Fixes ([Issues #5-7](https://github.com/deversmann/black-box/issues)):**
- ✅ Fixed metadata panel one-turn delay issue
- ✅ Fixed state accumulation bug (Parser overwrote Sensor's mood)
- ✅ Moved status bubbles to appear before responses
- ✅ Made status bubbles persistent in chat history
- ✅ Enhanced agent status messages (full Probe reasoning, Verdict failure details)

**Logging System ([Issue #8](https://github.com/deversmann/black-box/issues/8)):**
- ✅ **Structured JSON logging** with JSONFormatter
- ✅ **Agent execution timing** (automatic via base class wrapper)
- ✅ **API call logging** (latency, tokens, retries, backoff delays)
- ✅ **Orchestrator flow logging** (routing decisions, retries)
- ✅ **Log rotation** (10MB files, 5 backups = ~50MB max)
- ✅ **Sensitive data redaction** (API keys, passwords, tokens)
- ✅ **<2% performance overhead** on typical execution times
- ✅ **Queryable logs** with jq (find errors, calculate averages, trace sessions)

**Log Files:**
- Logs written to `./logs/swarm.log` in structured JSON format
- Each log entry includes: timestamp, level, logger, event_type, data, correlation_id

**Example log queries:**
```bash
# View all logs
jq '.' logs/swarm.log

# Find slow agents (>1s execution time)
jq 'select(.event_type == "agent_execution_complete" and .data.duration_ms > 1000)' logs/swarm.log

# Calculate average API latency
jq -s 'map(select(.event_type == "api_call_complete")) | map(.data.latency_ms) | add/length' logs/swarm.log

# Trace a specific session
jq --arg session "session_20260415_103045" 'select(.correlation_id == $session)' logs/swarm.log
```

### 📋 Phase 3: The Ledger (NEXT - [Milestone](https://github.com/deversmann/black-box/milestone/3))
Persistent memory with semantic search and cooldown filter

**Planned Features:**
- SQLite database schema for relational memory storage
- ChromaDB vector store for semantic similarity search
- Flash agent real memory retrieval (replace mock)
- Parser agent write to database
- Cooldown filter (24hr default to prevent repetition)
- Memory consolidation and importance decay

### 📋 Phase 4: Production Readiness ([Milestone](https://github.com/deversmann/black-box/milestone/4))
Testing, monitoring, Docker deployment, documentation

**Planned Features:**
- Comprehensive integration tests
- LangGraph DAG visualization for execution flow display
- Application-wide logging system
- Docker + Docker Compose deployment
- CI/CD pipeline
- Performance monitoring and metrics

### 📋 Phase 5: Advanced Features ([Milestone](https://github.com/deversmann/black-box/milestone/5))
Memory consolidation, caching, plugin system, preference learning

**Planned Features:**
- Advanced memory consolidation strategies
- Response caching for common queries
- Plugin system for custom agents
- Adaptive preference learning
- Multi-user support

## Quick Start

### Prerequisites

- Python 3.11 or higher
- OpenRouter API key ([get one here](https://openrouter.ai))
- Poetry or uv for dependency management

### Installation

```bash
# Clone the repository
git clone https://github.com/deversmann/black-box.git
cd black-box

# Install dependencies
poetry install

# Copy environment template
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# Run the Streamlit UI
streamlit run frontend/app.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=blackbox --cov-report=html

# Run specific test file
pytest tests/test_agents/test_sieve.py
```

### Docker (Future)

```bash
# Start the entire stack
docker-compose up

# Access the UI at http://localhost:8501
# API at http://localhost:8000
# Metrics at http://localhost:9090
```

## Configuration

The system is highly configurable via YAML files in `config/`:

```yaml
# Associative behavior
associative:
  default_p_tangent: 0.5
  aura_activation_threshold: 0.7
  mood_modifiers:
    jovial: 0.2
    frustrated: -0.2

# Memory thresholds
memory:
  cooldown_hours: 24
  thresholds:
    user_fact: 0.9      # High precision
    user_story: 0.7     # More recall

# Safety profile
safety:
  default_profile: "balanced"  # strict, balanced, experimental
```

## Project Structure

```
/black-box/
├── SPEC.md                   # Comprehensive technical specification
├── README.md                 # This file
├── LICENSE                   # MIT License
├── config/                   # Configuration files
├── src/blackbox/
│   ├── core/                 # Base abstractions (Agent, Orchestrator)
│   ├── agents/               # 11 specialized agents
│   ├── db/                   # Memory system (Ledger)
│   ├── models/               # LLM client
│   ├── plugins/              # Extensibility system
│   ├── api/                  # FastAPI backend
│   └── cli.py                # Admin CLI tools
├── frontend/                 # Streamlit UI
├── tests/                    # Comprehensive test suite
├── data/                     # Database and vector storage (gitignored)
└── docs/                     # Additional documentation
```

## Key Features in Detail

### 🛡️ Multi-Layer Safety
- **Pass 1:** Validate user input before processing
- **Pass 2:** Validate AI output before delivery
- **Configurable profiles:** Strict, Balanced, Experimental

### 🎯 Intent-Driven Responses
The **Sieve** agent distills your rambling questions into crisp intent signals, ensuring the system stays on target.

### 🧪 Logic Validation
The **Probe** agent acts as devil's advocate, vetoing responses that are logically incoherent or inappropriate given your mood.

### 📊 Observability
- Structured JSON logging
- Prometheus metrics (agent latency, memory hit rates, etc.)
- LangGraph DAG visualization

### 🔌 Extensibility
- Plugin system for adding new capabilities (web search, code execution, etc.)
- Easy to add new agent types
- Configurable memory types via tags

## Contributing

This is a personal project currently in early development. Contributions, ideas, and feedback are welcome!

### GitHub Issues & Milestones

Work is organized using GitHub Issues with milestones for each phase:

- **[Phase 2: Complete Agent Suite](https://github.com/deversmann/black-box/milestone/2)** (In Progress)
- **[Phase 3: The Ledger](https://github.com/deversmann/black-box/milestone/3)** (Planned)
- **[Phase 4: Production Readiness](https://github.com/deversmann/black-box/milestone/4)** (Planned)
- **[Phase 5: Advanced Features](https://github.com/deversmann/black-box/milestone/5)** (Planned)

**Labels:**
- `phase-2-wave-1`, `phase-2-wave-2`, `phase-2-wave-3` - Phase 2 waves
- `agent` - Agent-specific work
- `ui/ux` - User interface and experience
- `testing` - Test coverage and quality
- `bug`, `enhancement`, `documentation` - Standard labels

[View all open issues →](https://github.com/deversmann/black-box/issues)

### Development Setup

```bash
# Install development dependencies
poetry install --with dev

# Run tests
pytest

# Run with coverage
pytest --cov=blackbox --cov-report=html

# Run linter
ruff check src/

# Format code
black src/
```

### Workflow

1. Pick an issue from the [current milestone](https://github.com/deversmann/black-box/milestone/2)
2. Create a feature branch: `git checkout -b feature/vault-agent`
3. Implement with tests (target 80%+ coverage)
4. Update CHANGELOG.md with your changes
5. Commit with co-authorship: `Co-Authored-By: Your Name <email@example.com>`
6. Submit a pull request

## Roadmap & Vision

**Short Term (Phase 1-3):**
- Working MVP with core agents
- Persistent memory system
- Web chat interface

**Medium Term (Phase 4-5):**
- Production-ready deployment
- Plugin system
- Mobile app

**Long Term:**
- Multi-user support
- Voice interface
- Advanced preference learning
- Self-hosted model support
- Calendar, email, web search integration

## Architecture Decisions

### Why 11 Agents?
Separation of concerns. Each agent is a specialist:
- Easier to debug (which agent is misbehaving?)
- Better cost control (use cheap models for simple tasks)
- Parallelization opportunities (run independent agents concurrently)
- Maintainability (swap out agents without touching others)

### Why LangGraph?
- Type-safe state management
- Built-in DAG visualization
- Conditional branching (retry logic, Aura activation)
- Native streaming support
- Active development and community

### Why Hybrid Database?
- **SQLite:** Simple for single-user, easy to backup, zero configuration
- **ChromaDB:** Semantic search requires vector embeddings
- Easy migration path to PostgreSQL + pgvector for multi-user

## Performance Targets

- **Simple query:** < 2 seconds
- **Complex query:** < 4 seconds
- **High tangent (Aura active):** < 5 seconds
- **Memory scale:** 10,000+ memories without degradation

## Challenges & Solutions

### 1. Atomic Memory Rewriting
**Problem:** Parser must ensure memories are self-contained (no unresolved pronouns).

**Solution:** Few-shot prompting + entity tracking + context injection

### 2. Cooldown Filter Efficiency
**Problem:** Track memory usage per session without slowing search.

**Solution:** In-memory cache + DB index + background cleanup

### 3. Threshold Tuning
**Problem:** Similarity thresholds that work across query types.

**Solution:** Dynamic adjustment based on P(tangent) + per-user calibration + A/B testing

### 4. Latency Management
**Problem:** 11 agents could be slow.

**Solution:** Aggressive parallelization + model tiering + streaming + speculative execution

## Documentation

- **[SPEC.md](SPEC.md)** - Comprehensive technical specification
- **[docs/architecture.md](docs/architecture.md)** - Architecture deep dive *(coming soon)*
- **[docs/agent-reference.md](docs/agent-reference.md)** - Per-agent documentation *(coming soon)*
- **[docs/api-reference.md](docs/api-reference.md)** - API endpoints *(coming soon)*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Inspired by the vision of AI assistants that truly learn and grow with their users, moving beyond stateless chatbots toward genuine digital companionship.

---

**Status:** Phase 2 Wave 1 complete (Shield + Sensor). Wave 2 next (Vault + Probe).

**Questions?** [Open an issue](https://github.com/deversmann/black-box/issues/new) or check the [milestone tracker](https://github.com/deversmann/black-box/milestone/2)!
