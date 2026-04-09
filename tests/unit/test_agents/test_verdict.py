"""Tests for Verdict agent."""

import pytest

from blackbox.agents.verdict import Verdict
from blackbox.core.agent import AgentConfig, AgentInput
from blackbox.models.client import OpenRouterClient


@pytest.mark.asyncio
async def test_verdict_initialization(
    verdict_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Verdict agent initialization."""
    verdict = Verdict(verdict_config, mock_openrouter_client)

    assert verdict.name == "Verdict"
    assert verdict.config.model == "openai/gpt-5.4-nano"
    assert verdict.client == mock_openrouter_client


@pytest.mark.asyncio
async def test_verdict_pass(
    verdict_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Verdict with passing response."""
    # Mock a PASS verdict
    mock_openrouter_client.chat_completion.return_value = "PASS: Response is coherent and addresses all intent points"

    verdict = Verdict(verdict_config, mock_openrouter_client)

    agent_input = AgentInput(
        message="Explain neural networks",
        context={
            "draft_response": "Neural networks are...",
            "intent_signals": "- Explain neural networks",
        },
    )

    output = await verdict.execute(agent_input)

    # Verify PASS was detected
    assert output.result.startswith("PASS")
    assert output.metadata["validation_passed"] is True
    assert output.confidence == 0.95


@pytest.mark.asyncio
async def test_verdict_fail(
    verdict_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Verdict with failing response."""
    # Mock a FAIL verdict
    mock_openrouter_client.chat_completion.return_value = "FAIL: Response doesn't address backpropagation as requested"

    verdict = Verdict(verdict_config, mock_openrouter_client)

    agent_input = AgentInput(
        message="Explain neural networks and backpropagation",
        context={
            "draft_response": "Neural networks are computational models...",
            "intent_signals": "- Explain neural networks\n- Explain backpropagation",
        },
    )

    output = await verdict.execute(agent_input)

    # Verify FAIL was detected
    assert output.result.startswith("FAIL")
    assert output.metadata["validation_passed"] is False


def test_verdict_system_prompt(
    verdict_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Verdict system prompt generation."""
    verdict = Verdict(verdict_config, mock_openrouter_client)

    prompt = verdict.get_system_prompt()

    assert "Validator" in prompt
    assert "PASS" in prompt
    assert "FAIL" in prompt
    assert "Coherence" in prompt
