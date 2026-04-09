"""Tests for OpenRouter client."""

import os

import pytest

from blackbox.models.client import OpenRouterClient, OpenRouterMessage


def test_client_initialization() -> None:
    """Test client initialization with API key."""
    # Temporarily set env var
    original_key = os.environ.get("OPENROUTER_API_KEY")
    os.environ["OPENROUTER_API_KEY"] = "test-key-123"

    try:
        client = OpenRouterClient()
        assert client.api_key == "test-key-123"
        assert client.base_url == "https://openrouter.ai/api/v1"
    finally:
        # Restore original
        if original_key:
            os.environ["OPENROUTER_API_KEY"] = original_key
        else:
            os.environ.pop("OPENROUTER_API_KEY", None)


def test_client_initialization_no_key() -> None:
    """Test client raises error when API key is missing."""
    # Temporarily remove env var
    original_key = os.environ.get("OPENROUTER_API_KEY")
    os.environ.pop("OPENROUTER_API_KEY", None)

    try:
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY not found"):
            OpenRouterClient()
    finally:
        # Restore original
        if original_key:
            os.environ["OPENROUTER_API_KEY"] = original_key


@pytest.mark.asyncio
async def test_client_close() -> None:
    """Test client cleanup."""
    original_key = os.environ.get("OPENROUTER_API_KEY")
    os.environ["OPENROUTER_API_KEY"] = "test-key-123"

    try:
        client = OpenRouterClient()
        # Should not raise
        await client.close()
    finally:
        if original_key:
            os.environ["OPENROUTER_API_KEY"] = original_key
        else:
            os.environ.pop("OPENROUTER_API_KEY", None)


def test_openrouter_message() -> None:
    """Test OpenRouterMessage model."""
    msg = OpenRouterMessage(role="user", content="Hello")
    assert msg.role == "user"
    assert msg.content == "Hello"
