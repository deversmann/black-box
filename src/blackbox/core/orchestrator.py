"""LangGraph orchestration for the Black Box Swarm."""

import asyncio
from typing import Any

from langgraph.graph import StateGraph, END

from blackbox.agents.command import Command
from blackbox.agents.flash import Flash
from blackbox.agents.sensor import Sensor
from blackbox.agents.shield import Shield
from blackbox.agents.sieve import Sieve
from blackbox.agents.vault import Vault
from blackbox.agents.verdict import Verdict
from blackbox.core.agent import AgentConfig, AgentInput
from blackbox.core.config import Config
from blackbox.core.state import SwarmState
from blackbox.models.client import OpenRouterClient


class SwarmOrchestrator:
    """Orchestrates the swarm of agents using LangGraph."""

    def __init__(self, config: Config, client: OpenRouterClient) -> None:
        """Initialize the orchestrator.

        Args:
            config: Application configuration
            client: OpenRouter API client
        """
        self.config = config
        self.client = client

        # Initialize Phase 1 agents
        self.sieve = Sieve(
            AgentConfig(**config.agents["sieve"]),
            client,
        )
        self.flash = Flash(
            AgentConfig(**config.agents["flash"]),
        )
        self.vault = Vault(
            AgentConfig(**config.agents["vault"]),
        )
        self.command = Command(
            AgentConfig(**config.agents["command"]),
            client,
        )
        self.verdict = Verdict(
            AgentConfig(**config.agents["verdict"]),
            client,
        )

        # Initialize Wave 1 agents (Phase 2)
        self.shield = Shield(
            AgentConfig(**config.agents["shield"]),
            client,
        )
        self.sensor = Sensor(
            AgentConfig(**config.agents["sensor"]),
            client,
        )

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph execution graph.

        Phase 2 Wave 2 Flow:
        Shield Pass 1 → [Parallel: Sieve + Sensor] → Flash → Vault → Command
        → [Parallel: Verdict + Shield Pass 2] → END

        Returns:
            Compiled StateGraph ready for execution
        """
        # Create the graph with SwarmState
        workflow = StateGraph(SwarmState)

        # Add nodes for each agent
        workflow.add_node("shield_pass1", self._run_shield_pass1)
        workflow.add_node("parallel_ingress", self._run_parallel_ingress)
        workflow.add_node("flash", self._run_flash)
        workflow.add_node("vault", self._run_vault)
        workflow.add_node("command", self._run_command)
        workflow.add_node("verdict", self._run_verdict)
        workflow.add_node("shield_pass2", self._run_shield_pass2)

        # Define the execution flow
        # Entry: Shield Pass 1 checks input safety
        workflow.set_entry_point("shield_pass1")

        # Shield Pass 1 → Check if safe
        workflow.add_conditional_edges(
            "shield_pass1",
            self._check_shield_pass1,
            {
                "abort": END,  # Unsafe input - abort immediately
                "continue": "parallel_ingress",  # Safe - continue
            },
        )

        # Parallel ingress (Sieve + Sensor) → Flash
        workflow.add_edge("parallel_ingress", "flash")

        # Flash → Vault
        workflow.add_edge("flash", "vault")

        # Vault → Command
        workflow.add_edge("vault", "command")

        # Command → Verdict (NOT parallel anymore)
        workflow.add_edge("command", "verdict")

        # Verdict decides: retry Command OR continue to Shield Pass 2
        workflow.add_conditional_edges(
            "verdict",
            self._should_retry_after_verdict,
            {
                "retry": "command",  # Verdict failed - retry Command
                "continue": "shield_pass2",  # Verdict passed - check output safety
            },
        )

        # Shield Pass 2 → Check output safety
        workflow.add_conditional_edges(
            "shield_pass2",
            self._check_shield_pass2,
            {
                "abort": END,  # Unsafe output - abort
                "end": END,  # Safe output - deliver
            },
        )

        return workflow.compile()

    def _check_shield_pass1(self, state: SwarmState) -> str:
        """Check if Shield Pass 1 approved the input.

        Args:
            state: Current swarm state

        Returns:
            "abort" if unsafe, "continue" if safe
        """
        is_safe = state.get("shield_pass1_safe", False)
        return "continue" if is_safe else "abort"

    def _should_retry_after_verdict(self, state: SwarmState) -> str:
        """Determine if we should retry Command after Verdict.

        Args:
            state: Current swarm state

        Returns:
            "retry" or "continue"
        """
        validation_passed = state.get("validation_passed", False)
        retry_count = state.get("retry_count", 0)
        max_retries = 2

        # Verdict failed → retry if attempts remain
        if not validation_passed and retry_count < max_retries:
            return "retry"

        # Verdict passed or max retries exceeded → continue to Shield Pass 2
        return "continue"

    def _check_shield_pass2(self, state: SwarmState) -> str:
        """Check if Shield Pass 2 approved the output.

        Args:
            state: Current swarm state

        Returns:
            "abort" if unsafe, "end" if safe
        """
        is_safe = state.get("shield_pass2_safe", True)
        return "end" if is_safe else "abort"

    def _should_retry_or_abort(self, state: SwarmState) -> str:
        """Determine if we should retry, abort, or finish.

        Args:
            state: Current swarm state

        Returns:
            "retry", "abort", or "end"
        """
        validation_passed = state.get("validation_passed", False)
        shield_pass2_safe = state.get("shield_pass2_safe", True)
        retry_count = state.get("retry_count", 0)
        max_retries = 2

        # Shield Pass 2 failure → abort (don't deliver unsafe response)
        if not shield_pass2_safe:
            return "abort"

        # Verdict failure → retry if attempts remain
        # Note: retry_count is incremented in _run_verdict, not here
        if not validation_passed and retry_count < max_retries:
            return "retry"

        # All checks passed or max retries exceeded
        return "end"

    async def _run_sieve(self, state: SwarmState) -> dict[str, Any]:
        """Execute Sieve agent.

        Args:
            state: Current swarm state

        Returns:
            State updates from Sieve
        """
        # Give Sieve last 2-3 messages for context (6 messages = 3 turns)
        history = state.get("conversation_history", [])
        recent_context = history[-6:] if len(history) > 6 else history

        agent_input = AgentInput(
            message=state["user_input"],
            context={"recent_conversation": recent_context},
        )
        output = await self.sieve.execute(agent_input)

        return {
            "intent_signals": output.result,
            "detail_level": output.metadata.get("detail_level", "BRIEF"),
            "agents_involved": state.get("agents_involved", []) + ["Sieve"],
        }

    async def _run_flash(self, state: SwarmState) -> dict[str, Any]:
        """Execute Flash agent.

        Args:
            state: Current swarm state

        Returns:
            State updates from Flash
        """
        agent_input = AgentInput(
            message=state.get("intent_signals", ""),
            context={"session_id": state["session_id"]},
        )
        output = await self.flash.execute(agent_input)

        return {
            "memory_hits": output.metadata.get("memories", []),
            "agents_involved": state.get("agents_involved", []) + ["Flash"],
        }

    async def _run_vault(self, state: SwarmState) -> dict[str, Any]:
        """Execute Vault agent.

        Args:
            state: Current swarm state

        Returns:
            State updates from Vault
        """
        agent_input = AgentInput(
            message="",  # Vault doesn't use the user message directly
            context={"memory_hits": state.get("memory_hits", [])},
        )
        output = await self.vault.execute(agent_input)

        return {
            "facts": output.metadata.get("facts", []),
            "agents_involved": state.get("agents_involved", []) + ["Vault"],
        }

    async def _run_command(self, state: SwarmState) -> dict[str, Any]:
        """Execute Command agent.

        Args:
            state: Current swarm state

        Returns:
            State updates from Command
        """
        # Build context - include Verdict feedback on retry
        # Give Command the full sliding window (last 10 turns = 20 messages)
        history = state.get("conversation_history", [])
        sliding_window = history[-20:] if len(history) > 20 else history

        # Get detail level from Sieve
        detail_level = state.get("detail_level", "BRIEF")

        context = {
            "intent_signals": state.get("intent_signals", ""),
            "memories": state.get("memory_hits", []),
            "facts": state.get("facts", []),
            "user_state": state.get("user_state", "NEUTRAL"),
            "conversation_history": sliding_window,
            "detail_level": detail_level,
        }

        # On retry, include feedback from Verdict
        if state.get("retry_count", 0) > 0:
            context["verdict_feedback"] = state.get("verdict_feedback", "")

        agent_input = AgentInput(
            message=state["user_input"],
            context=context,
        )
        output = await self.command.execute(agent_input)

        return {
            "draft_response": output.result,
            "agents_involved": state.get("agents_involved", []) + ["Command"],
        }

    async def _run_verdict(self, state: SwarmState) -> dict[str, Any]:
        """Execute Verdict agent.

        Args:
            state: Current swarm state

        Returns:
            State updates from Verdict
        """
        agent_input = AgentInput(
            message=state["user_input"],
            context={
                "draft_response": state.get("draft_response", ""),
                "intent_signals": state.get("intent_signals", ""),
                "detail_level": state.get("detail_level", "BRIEF"),
            },
        )
        output = await self.verdict.execute(agent_input)

        validation_passed = output.metadata.get("validation_passed", False)

        # If validation passed, set final response
        final_response = None
        verdict_feedback = output.result  # Store feedback for retry

        if validation_passed:
            final_response = state.get("draft_response", "")

        # Increment retry count if validation failed
        # (This needs to happen in the node, not in the conditional function)
        result = {
            "validation_passed": validation_passed,
            "final_response": final_response,
            "verdict_feedback": verdict_feedback,
            "agents_involved": state.get("agents_involved", []) + ["Verdict"],
        }

        if not validation_passed:
            current_retry = state.get("retry_count", 0)
            result["retry_count"] = current_retry + 1

        return result

    async def _run_shield_pass1(self, state: SwarmState) -> dict[str, Any]:
        """Execute Shield Pass 1 - User input safety check.

        Args:
            state: Current swarm state

        Returns:
            State updates from Shield Pass 1
        """
        safety_profile = state.get("safety_profile", "balanced")

        agent_input = AgentInput(
            message=state["user_input"],
            context={
                "safety_profile": safety_profile,
                "pass_number": 1,
            },
        )
        output = await self.shield.execute(agent_input)

        is_safe = output.metadata.get("is_safe", False)

        return {
            "shield_pass1_result": output.result,
            "shield_pass1_safe": is_safe,
            "agents_involved": state.get("agents_involved", []) + ["Shield Pass 1"],
        }

    async def _run_shield_pass2(self, state: SwarmState) -> dict[str, Any]:
        """Execute Shield Pass 2 - AI output safety check.

        Args:
            state: Current swarm state

        Returns:
            State updates from Shield Pass 2
        """
        safety_profile = state.get("safety_profile", "balanced")

        # Check enhanced response if Aura ran, otherwise draft response
        response_to_check = (
            state.get("enhanced_response")
            if state.get("aura_activated")
            else state.get("draft_response", "")
        )

        agent_input = AgentInput(
            message=response_to_check,
            context={
                "safety_profile": safety_profile,
                "pass_number": 2,
            },
        )
        output = await self.shield.execute(agent_input)

        is_safe = output.metadata.get("is_safe", False)

        return {
            "shield_pass2_result": output.result,
            "shield_pass2_safe": is_safe,
            "agents_involved": state.get("agents_involved", []) + ["Shield Pass 2"],
            # Preserve final_response from Verdict (critical for UI)
            "final_response": state.get("final_response"),
            "draft_response": state.get("draft_response"),
        }

    async def _run_sensor(self, state: SwarmState) -> dict[str, Any]:
        """Execute Sensor agent - Mood detection and P(tangent) calculation.

        Args:
            state: Current swarm state

        Returns:
            State updates from Sensor
        """
        agent_input = AgentInput(
            message=state["user_input"],
            context={},
        )
        output = await self.sensor.execute(agent_input)

        mood = output.metadata.get("mood", "NEUTRAL")
        mood_confidence = output.metadata.get("confidence", 0.5)
        mood_modifier = output.metadata.get("mood_modifier", 0.0)
        reasoning = output.metadata.get("reasoning", "")

        # Calculate P(tangent) = base_slider + mood_modifier (clamped [0, 1])
        base_p_tangent = state.get("p_tangent", 0.5)
        calculated_p_tangent = max(0.0, min(1.0, base_p_tangent + mood_modifier))

        return {
            "user_mood": mood,
            "mood_confidence": mood_confidence,
            "mood_modifier": mood_modifier,
            "mood_reasoning": reasoning,
            "p_tangent": calculated_p_tangent,  # Update with calculated value
            "user_state": mood,  # Also set user_state for backward compatibility
            "agents_involved": state.get("agents_involved", []) + ["Sensor"],
        }

    async def _run_parallel_ingress(self, state: SwarmState) -> dict[str, Any]:
        """Run Sieve and Sensor in parallel using asyncio.gather.

        Args:
            state: Current swarm state

        Returns:
            Merged state updates from both agents
        """
        # Run Sieve and Sensor concurrently
        sieve_result, sensor_result = await asyncio.gather(
            self._run_sieve(state),
            self._run_sensor(state),
        )

        # Merge results (sensor result may override p_tangent from sieve)
        merged = {**sieve_result, **sensor_result}

        # Both results contain the full agents_involved list from state + their own agent
        # We need to merge them without duplicating the base agents
        # Take the base from state, then add only the NEW agents from each result
        base_agents = state.get("agents_involved", [])
        sieve_agents = sieve_result.get("agents_involved", [])
        sensor_agents = sensor_result.get("agents_involved", [])

        # Extract only the new agents (those not in base)
        new_from_sieve = [a for a in sieve_agents if a not in base_agents]
        new_from_sensor = [a for a in sensor_agents if a not in base_agents]

        # Combine: base + new from both (preserving order, removing duplicates)
        all_new = new_from_sieve + [a for a in new_from_sensor if a not in new_from_sieve]
        merged["agents_involved"] = base_agents + all_new

        return merged

    async def _run_parallel_egress(self, state: SwarmState) -> dict[str, Any]:
        """Run Verdict and Shield Pass 2 in parallel using asyncio.gather.

        Args:
            state: Current swarm state

        Returns:
            Merged state updates from both agents
        """
        # Run Verdict and Shield Pass 2 concurrently
        verdict_result, shield_result = await asyncio.gather(
            self._run_verdict(state),
            self._run_shield_pass2(state),
        )

        # Merge results
        merged = {**verdict_result, **shield_result}

        # Both results contain the full agents_involved list from state + their own agent
        # We need to merge them without duplicating the base agents
        base_agents = state.get("agents_involved", [])
        verdict_agents = verdict_result.get("agents_involved", [])
        shield_agents = shield_result.get("agents_involved", [])

        # Extract only the new agents (those not in base)
        new_from_verdict = [a for a in verdict_agents if a not in base_agents]
        new_from_shield = [a for a in shield_agents if a not in base_agents]

        # Combine: base + new from both (preserving order, removing duplicates)
        all_new = new_from_verdict + [a for a in new_from_shield if a not in new_from_verdict]
        merged["agents_involved"] = base_agents + all_new

        # Increment retry count if validation failed
        # (This needs to happen in the node, not in the conditional function)
        validation_passed = merged.get("validation_passed", False)
        if not validation_passed:
            current_retry = state.get("retry_count", 0)
            merged["retry_count"] = current_retry + 1

        return merged

    def _should_retry(self, state: SwarmState) -> str:
        """Determine if we should retry Command or finish.

        DEPRECATED: This function is from Phase 1 and is no longer used.
        Use _should_retry_or_abort instead.

        Args:
            state: Current swarm state

        Returns:
            "retry" or "end"
        """
        validation_passed = state.get("validation_passed", False)
        retry_count = state.get("retry_count", 0)
        max_retries = 2

        if not validation_passed and retry_count < max_retries:
            return "retry"
        return "end"

    async def process(
        self,
        user_input: str,
        session_id: str = "default",
        conversation_history: list[dict] | None = None,
        safety_profile: str | None = None,
    ) -> SwarmState:
        """Process a user message through the swarm.

        Args:
            user_input: The user's message
            session_id: Session identifier for memory context
            conversation_history: Recent conversation messages (last 10 turns)
                Format: [{"role": "user", "content": "..."}, ...]
            safety_profile: Safety profile to use (strict/balanced/experimental)

        Returns:
            Final state after all agents have executed
        """
        # Initialize state
        initial_state: SwarmState = {
            "user_input": user_input,
            "session_id": session_id,
            "conversation_history": conversation_history or [],
            "p_tangent": self.config.associative["default_p_tangent"],
            "aura_activated": False,
            "retry_count": 0,
            "agents_involved": [],
            "validation_passed": False,
            "safety_passed": True,
            "safety_profile": safety_profile
            or self.config.safety["default_profile"],
            "shield_pass1_safe": False,
            "shield_pass2_safe": False,
        }

        # Execute the graph
        result = await self.graph.ainvoke(initial_state)

        return result

    async def process_stream(
        self,
        user_input: str,
        session_id: str = "default",
        conversation_history: list[dict] | None = None,
        safety_profile: str | None = None,
        p_tangent: float | None = None,
    ):
        """Process a user message through the swarm with event streaming.

        Args:
            user_input: The user's message
            session_id: Session identifier for memory context
            conversation_history: Recent conversation messages (last 10 turns)
            safety_profile: Safety profile to use (strict/balanced/experimental)
            p_tangent: Base tangent probability (0.0-1.0), defaults to config value

        Yields:
            Events: {"type": "agent_start"|"agent_complete"|"final", "agent": str, "state": dict}
        """
        # Initialize state
        initial_state: SwarmState = {
            "user_input": user_input,
            "session_id": session_id,
            "conversation_history": conversation_history or [],
            "p_tangent": p_tangent if p_tangent is not None else self.config.associative["default_p_tangent"],
            "aura_activated": False,
            "retry_count": 0,
            "agents_involved": [],
            "validation_passed": False,
            "safety_passed": True,
            "safety_profile": safety_profile
            or self.config.safety["default_profile"],
            "shield_pass1_safe": False,
            "shield_pass2_safe": False,
        }

        # Track previous agents_involved list length to detect new completions
        previous_agent_count = 0
        # Track the final state from streaming
        final_state = None

        # Stream events from the graph
        async for event in self.graph.astream(initial_state):
            # event is a dict with node name as key
            for node_name, node_output in event.items():
                # Get current agents list (cumulative)
                current_agents_list = node_output.get("agents_involved", [])
                current_agent_count = len(current_agents_list)

                # If new agents were added (including retries), emit events
                if current_agent_count > previous_agent_count:
                    # Get the newly added agents
                    new_agents = current_agents_list[previous_agent_count:]

                    # Emit event for each new agent
                    for agent in new_agents:
                        yield {
                            "type": "agent_complete",
                            "agent": agent,
                            "state": node_output,
                        }

                    # Update count
                    previous_agent_count = current_agent_count

                # Keep track of the most recent state
                final_state = node_output

        # Yield final event with the last state from streaming
        # DO NOT call ainvoke() again - that would re-run the entire graph!
        if final_state:
            yield {"type": "final", "state": final_state}
