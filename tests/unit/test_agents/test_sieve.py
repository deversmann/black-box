"""Tests for Sieve agent."""

import pytest

from blackbox.agents.sieve import Sieve
from blackbox.core.agent import AgentConfig, AgentInput
from blackbox.models.client import OpenRouterClient


@pytest.mark.asyncio
async def test_sieve_initialization(
    sieve_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Sieve agent initialization."""
    sieve = Sieve(sieve_config, mock_openrouter_client)

    assert sieve.name == "Sieve"
    assert sieve.config.model == "openai/gpt-5.4-nano"
    assert sieve.client == mock_openrouter_client


@pytest.mark.asyncio
async def test_sieve_execute(
    sieve_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Sieve execution."""
    # Setup mock to return intent signals
    mock_openrouter_client.chat_completion.return_value = """- Explain neural networks
- Clarify backpropagation
- User has background knowledge"""

    sieve = Sieve(sieve_config, mock_openrouter_client)

    agent_input = AgentInput(
        message="Can you help me understand how neural networks work? I'm confused about backpropagation."
    )

    output = await sieve.execute(agent_input)

    # Verify output
    assert "neural networks" in output.result.lower()
    assert "backpropagation" in output.result.lower()
    assert output.metadata["agent"] == "Sieve"
    assert output.confidence == 0.95

    # Verify client was called correctly
    mock_openrouter_client.chat_completion.assert_called_once()
    call_args = mock_openrouter_client.chat_completion.call_args
    assert call_args.kwargs["model"] == "openai/gpt-5.4-nano"


def test_sieve_system_prompt(
    sieve_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Sieve system prompt generation."""
    sieve = Sieve(sieve_config, mock_openrouter_client)

    prompt = sieve.get_system_prompt()

    assert "Intent Distiller" in prompt
    assert "bullet points" in prompt.lower()
    assert "concise" in prompt.lower()
