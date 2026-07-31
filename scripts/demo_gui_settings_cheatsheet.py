#!/usr/bin/env python3
"""Settings cheat sheet + chat hotkey walkthrough for screen recording."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from oncue.ui.theme import COLOR, FONT, HOTKEY_CHIP_STYLE, MUTED_CARD_STYLE


def _center(widget, w: int, h: int) -> None:
    widget.resize(w, h)
    geo = widget.frameGeometry()
    screen = QApplication.primaryScreen()
    if screen:
        center = screen.availableGeometry().center()
        geo.moveCenter(center)
        widget.move(geo.topLeft())
    widget.raise_()
    widget.activateWindow()


def _hotkey_callout(hotkey: str, title: str, detail: str) -> QWidget:
    w = QWidget()
    w.setWindowTitle("OnCUE")
    w.setStyleSheet(
        f"background:{COLOR['bg']}; color:{COLOR['text']}; "
        f"border:2px solid {COLOR['accent_border']}; border-radius:12px;"
    )
    lay = QVBoxLayout(w)
    lay.setContentsMargins(16, 14, 16, 14)
    chip = QLabel(hotkey)
    chip.setStyleSheet(HOTKEY_CHIP_STYLE)
    chip.setFixedHeight(30)
    lay.addWidget(chip, alignment=Qt.AlignmentFlag.AlignLeft)
    t = QLabel(f"<b>{title}</b>")
    t.setTextFormat(Qt.TextFormat.RichText)
    t.setStyleSheet(f"font-size:14px; color:{COLOR['text']};")
    lay.addWidget(t)
    d = QLabel(detail)
    d.setWordWrap(True)
    d.setStyleSheet(f"color:{COLOR['text_muted']}; font-size:12px;")
    lay.addWidget(d)
    _center(w, 420, 150)
    return w


def _mock_ide() -> QWidget:
    """Fake editor behind the overlay — makes screen Q&A feel real."""
    w = QWidget()
    w.setWindowTitle("utils.ts — VS Code")
    w.setStyleSheet("background:#1e1e1e; color:#d4d4d4;")
    lay = QVBoxLayout(w)
    editor = QPlainTextEdit()
    editor.setReadOnly(True)
    editor.setFont(QFont("JetBrains Mono", 11))
    editor.setPlainText(
        "export function processCount(value: string) {\n"
        "  return value + 1;  // line 42\n"
        "}\n\n"
        "// TypeError: Cannot convert 'hello' to number\n"
    )
    lay.addWidget(editor)
    screen = QApplication.primaryScreen()
    if screen:
        g = screen.availableGeometry()
        w.setGeometry(g.left() + 40, g.top() + 30, 720, 420)
    return w


def _load_env_test() -> dict[str, str]:
    path = Path(__file__).resolve().parents[1] / ".env.test"
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def _apply_test_hosted(env: dict[str, str]) -> None:
    if not env.get("ONCUE_TOKEN"):
        return
    from urllib.parse import urlencode

    from oncue.config import Config, set_config
    from oncue.protocol import apply_url

    web = env.get("ONCUE_WEB_URL", "http://localhost:3001")
    rag = env.get("ONCUE_RAG_URL", f"{web}/mock/rag")
    backend = env.get("ONCUE_BACKEND_URL", "http://localhost:4000/v1")
    token = env["ONCUE_TOKEN"]
    apply_url(
        f"oncue://connect?{urlencode({'token': token, 'web': web, 'rag': rag, 'backend': backend})}"
    )
    set_config(
        Config(
            provider="hosted",
            oncue_token=token,
            web_url=web,
            rag_url=rag,
            backend_url=backend,
            hosted_model=env.get("HOSTED_MODEL", "oncue-default"),
        )
    )


def _stream_answer(overlay, text: str, on_done) -> None:
    idx = {"i": 0}

    def tick() -> None:
        i = idx["i"]
        if i < len(text):
            overlay.append_token(text[i])
            idx["i"] = i + 1
            QTimer.singleShot(18, tick)
        else:
            overlay.finish()
            QTimer.singleShot(on_done[0], on_done[1])

    tick()


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("OnCUE Cheatsheet Demo")

    env = _load_env_test()
    _apply_test_hosted(env)

    from oncue.ui.overlay import Overlay
    from oncue.ui.settings import SettingsDialog

    state: dict = {
        "settings": None,
        "overlay": None,
        "ide": None,
        "callout": None,
    }

    def close_callout() -> None:
        if state["callout"]:
            state["callout"].close()
            state["callout"] = None

    def show_callout(hotkey: str, title: str, detail: str, ms: int, nxt) -> None:
        close_callout()
        c = _hotkey_callout(hotkey, title, detail)
        c.show()
        state["callout"] = c
        QTimer.singleShot(ms, nxt)

    # --- 1. Settings: quick start cheat sheet --------------------------------
    def start_settings() -> None:
        settings = SettingsDialog()
        state["settings"] = settings
        _center(settings, 580, 640)
        settings.scroll_to_section("quick_start")
        settings.show()
        show_callout(
            "Settings",
            "Quick start — hotkey cheat sheet",
            "All five global hotkeys live here. Customize them under Behavior.",
            3200,
            settings_behavior,
        )

    def settings_behavior() -> None:
        settings = state["settings"]
        if settings:
            settings.scroll_to_section("behavior")
            settings.raise_()
        show_callout(
            "Settings → Behavior",
            "Customize every hotkey",
            "Change bindings, allowed folders, screen-share privacy, and system actions.",
            2800,
            close_settings_for_chat,
        )

    def close_settings_for_chat() -> None:
        close_callout()
        if state["settings"]:
            state["settings"].close()
            state["settings"] = None
        ide = _mock_ide()
        state["ide"] = ide
        ide.show()
        QTimer.singleShot(600, demo_screen_qa)

    # --- 2. Ctrl+Shift+Space — screen Q&A ------------------------------------
    def demo_screen_qa() -> None:
        overlay = Overlay()
        state["overlay"] = overlay
        overlay.set_trial_status(1)
        show_callout(
            "Ctrl+Shift+Space",
            "Screen Q&A",
            "Captures your screen, then type a question. Works over any window.",
            2400,
            run_screen_qa,
        )

    def run_screen_qa() -> None:
        close_callout()
        overlay = state["overlay"]
        overlay.show_for_input(chat=False)
        overlay.input.setText("what's this TypeError on line 42?")
        QTimer.singleShot(900, lambda: _submit_screen_qa(overlay))

    def _submit_screen_qa(overlay) -> None:
        overlay.show_question("what's this TypeError on line 42?")
        overlay.begin_answer("Analyzing screen…")
        answer = (
            "You're adding **1** to a **string** in `processCount`.\n\n"
            "- Use `Number(value) + 1` or `parseInt(value, 10) + 1`\n"
            "- Or validate input before the function runs\n\n"
            "Stack trace points to line 42 in `utils.ts`."
        )
        _stream_answer(overlay, answer, (2200, demo_chat))

    # --- 3. Ctrl+Shift+H — chat without screenshot ---------------------------
    def demo_chat() -> None:
        overlay = state["overlay"]
        overlay.hide()
        show_callout(
            "Ctrl+Shift+H",
            "Chat (no screenshot)",
            "Text-only follow-ups — press again to hide the overlay.",
            2200,
            run_chat,
        )

    def run_chat() -> None:
        close_callout()
        overlay = state["overlay"]
        overlay.show_for_input(chat=True)
        overlay.input.setText("show me the fixed function")
        QTimer.singleShot(900, lambda: _submit_chat(overlay))

    def _submit_chat(overlay) -> None:
        overlay.show_question("show me the fixed function")
        overlay.begin_answer("Thinking…")
        answer = (
            "```typescript\n"
            "export function processCount(value: string) {\n"
            "  const n = Number(value);\n"
            "  if (Number.isNaN(n)) throw new Error('Expected a number');\n"
            "  return n + 1;\n"
            "}\n"
            "```"
        )
        _stream_answer(overlay, answer, (2200, demo_voice))

    # --- 4. Ctrl+Shift+V — voice + screen (hold) -----------------------------
    def demo_voice() -> None:
        overlay = state["overlay"]
        overlay.hide()
        show_callout(
            "Ctrl+Shift+V",
            "Voice + screen (hold)",
            "Hold while you speak; release to send with screen context.",
            2200,
            run_voice,
        )

    def run_voice() -> None:
        close_callout()
        overlay = state["overlay"]
        overlay.show_for_input()
        overlay.set_status("🎤 Listening… (release to send)")
        overlay.input.hide()
        overlay.show_question("explain this error in simple terms")
        QTimer.singleShot(2000, demo_dictate)

    # --- 5. Ctrl+Shift+D — dictate at cursor ---------------------------------
    def demo_dictate() -> None:
        overlay = state["overlay"]
        if overlay:
            overlay.hide()
        show_callout(
            "Ctrl+Shift+D",
            "Dictate at cursor (hold)",
            "Transcribes into the focused field — WhatsApp, browser, Notepad. "
            "Set Speech → Hinglish for Roman Hindi.",
            2400,
            demo_meeting,
        )

    # --- 6. Ctrl+Shift+M — meeting audio -------------------------------------
    def demo_meeting() -> None:
        show_callout(
            "Ctrl+Shift+M",
            "Meeting audio (hold)",
            "Captures call audio + mic while held; ask about what was said after.",
            2200,
            run_meeting,
        )

    def run_meeting() -> None:
        close_callout()
        overlay = state["overlay"] or Overlay()
        state["overlay"] = overlay
        overlay.set_trial_status(1)
        overlay.show_for_input()
        overlay.set_status("📞 Recording meeting… (release when done)")
        overlay.input.hide()
        QTimer.singleShot(1800, finish_meeting)

    def finish_meeting() -> None:
        overlay = state["overlay"]
        overlay.show_question("summarize the action items from this call")
        overlay.begin_answer("Summarizing…")
        answer = (
            "**Action items from the call:**\n\n"
            "- Fix `processCount` type coercion before Friday\n"
            "- Add unit tests for string vs number inputs\n"
            "- Ship hotfix to staging after review"
        )
        _stream_answer(overlay, answer, (2000, cleanup))

    def cleanup() -> None:
        close_callout()
        if state["overlay"]:
            state["overlay"].close()
        if state["ide"]:
            state["ide"].close()
        app.quit()

    QTimer.singleShot(500, start_settings)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
