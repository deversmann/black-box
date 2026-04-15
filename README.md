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

## Project Status & Roadmap

**Current Phase:** 2.5 Complete ✅ (2026-04-15)

All 10 agents implemented and operational with structured JSON logging system. 70 tests passing, 85% coverage.

### Recent Milestones
- ✅ **Phase 2.5** - Structured JSON logging + UI/UX bug fixes (issues #5-8)
- ✅ **Phase 2** - Complete agent suite (Shield, Sensor, Vault, Probe, Aura, Parser)
- ✅ **Phase 1** - Core 4-agent MVP with conversational intelligence
- ✅ **Phase 0** - Design and technical specification

### Next Up
- 📋 **Phase 3** - The Ledger (persistent memory with SQLite + ChromaDB)
- 📋 **Phase 4** - Production readiness (Docker deployment, comprehensive testing)
- 📋 **Phase 5** - Advanced features (memory consolidation, caching, plugins)

**Detailed roadmap:** [docs/STATUS.md](docs/STATUS.md)  
**GitHub milestones:** https://github.com/deversmann/black-box/milestones

## Quick Start

### Prerequisites

- Python 3.11 or higher
- OpenRouter API key ([get one here](https://openrouter.ai/keys))

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
```

### Run

```bash
# Start the Streamlit UI
streamlit run frontend/app.py

# The app will open at http://localhost:8501
```

### Test

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=blackbox --cov-report=html
```

For detailed setup and troubleshooting, see [docs/guides/CONFIGURATION.md](docs/guides/CONFIGURATION.md).

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

See [docs/guides/CONFIGURATION.md](docs/guides/CONFIGURATION.md) for complete configuration reference.

## Project Structure

```
/black-box/
├── README.md                 # This file
├── LICENSE                   # MIT License
├── config/                   # Configuration files
├── src/blackbox/
│   ├── core/                 # Base abstractions (Agent, Orchestrator, Logging)
│   ├── agents/               # 10 specialized agents
│   ├── db/                   # Memory system (The Ledger)
│   ├── models/               # LLM client (OpenRouter)
│   ├── plugins/              # Extensibility system
│   ├── api/                  # FastAPI backend
│   └── cli.py                # Admin CLI tools
├── frontend/                 # Streamlit UI
├── tests/                    # Comprehensive test suite
├── data/                     # Database and vector storage (gitignored)
├── logs/                     # Structured JSON logs (gitignored)
└── docs/                     # Documentation
    ├── STATUS.md             # Project roadmap and current status
    ├── architecture/         # Architecture documentation
    │   ├── OVERVIEW.md       # System design philosophy
    │   ├── AGENTS.md         # All 10 agent specifications
    │   └── MEMORY.md         # Execution flow & The Ledger
    └── guides/               # Development guides
        ├── CONFIGURATION.md  # Tech stack & configuration
        ├── DEVELOPMENT.md    # Core abstractions & testing
        └── CHALLENGES.md     # Technical challenges & solutions
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
- Structured JSON logging with automatic redaction
- Queryable logs with jq (agent timing, API latency, session tracing)
- <2% performance overhead
- Log rotation (10MB files, 5 backups)

Example log queries:
```bash
# Find slow agents (>1s execution time)
jq 'select(.event_type == "agent_execution_complete" and .data.duration_ms > 1000)' logs/swarm.log

# Calculate average API latency
jq -s 'map(select(.event_type == "api_call_complete")) | map(.data.latency_ms) | add/length' logs/swarm.log

# Trace a specific session
jq --arg session "session_id_here" 'select(.correlation_id == $session)' logs/swarm.log
```

### 🔌 Extensibility
- Plugin system for adding new capabilities (web search, code execution, etc.)
- Easy to add new agent types
- Configurable memory types via tags

## Contributing

This is a personal project currently in early development. Contributions, ideas, and feedback are welcome!

### GitHub Issues & Milestones

Work is organized using GitHub Issues with milestones for each phase:

- **[Phase 3: The Ledger](https://github.com/deversmann/black-box/milestone/3)** (Next)
- **[Phase 4: Production Readiness](https://github.com/deversmann/black-box/milestone/4)** (Planned)
- **[Phase 5: Advanced Features](https://github.com/deversmann/black-box/milestone/5)** (Planned)

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
ruff format src/
```

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

## Documentation

- **[docs/STATUS.md](docs/STATUS.md)** - Project roadmap and current status
- **[docs/architecture/OVERVIEW.md](docs/architecture/OVERVIEW.md)** - System design philosophy
- **[docs/architecture/AGENTS.md](docs/architecture/AGENTS.md)** - All 10 agent specifications
- **[docs/architecture/MEMORY.md](docs/architecture/MEMORY.md)** - Execution flow & The Ledger
- **[docs/guides/CONFIGURATION.md](docs/guides/CONFIGURATION.md)** - Tech stack & configuration
- **[docs/guides/DEVELOPMENT.md](docs/guides/DEVELOPMENT.md)** - Core abstractions & testing
- **[docs/guides/CHALLENGES.md](docs/guides/CHALLENGES.md)** - Technical challenges & solutions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Inspired by the vision of AI assistants that truly learn and grow with their users, moving beyond stateless chatbots toward genuine digital companionship.

---

**Questions?** [Open an issue](https://github.com/deversmann/black-box/issues/new) or check the [documentation](docs/)!
