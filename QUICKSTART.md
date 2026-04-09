# Black Box Swarm - Quick Start Guide

## Phase 1 MVP Status ✅

**Completed Components:**
- ✅ 4 Core Agents (Sieve, Flash, Command, Verdict)
- ✅ LangGraph Orchestration
- ✅ OpenRouter Integration
- ✅ Streamlit Chat UI
- ✅ Unit & Integration Tests (19 tests, 90% coverage)
- ✅ Configuration System
- ✅ Project Structure

## Prerequisites

- Python 3.11 or higher
- OpenRouter API key ([get one here](https://openrouter.ai/))

## Setup (First Time)

1. **Clone and navigate to the project:**
   ```bash
   cd /Users/deversma/Development/black-box
   ```

2. **Run setup script:**
   ```bash
   ./scripts/setup.sh
   ```

3. **Configure your API key:**
   Edit `.env` and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   ```

## Running the Application

### Option 1: Using the start script (recommended)
```bash
./scripts/start.sh
```

### Option 2: Directly with Streamlit
```bash
streamlit run frontend/app.py
```

The app will open in your browser at `http://localhost:8501`

## Running Tests

```bash
# All tests
pytest

# With coverage report
pytest --cov=blackbox --cov-report=html

# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_agents/test_sieve.py -v
```

## Phase 1 Features

### Agents
1. **Sieve** - Distills user input into intent signals
2. **Flash** - Memory retrieval (mock: returns 3 hardcoded memories)
3. **Command** - Synthesizes contextual responses
4. **Verdict** - Validates response quality

### Execution Flow
```
User Input → Sieve → Flash → Command → Verdict → Final Response
                                  ↑          ↓
                                  └─(retry)──┘
```

### UI Features
- Chat interface with message history
- Associative slider (P(tangent)) - controls creativity (0.0 - 1.0)
- Debug panel showing which agents executed
- Session tracking

## Testing the System

Try these example messages in the UI:

1. **Simple Question:**
   - "What are Python decorators?"
   - Should see: Sieve → Flash → Command → Verdict

2. **Technical Request:**
   - "Explain neural networks with code examples"
   - Flash will return mock memories about your (fictional) background

3. **Adjust Creativity:**
   - Move the Associative Slider to different values
   - Higher values (0.7+) will activate Aura in Phase 2

## Configuration

Edit `config/default.yaml` to customize:

- **Model assignments:** Which OpenRouter model each agent uses
- **Temperature:** Creativity level per agent
- **Timeouts:** Max execution time per agent
- **P(tangent) defaults:** Associative behavior settings

Current models:
- **High reasoning:** `openai/gpt-5.4` (Command)
- **Fast agents:** `openai/gpt-5.4-nano` (Sieve, Flash, Verdict)

## Project Structure

```
/black-box/
├── config/
│   └── default.yaml           # Configuration
├── src/blackbox/
│   ├── core/                  # Base abstractions
│   │   ├── agent.py          # Agent ABC
│   │   ├── state.py          # SwarmState TypedDict
│   │   ├── config.py         # Config loader
│   │   └── orchestrator.py   # LangGraph coordination
│   ├── agents/               # Agent implementations
│   │   ├── sieve.py
│   │   ├── flash.py          # Mock memory retrieval
│   │   ├── command.py
│   │   └── verdict.py
│   └── models/
│       └── client.py         # OpenRouter API client
├── frontend/
│   └── app.py                # Streamlit UI
├── tests/
│   ├── unit/                 # Agent unit tests
│   └── integration/          # End-to-end tests
└── scripts/
    ├── setup.sh              # Initial setup
    └── start.sh              # Launch app
```

## Next Steps (Phase 2)

To continue to Phase 2, we'll add:
- **7 more agents:** Shield, Sensor, Vault, Probe, Aura, Parser
- **Personality system:** P(tangent) calculation, mood detection
- **Safety profiles:** Configurable content filtering
- **Enhanced UI:** Mood display, agent execution visualization

## Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -e ".[dev]"
```

### "OPENROUTER_API_KEY not found"
Make sure `.env` exists and contains:
```
OPENROUTER_API_KEY=your_key_here
```

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

## Development

### Adding a new agent (future phases)

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

## Support

- **Issues:** [GitHub Issues](https://github.com/blackbox-swarm/issues)
- **Spec:** See `SPEC.md` for detailed technical documentation
- **Tests:** See `tests/README.md` for testing guide

---

**Phase 1 MVP Complete** ✨  
All tests passing • 90% code coverage • Ready for Phase 2
