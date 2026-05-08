"""TUI interface for Ollama Agent using Textual."""

import asyncio
from typing import Optional
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Header,
    Footer,
    Input,
    Static,
    ListView,
    ListItem,
    TextLog,
    ProgressBar,
)
from textual.binding import Binding
from textual import events
from textual.message import Message
from .agent import OllamaAgent
from .config import Config
from datetime import datetime


class ConversationItem(Static):
    """Widget for displaying a single conversation message."""

    def __init__(self, role: str, content: str, timestamp: str, **kwargs):
        """Initialize conversation item.

        Args:
            role: Message role (user/assistant)
            content: Message content
            timestamp: Message timestamp
        """
        super().__init__(**kwargs)
        self.role = role
        self.content = content
        self.timestamp = timestamp

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        role_label = "You" if self.role == "user" else "Assistant"
        role_style = "[bold blue]" if self.role == "user" else "[bold green]"
        yield Static(
            f"{role_style}{role_label}[/] [{self.timestamp}]\n{self.content}",
            markup=True,
            classes="message-content",
        )


class SessionListItem(ListItem):
    """Widget for session list items."""

    def __init__(self, session_id: str, title: str, **kwargs):
        """Initialize session list item.

        Args:
            session_id: Session identifier
            title: Session title
        """
        super().__init__(**kwargs)
        self.session_id = session_id
        self.title = title

    def compose(self) -> ComposeResult:
        """Compose the widget."""
        yield Static(self.title, markup=True)


class StatusBar(Static):
    """Status bar showing connection status and model."""

    def __init__(self, **kwargs):
        """Initialize status bar."""
        super().__init__("● Disconnected | Model: None", **kwargs)

    def update_status(self, connected: bool, model: Optional[str] = None):
        """Update status display.

        Args:
            connected: Whether connected to Ollama
            model: Current model name
        """
        status_icon = "●" if connected else "○"
        status_color = "green" if connected else "red"
        model_text = model or "None"
        self.update(f"{status_icon} [{status_color}]Connected[/] | Model: [yellow]{model_text}[/]")


