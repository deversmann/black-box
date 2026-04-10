"""Integration tests for the full swarm flow."""

from unittest.mock import AsyncMock

import pytest

from blackbox.core.orchestrator import SwarmOrchestrator


@pytest.mark.asyncio
async def test_full_swarm_execution(
    mock_config: any,
    mock_openrouter_client: AsyncMock,
) -> None:
    """Test complete execution through all Phase 2 Wave 1 agents."""
    # Setup mock responses for each agent
    async def mock_chat_completion(model: str, messages: list, **kwargs: any) -> str:
        # Return different responses based on which agent is calling
        system_prompt = messages[0].content if messages else ""

        if "Shield" in system_prompt:
            # Shield response (Pass 1 or Pass 2)
            return "SAFE: Educational programming question"
        elif "Sensor" in system_prompt or "Empath" in system_prompt:
            # Sensor response
            return "STATE: NEUTRAL\nCONFIDENCE: 0.9\nREASONING: Clear question"
        elif "Intent Distiller" in system_prompt:
            # Sieve response
            return "DETAIL_LEVEL: DETAILED\nINTENT:\n- Explain Python decorators\n- Provide code examples"
        elif "Validator" in system_prompt:
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

    # Verify all Wave 1 agents ran
    assert "Shield Pass 1" in result["agents_involved"]
    assert "Sieve" in result["agents_involved"]
    assert "Sensor" in result["agents_involved"]
    assert "Flash" in result["agents_involved"]
    assert "Command" in result["agents_involved"]
    assert "Verdict" in result["agents_involved"]
    assert "Shield Pass 2" in result["agents_involved"]

    # Verify Shield Pass 1 safety check
    assert result["shield_pass1_safe"] is True

    # Verify Sensor mood detection
    assert result["user_mood"] is not None
    assert result["mood_modifier"] is not None
    assert result["p_tangent"] is not None

    # Verify intent was extracted
    assert result["intent_signals"] is not None
    assert "decorators" in result["intent_signals"].lower()

    # Verify detail level detected
    assert result["detail_level"] == "DETAILED"

    # Verify memories were retrieved (mock)
    assert result["memory_hits"] is not None
    assert len(result["memory_hits"]) == 3

    # Verify response was generated
    assert result["draft_response"] is not None
    assert len(result["draft_response"]) > 0

    # Verify validation passed
    assert result["validation_passed"] is True
    assert result["shield_pass2_safe"] is True
    assert result["final_response"] is not None


@pytest.mark.asyncio
async def test_retry_on_validation_failure(
    mock_config: any,
    mock_openrouter_client: AsyncMock,
) -> None:
    """Test that Command retries when Verdict fails."""
    call_count = {"verdict": 0}

    async def mock_chat_completion(model: str, messages: list, **kwargs: any) -> str:
        system_prompt = messages[0].content if messages else ""

        if "Shield" in system_prompt:
            # Shield always passes in this test
            return "SAFE: Test content"
        elif "Sensor" in system_prompt or "Empath" in system_prompt:
            # Sensor response
            return "STATE: NEUTRAL\nCONFIDENCE: 0.9\nREASONING: Test"
        elif "Validator" in system_prompt:
            call_count["verdict"] += 1
            # Fail first time, pass second time
            if call_count["verdict"] == 1:
                return "FAIL: Response is incomplete"
            else:
                return "PASS: Response is now complete"
        elif "Intent Distiller" in system_prompt:
            return "DETAIL_LEVEL: BRIEF\nINTENT:\n- Test intent"
        else:
            # Command - different response on retry
            return f"Response attempt {call_count['verdict']}"

    mock_openrouter_client.chat_completion.side_effect = mock_chat_completion

    orchestrator = SwarmOrchestrator(mock_config, mock_openrouter_client)

    result = await orchestrator.process(
        user_input="Test message",
        session_id="test_session",
    )

    # Verify retry happened - Verdict should have been called twice
    assert call_count["verdict"] == 2
    # Verify final result passed validation
    assert result["validation_passed"] is True
