# Black Box Swarm - Configuration Guide

Complete reference for technology stack, project structure, and configuration.

---

## Technology Stack

### Backend

- **Language:** Python 3.11+
- **Orchestration:** LangGraph (typed state management, DAG execution, conditional branching)
- **API Framework:** FastAPI (async, WebSocket support, auto-docs)
- **ORM:** SQLAlchemy
- **Vector Store:** ChromaDB (embedded mode)

### Frontend

- **Framework:** Streamlit (all-Python, rapid prototyping)
- **Future:** React for production multi-user

### AI Models

- **Provider:** OpenRouter.ai (OpenAI API compatible, multi-provider support)
- **Model Tiering:**
  - **High-reasoning:** `gpt-4o` for Command, Aura, Probe
  - **Fast/cheap:** `gpt-4o-mini` for Shield, Sieve, Sensor, Vault, Parser

### Deployment

- **Containerization:** Docker + Docker Compose
- **Monitoring:** Prometheus metrics, structured JSON logging (Python logging module)

---

## Project Structure

```
/black-box/
├── pyproject.toml                 # Poetry/uv dependencies
├── .env.example                   # Environment variables template
├── README.md
├── config/
│   ├── default.yaml               # Base configuration
│   ├── development.yaml           # Dev overrides
│   ├── testing.yaml               # Test config
│   └── production.yaml            # Production config
├── src/
│   └── blackbox/
│       ├── __init__.py
│       ├── core/
│       │   ├── agent.py           # Base Agent ABC
│       │   ├── state.py           # SwarmState TypedDict
│       │   ├── orchestrator.py    # LangGraph orchestration
│       │   ├── logging.py         # Structured logging
│       │   ├── metrics.py         # Prometheus metrics
│       │   └── cache.py           # Response caching
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── shield.py          # Safety (2-pass)
│       │   ├── sieve.py           # Intent distiller
│       │   ├── sensor.py          # Mood detector
│       │   ├── flash.py           # Vector search
│       │   ├── vault.py           # DB queries
│       │   ├── probe.py           # Logic checker
│       │   ├── aura.py            # Storyteller
│       │   ├── command.py         # Master synthesizer
│       │   ├── verdict.py         # Response validator
│       │   └── parser.py          # Memory extractor
│       ├── models/
│       │   ├── __init__.py
│       │   └── client.py          # OpenRouter API client
│       ├── db/
│       │   ├── __init__.py
│       │   ├── models.py          # SQLAlchemy models
│       │   ├── vector_store.py    # ChromaDB wrapper
│       │   ├── memory_manager.py  # High-level memory API
│       │   ├── consolidation.py   # Memory merging (Phase 5)
│       │   └── decay.py           # Temporal decay (Phase 5)
│       ├── plugins/
│       │   ├── __init__.py
│       │   ├── base.py            # Plugin ABC
│       │   └── registry.py        # Plugin manager
│       ├── api/
│       │   ├── __init__.py
│       │   └── main.py            # FastAPI app
│       └── cli.py                 # Admin CLI tools
├── frontend/
│   └── app.py                     # Streamlit chat interface
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_agents/
│   │   │   ├── test_sieve.py
│   │   │   ├── test_flash.py
│   │   │   └── ...
│   │   ├── test_memory_manager.py
│   │   └── test_vector_store.py
│   ├── integration/
│   │   ├── test_swarm_flow.py
│   │   ├── test_memory_persistence.py
│   │   └── test_cooldown_filter.py
│   └── fixtures/
│       ├── sample_conversations.json
│       └── test_memories.json
├── data/                          # Git-ignored
│   ├── ledger.db                 # SQLite database
│   └── chroma/                   # ChromaDB storage
├── logs/                          # Git-ignored
│   └── swarm.log
├── scripts/
│   ├── start.sh                  # Launch script
│   └── setup.sh                  # Initial setup
└── docs/
    ├── STATUS.md                 # Project roadmap
    ├── architecture/             # Architecture docs
    └── guides/                   # Development guides
```

---

## Configuration Reference

### Example: `config/default.yaml`

