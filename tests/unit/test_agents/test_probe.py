"""Tests for Probe agent."""

import pytest

from blackbox.agents.probe import Probe
from blackbox.core.agent import AgentConfig, AgentInput


@pytest.mark.asyncio
async def test_probe_initialization(
    probe_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Probe agent initialization."""
    probe = Probe(probe_config, mock_openrouter_client)

    assert probe.name == "Probe"
    assert probe.config.model == "openai/gpt-5.4"


@pytest.mark.asyncio
async def test_probe_approve_valid_response(
    probe_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Probe approves a logically sound, relevant response."""
    probe = Probe(probe_config, mock_openrouter_client)

    # Mock LLM response: APPROVE
    mock_openrouter_client.chat_completion.return_value = """DECISION: APPROVE
REASONING: Logically sound and directly addresses the user's question"""

    agent_input = AgentInput(
        message="",
        context={
            "draft_response": "Python decorators are functions that modify other functions...",
            "intent_signals": "- Explain what decorators are\n- Keep it brief",
            "user_state": "NEUTRAL",
            "p_tangent": 0.5,
        },
    )

    output = await probe.execute(agent_input)

    # Verify approval
    assert output.metadata["decision"] == "APPROVE"
    assert output.metadata["approved"] is True
    assert output.confidence == 1.0


@pytest.mark.asyncio
async def test_probe_veto_inappropriate_tangent(
    probe_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Probe vetoes response with tangents when user is HURRIED."""
    probe = Probe(probe_config, mock_openrouter_client)

    # Mock LLM response: VETO
    mock_openrouter_client.chat_completion.return_value = """DECISION: VETO
REASONING: User is HURRIED but response includes unnecessary tangents about metaclasses"""

    agent_input = AgentInput(
        message="",
        context={
            "draft_response": "Decorators are great! Speaking of which, let me tell you about metaclasses...",
            "intent_signals": "- Quick explanation of decorators",
            "user_state": "HURRIED",
            "p_tangent": 0.3,
        },
    )

    output = await probe.execute(agent_input)

    # Verify veto
    assert output.metadata["decision"] == "VETO"
    assert output.metadata["approved"] is False
    assert output.confidence == 0.0


@pytest.mark.asyncio
async def test_probe_suggest_improvement(
    probe_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Probe suggests improvements but still approves."""
    probe = Probe(probe_config, mock_openrouter_client)

    # Mock LLM response: SUGGEST
    mock_openrouter_client.chat_completion.return_value = """DECISION: SUGGEST
REASONING: Could mention context managers as related, but core answer is solid"""

    agent_input = AgentInput(
        message="",
        context={
            "draft_response": "Decorators modify function behavior at call time...",
            "intent_signals": "- Explain decorators in detail",
            "user_state": "CURIOUS",
            "p_tangent": 0.6,
        },
    )

    output = await probe.execute(agent_input)

    # Verify SUGGEST is treated as approval
    assert output.metadata["decision"] == "SUGGEST"
    assert output.metadata["approved"] is True
    assert output.confidence == 1.0


@pytest.mark.asyncio
async def test_probe_lenient_with_jovial_user(
    probe_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Probe allows creative tangents for JOVIAL users."""
    probe = Probe(probe_config, mock_openrouter_client)

    # Mock LLM response: APPROVE (lenient with tangents)
    mock_openrouter_client.chat_completion.return_value = """DECISION: APPROVE
REASONING: User is JOVIAL and tangents add educational value"""

    agent_input = AgentInput(
        message="",
        context={
            "draft_response": "Decorators are like function wrappers! Fun fact: they're used extensively in web frameworks...",
            "intent_signals": "- Tell me about decorators",
            "user_state": "JOVIAL",
            "p_tangent": 0.8,
        },
    )

    output = await probe.execute(agent_input)

    # Verify approval despite tangents
    assert output.metadata["decision"] == "APPROVE"
    assert output.metadata["approved"] is True


@pytest.mark.asyncio
async def test_probe_strict_with_frustrated_user(
    probe_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Probe is strict with FRUSTRATED users."""
    probe = Probe(probe_config, mock_openrouter_client)

    # Mock LLM response: VETO
    mock_openrouter_client.chat_completion.return_value = """DECISION: VETO
REASONING: User is FRUSTRATED and needs direct clarity, not examples"""

    agent_input = AgentInput(
        message="",
        context={
            "draft_response": "Well, decorators are complex. Let me show you 5 examples...",
            "intent_signals": "- Why isn't this decorator working???",
            "user_state": "FRUSTRATED",
            "p_tangent": 0.2,
        },
    )

    output = await probe.execute(agent_input)

    # Verify veto for FRUSTRATED user
    assert output.metadata["decision"] == "VETO"
    assert output.metadata["approved"] is False


@pytest.mark.asyncio
async def test_probe_malformed_response(
    probe_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Probe handles malformed LLM responses gracefully."""
    probe = Probe(probe_config, mock_openrouter_client)

    # Mock malformed response (missing DECISION/REASONING)
    mock_openrouter_client.chat_completion.return_value = "This looks good to me!"

    agent_input = AgentInput(
        message="",
        context={
            "draft_response": "Some response",
            "intent_signals": "Some intent",
            "user_state": "NEUTRAL",
            "p_tangent": 0.5,
        },
    )

    output = await probe.execute(agent_input)

    # Should default to APPROVE if parsing fails
    assert output.metadata["decision"] == "APPROVE"
    assert output.metadata["approved"] is True


def test_probe_system_prompt(
    probe_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Probe system prompt generation."""
    probe = Probe(probe_config, mock_openrouter_client)

    prompt = probe.get_system_prompt()

    assert "Devil's Advocate" in prompt
    assert "Logical Coherence" in prompt
    assert "Relevance to Intent" in prompt
    assert "Appropriateness of Tangents" in prompt
    assert "APPROVE" in prompt
    assert "VETO" in prompt
    assert "SUGGEST" in prompt
    assert "HURRIED" in prompt
    assert "FRUSTRATED" in prompt
