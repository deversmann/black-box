# Black Box Swarm - Agent Definitions

Complete specifications for all 10 specialized AI agents that comprise the Black Box Swarm.

## Quick Reference

| Agent | Layer | Role | Model Tier | Key Responsibility |
|-------|-------|------|------------|-------------------|
| **Shield** | Ingress | Safety Validator | Fast | Two-pass safety validation (input + output) |
| **Sieve** | Ingress | Intent Distiller | Fast | Extract intent, detect detail level |
| **Sensor** | Ingress | Mood Detector | Fast | Analyze user state, calculate P(tangent) |
| **Flash** | Context | Memory Search | Fast | Vector search in The Ledger |
| **Vault** | Context | Fact Retriever | Fast | Query relational database |
| **Probe** | Synthesis | Logic Validator | High | Stress-test reasoning, veto power |
| **Aura** | Synthesis | Storyteller | High | Add narrative flair (P(tangent) ≥ 0.7) |
| **Command** | Synthesis | Master Synthesizer | High | Weave all inputs into response |
| **Verdict** | Egress | Quality Validator | Fast | Final intent check, truncation detection |
| **Parser** | Egress | Memory Extractor | Fast | Extract atomic memories for storage |

---

## A. The Ingress Layer (Input Processing)

### **Shield** (Safety/Ethics)
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

### **Sieve** (Intent Distiller)
Summarizes user input into high-density "Intent Signals" AND detects desired response detail level. Strips fluff to ensure the swarm stays on target.

**Purpose:** 
- Reduce cognitive load for downstream agents by providing concise, actionable intent
- Detect if user wants BRIEF (default), DETAILED, or COMPREHENSIVE response
- Resolve pronouns and references using recent conversation context (last 3 turns)

**Output Format:**
```
DETAIL_LEVEL: [BRIEF | DETAILED | COMPREHENSIVE]
INTENT:
- Bullet point 1
- Bullet point 2
```

**Example with Context:**
```
Recent conversation:
User: "How do decorators work?"
Assistant: "Decorators let you modify functions..."

Current input: "Can you explain error handling in detail with examples?"

Output:
DETAIL_LEVEL: DETAILED
INTENT:
- Explain error handling for Python decorators
- Include code examples
- Follow-up to previous decorator question
```

**Detail Level Triggers:**
- **BRIEF:** Default conversational questions
- **DETAILED:** "in detail", "with examples", "explain more", "tell me more"
- **COMPREHENSIVE:** "everything about", "complete guide", "step by step", "all the details"

---

### **Sensor** (Empath)
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

## B. The Context Layer (Memory Retrieval)

### **Flash** (Quick Thinker)
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

### **Vault** (Librarian)
Non-creative agent. Queries the Relational Database for hard facts and logic based on Flash's hits. Returns raw data without embellishment.

**Purpose:** Separate factual retrieval from creative synthesis. Vault provides ingredients; Command cooks the meal.

---

## C. The Synthesis Layer (Creation)

### **Probe** (Devil's Advocate)
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

### **Aura** (Storyteller)
Narrative "decorator." Activates only during high-associativity/jovial states to transform raw `USER_STORY` data into vivid, poetic "Flavor Text."

**Activation Condition:** `P(tangent) ≥ 0.7`

**Purpose:** Add emotional resonance and narrative flair without sacrificing accuracy.

**Style:** Uses metaphors, sensory details, emotional language.

---

### **Command** (Master)
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

## D. The Egress Layer (Validation & Archiving)

### **Verdict** (Adjudicator)
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

### **Parser** (Architect)
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

## Related Documentation

- [Architecture Overview](OVERVIEW.md) - System design philosophy and patterns
- [Execution Flow & Memory](MEMORY.md) - How agents work together, The Ledger database
- [Configuration Guide](../guides/CONFIGURATION.md) - Model assignments and agent configuration
