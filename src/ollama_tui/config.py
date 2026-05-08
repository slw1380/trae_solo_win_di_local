"""Configuration management for Ollama TUI Agent."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class OllamaConfig:
    """Configuration for Ollama connection."""

    base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    default_model: str = field(default_factory=lambda: os.getenv("OLLAMA_DEFAULT_MODEL", "llama3.2"))
    timeout: int = 120


@dataclass
class AgentConfig:
    """Configuration for agent behavior."""

    system_message: str = (
        "You are a helpful AI assistant running on a local Ollama instance. "
        "You have access to various tools and can help users with a wide range of tasks. "
        "Always be helpful, concise, and accurate in your responses."
    )
    max_round: int = 10
    temperature: float = 0.7
    max_tokens: int = 4096


@dataclass
class TUIConfig:
    """Configuration for TUI appearance."""

    theme: str = "dark"
    show_timestamps: bool = True
    stream_delay: float = 0.01


@dataclass
class Config:
    """Main configuration class."""

    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    tui: TUIConfig = field(default_factory=TUIConfig)

    config_dir: Path = field(default_factory=lambda: Path.home() / ".config" / "ollama-tui-agent")

    def __post_init__(self):
        """Ensure config directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment variables and files."""
        return cls()

    def save(self):
        """Save configuration (placeholder for future implementation)."""
        pass
