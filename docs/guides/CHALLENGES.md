# Black Box Swarm - Technical Challenges

Critical implementation challenges and their solutions.

---

## Challenge 1: Atomic Memory Rewriting

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

## Challenge 2: Cooldown Filter Efficiency

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

## Challenge 3: Vector Search Threshold Tuning

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

## Challenge 4: Latency Management

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

## Related Documentation

- [Development Guide](DEVELOPMENT.md) - Implementation rules and patterns
- [Architecture Overview](../architecture/OVERVIEW.md) - System design philosophy
- [Memory System](../architecture/MEMORY.md) - Database design and memory retrieval
