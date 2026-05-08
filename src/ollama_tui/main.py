"""Main entry point for Ollama TUI Agent."""

import asyncio
import sys
from .tui import OllamaTUI
from .config import Config


def main():
    """Main entry point."""
    try:
        config = Config.load()
        app = OllamaTUI(config)
        asyncio.run(app.run_async())
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
