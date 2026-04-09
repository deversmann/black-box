"""OpenRouter API client for model interactions."""

import os
from typing import Any

import httpx
from pydantic import BaseModel, Field


class OpenRouterMessage(BaseModel):
    """Message format for OpenRouter API."""

    role: str  # "system", "user", or "assistant"
    content: str


class OpenRouterRequest(BaseModel):
    """Request payload for OpenRouter API."""

    model: str
    messages: list[OpenRouterMessage]
    temperature: float = 0.7
    max_tokens: int = 500


class OpenRouterResponse(BaseModel):
    """Response from OpenRouter API."""

    id: str
    model: str
    choices: list[dict[str, Any]]
    usage: dict[str, int] = Field(default_factory=dict)


class OpenRouterClient:
    """Client for interacting with OpenRouter.ai API."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://openrouter.ai/api/v1",
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        """Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
            base_url: Base URL for OpenRouter API
            retry_attempts: Number of retry attempts on failure
            retry_delay: Delay between retries in seconds
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment")

        self.base_url = base_url
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/blackbox-swarm",
                "X-Title": "Black Box Swarm",
            },
            timeout=30.0,
        )

    async def chat_completion(
        self,
        model: str,
        messages: list[OpenRouterMessage],
        temperature: float = 0.7,
        max_tokens: int = 500,
    ) -> str:
        """Send a chat completion request to OpenRouter.

        Args:
            model: Model identifier (e.g., "openai/gpt-5.4-nano")
            messages: List of messages in the conversation
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            The generated text response

        Raises:
            httpx.HTTPError: If the API request fails
        """
        request = OpenRouterRequest(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        for attempt in range(self.retry_attempts):
            try:
                response = await self.client.post(
                    "/chat/completions",
                    json=request.model_dump(),
                )
                response.raise_for_status()

                data = response.json()
                return data["choices"][0]["message"]["content"]

            except httpx.HTTPError as e:
                if attempt == self.retry_attempts - 1:
                    raise
                # Wait before retrying
                import asyncio

                await asyncio.sleep(self.retry_delay * (attempt + 1))

        raise RuntimeError("Failed to complete chat request after all retries")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
