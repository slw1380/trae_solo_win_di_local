"""AutoGen agent implementation for Ollama TUI."""

from typing import Any, Callable, Optional
import asyncio
from autogen_agentchat import ChatAgent, Team
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import ChatMessage, TextMessage
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from .ollama_client import OllamaClient
from .config import AgentConfig, OllamaConfig


class OllamaAgent:
    """Agent wrapper for Ollama using AutoGen."""

    def __init__(self, ollama_config: OllamaConfig, agent_config: AgentConfig):
        """Initialize Ollama agent.

        Args:
            ollama_config: Ollama connection configuration
            agent_config: Agent behavior configuration
        """
        self.ollama_client = OllamaClient(ollama_config)
        self.agent_config = agent_config
        self._current_model = ollama_config.default_model
        self._conversation_history: list[dict[str, str]] = []

    @property
    def current_model(self) -> str:
        """Get current model name."""
        return self._current_model

    async def set_model(self, model: str):
        """Set the current model.

        Args:
            model: Model name to use
        """
        self._current_model = model

    async def get_available_models(self) -> list[str]:
        """Get list of available models.

        Returns:
            List of model names
        """
        return await self.ollama_client.list_models()

    async def chat(
        self,
        message: str,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Send a chat message and get response.

        Args:
            message: User message
            stream_callback: Optional callback for streaming responses

        Returns:
            Complete response text
        """
        self._conversation_history.append({"role": "user", "content": message})

        full_response = []
        async for chunk in self.ollama_client.chat(
            model=self._current_model,
            messages=self._conversation_history,
            stream=True,
            options={
                "temperature": self.agent_config.temperature,
                "num_predict": self.agent_config.max_tokens,
            },
        ):
            full_response.append(chunk)
            if stream_callback:
                stream_callback(chunk)

        response_text = "".join(full_response)
        self._conversation_history.append({"role": "assistant", "content": response_text})

        return response_text

    async def chat_with_history(
        self,
        messages: list[dict[str, str]],
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Send chat with custom message history.

        Args:
            messages: List of message dictionaries
            stream_callback: Optional callback for streaming responses

        Returns:
            Complete response text
        """
        full_response = []
        async for chunk in self.ollama_client.chat(
            model=self._current_model,
            messages=messages,
            stream=True,
            options={
                "temperature": self.agent_config.temperature,
                "num_predict": self.agent_config.max_tokens,
            },
        ):
            full_response.append(chunk)
            if stream_callback:
                stream_callback(chunk)

        return "".join(full_response)

    def clear_history(self):
        """Clear conversation history."""
        self._conversation_history = []

    def get_history(self) -> list[dict[str, str]]:
        """Get conversation history.

        Returns:
            List of message dictionaries
        """
        return self._conversation_history.copy()

    async def close(self):
        """Close the agent and cleanup resources."""
        await self.ollama_client.close()


class OllamaTeam:
    """Multi-agent team using Ollama."""

    def __init__(self, ollama_config: OllamaConfig, agent_config: AgentConfig):
        """Initialize Ollama team.

        Args:
            ollama_config: Ollama connection configuration
            agent_config: Agent behavior configuration
        """
        self.ollama_config = ollama_config
        self.agent_config = agent_config
        self.ollama_client = OllamaClient(ollama_config)

    async def run_team_task(
        self,
        task: str,
        team_members: list[str],
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Run a task with a team of agents.

        Args:
            task: Task description
            team_members: List of team member names
            stream_callback: Optional callback for streaming responses

        Returns:
            Team's response
        """
        messages = []

        system_prompt = (
            f"{self.agent_config.system_message}\n\n"
            f"You are working with the following team members: {', '.join(team_members)}\n"
            f"Collaborate to solve the following task: {task}"
        )

        messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": task})

        full_response = []
        async for chunk in self.ollama_client.chat(
            model=self.ollama_config.default_model,
            messages=messages,
            stream=True,
        ):
            full_response.append(chunk)
            if stream_callback:
                stream_callback(chunk)

        return "".join(full_response)

    async def close(self):
        """Close team and cleanup resources."""
        await self.ollama_client.close()
