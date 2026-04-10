"""Streamlit chat interface for Black Box Swarm."""

import asyncio
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from blackbox.core.config import load_config
from blackbox.core.orchestrator import SwarmOrchestrator
from blackbox.models.client import OpenRouterClient

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


# Page configuration
st.set_page_config(
    page_title="Black Box Swarm",
    page_icon="🧠",
    layout="wide",
)


def get_swarm() -> SwarmOrchestrator:
    """Get a fresh swarm orchestrator for each request.

    Note: We don't cache this because the httpx client needs to be
    created in the same event loop where it will be used.
    """
    config = load_config()
    client = OpenRouterClient()
    return SwarmOrchestrator(config, client)


async def process_message_stream(
    prompt: str,
    session_id: str,
    conversation_history: list[dict],
    status_container,
    safety_profile: str = "balanced",
):
    """Process a message through the swarm with streaming updates.

    Args:
        prompt: User message
        session_id: Session identifier
        conversation_history: Recent conversation messages for context
        status_container: Streamlit status container for updates
        safety_profile: Safety profile to use (strict/balanced/experimental)

    Yields:
        Events from the swarm processing

    Returns:
        Final result dictionary from swarm processing
    """
    orchestrator = get_swarm()

    # Agent emoji mapping (Phase 2 Wave 1)
    agent_icons = {
        "Shield Pass 1": "🛡️",
        "Shield Pass1": "🛡️",
        "Shield_Pass1": "🛡️",
        "Shieldpass1": "🛡️",
        "Shield Pass 2": "🛡️",
        "Shield Pass2": "🛡️",
        "Shield_Pass2": "🛡️",
        "Shieldpass2": "🛡️",
        "Sieve": "🔍",
        "Sensor": "🎭",
        "Flash": "💾",
        "Command": "🧠",
        "Verdict": "✅",
    }

    agent_descriptions = {
        "Shield Pass 1": lambda state: f"Input Safety: {'✓ Safe' if state.get('shield_pass1_safe') else '✗ Unsafe'}",
        "Shield Pass1": lambda state: f"Input Safety: {'✓ Safe' if state.get('shield_pass1_safe') else '✗ Unsafe'}",
        "Shield_Pass1": lambda state: f"Input Safety: {'✓ Safe' if state.get('shield_pass1_safe') else '✗ Unsafe'}",
        "Shieldpass1": lambda state: f"Input Safety: {'✓ Safe' if state.get('shield_pass1_safe') else '✗ Unsafe'}",
        "Shield Pass 2": lambda state: f"Output Safety: {'✓ Safe' if state.get('shield_pass2_safe') else '✗ Unsafe'}",
        "Shield Pass2": lambda state: f"Output Safety: {'✓ Safe' if state.get('shield_pass2_safe') else '✗ Unsafe'}",
        "Shield_Pass2": lambda state: f"Output Safety: {'✓ Safe' if state.get('shield_pass2_safe') else '✗ Unsafe'}",
        "Shieldpass2": lambda state: f"Output Safety: {'✓ Safe' if state.get('shield_pass2_safe') else '✗ Unsafe'}",
        "Sieve": lambda state: f"Intent: {state.get('detail_level', 'BRIEF')}",
        "Sensor": lambda state: f"Mood: {state.get('user_mood', 'NEUTRAL')} ({state.get('mood_modifier', 0):+.1f})",
        "Flash": lambda state: f"Memories: {len(state.get('memory_hits', []))}",
        "Command": "Synthesizing response",
        "Verdict": lambda state: f"{'✓ Pass' if state.get('validation_passed') else '✗ Fail'}",
    }

    try:
        final_state = None

        # Expected agent flow for showing "Running..." indicators
        # Note: Command and Verdict can appear multiple times (retries)
        expected_flow = [
            "Shield Pass 1",
            "Sieve",
            "Sensor",
            "Flash",
            "Command",
            "Verdict",
            "Shield Pass 2",
        ]

        # Track agents seen in THIS execution only (not across session)
        agents_in_current_execution = []
        running_message = None

        async for event in orchestrator.process_stream(
            user_input=prompt,
            session_id=session_id,
            conversation_history=conversation_history,
            safety_profile=safety_profile,
        ):
            event_type = event.get("type")

            if event_type == "agent_complete":
                agent_name = event.get("agent", "Unknown")
                icon = agent_icons.get(agent_name, "⚙️")

                # Get dynamic description
                desc_func = agent_descriptions.get(agent_name)
                if callable(desc_func):
                    description = desc_func(event.get("state", {}))
                else:
                    description = desc_func or "Processing"

                # Clear any running message
                if running_message:
                    running_message.empty()
                    running_message = None

                # Add agent to current execution list
                agents_in_current_execution.append(agent_name)

                # Count how many times THIS agent has appeared in THIS execution
                agent_count_in_execution = agents_in_current_execution.count(
                    agent_name
                )

                # Show retry indicator if this agent has run before in this execution
                if agent_count_in_execution > 1:
                    # This is a retry
                    status_container.write(
                        f"{icon} {agent_name} (🔁 Retry #{agent_count_in_execution - 1}): {description}"
                    )
                else:
                    status_container.write(f"{icon} {agent_name}: {description}")

                # Predict next agent based on current state
                state = event.get("state", {})

                # After Verdict, could be Shield Pass 2 OR retry Command
                if agent_name == "Verdict":
                    validation_passed = state.get("validation_passed", False)
                    retry_count = state.get("retry_count", 0)
                    max_retries = 2

                    if not validation_passed and retry_count <= max_retries:
                        # Verdict failed and retries remain - next is retry Command
                        next_icon = agent_icons.get("Command", "🧠")
                        running_message = status_container.empty()
                        running_message.markdown(
                            f"_🔄 Running: {next_icon} Command (Retry {retry_count})..._"
                        )
                    else:
                        # Verdict passed or max retries - next is Shield Pass 2
                        next_icon = agent_icons.get("Shield Pass 2", "🛡️")
                        running_message = status_container.empty()
                        running_message.markdown(
                            f"_🔄 Running: {next_icon} Shield Pass 2..._"
                        )
                elif agent_name == "Command":
                    # After Command, always Verdict
                    next_icon = agent_icons.get("Verdict", "✅")
                    running_message = status_container.empty()
                    running_message.markdown(
                        f"_🔄 Running: {next_icon} Verdict..._"
                    )
                elif agent_name == "Shield Pass 2":
                    # Shield Pass 2 is the last step - clear running message
                    if running_message:
                        running_message.empty()
                        running_message = None
                else:
                    # Normal flow - find next expected agent
                    current_idx = (
                        expected_flow.index(agent_name)
                        if agent_name in expected_flow
                        else -1
                    )
                    if current_idx >= 0 and current_idx < len(expected_flow) - 1:
                        next_agent = expected_flow[current_idx + 1]
                        next_icon = agent_icons.get(next_agent, "⚙️")
                        running_message = status_container.empty()
                        running_message.markdown(
                            f"_🔄 Running: {next_icon} {next_agent}..._"
                        )

            elif event_type == "final":
                final_state = event.get("state")
                if running_message:
                    running_message.empty()
                    running_message = None
                status_container.update(label="✨ Complete!", state="complete")

        return final_state

    finally:
        # Clean up the httpx client
        await orchestrator.client.close()


