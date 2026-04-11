"""Tests for Aura agent."""

import pytest

from blackbox.agents.aura import Aura
from blackbox.core.agent import AgentConfig, AgentInput


@pytest.mark.asyncio
async def test_aura_initialization(
    aura_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Aura agent initialization."""
    aura = Aura(aura_config, mock_openrouter_client)

    assert aura.name == "Aura"
    assert aura.config.model == "openai/gpt-5.4"


@pytest.mark.asyncio
async def test_aura_enhances_response(
    aura_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Aura enhances draft response with narrative flair."""
    aura = Aura(aura_config, mock_openrouter_client)

    # Mock enhanced response (more engaging than draft)
    mock_openrouter_client.chat_completion.return_value = """Python decorators are like magical wrappers for your functions. Imagine taking a basic function and wrapping it in layers of extra behavior - logging, timing, validation - without touching its core. The decorator takes your function, gives it superpowers, and hands it back, ready to do more than it could before."""

    agent_input = AgentInput(
        message="",
        context={
            "draft_response": "Python decorators are functions that modify other functions. They take a function as input and return a new function with added behavior.",
            "user_mood": "JOVIAL",
            "p_tangent": 0.8,
        },
    )

    output = await aura.execute(agent_input)

    # Verify enhancement
    assert "magical wrappers" in output.result
    assert "superpowers" in output.result
    assert output.metadata["agent"] == "Aura"
    assert output.metadata["enhanced_length"] > output.metadata["original_length"]
    assert output.confidence == 1.0


@pytest.mark.asyncio
async def test_aura_tracks_enhancement_ratio(
    aura_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Aura tracks enhancement ratio."""
    aura = Aura(aura_config, mock_openrouter_client)

    draft = "Short response."
    enhanced = "This is a longer, more engaging response with narrative flair."

    mock_openrouter_client.chat_completion.return_value = enhanced

    agent_input = AgentInput(
        message="",
        context={
            "draft_response": draft,
            "user_mood": "CURIOUS",
            "p_tangent": 0.75,
        },
    )

    output = await aura.execute(agent_input)

    # Verify ratio tracking
    assert output.metadata["original_length"] == len(draft)
    assert output.metadata["enhanced_length"] == len(enhanced)
    assert output.metadata["enhancement_ratio"] > 1.0


@pytest.mark.asyncio
async def test_aura_handles_empty_draft(
    aura_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Aura handles empty draft gracefully."""
    aura = Aura(aura_config, mock_openrouter_client)

    mock_openrouter_client.chat_completion.return_value = "Enhanced response"

    agent_input = AgentInput(
        message="",
        context={
            "draft_response": "",
            "user_mood": "NEUTRAL",
            "p_tangent": 0.7,
        },
    )

    output = await aura.execute(agent_input)

    # Should handle gracefully
    assert output.metadata["enhancement_ratio"] == 1.0
    assert output.result == "Enhanced response"


@pytest.mark.asyncio
async def test_aura_with_jovial_mood(
    aura_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Aura adapts to JOVIAL mood."""
    aura = Aura(aura_config, mock_openrouter_client)

    mock_openrouter_client.chat_completion.return_value = (
        "Decorators are awesome! They're like superpowers for your functions! 🎉"
    )

    agent_input = AgentInput(
        message="",
        context={
            "draft_response": "Decorators modify functions.",
            "user_mood": "JOVIAL",
            "p_tangent": 0.9,
        },
    )

    output = await aura.execute(agent_input)

    # Verify playful enhancement
    assert output.result  # Got enhanced response
    assert output.confidence == 1.0


@pytest.mark.asyncio
async def test_aura_with_curious_mood(
    aura_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Aura adapts to CURIOUS mood."""
    aura = Aura(aura_config, mock_openrouter_client)

    mock_openrouter_client.chat_completion.return_value = (
        "Have you ever wondered how decorators work? It's a fascinating journey into Python's metaprogramming..."
    )

    agent_input = AgentInput(
        message="",
        context={
            "draft_response": "Decorators modify functions.",
            "user_mood": "CURIOUS",
            "p_tangent": 0.85,
        },
    )

    output = await aura.execute(agent_input)

    # Verify exploratory enhancement
    assert output.result
    assert output.confidence == 1.0


def test_aura_system_prompt(aura_config: AgentConfig, mock_openrouter_client) -> None:
    """Test Aura system prompt generation."""
    aura = Aura(aura_config, mock_openrouter_client)

    prompt = aura.get_system_prompt()

    assert "Storyteller" in prompt
    assert "Metaphors" in prompt
    assert "Sensory Details" in prompt
    assert "Emotional Language" in prompt
    assert "narrative decorator" in prompt
    assert "NEVER change facts" in prompt
    assert "P(tangent)" in prompt
