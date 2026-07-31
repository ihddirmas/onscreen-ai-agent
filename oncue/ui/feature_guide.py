"""In-app feature guide — hotkey cheat sheet and setup flows.

Inspired by Parakeet (web session → desktop deep link, screen-share privacy)
and Clicky (push-to-talk hotkeys, per-feature tutorials, tray-first UX).
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from oncue.config import get_config
from oncue.ui.theme import COLOR, DIALOG_STYLE

_SECTIONS: list[tuple[str, str]] = [
    (
        "1. Get connected (Parakeet-style)",
        "Sign in at your OnCUE dashboard → click <b>Open OnCUE app</b>. "
        "That sends an <code>oncue://connect</code> link with your license key, "
        "website URL, RAG URL, and LiteLLM backend — no manual copy-paste.\n\n"
        "Or open <b>Settings → OnCUE hosted</b> and paste your key + URLs.",
    ),
    (
        "2. Ask about your screen (Clicky-style)",
        "<b>Ctrl+Shift+Space</b> — capture screenshot → type a question → Enter. "
        "The overlay streams the answer. Default prompt analyzes what's on screen "
        "(code errors, quizzes, docs).\n\n"
        "Tip: enable <b>Hide overlay from screen sharing</b> before Zoom/Meet "
        "(Parakeet-style privacy). You still see it; viewers don't.",
    ),
    (
        "3. Chat without a screenshot",
        "<b>Ctrl+Shift+H</b> — open the overlay for text-only chat. "
        "Press again to hide. Good for follow-ups after a screen capture.",
    ),
    (
        "4. Voice + screen (hold to talk)",
        "<b>Ctrl+Shift+V</b> (hold) — records mic (+ optional screen context) "
        "while held; release to send. Like Clicky's push-to-talk.",
    ),
    (
        "5. Dictation at cursor",
        "<b>Ctrl+Shift+D</b> (hold) — transcribes speech into whatever field "
        "is focused (browser, WhatsApp, Notepad). Set <b>Speech → Language</b> "
        "to Hinglish for Roman Hindi.",
    ),
    (
        "6. Meeting audio",
        "<b>Ctrl+Shift+M</b> (hold) — captures system audio + mic during a call, "
        "then lets you ask the agent about what was said.",
    ),
    (
        "7. Bring your own key (BYO)",
        "Settings → Provider → groq / claude / gpt / gemini. "
        "Paste API keys under <b>API keys</b>. Groq is free for dev. "
        "No hosted trial meter in BYO mode.",
    ),
    (
        "8. Speech & privacy",
        "<b>Speech</b> — pick Hinglish/Hindi/English, Groq cloud vs local Whisper.\n"
        "<b>Behavior</b> — customize every hotkey, allowed folders for file tools, "
        "browser for web search, and whether the agent may open apps/files.",
    ),
    (
        "9. Tray menu (always available)",
        "Right-click the tray icon: Ask about screen, Show overlay, Settings, "
        "Speak answers aloud, Hide from screen sharing, Allow system actions, "
        "Pause agent, Quit.",
    ),
]


class FeatureGuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OnCUE — Feature guide")
        self.setMinimumSize(520, 480)
        self.setStyleSheet(DIALOG_STYLE)

        outer = QVBoxLayout(self)
        title = QLabel("How OnCUE works")
        title.setStyleSheet(
            f"font-size: 17px; font-weight: 600; color: {COLOR['text']};"
        )
        outer.addWidget(title)

        cfg = get_config()
        sub = QLabel(
            f"Current provider: <b>{cfg.provider}</b>"
            + (f" · web: {cfg.web_url}" if cfg.web_url else "")
        )
        sub.setWordWrap(True)
        sub.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: 11px;")
        outer.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        inner = QWidget()
        lay = QVBoxLayout(inner)
        lay.setSpacing(16)

        for heading, body in _SECTIONS:
            h = QLabel(heading)
            h.setStyleSheet(
                f"font-weight: 600; color: {COLOR['accent_border']}; font-size: 13px;"
            )
            lay.addWidget(h)
            b = QLabel(body)
            b.setWordWrap(True)
            b.setTextFormat(Qt.TextFormat.RichText)
            b.setOpenExternalLinks(True)
            b.setStyleSheet(
                f"color: {COLOR['text_muted_strong']}; line-height: 1.45; font-size: 12px;"
            )
            lay.addWidget(b)

        lay.addStretch()
        scroll.setWidget(inner)
        outer.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        buttons.button(QDialogButtonBox.StandardButton.Close).clicked.connect(self.accept)
        outer.addWidget(buttons)
