"""Tests for Shield agent."""

import pytest

from blackbox.agents.shield import Shield
from blackbox.core.agent import AgentConfig, AgentInput
from blackbox.models.client import OpenRouterClient


@pytest.mark.asyncio
async def test_shield_initialization(
    shield_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Shield agent initialization."""
    shield = Shield(shield_config, mock_openrouter_client)

    assert shield.name == "Shield"
    assert shield.config.model == "openai/gpt-5.4-nano"
    assert shield.client == mock_openrouter_client


@pytest.mark.asyncio
async def test_shield_pass1_safe_content(
    shield_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Shield Pass 1 with safe content."""
    # Setup mock to return SAFE
    mock_openrouter_client.chat_completion.return_value = (
        "SAFE: Educational programming question"
    )

    shield = Shield(shield_config, mock_openrouter_client)

    agent_input = AgentInput(
        message="How do Python decorators work?",
        context={
            "safety_profile": "balanced",
            "pass_number": 1,
        },
    )

    output = await shield.execute(agent_input)

    # Verify output
    assert output.result.startswith("SAFE")
    assert output.metadata["agent"] == "Shield"
    assert output.metadata["is_safe"] is True
    assert output.metadata["safety_profile"] == "balanced"
    assert output.metadata["pass_number"] == 1

    # Verify client was called correctly
    mock_openrouter_client.chat_completion.assert_called_once()


@pytest.mark.asyncio
async def test_shield_pass1_unsafe_content(
    shield_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Shield Pass 1 with unsafe content."""
    # Setup mock to return UNSAFE
    mock_openrouter_client.chat_completion.return_value = (
        "UNSAFE: Illegal activities"
    )

    shield = Shield(shield_config, mock_openrouter_client)

    agent_input = AgentInput(
        message="How do I hack into a bank?",
        context={
            "safety_profile": "balanced",
            "pass_number": 1,
        },
    )

    output = await shield.execute(agent_input)

    # Verify output
    assert output.result.startswith("UNSAFE")
    assert output.metadata["is_safe"] is False
    assert output.metadata["pass_number"] == 1


@pytest.mark.asyncio
async def test_shield_pass2_safe_output(
    shield_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Shield Pass 2 with safe AI output."""
    # Setup mock to return SAFE
    mock_openrouter_client.chat_completion.return_value = (
        "SAFE: Helpful educational response"
    )

    shield = Shield(shield_config, mock_openrouter_client)

    agent_input = AgentInput(
        message="Decorators in Python allow you to modify functions...",
        context={
            "safety_profile": "balanced",
            "pass_number": 2,
        },
    )

    output = await shield.execute(agent_input)

    # Verify output
    assert output.result.startswith("SAFE")
    assert output.metadata["is_safe"] is True
    assert output.metadata["pass_number"] == 2


@pytest.mark.asyncio
async def test_shield_strict_profile(
    shield_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Shield with strict safety profile."""
    mock_openrouter_client.chat_completion.return_value = (
        "UNSAFE: Violence or gore"
    )

    shield = Shield(shield_config, mock_openrouter_client)

    agent_input = AgentInput(
        message="Tell me about violence in history",
        context={
            "safety_profile": "strict",
            "pass_number": 1,
        },
    )

    output = await shield.execute(agent_input)

    # Verify strict profile was applied
    assert output.metadata["safety_profile"] == "strict"


@pytest.mark.asyncio
async def test_shield_experimental_profile(
    shield_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Shield with experimental safety profile (minimal filtering)."""
    mock_openrouter_client.chat_completion.return_value = (
        "SAFE: Mature topic with appropriate context"
    )

    shield = Shield(shield_config, mock_openrouter_client)

    agent_input = AgentInput(
        message="Explain the history of warfare tactics",
        context={
            "safety_profile": "experimental",
            "pass_number": 1,
        },
    )

    output = await shield.execute(agent_input)

    # Verify experimental profile allows more content
    assert output.metadata["safety_profile"] == "experimental"
    assert output.metadata["is_safe"] is True


def test_shield_system_prompt_pass1(
    shield_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Shield system prompt generation for Pass 1."""
    shield = Shield(shield_config, mock_openrouter_client)

    prompt = shield.get_system_prompt("balanced", 1)

    assert "Shield" in prompt
    assert "BALANCED" in prompt
    assert "user input BEFORE processing" in prompt
    assert "Safety Profile" in prompt


def test_shield_system_prompt_pass2(
    shield_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Shield system prompt generation for Pass 2."""
    shield = Shield(shield_config, mock_openrouter_client)

    prompt = shield.get_system_prompt("balanced", 2)

    assert "Shield" in prompt
    assert "BALANCED" in prompt
    assert "AI-generated response BEFORE delivery" in prompt


def test_shield_system_prompt_strict(
    shield_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Shield system prompt for strict profile."""
    shield = Shield(shield_config, mock_openrouter_client)

    prompt = shield.get_system_prompt("strict", 1)

    assert "STRICT" in prompt
    assert "blocking" in prompt.lower()
