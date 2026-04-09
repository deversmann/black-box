# Black Box Swarm - Technical Specification
**Version:** 1.0.0  
**Last Updated:** 2026-04-09  
**Status:** Design Phase

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Agent Definitions & Roles](#agent-definitions--roles)
3. [Execution Flow](#execution-flow)
4. [The Ledger - Memory System](#the-ledger---memory-system)
5. [Technical Architecture](#technical-architecture)
6. [Implementation Phases](#implementation-phases)
7. [Configuration Reference](#configuration-reference)
8. [Critical Technical Challenges](#critical-technical-challenges)
9. [Testing & Validation](#testing--validation)
10. [Implementation Rules](#implementation-rules)

---

## System Overview

The **Black Box Swarm** is a multi-agent AI system designed as a "Learning Assistant" that balances technical precision with organic, associative personality. Unlike traditional chatbots, this system:

- **Learns and remembers** user facts, stories, preferences, and relationships through a persistent memory system called "The Ledger"
- **Develops personality** through an "Associative Slider" that controls response creativity and tangent probability
- **Adapts to user mood** by detecting emotional state and adjusting response style accordingly
- **Operates as a swarm** with 11 specialized AI agents coordinating to handle input processing, memory retrieval, creative synthesis, and quality control

The goal is to create an assistant that feels more like a knowledgeable friend than a generic AI tool—one that remembers your life, understands context, and can engage at varying levels of creativity based on your preferences and mood.

### Architecture Pattern: Decoupled Swarm

Instead of one model doing all the work, specialized agents handle distinct responsibilities:
- **Input Perception** (Shield, Sieve, Sensor)
- **Knowledge Retrieval** (Flash, Vault)
- **Creative Synthesis** (Probe, Aura, Command)
- **Quality Control** (Verdict, Shield Pass 2, Parser)

This architecture enables:
- **Model tiering**: Use fast, cheap models for simple tasks; powerful models for creative synthesis
- **Parallelization**: Run independent agents concurrently to minimize latency
- **Separation of concerns**: Isolate safety, memory, creativity into specialized components
- **Maintainability**: Add, modify, or replace agents without disrupting the whole system

---

## Agent Definitions & Roles

### A. The Ingress Layer (Input Processing)

#### **Shield** (Safety/Ethics)
**Two-pass agent**: Validates user input (Pass 1) and AI-generated output (Pass 2) against a configurable Safety Profile.

**Safety Profiles:**
- **Strict**: Block harmful, illegal, or offensive content. No exceptions.
- **Balanced**: Block clearly harmful/illegal content. Allow mature topics with disclaimers.
- **Experimental**: Minimal filtering. Only block extreme violations.

**Output Format:**
```
SAFE: [brief reason]
or
UNSAFE: [violation type]
```

If Pass 1 fails, the swarm aborts immediately. If Pass 2 fails, the response is not delivered to the user.

---

#### **Sieve** (Intent Distiller)
Summarizes user input into high-density "Intent Signals." Strips fluff to ensure the swarm stays on target.

**Purpose:** Reduce cognitive load for downstream agents by providing concise, actionable intent.

**Example:**
```
Input: "Hey, I was wondering if you could help me understand how neural networks work? 
        I've been reading about them but I'm confused about backpropagation."

Output:
- Explain neural networks fundamentals
- Clarify backpropagation mechanism
- User has some background knowledge
```

---

#### **Sensor** (Empath)
Performs sentiment and cognitive load analysis. Outputs the user's "State" to dictate response style.

**User States:**
- `JOVIAL` - Playful, excited, in a good mood (+0.2 to P(tangent))
- `CURIOUS` - Engaged, asking exploratory questions (+0.1)
- `NEUTRAL` - Standard interaction (0)
- `FOCUSED` - Task-oriented, wants direct answers (-0.1)
- `FRUSTRATED` - Confused, struggling, needs clarity (-0.2)
- `HURRIED` - Short messages, wants quick answers (-0.2)

**Output Format:**
```
STATE: [state]
CONFIDENCE: [0.0-1.0]
REASONING: [brief explanation]
```

---

### B. The Context Layer (Memory Retrieval)

#### **Flash** (Quick Thinker)
Low-latency vector search agent. Fetches memories from The Ledger based on semantic similarity.

**Retrieval Strategy:**
- `USER_FACT`: 90% similarity threshold (adjustable via Associative Slider)
- `USER_STORY`: 70% threshold (lower to allow tangential stories)
- Applies **Cooldown Filter** to prevent repetitive mentions

**Threshold Adjustment:**
```
fact_threshold = 0.9 - (P(tangent) × 0.2)    # Range: 0.7-0.9
story_threshold = 0.7 - (P(tangent) × 0.1)   # Range: 0.6-0.7
```

**Cooldown Filter:** 
Tracks which memories were used in the current session. Default cooldown period: 24 hours (configurable).

---

#### **Vault** (Librarian)
Non-creative agent. Queries the Relational Database for hard facts and logic based on Flash's hits. Returns raw data without embellishment.

**Purpose:** Separate factual retrieval from creative synthesis. Vault provides ingredients; Command cooks the meal.

---

### C. The Synthesis Layer (Creation)

#### **Probe** (Devil's Advocate)
High-logic agent that stress-tests the proposed logic.

**Criteria:**
1. Logical coherence
2. Relevance to user intent
3. Appropriateness of tangents given user state

**Output Format:**
```
APPROVE: [brief reason]
or
VETO: [what's wrong]
or
SUGGEST: [improvement]
```

**Special Behavior:** If Sensor reports user is `HURRIED` or `FRUSTRATED`, Probe vetoes tangents aggressively.

---

#### **Aura** (Storyteller)
Narrative "decorator." Activates only during high-associativity/jovial states to transform raw `USER_STORY` data into vivid, poetic "Flavor Text."

**Activation Condition:** `P(tangent) ≥ 0.7`

**Purpose:** Add emotional resonance and narrative flair without sacrificing accuracy.

**Style:** Uses metaphors, sensory details, emotional language.

---

#### **Command** (Master)
The Editor-in-Chief. Receives all inputs (Intent, State, Facts, Stories, Critiques) and weaves them into a single cohesive output.

**Inputs:**
- Intent signals from Sieve
- User state from Sensor
- Memories from Flash
- Facts from Vault
- Constraints from Probe (if run)
- P(tangent) value

**Output:** Draft response that addresses intent while honoring user state and memory context.

**Responsibilities:**
- Manage the **Pivot** from fact to tangent
- Balance precision with personality
- Synthesize multiple information sources into coherent narrative

---

### D. The Egress Layer (Validation & Archiving)

#### **Verdict** (Adjudicator)
Final auditor. Ensures the response actually satisfies Sieve's intent and checks for repetitive content.

**Validation Criteria:**
1. Does response address the core intent?
2. Is it coherent and logically sound?
3. Is it repetitive or overly verbose?

**Output Format:**
```
PASS: [brief reason]
or
FAIL: [what's missing]
```

If Verdict fails, the swarm can retry (send back to Command with feedback).

---

#### **Parser** (Architect)
Post-response background agent. Deconstructs the final interaction into atomic units, tags them, and writes them to The Ledger.

**Critical Responsibility: Atomic Memory Rewriting**
Memories must be self-contained (no unresolved pronouns or references).

**Example:**
```
Input: "It broke yesterday"
Context: Previous mention of "Honda Shadow motorcycle"
Rewritten Memory: "The user's Honda Shadow motorcycle broke yesterday"
```

**Memory Extraction Output (JSON):**
```json
[
  {
    "content": "The user's Honda Shadow motorcycle broke yesterday",
    "type": "user_fact",
    "tags": ["motorcycle", "honda_shadow", "repair"],
    "importance": 0.8
  },
  {
    "content": "The user is learning Python decorators",
    "type": "task_goal",
    "tags": ["python", "programming", "learning"],
    "importance": 0.6
  }
]
```

---

## Execution Flow

### The Swarm Loop

```
1. PERCEPTION
   User Input 
   → Shield (Pass 1: Safety Check)
   → [Parallel] Sieve (Intent) + Sensor (Mood)
   → Flash (Memory Search)

2. PROCESSING
   → Vault (Fact Retrieval based on Flash hits)
   → Probe (Logic Validation) - optional, can run in parallel with Command draft

3. SYNTHESIS
   → Command (Draft Response)
   → [If P(tangent) ≥ 0.7] Aura (Add Narrative Flavor)

4. VERIFICATION
   → [Parallel] Verdict (Intent Check) + Shield (Pass 2: Safety)

5. DELIVERY
   → Response sent to User

6. PERSISTENCE
   → Parser (Background: Extract & Store Memories in The Ledger)
```

### Conditional Branching

**Retry Logic:**
- If Verdict fails → send back to Command with feedback
- If Probe vetoes → send back to Command with veto reason
- Max retries: 2 (configurable)

**Aura Activation:**
- If `P(tangent) < 0.7` → skip Aura, go directly from Command to Verdict
- If `P(tangent) ≥ 0.7` → Aura enhances Command's output before Verdict

**Safety Abort:**
- If Shield Pass 1 fails → abort immediately, return safety message to user
- If Shield Pass 2 fails → abort, do not deliver response

---

## The Ledger - Memory System

### Architecture: Hybrid Database Approach

**Relational Database (SQLite + SQLAlchemy):**
- Structured data: memories, tags, sessions, interactions
- Handles relationships, access counts, timestamps
- Easy migration path to PostgreSQL for multi-user

**Vector Database (ChromaDB - Embedded):**
- Semantic embeddings for memory search
- Cosine similarity matching
- Fast vector search without external dependencies

### Database Schema

#### **memories** table
```sql
id                   INTEGER PRIMARY KEY
content              TEXT NOT NULL           -- The atomic memory
memory_type          VARCHAR(50) NOT NULL    -- user_fact, user_story, etc.
importance           FLOAT                   -- 0.0-1.0
created_at           DATETIME
last_accessed        DATETIME
access_count         INTEGER DEFAULT 0
last_used_in_session VARCHAR(100)            -- For cooldown filter
```

#### **tags** table
```sql
id    INTEGER PRIMARY KEY
name  VARCHAR(100) UNIQUE
```

#### **memory_tags** table (many-to-many)
```sql
memory_id  INTEGER FOREIGN KEY → memories.id
tag_id     INTEGER FOREIGN KEY → tags.id
PRIMARY KEY (memory_id, tag_id)
```

#### **memory_embeddings** table
```sql
id         INTEGER PRIMARY KEY
memory_id  INTEGER UNIQUE FOREIGN KEY → memories.id
chroma_id  VARCHAR(100) UNIQUE         -- Pointer to ChromaDB vector
```

#### **sessions** table
```sql
id             VARCHAR(100) PRIMARY KEY  -- UUID
started_at     DATETIME
last_activity  DATETIME
metadata       JSON                      -- Flexible session data
```

#### **interactions** table
```sql
id                INTEGER PRIMARY KEY
session_id        VARCHAR(100) FOREIGN KEY → sessions.id
user_input        TEXT NOT NULL
assistant_output  TEXT NOT NULL
created_at        DATETIME
p_tangent         FLOAT
user_state        VARCHAR(50)
agents_involved   JSON                    -- List of agents that ran
```

### Memory Types (Configurable Tags)

| Type | Description | Similarity Threshold | Use Case |
|------|-------------|----------------------|----------|
| `USER_FACT` | Factual information about the user | 0.9 | "User lives in Seattle", "User is allergic to peanuts" |
| `USER_STORY` | Anecdotes and narratives | 0.7 | "User's first motorcycle was a Honda Shadow" |
| `AI_LOGIC` | Reasoning patterns, decision trees | 0.8 | "User prefers concise explanations for technical topics" |
| `TASK/GOAL` | Ongoing projects, objectives | 0.85 | "User is learning Python", "User wants to build a mobile app" |
| `PREFERENCE` | Likes, dislikes, communication style | 0.75 | "User dislikes verbose responses", "User enjoys historical tangents" |
| `RELATIONSHIP` | People in user's life, context | 0.8 | "User's mother is a retired teacher", "User's friend Alex is a chef" |

### Cooldown Filter

**Purpose:** Prevent the assistant from harping on the same story/fact in a single session.

**Implementation:**
1. When Flash retrieves a memory, mark it with current `session_id` and timestamp
2. Before returning memories, filter out any with:
   - `last_used_in_session == current_session_id`
   - `last_accessed > (now - cooldown_hours)`
3. Default cooldown: 24 hours (configurable)

**Optimization:**
- In-memory cache of recently used memory IDs per session (fast path)
- Database index on `(last_used_in_session, last_accessed)` for queries
- Background cleanup job removes cooldown markers older than 48 hours

---

## Technical Architecture

### Technology Stack

**Backend:**
- **Language:** Python 3.11+
- **Orchestration:** LangGraph (typed state management, DAG execution, conditional branching)
- **API Framework:** FastAPI (async, WebSocket support, auto-docs)
- **ORM:** SQLAlchemy
- **Vector Store:** ChromaDB (embedded mode)

**Frontend:**
- **Framework:** Streamlit (all-Python, rapid prototyping)
- **Future:** React for production multi-user

**AI Models:**
- **Provider:** OpenRouter.ai (OpenAI API compatible, multi-provider support)
- **Model Tiering:**
  - **High-reasoning:** `gpt-4o` for Command, Aura, Probe
  - **Fast/cheap:** `gpt-4o-mini` for Shield, Sieve, Sensor, Vault, Parser

**Deployment:**
- **Containerization:** Docker + Docker Compose
- **Monitoring:** Prometheus metrics, structured logging (structlog)

### Project Structure

```
/black-box/
├── pyproject.toml                 # Poetry/uv dependencies
├── .env.example                   # Environment variables template
├── README.md
├── SPEC.md                        # This file
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
    ├── architecture.md           # Detailed architecture diagrams
    ├── agent-reference.md        # Per-agent documentation
    └── api-reference.md          # API endpoints
```

### Core Abstractions

#### **Base Agent Interface** (`src/blackbox/core/agent.py`)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel

class AgentConfig(BaseModel):
    """Configuration for an individual agent"""
    name: str
    model: str              # e.g., "openai/gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 500
    timeout: int = 30       # seconds

class AgentInput(BaseModel):
    """Standardized input to agents"""
    message: str
    context: Dict[str, Any] = {}

class AgentOutput(BaseModel):
    """Standardized output from agents"""
    result: str
    metadata: Dict[str, Any] = {}
    confidence: float = 1.0

class Agent(ABC):
    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.name
    
    @abstractmethod
    async def execute(self, input: AgentInput) -> AgentOutput:
        """Execute the agent's primary function"""
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
```

#### **Shared State** (`src/blackbox/core/state.py`)

```python
from typing import TypedDict, List, Optional, Dict
from langgraph.graph import add_messages

class SwarmState(TypedDict):
    """The state passed between agents in the swarm"""
    # Input
    user_input: str
    session_id: str
    
    # Ingress outputs
    intent_signals: Optional[str]
    user_state: Optional[str]           # JOVIAL, FRUSTRATED, etc.
    
    # Context outputs
    memory_hits: Optional[List[Dict]]   # From Flash
    facts: Optional[List[str]]          # From Vault
    
    # Synthesis outputs
    draft_response: Optional[str]       # From Command
    enhanced_response: Optional[str]    # From Aura (if activated)
    
    # Egress outputs
    final_response: Optional[str]
    validation_passed: bool
    safety_passed: bool
    
    # Metadata
    p_tangent: float                    # Slider + mood modifier
    aura_activated: bool
    retry_count: int
    agents_involved: List[str]
```

---

## Implementation Phases

### Phase 1: Core Swarm MVP
**Goal:** Prove the swarm pattern works end-to-end.

**Agents:** 4 core agents
- Sieve (Intent)
- Flash (Memory - mock, returns empty)
- Command (Synthesis)
- Verdict (Validation)

**Deliverables:**
- LangGraph orchestration with DAG visualization
- OpenRouter.ai integration
- Streamlit chat interface with associative slider
- Basic retry logic

**Success Criteria:**
- User sends message → receives coherent response
- Can visualize agent execution flow
- Response time < 5 seconds

---

### Phase 2: Complete Agent Suite
**Goal:** Implement all 11 agents and personality system.

**New Agents:**
- Shield (2-pass safety)
- Sensor (mood detection)
- Vault (DB queries)
- Probe (logic validation)
- Aura (narrative enhancement)
- Parser (memory extraction)

**Key Features:**
- P(tangent) calculation: `Slider + MoodModifier`
- Aura activation at P(tangent) ≥ 0.7
- Safety profile enforcement
- Parser extracts but doesn't store yet

**Success Criteria:**
- All agents execute in correct order
- Aura adds narrative flair when slider is high
- Probe vetoes incoherent responses
- Parser outputs structured memory JSON

---

### Phase 3: The Ledger - Memory System
**Goal:** Implement persistent memory storage and retrieval.

**Components:**
- SQLite + SQLAlchemy (relational data)
- ChromaDB (vector embeddings)
- Memory Manager (CRUD API)
- Cooldown Filter

**Deliverables:**
- Full database schema implementation
- Flash performs real vector search with thresholds
- Parser stores atomic memories
- Cooldown filter prevents repetition
- CLI tools for memory queries

**Success Criteria:**
- Memories persist across sessions
- Vector search returns relevant results
- Cooldown prevents same memory twice in 24 hours
- Parser creates self-contained atomic memories

---

### Phase 4: Production Readiness
**Goal:** Add testing, monitoring, deployment.

**Components:**
- Comprehensive test suite (unit, integration, E2E)
- Structured logging (JSON, structlog)
- Prometheus metrics
- Docker deployment
- Environment-specific configs
- Admin CLI tools

**Success Criteria:**
- 80%+ test coverage
- Can deploy with `docker-compose up`
- Metrics visible via Prometheus endpoint
- All tests passing

---

### Phase 5: Advanced Features
**Goal:** Optimization and extensibility.

**Features:**
- Memory consolidation (merge duplicates)
- Temporal decay (reduce importance of old memories)
- Response caching
- Plugin system for extensibility
- Preference learning from implicit feedback
- Dynamic P(tangent) adjustment

**Success Criteria:**
- Response time < 2s for 80% of queries
- Memory system scales to 10,000+ memories
- Can add plugins without core changes
- System learns user preferences over time

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
  level: "INFO"
  format: "json"
  output: "stdout"
  file: "./logs/swarm.log"

# Metrics configuration
metrics:
  enabled: true
  port: 9090
```

---

## Critical Technical Challenges

### Challenge 1: Atomic Memory Rewriting

**Problem:** Parser must rewrite memories to be self-contained (no unresolved pronouns).

**Solution:**
1. **Few-shot prompting** - Provide examples in Parser's system prompt
2. **Entity tracking** - Maintain session-level entity map (pronouns → explicit references)
3. **Context injection** - Pass recent conversation history to Parser
4. **Validation** - Heuristic check for unresolved pronouns

**Example:**
```
Input: "It broke yesterday"
Context: Previous message mentioned "Honda Shadow motorcycle"
Rewritten: "The user's Honda Shadow motorcycle broke yesterday"
```

**Implementation:**
```python
class EntityTracker:
    def __init__(self):
        self.entities = {}  # {"it": "Honda Shadow", "she": "User's mother"}
    
    def update_from_conversation(self, text: str):
        """Extract entities using NLP (spaCy, etc.)"""
        pass
    
    def resolve_pronouns(self, text: str) -> str:
        """Replace pronouns with explicit references"""
        pass
```

---

### Challenge 2: Cooldown Filter Efficiency

**Problem:** Track which memories were used in which sessions without slowing down search.

**Solution:**
1. **In-memory session cache** - Python dict of recently used memory IDs (hot path)
2. **Database index** - Index on `(last_used_in_session, last_accessed)`
3. **Background cleanup** - Periodically clear old cooldown markers (48+ hours)
4. **Two-tier check** - Fast in-memory first, then DB timestamp if needed

**Implementation:**
```python
class CooldownFilter:
    def __init__(self):
        self.session_cache = {}  # {session_id: set(memory_ids)}
    
    def mark_used(self, session_id: str, memory_id: int):
        if session_id not in self.session_cache:
            self.session_cache[session_id] = set()
        self.session_cache[session_id].add(memory_id)
    
    def is_cooled_down(self, session_id: str, memory_id: int, hours: int = 24) -> bool:
        # Check in-memory cache first
        if memory_id in self.session_cache.get(session_id, set()):
            # Then check timestamp in DB
            return self._check_db_timestamp(memory_id, hours)
        return True
```

---

### Challenge 3: Vector Search Threshold Tuning

**Problem:** Setting similarity thresholds that work across different query types.

**Solution:**
1. **Initial baselines** - Conservative starting points
   - USER_FACT: 0.90 (high precision)
   - USER_STORY: 0.70 (allow more recall)
2. **A/B testing framework** - Test threshold variants, track metrics
3. **Implicit feedback** - Monitor if Flash finds results, if Verdict approves responses
4. **Per-user calibration** - Adjust based on memory density
   ```python
   def calibrate_threshold(user_memory_count: int, base_threshold: float) -> float:
       if user_memory_count < 50:
           return base_threshold - 0.1  # Fewer memories → lower threshold
       elif user_memory_count > 500:
           return base_threshold + 0.05  # More memories → higher threshold
       return base_threshold
   ```

---

### Challenge 4: Latency Management

**Problem:** 11 agents could create significant latency (5+ seconds).

**Target Latencies:**
- Simple query: < 2s
- Complex query: < 4s
- High tangent (Aura): < 5s

**Solutions:**

1. **Aggressive Parallelization** (via LangGraph)
   - Sieve + Sensor (both process user input)
   - Verdict + Shield Pass 2 (both validate output)

2. **Model Tiering**
   - Fast agents (gpt-4o-mini): < 500ms
   - High-reasoning (gpt-4o): 1-2s acceptable

3. **Streaming**
   - Stream agent outputs as they complete
   - User sees progress, not just final result

4. **Speculative Execution**
   - Start Aura early, cancel if P(tangent) < 0.7
   ```python
   aura_task = asyncio.create_task(self._run_aura(state))
   if state['p_tangent'] < 0.7:
       aura_task.cancel()
   ```

5. **Response Caching** (Phase 5)
   - Cache identical queries (5-minute TTL)
   - Semantic caching for similar queries

---

## Testing & Validation

### Testing Strategy

#### **Unit Tests**
- Each agent in isolation with mocked LLM responses
- Memory Manager CRUD operations
- Vector store search accuracy
- Cooldown filter logic

**Example:**
```python
@pytest.mark.asyncio
async def test_sieve_extracts_intent():
    config = AgentConfig(name="Sieve", model="openai/gpt-4o-mini", ...)
    agent = SieveAgent(config)
    
    result = await agent.execute(AgentInput(
        message="I'm trying to learn Python but I'm confused about decorators"
    ))
    
    assert "python" in result.result.lower()
    assert "decorator" in result.result.lower()
```

#### **Integration Tests**
- Full swarm execution
- Memory persistence across sessions
- Cooldown filter integration
- Safety profile enforcement

#### **End-to-End Tests**
- Streamlit UI interaction
- WebSocket streaming
- Multi-turn conversations
- Memory accumulation over time

#### **Load Tests**
- Concurrent sessions
- Large memory databases (10k+ memories)
- Vector search performance

### Validation Checklists

**Phase 1 (MVP):**
- [ ] Can send message through Streamlit UI
- [ ] Receives coherent response
- [ ] LangGraph visualization shows execution flow
- [ ] Response time < 5 seconds

**Phase 2 (Full Swarm):**
- [ ] All 11 agents execute in correct order
- [ ] Aura activates when slider > 0.7
- [ ] Sensor detects mood correctly
- [ ] Probe vetoes incoherent responses
- [ ] Parser outputs structured JSON

**Phase 3 (Memory):**
- [ ] Memories persist across app restarts
- [ ] Vector search returns relevant results
- [ ] Cooldown prevents repetition within 24 hours
- [ ] Parser creates atomic memories (no unresolved pronouns)

**Phase 4 (Production):**
- [ ] 80%+ test coverage
- [ ] Docker: `docker-compose up` works
- [ ] Metrics visible via Prometheus
- [ ] All tests passing

**Phase 5 (Advanced):**
- [ ] Response time < 2s for 80% of queries
- [ ] Memory consolidation removes duplicates
- [ ] Plugin system functional
- [ ] Preference learning works

---

## Implementation Rules

### For Developers

1. **Model Tiering:** Use high-reasoning models (GPT-4o/Claude Opus) for Command, Aura, and Probe. Use small, fast models (GPT-4o-mini/Claude Haiku) for Sieve, Sensor, Vault, and Parser.

2. **Parallelization:** Agents in the Perception and Verification phases must run concurrently to minimize latency.

3. **The Associative Slider:** Implement as:
   ```python
   P(tangent) = base_slider + mood_modifier
   # Where:
   # base_slider: 0.0-1.0 (user-controlled)
   # mood_modifier: ±0.2 based on user state
   ```

4. **Atomic Memory:** Ensure Parser rewrites memories to be self-contained (e.g., replacing "It is broken" with "The user's Honda Shadow is broken") before storing in the Ledger.

5. **Cooldown Filter:** Any memory ID used must be added to a "Recently Used" queue in Flash to prevent the AI from harping on the same story in a single session.

6. **Safety First:** Shield runs twice—once on input, once on output. If either fails, the swarm must abort gracefully.

7. **State Immutability:** SwarmState should be treated as immutable within agents. Create new state objects rather than mutating existing ones.

8. **Error Handling:** Each agent must handle LLM failures gracefully. Retry up to 3 times with exponential backoff.

9. **Logging:** Every agent execution must be logged with:
   - Agent name
   - Input/output lengths
   - Duration (ms)
   - Success/failure status
   - Metadata (model used, tokens consumed)

10. **Configuration:** All magic numbers (thresholds, timeouts, cooldown periods) must be configurable via YAML.

---

## Appendix: Key Formulas

### P(tangent) Calculation
```
P(tangent) = Slider + MoodModifier

Where:
- Slider ∈ [0.0, 1.0] (user-controlled)
- MoodModifier ∈ {-0.2, -0.1, 0.0, +0.1, +0.2}
  - JOVIAL: +0.2
  - CURIOUS: +0.1
  - NEUTRAL: 0.0
  - FOCUSED: -0.1
  - FRUSTRATED: -0.2
  - HURRIED: -0.2

Final P(tangent) clamped to [0.0, 1.0]
```

### Similarity Threshold Adjustment
```
fact_threshold = 0.9 - (P(tangent) × 0.2)
story_threshold = 0.7 - (P(tangent) × 0.1)

Example:
- P(tangent) = 0.0 → fact: 0.9, story: 0.7
- P(tangent) = 0.5 → fact: 0.8, story: 0.65
- P(tangent) = 1.0 → fact: 0.7, story: 0.6
```

### Temporal Decay (Phase 5)
```
importance_new = importance_old × e^(-λt)

Where:
- λ = decay rate (configurable, default: 0.001)
- t = days since last access
```

---

## Document Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-09 | Initial comprehensive specification combining conceptual design with implementation details |

---

**Status:** This specification is ready for implementation. Proceed to Phase 1 to begin building the Core Swarm MVP.
