"""Pytest configuration and shared fixtures."""

from unittest.mock import AsyncMock, Mock

import pytest

from blackbox.core.agent import AgentConfig
from blackbox.core.config import Config
from blackbox.models.client import OpenRouterClient


@pytest.fixture
def mock_openrouter_client() -> AsyncMock:
    """Mock OpenRouter client for testing."""
    client = AsyncMock(spec=OpenRouterClient)
    client.chat_completion = AsyncMock(return_value="Mock response from model")
    return client


@pytest.fixture
def sieve_config() -> AgentConfig:
    """Configuration for Sieve agent."""
    return AgentConfig(
        name="Sieve",
        model="openai/gpt-5.4-nano",
        temperature=0.5,
        max_tokens=300,
        timeout=10,
    )


@pytest.fixture
def flash_config() -> AgentConfig:
    """Configuration for Flash agent."""
    return AgentConfig(
        name="Flash",
        model="openai/gpt-5.4-nano",
        temperature=0.0,
        max_tokens=100,
        timeout=5,
    )


@pytest.fixture
def command_config() -> AgentConfig:
    """Configuration for Command agent."""
    return AgentConfig(
        name="Command",
        model="openai/gpt-5.4",
        temperature=0.7,
        max_tokens=1000,
        timeout=30,
    )


@pytest.fixture
def verdict_config() -> AgentConfig:
    """Configuration for Verdict agent."""
    return AgentConfig(
        name="Verdict",
        model="openai/gpt-5.4-nano",
        temperature=0.3,
        max_tokens=200,
        timeout=10,
    )


@pytest.fixture
def shield_config() -> AgentConfig:
    """Configuration for Shield agent."""
    return AgentConfig(
        name="Shield",
        model="openai/gpt-5.4-nano",
        temperature=0.2,
        max_tokens=150,
        timeout=10,
    )


@pytest.fixture
def sensor_config() -> AgentConfig:
    """Configuration for Sensor agent."""
    return AgentConfig(
        name="Sensor",
        model="openai/gpt-5.4-nano",
        temperature=0.5,
        max_tokens=200,
        timeout=10,
    )


@pytest.fixture
def vault_config() -> AgentConfig:
    """Configuration for Vault agent."""
    return AgentConfig(
        name="Vault",
        model="openai/gpt-5.4-nano",
        temperature=0.0,
        max_tokens=200,
        timeout=5,
    )


@pytest.fixture
def probe_config() -> AgentConfig:
    """Configuration for Probe agent."""
    return AgentConfig(
        name="Probe",
        model="openai/gpt-5.4",
        temperature=0.6,
        max_tokens=400,
        timeout=20,
    )


@pytest.fixture
def aura_config() -> AgentConfig:
    """Configuration for Aura agent."""
    return AgentConfig(
        name="Aura",
        model="openai/gpt-5.4",
        temperature=0.9,
        max_tokens=800,
        timeout=30,
    )


@pytest.fixture
def parser_config() -> AgentConfig:
    """Configuration for Parser agent."""
    return AgentConfig(
        name="Parser",
        model="openai/gpt-5.4-nano",
        temperature=0.3,
        max_tokens=1000,
        timeout=20,
    )


@pytest.fixture
def mock_config() -> Mock:
    """Mock configuration for testing."""
    config = Mock(spec=Config)
    config.agents = {
        "sieve": {
            "name": "Sieve",
            "model": "openai/gpt-5.4-nano",
            "temperature": 0.5,
            "max_tokens": 300,
            "timeout": 10,
        },
        "flash": {
            "name": "Flash",
            "model": "openai/gpt-5.4-nano",
            "temperature": 0.0,
            "max_tokens": 100,
            "timeout": 5,
        },
        "command": {
            "name": "Command",
            "model": "openai/gpt-5.4",
            "temperature": 0.7,
            "max_tokens": 1000,
            "timeout": 30,
        },
        "verdict": {
            "name": "Verdict",
            "model": "openai/gpt-5.4-nano",
            "temperature": 0.3,
            "max_tokens": 200,
            "timeout": 10,
        },
        # Wave 1 agents
        "shield": {
            "name": "Shield",
            "model": "openai/gpt-5.4-nano",
            "temperature": 0.2,
            "max_tokens": 150,
            "timeout": 10,
        },
        "sensor": {
            "name": "Sensor",
            "model": "openai/gpt-5.4-nano",
            "temperature": 0.5,
            "max_tokens": 200,
            "timeout": 10,
        },
        # Wave 2 agents
        "vault": {
            "name": "Vault",
            "model": "openai/gpt-5.4-nano",
            "temperature": 0.0,
            "max_tokens": 200,
            "timeout": 5,
        },
        "probe": {
            "name": "Probe",
            "model": "openai/gpt-5.4",
            "temperature": 0.6,
            "max_tokens": 400,
            "timeout": 20,
        },
        # Wave 3 agents
        "aura": {
            "name": "Aura",
            "model": "openai/gpt-5.4",
            "temperature": 0.9,
            "max_tokens": 800,
            "timeout": 30,
        },
        "parser": {
            "name": "Parser",
            "model": "openai/gpt-5.4-nano",
            "temperature": 0.3,
            "max_tokens": 1000,
            "timeout": 20,
        },
    }
    config.associative = {
        "default_p_tangent": 0.5,
        "aura_activation_threshold": 0.7,
    }
    config.safety = {
        "default_profile": "balanced",
    }
    return config
