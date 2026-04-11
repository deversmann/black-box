"""Tests for Parser agent."""

import json

import pytest

from blackbox.agents.parser import Parser
from blackbox.core.agent import AgentConfig, AgentInput


@pytest.mark.asyncio
async def test_parser_initialization(
    parser_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Parser agent initialization."""
    parser = Parser(parser_config, mock_openrouter_client)

    assert parser.name == "Parser"
    assert parser.config.model == "openai/gpt-5.4-nano"


@pytest.mark.asyncio
async def test_parser_extracts_memories(
    parser_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Parser extracts structured memories."""
    parser = Parser(parser_config, mock_openrouter_client)

    # Mock JSON response with memories
    mock_memories = [
        {
            "content": "The user is learning Python decorators",
            "type": "task_goal",
            "tags": ["python", "decorators", "programming", "learning"],
            "importance": 0.6,
        },
        {
            "content": "The user prefers detailed explanations with code examples",
            "type": "preference",
            "tags": ["learning_style", "code_examples", "detail"],
            "importance": 0.7,
        },
    ]
    mock_openrouter_client.chat_completion.return_value = json.dumps(mock_memories)

    agent_input = AgentInput(
        message="",
        context={
            "user_message": "How do decorators work? Please explain in detail with examples.",
            "final_response": "Decorators are functions that modify other functions...",
            "conversation_history": [],
        },
    )

    output = await parser.execute(agent_input)

    # Verify memories extracted
    result_memories = json.loads(output.result)
    assert len(result_memories) == 2
    assert result_memories[0]["type"] == "task_goal"
    assert result_memories[1]["type"] == "preference"
    assert output.metadata["memories_extracted"] == 2
    assert output.metadata["is_stored"] is False  # Phase 2: no storage


@pytest.mark.asyncio
async def test_parser_atomic_rewriting(
    parser_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Parser resolves pronouns for atomic memories."""
    parser = Parser(parser_config, mock_openrouter_client)

    # Mock response showing pronoun resolution
    mock_memories = [
        {
            "content": "The user's Honda Shadow motorcycle broke yesterday",
            "type": "user_fact",
            "tags": ["motorcycle", "honda_shadow", "repair"],
            "importance": 0.8,
        }
    ]
    mock_openrouter_client.chat_completion.return_value = json.dumps(mock_memories)

    agent_input = AgentInput(
        message="",
        context={
            "user_message": "It broke yesterday",  # Pronoun "it"
            "final_response": "Sorry to hear about your motorcycle. When did it break?",
            "conversation_history": [
                {"role": "user", "content": "I have a Honda Shadow motorcycle"},
                {"role": "assistant", "content": "Nice! How long have you had it?"},
            ],
        },
    )

    output = await parser.execute(agent_input)

    # Verify atomic rewriting (no pronouns)
    result_memories = json.loads(output.result)
    assert len(result_memories) == 1
    assert "Honda Shadow motorcycle" in result_memories[0]["content"]
    assert "it" not in result_memories[0]["content"]  # Pronoun resolved


@pytest.mark.asyncio
async def test_parser_handles_empty_response(
    parser_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Parser returns empty array when nothing to remember."""
    parser = Parser(parser_config, mock_openrouter_client)

    # Mock empty response
    mock_openrouter_client.chat_completion.return_value = "[]"

    agent_input = AgentInput(
        message="",
        context={
            "user_message": "Thanks!",
            "final_response": "You're welcome!",
            "conversation_history": [],
        },
    )

    output = await parser.execute(agent_input)

    # Verify empty response
    result_memories = json.loads(output.result)
    assert result_memories == []
    assert output.metadata["memories_extracted"] == 0


@pytest.mark.asyncio
async def test_parser_handles_markdown_json(
    parser_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Parser handles JSON wrapped in markdown code blocks."""
    parser = Parser(parser_config, mock_openrouter_client)

    # Mock response with markdown code blocks
    mock_memories = [{"content": "Test memory", "type": "user_fact", "tags": ["test"], "importance": 0.5}]
    mock_openrouter_client.chat_completion.return_value = (
        f"```json\n{json.dumps(mock_memories)}\n```"
    )

    agent_input = AgentInput(
        message="",
        context={
            "user_message": "Test",
            "final_response": "Response",
            "conversation_history": [],
        },
    )

    output = await parser.execute(agent_input)

    # Should parse correctly despite markdown
    result_memories = json.loads(output.result)
    assert len(result_memories) == 1


@pytest.mark.asyncio
async def test_parser_handles_invalid_json(
    parser_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Parser handles invalid JSON gracefully."""
    parser = Parser(parser_config, mock_openrouter_client)

    # Mock invalid JSON response
    mock_openrouter_client.chat_completion.return_value = "This is not valid JSON!"

    agent_input = AgentInput(
        message="",
        context={
            "user_message": "Test",
            "final_response": "Response",
            "conversation_history": [],
        },
    )

    output = await parser.execute(agent_input)

    # Should return empty array on parse failure
    result_memories = json.loads(output.result)
    assert result_memories == []
    assert output.metadata["memories_extracted"] == 0


@pytest.mark.asyncio
async def test_parser_all_memory_types(
    parser_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Parser can extract all 6 memory types."""
    parser = Parser(parser_config, mock_openrouter_client)

    # Mock response with all memory types
    mock_memories = [
        {"content": "user_fact example", "type": "user_fact", "tags": ["fact"], "importance": 0.8},
        {"content": "user_story example", "type": "user_story", "tags": ["story"], "importance": 0.7},
        {"content": "task_goal example", "type": "task_goal", "tags": ["goal"], "importance": 0.6},
        {"content": "preference example", "type": "preference", "tags": ["pref"], "importance": 0.5},
        {"content": "relationship example", "type": "relationship", "tags": ["rel"], "importance": 0.4},
        {"content": "ai_logic example", "type": "ai_logic", "tags": ["logic"], "importance": 0.3},
    ]
    mock_openrouter_client.chat_completion.return_value = json.dumps(mock_memories)

    agent_input = AgentInput(
        message="",
        context={
            "user_message": "Rich conversation",
            "final_response": "Detailed response",
            "conversation_history": [],
        },
    )

    output = await parser.execute(agent_input)

    # Verify all types present
    result_memories = json.loads(output.result)
    assert len(result_memories) == 6
    types = [m["type"] for m in result_memories]
    assert "user_fact" in types
    assert "user_story" in types
    assert "task_goal" in types
    assert "preference" in types
    assert "relationship" in types
    assert "ai_logic" in types


def test_parser_system_prompt(
    parser_config: AgentConfig, mock_openrouter_client
) -> None:
    """Test Parser system prompt generation."""
    parser = Parser(parser_config, mock_openrouter_client)

    prompt = parser.get_system_prompt()

    assert "Architect" in prompt
    assert "Atomic Memory Rewriting" in prompt
    assert "user_fact" in prompt
    assert "user_story" in prompt
    assert "task_goal" in prompt
    assert "preference" in prompt
    assert "relationship" in prompt
    assert "ai_logic" in prompt
    assert "importance" in prompt
    assert "tags" in prompt
