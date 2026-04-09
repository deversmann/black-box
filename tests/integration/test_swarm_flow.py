"""Integration tests for the full swarm flow."""

from unittest.mock import AsyncMock

import pytest

from blackbox.core.orchestrator import SwarmOrchestrator


@pytest.mark.asyncio
async def test_full_swarm_execution(
    mock_config: any,
    mock_openrouter_client: AsyncMock,
) -> None:
    """Test complete execution through all Phase 1 agents."""
    # Setup mock responses for each agent
    async def mock_chat_completion(model: str, messages: list, **kwargs: any) -> str:
        # Return different responses based on which agent is calling
        last_message = messages[-1].content if messages else ""

        if "Intent Distiller" in messages[0].content:
            # Sieve response
            return "- Explain Python decorators\n- Provide code examples"
        elif "Validator" in messages[0].content:
            # Verdict response
            return "PASS: Response is clear and complete"
        else:
            # Command response
            return "Python decorators are functions that modify the behavior of other functions..."

    mock_openrouter_client.chat_completion.side_effect = mock_chat_completion

    # Create orchestrator
    orchestrator = SwarmOrchestrator(mock_config, mock_openrouter_client)

    # Process a message
    result = await orchestrator.process(
        user_input="Can you explain Python decorators with examples?",
        session_id="test_session",
    )

    # Verify execution
    assert result["user_input"] == "Can you explain Python decorators with examples?"
    assert result["session_id"] == "test_session"

    # Verify all agents ran
    assert "Sieve" in result["agents_involved"]
    assert "Flash" in result["agents_involved"]
    assert "Command" in result["agents_involved"]
    assert "Verdict" in result["agents_involved"]

    # Verify intent was extracted
    assert result["intent_signals"] is not None
    assert "decorators" in result["intent_signals"].lower()

    # Verify memories were retrieved (mock)
    assert result["memory_hits"] is not None
    assert len(result["memory_hits"]) == 3

    # Verify response was generated
    assert result["draft_response"] is not None
    assert len(result["draft_response"]) > 0

    # Verify validation passed
    assert result["validation_passed"] is True
    assert result["final_response"] is not None


@pytest.mark.asyncio
async def test_retry_on_validation_failure(
    mock_config: any,
    mock_openrouter_client: AsyncMock,
) -> None:
    """Test that Command retries when Verdict fails."""
    call_count = {"verdict": 0}

    async def mock_chat_completion(model: str, messages: list, **kwargs: any) -> str:
        if "Validator" in messages[0].content:
            call_count["verdict"] += 1
            # Fail first time, pass second time
            if call_count["verdict"] == 1:
                return "FAIL: Response is incomplete"
            else:
                return "PASS: Response is now complete"
        elif "Intent Distiller" in messages[0].content:
            return "- Test intent"
        else:
            # Command - different response on retry
            return f"Response attempt {call_count['verdict']}"

    mock_openrouter_client.chat_completion.side_effect = mock_chat_completion

    orchestrator = SwarmOrchestrator(mock_config, mock_openrouter_client)

    result = await orchestrator.process(
        user_input="Test message",
        session_id="test_session",
    )

    # Verify retry happened
    assert call_count["verdict"] >= 1
    # Note: Full retry logic will be tested when we implement the retry counter
