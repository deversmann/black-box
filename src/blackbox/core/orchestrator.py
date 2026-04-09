"""LangGraph orchestration for the Black Box Swarm."""

from typing import Any

from langgraph.graph import StateGraph, END

from blackbox.agents.command import Command
from blackbox.agents.flash import Flash
from blackbox.agents.sieve import Sieve
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
        self.command = Command(
            AgentConfig(**config.agents["command"]),
            client,
        )
        self.verdict = Verdict(
            AgentConfig(**config.agents["verdict"]),
            client,
        )

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph execution graph.

        Returns:
            Compiled StateGraph ready for execution
        """
        # Create the graph with SwarmState
        workflow = StateGraph(SwarmState)

        # Add nodes for each agent
        workflow.add_node("sieve", self._run_sieve)
        workflow.add_node("flash", self._run_flash)
        workflow.add_node("command", self._run_command)
        workflow.add_node("verdict", self._run_verdict)

        # Define the execution flow
        workflow.set_entry_point("sieve")
        workflow.add_edge("sieve", "flash")
        workflow.add_edge("flash", "command")
        workflow.add_edge("command", "verdict")

        # Verdict decides if we're done or need to retry
        workflow.add_conditional_edges(
            "verdict",
            self._should_retry,
            {
                "retry": "command",  # Retry synthesis
                "end": END,  # Finish
            },
        )

        return workflow.compile()

    async def _run_sieve(self, state: SwarmState) -> dict[str, Any]:
        """Execute Sieve agent.

        Args:
            state: Current swarm state

        Returns:
            State updates from Sieve
        """
        agent_input = AgentInput(message=state["user_input"])
        output = await self.sieve.execute(agent_input)

        return {
            "intent_signals": output.result,
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

    async def _run_command(self, state: SwarmState) -> dict[str, Any]:
        """Execute Command agent.

        Args:
            state: Current swarm state

        Returns:
            State updates from Command
        """
        # Build context - include Verdict feedback on retry
        context = {
            "intent_signals": state.get("intent_signals", ""),
            "memories": state.get("memory_hits", []),
            "user_state": state.get("user_state", "NEUTRAL"),
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
            },
        )
        output = await self.verdict.execute(agent_input)

        validation_passed = output.metadata.get("validation_passed", False)

        # If validation passed, set final response
        final_response = None
        verdict_feedback = output.result  # Store feedback for retry

        if validation_passed:
            final_response = state.get("draft_response", "")

        return {
            "validation_passed": validation_passed,
            "final_response": final_response,
            "verdict_feedback": verdict_feedback,
            "agents_involved": state.get("agents_involved", []) + ["Verdict"],
        }

    def _should_retry(self, state: SwarmState) -> str:
        """Determine if we should retry Command or finish.

        Args:
            state: Current swarm state

        Returns:
            "retry" or "end"
        """
        validation_passed = state.get("validation_passed", False)
        retry_count = state.get("retry_count", 0)
        max_retries = 2

        if not validation_passed and retry_count < max_retries:
            # Increment retry count for next iteration
            state["retry_count"] = retry_count + 1
            return "retry"
        return "end"

    async def process(self, user_input: str, session_id: str = "default") -> SwarmState:
        """Process a user message through the swarm.

        Args:
            user_input: The user's message
            session_id: Session identifier for memory context

        Returns:
            Final state after all agents have executed
        """
        # Initialize state
        initial_state: SwarmState = {
            "user_input": user_input,
            "session_id": session_id,
            "p_tangent": self.config.associative["default_p_tangent"],
            "aura_activated": False,
            "retry_count": 0,
            "agents_involved": [],
            "validation_passed": False,
            "safety_passed": True,  # Phase 1: Always pass safety
        }

        # Execute the graph
        result = await self.graph.ainvoke(initial_state)

        return result
