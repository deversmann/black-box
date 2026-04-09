"""Streamlit chat interface for Black Box Swarm."""

import asyncio
from datetime import datetime

import streamlit as st

from blackbox.core.config import load_config
from blackbox.core.orchestrator import SwarmOrchestrator
from blackbox.models.client import OpenRouterClient


# Page configuration
st.set_page_config(
    page_title="Black Box Swarm",
    page_icon="🧠",
    layout="wide",
)


@st.cache_resource
def init_swarm() -> SwarmOrchestrator:
    """Initialize the swarm orchestrator (cached)."""
    config = load_config()
    client = OpenRouterClient()
    return SwarmOrchestrator(config, client)


def main() -> None:
    """Main Streamlit application."""
    st.title("🧠 Black Box Swarm")
    st.caption("Multi-agent AI learning assistant - Phase 1 MVP")

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
            with st.spinner("Thinking..."):
                orchestrator = init_swarm()

                # Run async process in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    orchestrator.process(
                        user_input=prompt,
                        session_id=st.session_state.session_id,
                    )
                )
                loop.close()

                # Get response
                response = result.get("final_response") or result.get("draft_response") or "I apologize, but I wasn't able to generate a response. Please try again."

                # Display response
                st.markdown(response)

                # Store in chat history
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Update debug info
                st.session_state.last_agents = result.get("agents_involved", [])

                # Show validation status
                if not result.get("validation_passed", True):
                    st.warning("⚠️ Response validation failed - showing draft")


if __name__ == "__main__":
    main()