```yaml
system:
  name: "Black Box Swarm"
  version: "1.0.0"
  environment: "production"

# Agent model assignments
agents:
  # High-reasoning agents (gpt-4o)
  command:
    name: "Command"
    model: "openai/gpt-4o"
    temperature: 0.7
    max_tokens: 1000
    timeout: 30
  
  aura:
    name: "Aura"
    model: "openai/gpt-4o"
    temperature: 0.9
    max_tokens: 800
    timeout: 30
  
  probe:
    name: "Probe"
    model: "openai/gpt-4o"
    temperature: 0.6
    max_tokens: 400
    timeout: 20
  
  # Fast agents (gpt-4o-mini)
  sieve:
    name: "Sieve"
    model: "openai/gpt-4o-mini"
    temperature: 0.5
    max_tokens: 300
    timeout: 10
  
  sensor:
    name: "Sensor"
    model: "openai/gpt-4o-mini"
    temperature: 0.5
    max_tokens: 200
    timeout: 10
  
  flash:
    name: "Flash"
    model: "openai/gpt-4o-mini"
    temperature: 0.0
    max_tokens: 100
    timeout: 5
  
  vault:
    name: "Vault"
    model: "openai/gpt-4o-mini"
    temperature: 0.0
    max_tokens: 200
    timeout: 5
  
  shield:
    name: "Shield"
    model: "openai/gpt-4o-mini"
    temperature: 0.2
    max_tokens: 150
    timeout: 10
  
  verdict:
    name: "Verdict"
    model: "openai/gpt-4o-mini"
    temperature: 0.3
    max_tokens: 200
    timeout: 10
  
  parser:
    name: "Parser"
    model: "openai/gpt-4o-mini"
    temperature: 0.3
    max_tokens: 1000
    timeout: 20

# OpenRouter configuration
openrouter:
  api_key_env: "OPENROUTER_API_KEY"
  base_url: "https://openrouter.ai/api/v1"
  retry_attempts: 3
  retry_delay: 1.0

# Memory system configuration
memory:
  db_url: "sqlite:///./data/ledger.db"
  vector_store_path: "./data/chroma"
  cooldown_hours: 24
  max_search_results: 5
  
  # Similarity thresholds (adjusted by p_tangent)
  thresholds:
    user_fact: 0.9
    user_story: 0.7
    ai_logic: 0.8
    task_goal: 0.85
    preference: 0.75
    relationship: 0.8

# Safety configuration
safety:
  default_profile: "balanced"
  profiles:
    strict:
      description: "Block harmful, illegal, or offensive content"
      filters:
        - violence
        - illegal_activity
        - hate_speech
        - self_harm
    balanced:
      description: "Allow mature topics with context"
      filters:
        - illegal_activity
        - extreme_violence
        - self_harm
    experimental:
      description: "Minimal filtering"
      filters:
        - illegal_activity

# Associative behavior
associative:
  default_p_tangent: 0.5
  aura_activation_threshold: 0.7
  mood_modifiers:
    jovial: 0.2
    curious: 0.1
    neutral: 0.0
    focused: -0.1
    frustrated: -0.2
    hurried: -0.2

# Logging configuration
logging:
  level: "INFO"           # DEBUG, INFO, WARNING, ERROR
  format: "json"          # Structured JSON logs
  output: "both"          # stdout, file, both
  file: "./logs/swarm.log"
  rotation:
    max_bytes: 10485760   # 10MB per file
    backup_count: 5       # Keep 5 backup files (~50MB total)

# Metrics configuration
metrics:
  enabled: true
  port: 9090
```

---

## Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -e ".[dev]"
```

### "OPENROUTER_API_KEY not found"
This means the `.env` file is missing or not properly configured.

**Fix:**
```bash
# 1. Copy the example file
cp .env.example .env

# 2. Edit and add your API key
nano .env

# Make sure it looks like this:
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here

# 3. Verify it's set
grep OPENROUTER_API_KEY .env
```

Get an API key at: https://openrouter.ai/keys

### Tests failing
```bash
# Reinstall dependencies
pip install -e ".[dev]"

# Clear cache
rm -rf .pytest_cache __pycache__
pytest
```

### Streamlit port already in use
```bash
# Use different port
streamlit run frontend/app.py --server.port 8502
```

---

## Related Documentation

- [Development Guide](DEVELOPMENT.md) - Core abstractions, testing, implementation rules
- [Architecture Overview](../architecture/OVERVIEW.md) - System design philosophy