class OllamaTUI(App):
    """Main TUI application for Ollama Agent."""

    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        height: 100%;
        layout: horizontal;
    }

    #sidebar {
        width: 30%;
        min-width: 20;
        max-width: 40;
        border: solid $primary;
        background: $panel;
    }

    #sidebar-header {
        height: 3;
        padding: 1;
        background: $primary;
        color: $text;
        content-align: center middle;
    }

    #session-list {
        height: 1fr;
        border: solid $primary;
    }

    #sidebar-buttons {
        height: auto;
        padding: 1;
        layout: horizontal;
        spacing: 1;
    }

    #sidebar-buttons Button {
        width: 1fr;
    }

    #chat-area {
        width: 70%;
        layout: vertical;
    }

    #status-bar {
        height: 3;
        padding: 1;
        background: $primary-darken-1;
        color: $text;
    }

    #messages {
        height: 1fr;
        padding: 1;
        border: solid $primary;
    }

    #message-container {
        height: 100%;
        layout: vertical;
    }

    #input-area {
        height: auto;
        padding: 1;
        border: solid $primary;
        background: $panel;
    }

    #input-container {
        layout: horizontal;
        height: auto;
    }

    #message-input {
        width: 1fr;
    }

    #send-button {
        width: auto;
    }

    .message-content {
        margin: 1 0;
        padding: 1;
        background: $panel;
    }

    #session-list ListView {
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("ctrl+n", "new_session", "New Session", show=True),
        Binding("ctrl+k", "clear_chat", "Clear Chat", show=True),
        Binding("ctrl+m", "switch_model", "Switch Model", show=True),
        Binding("enter", "send_message", "Send", show=False),
    ]

    def __init__(self, config: Optional[Config] = None):
        """Initialize the TUI application.

        Args:
            config: Application configuration
        """
        super().__init__()
        self.config = config or Config.load()
        self.agent = OllamaAgent(self.config.ollama, self.config.agent)
        self.sessions: dict[str, list[dict[str, str]]] = {}
        self.current_session_id: Optional[str] = None
        self.is_connected = False
        self.is_loading = False

    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header()

        with Container(id="main-container"):
            with Container(id="sidebar"):
                yield Static("Sessions", id="sidebar-header", markup=True)
                yield ListView(id="session-list")
                with Container(id="sidebar-buttons"):
                    yield Button("New", id="new-session-btn", variant="primary")
                    yield Button("Delete", id="delete-session-btn", variant="error")

            with Container(id="chat-area"):
                yield StatusBar(id="status-bar")

                with Container(id="messages"):
                    yield VerticalScroll(id="message-container")

                with Container(id="input-area"):
                    with Horizontal(id="input-container"):
                        yield Input(placeholder="Type your message...", id="message-input")
                        yield Button("Send", id="send-button", variant="primary")

        yield Footer()

    async def on_mount(self):
        """Handle mount event."""
        self.title = "Ollama TUI Agent"
        await self._check_connection()
        await self._create_new_session()
        await self._load_models()

    async def _check_connection(self):
        """Check Ollama connection."""
        status_bar = self.query_one("#status-bar", StatusBar)
        try:
            self.is_connected = await self.agent.ollama_client.check_connection()
            models = await self.agent.get_available_models()
            if models:
                await self.agent.set_model(models[0])
            status_bar.update_status(self.is_connected, self.agent.current_model)
        except Exception as e:
            self.is_connected = False
            status_bar.update_status(False)
            self.notify(f"Connection error: {e}", severity="error")

    async def _load_models(self):
        """Load available models."""
        if not self.is_connected:
            return

        try:
            models = await self.agent.get_available_models()
            if not models:
                self.notify("No models available. Please pull a model first.", severity="warning")
        except Exception as e:
            self.notify(f"Failed to load models: {e}", severity="error")

    async def _create_new_session(self):
        """Create a new chat session."""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.sessions[session_id] = []
        self.current_session_id = session_id

        session_list = self.query_one("#session-list", ListView)
        await session_list.append(
            SessionListItem(session_id, f"Session {len(self.sessions)}", id=f"session-{session_id}")
        )

        await session_list.clear_children()
        for sess_id, _ in list(self.sessions.items())[-5:]:
            await session_list.append(
                SessionListItem(sess_id, f"Session {len(self.sessions)}", id=f"session-{sess_id}")
            )

        await session_list.index(len(self.sessions) - 1)

    def _switch_session(self, session_id: str):
        """Switch to a different session.

        Args:
            session_id: Session to switch to
        """
        if session_id in self.sessions:
            self.current_session_id = session_id
            self._display_session_history()

    def _display_session_history(self):
        """Display current session history."""
        if not self.current_session_id:
            return

        message_container = self.query_one("#message-container", VerticalScroll)
        message_container.remove_children()

        history = self.sessions.get(self.current_session_id, [])
        for msg in history:
            timestamp = datetime.now().strftime("%H:%M")
            item = ConversationItem(
                role=msg["role"],
                content=msg["content"],
                timestamp=timestamp,
            )
            message_container.mount(item)

        message_container.scroll_end(animate=False)

    async def _send_message(self):
        """Send message and get response."""
        if not self.is_connected:
            self.notify("Not connected to Ollama", severity="error")
            return

        input_widget = self.query_one("#message-input", Input)
        message = input_widget.value.strip()

        if not message:
            return

        if not self.current_session_id:
            await self._create_new_session()

        input_widget.value = ""
        self.is_loading = True

        message_container = self.query_one("#message-container", VerticalScroll)
        user_item = ConversationItem(
            role="user",
            content=message,
            timestamp=datetime.now().strftime("%H:%M"),
        )
        await message_container.mount(user_item)

        self.sessions[self.current_session_id].append({"role": "user", "content": message})

        assistant_item = ConversationItem(
            role="assistant",
            content="",
            timestamp=datetime.now().strftime("%H:%M"),
        )
        response_placeholder = await message_container.mount(assistant_item)

        response_text = []
        try:
            async def stream_callback(chunk: str):
                response_text.append(chunk)
                current_text = "".join(response_text)
                assistant_item = ConversationItem(
                    role="assistant",
                    content=current_text,
                    timestamp=datetime.now().strftime("%H:%M"),
                )
                await response_placeholder.remove()
                response_placeholder = await message_container.mount(assistant_item)
                await message_container.scroll_end(animate=False)

            await self.agent.chat(message, stream_callback=stream_callback)

            if self.current_session_id:
                self.sessions[self.current_session_id].append(
                    {"role": "assistant", "content": "".join(response_text)}
                )

        except Exception as e:
            self.notify(f"Error: {e}", severity="error")
        finally:
            self.is_loading = False

    def action_send_message(self):
        """Handle send message action."""
        asyncio.create_task(self._send_message())

    def action_new_session(self):
        """Handle new session action."""
        asyncio.create_task(self._create_new_session())

    def action_clear_chat(self):
        """Clear current chat."""
        if self.current_session_id:
            self.sessions[self.current_session_id] = []
            message_container = self.query_one("#message-container", VerticalScroll)
            message_container.remove_children()
            self.agent.clear_history()

    async def action_switch_model(self):
        """Switch model."""
        if not self.is_connected:
            self.notify("Not connected to Ollama", severity="error")
            return

        models = await self.agent.get_available_models()
        if not models:
            self.notify("No models available", severity="warning")
            return

        current_index = 0
        if self.agent.current_model in models:
            current_index = models.index(self.agent.current_model)

        next_index = (current_index + 1) % len(models)
        await self.agent.set_model(models[next_index])

        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.update_status(self.is_connected, self.agent.current_model)
        self.notify(f"Switched to model: {self.agent.current_model}")

    async def on_list_view_selected(self, event: ListView.Selected):
        """Handle session selection."""
        if isinstance(event.item, SessionListItem):
            self._switch_session(event.item.session_id)

    async def on_button_pressed(self, event: Button.Pressed):
        """Handle button presses."""
        button_id = event.button.id

        if button_id == "new-session-btn":
            await self._create_new_session()
        elif button_id == "delete-session-btn":
            if self.current_session_id:
                del self.sessions[self.current_session_id]
                self.current_session_id = None
                session_list = self.query_one("#session-list", ListView)
                await session_list.clear_children()
                message_container = self.query_one("#message-container", VerticalScroll)
                message_container.remove_children()

                if self.sessions:
                    self.current_session_id = list(self.sessions.keys())[-1]
                    self._display_session_history()
        elif button_id == "send-button":
            await self._send_message()

    def on_input_submitted(self, event: Input.Submitted):
        """Handle input submission."""
        if event.input.id == "message-input":
            asyncio.create_task(self._send_message())

    async def cleanup(self):
        """Cleanup resources."""
        await self.agent.close()
