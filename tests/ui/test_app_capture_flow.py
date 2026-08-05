"""Integration test for OnCUE's core loop: hotkey-triggered capture ->
screenshot -> agent stream (real QThread, fake LLM) -> overlay renders the
answer. External services (hotkeys, audio devices, screenshot capture, TTS,
model provider) are stubbed at their real boundaries so the test never
touches OS-level global hotkeys or hardware — everything else, including the
Qt signal wiring between OnCUEApp, AgentWorker, and Overlay across threads,
runs for real."""
from __future__ import annotations

from langchain_core.messages import AIMessageChunk
from PySide6.QtWidgets import QApplication

import oncue.config as config_module
from oncue.app import OnCUEApp


class _NoopHotkeyManager:
    """Registering a real HotkeyManager would install a global OS keyboard
    hook — never do that from an automated test."""

    def register(self, *args, **kwargs):
        pass

    def start(self):
        pass

    def stop(self):
        pass


class _FakeStreamingAgent:
    """Yields the same event shape AgentWorker._stream expects, so the real
    threading/signal code path runs without needing a real model provider."""

    def __init__(self, tokens: list[str]):
        self._tokens = tokens

    def stream(self, payload, config, stream_mode):
        for text in self._tokens:
            yield "messages", (AIMessageChunk(content=text), {"langgraph_node": "agent"})


def _build_app(qtbot, monkeypatch) -> OnCUEApp:
    config_module.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    config_module.CONFIG_FILE.write_text("", encoding="utf-8")  # exists() -> skip onboarding modal

    monkeypatch.setattr("oncue.app.HotkeyManager", _NoopHotkeyManager)
    monkeypatch.setattr("oncue.audio.warmup_system_audio", lambda: None)
    monkeypatch.setattr("oncue.app.screenshot_png", lambda: b"\x89PNG-fake-bytes")

    app = OnCUEApp(QApplication.instance())
    qtbot.addWidget(app.overlay)
    qtbot.addWidget(app.indicator)
    app._tts_enabled = False  # avoid a real edge-tts/pygame call once the answer completes
    return app


def test_capture_hotkey_streams_agent_answer_into_overlay(qtbot, monkeypatch):
    app = _build_app(qtbot, monkeypatch)
    app._agent = _FakeStreamingAgent(["Hello ", "world"])  # skip build_agent() / a real provider

    app._on_capture()

    assert app.overlay.isVisible()
    assert "📸" in app.overlay.question.text()

    qtbot.waitUntil(lambda: app._worker is not None and app._worker.isFinished(), timeout=3000)
    qtbot.waitUntil(lambda: "Hello world" in app.overlay.answer.toPlainText(), timeout=1000)
    assert app.overlay.input.isVisible()  # finish() re-opens the input for a follow-up


def test_capture_while_busy_is_ignored(qtbot, monkeypatch):
    app = _build_app(qtbot, monkeypatch)
    app._agent = _FakeStreamingAgent(["should never stream"])
    app._recording_meeting = True  # simulate an in-flight voice capture

    app._on_capture()

    assert app._pending_png is None  # _busy() short-circuited before the screenshot was taken
    assert app._worker is None
