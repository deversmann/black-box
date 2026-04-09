"""Tests for Flash agent."""

import pytest

from blackbox.agents.flash import Flash
from blackbox.core.agent import AgentConfig, AgentInput


@pytest.mark.asyncio
async def test_flash_initialization(flash_config: AgentConfig) -> None:
    """Test Flash agent initialization."""
    flash = Flash(flash_config)

    assert flash.name == "Flash"
    assert flash.config.model == "openai/gpt-5.4-nano"


@pytest.mark.asyncio
async def test_flash_execute_returns_mock_memories(flash_config: AgentConfig) -> None:
    """Test Flash returns hardcoded mock memories."""
    flash = Flash(flash_config)

    agent_input = AgentInput(
        message="Test intent signals",
        context={"session_id": "test_session"},
    )

    output = await flash.execute(agent_input)

    # Verify mock memories are returned
    memories = output.metadata["memories"]
    assert len(memories) == 3
    assert memories[0]["type"] == "USER_FACT"
    assert memories[1]["type"] == "USER_STORY"
    assert memories[2]["type"] == "PREFERENCE"

    # Verify metadata
    assert output.metadata["agent"] == "Flash"
    assert output.metadata["is_mock"] is True
    assert output.confidence == 1.0


def test_flash_system_prompt(flash_config: AgentConfig) -> None:
    """Test Flash system prompt generation."""
    flash = Flash(flash_config)

    prompt = flash.get_system_prompt()

    assert "Memory Retrieval" in prompt
    assert "Ledger" in prompt
