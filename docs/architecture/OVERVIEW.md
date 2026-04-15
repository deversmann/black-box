# Black Box Swarm - Architecture Overview

**Version:** 1.0.0  
**Last Updated:** 2026-04-09

---

## System Overview

The **Black Box Swarm** is a multi-agent AI system designed as a "Learning Assistant" that balances technical precision with organic, associative personality. Unlike traditional chatbots, this system:

- **Learns and remembers** user facts, stories, preferences, and relationships through a persistent memory system called "The Ledger"
- **Develops personality** through an "Associative Slider" that controls response creativity and tangent probability
- **Adapts to user mood** by detecting emotional state and adjusting response style accordingly
- **Operates as a swarm** with 11 specialized AI agents coordinating to handle input processing, memory retrieval, creative synthesis, and quality control

The goal is to create an assistant that feels more like a knowledgeable friend than a generic AI tool—one that remembers your life, understands context, and can engage at varying levels of creativity based on your preferences and mood.

## Architecture Pattern: Decoupled Swarm

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

## Related Documentation

- [**Agent Definitions**](AGENTS.md) - Detailed specifications for all 10 agents
- [**Execution Flow & Memory**](MEMORY.md) - Swarm loop, conditional routing, The Ledger database
- [**Configuration Guide**](../guides/CONFIGURATION.md) - Tech stack, setup, and configuration
- [**Development Guide**](../guides/DEVELOPMENT.md) - Core abstractions, testing, and implementation rules
- [**Technical Challenges**](../guides/CHALLENGES.md) - Critical implementation challenges and solutions
