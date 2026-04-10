"""Shared state definition for the swarm."""

from typing import TypedDict


class SwarmState(TypedDict, total=False):
    """The state passed between agents in the swarm.

    This TypedDict defines all possible state fields. Fields marked as required
    must be present at initialization. Optional fields can be added as agents
    execute.
    """

    # Input (required)
    user_input: str
    session_id: str
    conversation_history: list[dict] | None  # Recent messages for context

    # Ingress outputs
    intent_signals: str | None  # From Sieve
    detail_level: str | None  # From Sieve: BRIEF, DETAILED, COMPREHENSIVE
    user_state: str | None  # From Sensor (JOVIAL, FRUSTRATED, etc.)

    # Context outputs
    memory_hits: list[dict] | None  # From Flash
    facts: list[str] | None  # From Vault

    # Synthesis outputs
    draft_response: str | None  # From Command
    enhanced_response: str | None  # From Aura (if activated)

    # Egress outputs
    final_response: str | None
    validation_passed: bool
    safety_passed: bool
    verdict_feedback: str | None  # Feedback from Verdict for retry

    # Metadata
    p_tangent: float  # Slider + mood modifier
    aura_activated: bool
    retry_count: int
    agents_involved: list[str]
