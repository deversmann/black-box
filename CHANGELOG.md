# Changelog

All notable changes to the Black Box Swarm project will be documented in this file.

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

- **Response length tuning**: Command now produces conversational responses
  - Updated system prompt to emphasize concise, conversational style
  - Reduced max_tokens from 1000 → 800 (~400-500 words)
  - Added explicit length guidelines: 2-3 paragraphs by default
  - Verdict now validates conciseness
  - Responses expand only when user asks for detail/examples

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
