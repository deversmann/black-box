"""Tests for Sensor agent."""

import pytest

from blackbox.agents.sensor import Sensor
from blackbox.core.agent import AgentConfig, AgentInput
from blackbox.models.client import OpenRouterClient


@pytest.mark.asyncio
async def test_sensor_initialization(
    sensor_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Sensor agent initialization."""
    sensor = Sensor(sensor_config, mock_openrouter_client)

    assert sensor.name == "Sensor"
    assert sensor.config.model == "openai/gpt-5.4-nano"
    assert sensor.client == mock_openrouter_client


@pytest.mark.asyncio
async def test_sensor_detect_jovial(
    sensor_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Sensor detects JOVIAL mood."""
    # Setup mock to return JOVIAL state
    mock_openrouter_client.chat_completion.return_value = """STATE: JOVIAL
CONFIDENCE: 0.9
REASONING: Enthusiastic language with emoji and exclamation mark"""

    sensor = Sensor(sensor_config, mock_openrouter_client)

    agent_input = AgentInput(
        message="This is awesome! 😄 Can you explain more about decorators?"
    )

    output = await sensor.execute(agent_input)

    # Verify output
    assert output.metadata["mood"] == "JOVIAL"
    assert output.metadata["confidence"] == 0.9
    assert output.metadata["mood_modifier"] == 0.2  # JOVIAL = +0.2
    assert "Enthusiastic" in output.metadata["reasoning"]


@pytest.mark.asyncio
async def test_sensor_detect_frustrated(
    sensor_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Sensor detects FRUSTRATED mood."""
    mock_openrouter_client.chat_completion.return_value = """STATE: FRUSTRATED
CONFIDENCE: 0.85
REASONING: Explicit confusion statement and defeated tone"""

    sensor = Sensor(sensor_config, mock_openrouter_client)

    agent_input = AgentInput(
        message="I'm so confused about decorators. Nothing makes sense..."
    )

    output = await sensor.execute(agent_input)

    # Verify output
    assert output.metadata["mood"] == "FRUSTRATED"
    assert output.metadata["confidence"] == 0.85
    assert output.metadata["mood_modifier"] == -0.2  # FRUSTRATED = -0.2
    assert "confusion" in output.metadata["reasoning"].lower()


@pytest.mark.asyncio
async def test_sensor_detect_neutral(
    sensor_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Sensor detects NEUTRAL mood."""
    mock_openrouter_client.chat_completion.return_value = """STATE: NEUTRAL
CONFIDENCE: 0.9
REASONING: Clear, straightforward question with no emotional indicators"""

    sensor = Sensor(sensor_config, mock_openrouter_client)

    agent_input = AgentInput(message="What are Python decorators?")

    output = await sensor.execute(agent_input)

    # Verify output
    assert output.metadata["mood"] == "NEUTRAL"
    assert output.metadata["mood_modifier"] == 0.0  # NEUTRAL = 0.0


@pytest.mark.asyncio
async def test_sensor_detect_hurried(
    sensor_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Sensor detects HURRIED mood."""
    mock_openrouter_client.chat_completion.return_value = """STATE: HURRIED
CONFIDENCE: 0.8
REASONING: Very brief one-word question suggests time pressure"""

    sensor = Sensor(sensor_config, mock_openrouter_client)

    agent_input = AgentInput(message="decorators?")

    output = await sensor.execute(agent_input)

    # Verify output
    assert output.metadata["mood"] == "HURRIED"
    assert output.metadata["mood_modifier"] == -0.2  # HURRIED = -0.2


@pytest.mark.asyncio
async def test_sensor_detect_curious(
    sensor_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Sensor detects CURIOUS mood."""
    mock_openrouter_client.chat_completion.return_value = """STATE: CURIOUS
CONFIDENCE: 0.85
REASONING: Exploratory question with wonder language"""

    sensor = Sensor(sensor_config, mock_openrouter_client)

    agent_input = AgentInput(
        message="I wonder how this could apply to my project?"
    )

    output = await sensor.execute(agent_input)

    # Verify output
    assert output.metadata["mood"] == "CURIOUS"
    assert output.metadata["mood_modifier"] == 0.1  # CURIOUS = +0.1


@pytest.mark.asyncio
async def test_sensor_detect_focused(
    sensor_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Sensor detects FOCUSED mood."""
    mock_openrouter_client.chat_completion.return_value = """STATE: FOCUSED
CONFIDENCE: 0.9
REASONING: Task-oriented language with imperative tone"""

    sensor = Sensor(sensor_config, mock_openrouter_client)

    agent_input = AgentInput(
        message="I need to fix this bug. How do I handle errors?"
    )

    output = await sensor.execute(agent_input)

    # Verify output
    assert output.metadata["mood"] == "FOCUSED"
    assert output.metadata["mood_modifier"] == -0.1  # FOCUSED = -0.1


def test_sensor_system_prompt(
    sensor_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Sensor system prompt generation."""
    sensor = Sensor(sensor_config, mock_openrouter_client)

    prompt = sensor.get_system_prompt()

    assert "Sensor" in prompt
    assert "Empath" in prompt
    assert "JOVIAL" in prompt
    assert "FRUSTRATED" in prompt
    assert "emotional state" in prompt.lower()


def test_sensor_mood_modifiers():
    """Test that Sensor has correct mood modifier mappings."""
    assert Sensor.MOOD_MODIFIERS["JOVIAL"] == 0.2
    assert Sensor.MOOD_MODIFIERS["CURIOUS"] == 0.1
    assert Sensor.MOOD_MODIFIERS["NEUTRAL"] == 0.0
    assert Sensor.MOOD_MODIFIERS["FOCUSED"] == -0.1
    assert Sensor.MOOD_MODIFIERS["FRUSTRATED"] == -0.2
    assert Sensor.MOOD_MODIFIERS["HURRIED"] == -0.2


@pytest.mark.asyncio
async def test_sensor_malformed_response(
    sensor_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Sensor handles malformed LLM response gracefully."""
    # Setup mock to return malformed response
    mock_openrouter_client.chat_completion.return_value = (
        "This is not a valid format"
    )

    sensor = Sensor(sensor_config, mock_openrouter_client)

    agent_input = AgentInput(message="Test message")

    output = await sensor.execute(agent_input)

    # Verify defaults are used
    assert output.metadata["mood"] == "NEUTRAL"  # Default
    assert output.metadata["confidence"] == 0.5  # Default
    assert output.metadata["mood_modifier"] == 0.0  # NEUTRAL modifier


@pytest.mark.asyncio
async def test_sensor_partial_response(
    sensor_config: AgentConfig,
    mock_openrouter_client: OpenRouterClient,
) -> None:
    """Test Sensor handles partial LLM response."""
    # Setup mock with only STATE, missing CONFIDENCE and REASONING
    mock_openrouter_client.chat_completion.return_value = "STATE: JOVIAL"

    sensor = Sensor(sensor_config, mock_openrouter_client)

    agent_input = AgentInput(message="Yay! 😄")

    output = await sensor.execute(agent_input)

    # Verify STATE is parsed, defaults for missing fields
    assert output.metadata["mood"] == "JOVIAL"
    assert output.metadata["confidence"] == 0.5  # Default when missing
    assert output.metadata["mood_modifier"] == 0.2  # JOVIAL modifier