def main() -> None:
    """Main Streamlit application."""
    st.title("🧠 Black Box Swarm")
    st.caption("Multi-agent AI learning assistant - Phase 2 Wave 1: Shield + Sensor")

    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")

        # Associative slider (P(tangent))
        p_tangent = st.slider(
            "Associative Slider",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Controls response creativity and tangent probability. Higher = more creative.",
        )

        # Safety profile selector (Wave 1)
        safety_profile = st.selectbox(
            "Safety Profile",
            ["strict", "balanced", "experimental"],
            index=1,  # Default to balanced
            help="Controls content filtering. Strict = maximum safety, Experimental = minimal filtering.",
        )

        st.divider()

        # Metadata Panel (Wave 1)
        st.header("Current State")

        if "last_state" in st.session_state:
            state = st.session_state.last_state

            # Custom CSS for metadata values
            st.markdown(
                """
                <style>
                .metadata-value {
                    background-color: #1e1e1e;
                    color: #4ade80;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 0.85rem;
                    font-weight: 500;
                    margin-top: 4px;
                    margin-bottom: 12px;
                    font-family: 'Monaco', 'Menlo', monospace;
                }
                .metadata-label {
                    font-size: 0.75rem;
                    color: #9ca3af;
                    margin-bottom: 2px;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            # Mood display
            mood = state.get("user_mood", "NEUTRAL")
            mood_emoji = {
                "JOVIAL": "😄",
                "CURIOUS": "🤔",
                "NEUTRAL": "😐",
                "FOCUSED": "🎯",
                "FRUSTRATED": "😤",
                "HURRIED": "⏱️",
            }
            st.markdown('<div class="metadata-label">Mood</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="metadata-value">{mood_emoji.get(mood, "😐")} {mood}</div>',
                unsafe_allow_html=True,
            )

            # P(tangent) calculated value
            p_tangent_calc = state.get("p_tangent", 0.5)
            st.markdown(
                '<div class="metadata-label">P(tangent)</div>', unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="metadata-value">{p_tangent_calc:.2f}</div>',
                unsafe_allow_html=True,
            )

            # Detail Level
            detail = state.get("detail_level", "BRIEF")
            st.markdown(
                '<div class="metadata-label">Detail Level</div>', unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="metadata-value">{detail}</div>', unsafe_allow_html=True
            )

            # Aura Status
            aura = state.get("aura_activated", False)
            aura_status = "✨ Active" if aura else "Inactive"
            st.markdown(
                '<div class="metadata-label">Aura</div>', unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="metadata-value">{aura_status}</div>',
                unsafe_allow_html=True,
            )

            # Safety Profile (current)
            safety = state.get("safety_profile", "balanced")
            st.markdown(
                '<div class="metadata-label">Safety</div>', unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="metadata-value">{safety.capitalize()}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.caption("_No state yet - send a message_")

        st.divider()

        # Session info
        if "session_id" not in st.session_state:
            st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        st.caption(f"Session: `{st.session_state.session_id}`")

        # Debug info
        with st.expander("Debug Info"):
            if "last_agents" in st.session_state:
                st.write("**Agents Involved:**")
                for agent in st.session_state.last_agents:
                    st.write(f"- {agent}")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        # Process through swarm
        with st.chat_message("assistant"):
            # Get last 10 turns (20 messages) for sliding window
            # Don't include the current message (it's passed separately)
            history = (
                st.session_state.messages[-20:]
                if len(st.session_state.messages) > 20
                else st.session_state.messages
            )

            # Show agent progress with status indicator
            with st.status("🧠 Processing through the swarm...", expanded=True) as status:
                # Run async process with streaming updates
                result = asyncio.run(
                    process_message_stream(
                        prompt=prompt,
                        session_id=st.session_state.session_id,
                        conversation_history=history,
                        status_container=status,
                        safety_profile=safety_profile,
                    )
                )

            # Get response
            response = (
                result.get("final_response")
                or result.get("draft_response")
                or "I apologize, but I wasn't able to generate a response. Please try again."
            )

            # Display response
            st.markdown(response)

            # Store in chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Update debug info and state
            st.session_state.last_agents = result.get("agents_involved", [])
            st.session_state.last_state = result  # Store for metadata panel

            # Show validation status
            if not result.get("validation_passed", True):
                st.warning("⚠️ Response validation failed - showing draft")

            # Show safety abort warning (Wave 1)
            if not result.get("shield_pass1_safe", True):
                st.error("🛡️ Shield Pass 1: Input blocked by safety filter")
            elif not result.get("shield_pass2_safe", True):
                st.error("🛡️ Shield Pass 2: Output blocked by safety filter")


if __name__ == "__main__":
    main()
