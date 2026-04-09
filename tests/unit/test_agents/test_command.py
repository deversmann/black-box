"""Tests for Command agent."""

import pytest

from blackbox.agents.command import Command
from blackbox.core.agent import AgentConfig, AgentInput
from blackbox.models.client import OpenRouterClient


@pytest.mark.asyncio
async def test_command_initialization(
    command_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Command agent initialization."""
    command = Command(command_config, mock_openrouter_client)

    assert command.name == "Command"
    assert command.config.model == "openai/gpt-5.4"
    assert command.client == mock_openrouter_client


@pytest.mark.asyncio
async def test_command_execute(
    command_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Command execution with context."""
    # Setup mock response
    mock_openrouter_client.chat_completion.return_value = "Neural networks are computational models inspired by the human brain..."

    command = Command(command_config, mock_openrouter_client)

    # Prepare test input with context
    memories = [
        {
            "id": "mem_001",
            "type": "USER_FACT",
            "content": "User is a software engineer",
            "similarity": 0.9,
        }
    ]

    agent_input = AgentInput(
        message="Explain neural networks",
        context={
            "intent_signals": "- Explain neural networks\n- Provide examples",
            "memories": memories,
            "user_state": "CURIOUS",
        },
    )

    output = await command.execute(agent_input)

    # Verify output
    assert len(output.result) > 0
    assert output.metadata["agent"] == "Command"
    assert output.metadata["used_memories"] == 1
    assert output.confidence == 0.9

    # Verify client was called with correct model
    mock_openrouter_client.chat_completion.assert_called_once()
    call_args = mock_openrouter_client.chat_completion.call_args
    assert call_args.kwargs["model"] == "openai/gpt-5.4"


def test_command_system_prompt(
    command_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Command system prompt generation."""
    command = Command(command_config, mock_openrouter_client)

    prompt = command.get_system_prompt()

    assert "Master Synthesizer" in prompt
    assert "intent signals" in prompt.lower()
    assert "memory" in prompt.lower()
