"""Tests for configuration loading."""

import pytest

from blackbox.core.config import load_config, Config


def test_load_default_config() -> None:
    """Test loading default configuration."""
    config = load_config()

    assert isinstance(config, Config)
    assert config.system["name"] == "Black Box Swarm"
    assert "sieve" in config.agents
    assert "command" in config.agents
    assert "flash" in config.agents
    assert "verdict" in config.agents


def test_config_agent_models() -> None:
    """Test agent model assignments."""
    config = load_config()

    # High-reasoning agent (Command)
    assert config.agents["command"]["model"] == "openai/gpt-5.4"

    # Fast agents
    assert config.agents["sieve"]["model"] == "openai/gpt-5.4-nano"
    assert config.agents["flash"]["model"] == "openai/gpt-5.4-nano"
    assert config.agents["verdict"]["model"] == "openai/gpt-5.4-nano"


def test_config_associative_settings() -> None:
    """Test associative behavior settings."""
    config = load_config()

    assert config.associative["default_p_tangent"] == 0.5
    assert config.associative["aura_activation_threshold"] == 0.7
    assert "jovial" in config.associative["mood_modifiers"]


def test_load_nonexistent_config() -> None:
    """Test loading nonexistent config raises error."""
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.yaml")
