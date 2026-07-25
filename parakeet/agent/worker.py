"""QThread that runs the agent stream and emits Qt signals for the overlay.

Signals replace the original brief's WebSocket events:
  status(str)          — "Using web_search…" style progress lines
  token(str)           — streamed answer text
  confirm_request(str) — human-in-the-loop gate; UI must call provide_confirmation()
  done() / error(str)
"""

from __future__ import annotations

import threading

from PySide6.QtCore import QThread, Signal
from langchain_core.messages import AIMessageChunk, HumanMessage
from langgraph.types import Command


def _text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


class AgentWorker(QThread):
    status = Signal(str)
    token = Signal(str)
    confirm_request = Signal(str)
    done = Signal()
    error = Signal(str)

    def __init__(self, agent, message: HumanMessage, thread_id: str, parent=None):
        super().__init__(parent)
        self._agent = agent
        self._message = message
        self._thread_id = thread_id
        self._confirm_result = False
        self._confirm_event = threading.Event()
        self._pending_action = ""

    def provide_confirmation(self, allowed: bool) -> None:
        """Called from the UI thread when the user clicks Allow/Deny."""
        self._confirm_result = allowed
        self._confirm_event.set()

    def run(self) -> None:
        config = {"configurable": {"thread_id": self._thread_id}}
        payload = {"messages": [self._message]}
        try:
            while True:
                interrupted = self._stream(payload, config)
                if not interrupted:
                    break
                self._confirm_event.clear()
                self.confirm_request.emit(self._pending_action)
                self._confirm_event.wait()
                payload = Command(resume=self._confirm_result)
            self.done.emit()
        except Exception as e:  # surfaced on the overlay
            text = str(e)
            if "rate_limit" in text or "429" in text or "413" in text:
                self.error.emit(
                    "Groq free-tier limit reached — wait about a minute and try again.\n"
                    f"({type(e).__name__}: {text[:200]})"
                )
            else:
                self.error.emit(f"{type(e).__name__}: {e}")

    def _stream(self, payload, config) -> bool:
        """Stream one leg of the run. Returns True if paused on an interrupt."""
        for mode, chunk in self._agent.stream(
            payload, config, stream_mode=["updates", "messages"]
        ):
            if mode == "messages":
                msg_chunk, meta = chunk
                if isinstance(msg_chunk, AIMessageChunk) and meta.get("langgraph_node") == "agent":
                    text = _text_of(msg_chunk.content)
                    if text:
                        self.token.emit(text)
            else:  # updates
                for node, update in chunk.items():
                    if node == "__interrupt__":
                        intr = update[0]
                        value = getattr(intr, "value", {}) or {}
                        self._pending_action = value.get("action", "Allow this action?")
                        return True
                    if node == "agent" and isinstance(update, dict):
                        for msg in update.get("messages", []):
                            for call in getattr(msg, "tool_calls", []) or []:
                                self.status.emit(f"Using {call['name']}…")
        return False
