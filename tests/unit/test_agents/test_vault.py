"""Tests for Vault agent."""

import pytest

from blackbox.agents.vault import Vault
from blackbox.core.agent import AgentConfig, AgentInput


@pytest.mark.asyncio
async def test_vault_initialization(vault_config: AgentConfig) -> None:
    """Test Vault agent initialization."""
    vault = Vault(vault_config)

    assert vault.name == "Vault"
    assert vault.config.model == "openai/gpt-5.4-nano"


@pytest.mark.asyncio
async def test_vault_execute_returns_mock_facts(vault_config: AgentConfig) -> None:
    """Test Vault returns hardcoded mock facts."""
    vault = Vault(vault_config)

    # Simulate memory hits from Flash
    mock_memory_hits = [
        {"id": "mem_001", "type": "USER_FACT"},
        {"id": "mem_002", "type": "PREFERENCE"},
    ]

    agent_input = AgentInput(
        message="",  # Vault doesn't need the message
        context={"memory_hits": mock_memory_hits},
    )

    output = await vault.execute(agent_input)

    # Verify mock facts are returned
    facts = output.metadata["facts"]
    assert len(facts) == 5
    assert all(isinstance(fact, str) for fact in facts)

    # Verify metadata
    assert output.metadata["agent"] == "Vault"
    assert output.metadata["is_mock"] is True
    assert output.metadata["memory_context_count"] == 2
    assert output.confidence == 1.0


@pytest.mark.asyncio
async def test_vault_execute_handles_empty_memory_hits(
    vault_config: AgentConfig,
) -> None:
    """Test Vault handles empty memory hits gracefully."""
    vault = Vault(vault_config)

    agent_input = AgentInput(
        message="",
        context={},  # No memory_hits provided
    )

    output = await vault.execute(agent_input)

    # Should still return mock facts
    facts = output.metadata["facts"]
    assert len(facts) == 5
    assert output.metadata["memory_context_count"] == 0


def test_vault_system_prompt(vault_config: AgentConfig) -> None:
    """Test Vault system prompt generation."""
    vault = Vault(vault_config)

    prompt = vault.get_system_prompt()

    assert "Librarian" in prompt
    assert "Ledger" in prompt
    assert "relational" in prompt.lower()
