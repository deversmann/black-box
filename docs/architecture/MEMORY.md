# Black Box Swarm - Execution Flow & Memory System

How agents coordinate and how memories are stored and retrieved.

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

## Related Documentation

- [Agent Definitions](AGENTS.md) - Detailed specifications for each agent
- [Architecture Overview](OVERVIEW.md) - System design philosophy
- [Technical Challenges](../guides/CHALLENGES.md) - Memory system implementation challenges
