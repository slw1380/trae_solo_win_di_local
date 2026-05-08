"""Ollama API client for interacting with local Ollama instance."""

from typing import AsyncIterator, Optional
import json
import httpx
from .config import OllamaConfig


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, config: OllamaConfig):
        """Initialize Ollama client.

        Args:
            config: Ollama configuration
        """
        self.config = config
        self.base_url = config.base_url
        self.timeout = httpx.Timeout(config.timeout, connect=10.0)
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def list_models(self) -> list[str]:
        """List available models.

        Returns:
            List of model names
        """
        client = await self._get_client()
        try:
            response = await client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except httpx.HTTPError as e:
            raise ConnectionError(f"Failed to connect to Ollama: {e}")

    async def check_connection(self) -> bool:
        """Check if Ollama is accessible.

        Returns:
            True if connection successful
        """
        try:
            await self.list_models()
            return True
        except Exception:
            return False

    async def chat(
        self,
        model: str,
        messages: list[dict[str, str]],
        stream: bool = True,
        options: Optional[dict] = None,
    ) -> AsyncIterator[str]:
        """Send chat request to Ollama.

        Args:
            model: Model name to use
            messages: List of message dictionaries with 'role' and 'content'
            stream: Whether to stream the response
            options: Additional model options

        Yields:
            Text chunks from the response
        """
        client = await self._get_client()

        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }

        if options:
            payload["options"] = options

        try:
            async with client.stream("POST", "/api/chat", json=payload) as response:
                response.raise_for_status()

                if stream:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "message" in data:
                                    content = data["message"].get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
                else:
                    data = response.json()
                    if "message" in data:
                        yield data["message"].get("content", "")

        except httpx.HTTPError as e:
            raise ConnectionError(f"Failed to chat with Ollama: {e}")

    async def generate(
        self,
        model: str,
        prompt: str,
        stream: bool = True,
        options: Optional[dict] = None,
    ) -> AsyncIterator[str]:
        """Send generate request to Ollama.

        Args:
            model: Model name to use
            prompt: Input prompt
            stream: Whether to stream the response
            options: Additional model options

        Yields:
            Text chunks from the response
        """
        client = await self._get_client()

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
        }

        if options:
            payload["options"] = options

        try:
            async with client.stream("POST", "/api/generate", json=payload) as response:
                response.raise_for_status()

                if stream:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    content = data["response"]
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
                else:
                    data = response.json()
                    if "response" in data:
                        yield data["response"]

        except httpx.HTTPError as e:
            raise ConnectionError(f"Failed to generate with Ollama: {e}")
