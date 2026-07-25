"""Tiny dictation indicator pill.

Unlike the overlay, this must NEVER steal focus — the whole point of dictation
is that the user's cursor stays in the text box they're dictating into.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

_STYLE = """
QFrame#pill {
    background-color: rgba(18, 18, 24, 235);
    border: 1px solid rgba(120, 200, 120, 120);
    border-radius: 16px;
}
QLabel { color: #f0f0f0; font-size: 13px; }
"""


class DictationIndicator(QWidget):
    def __init__(self, content_protection: bool = True):
        super().__init__(
            None,
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setStyleSheet(_STYLE)
        self._content_protection = content_protection

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        pill = QFrame(objectName="pill")
        root.addWidget(pill)
        lay = QHBoxLayout(pill)
        lay.setContentsMargins(18, 8, 18, 8)
        self.label = QLabel("")
        lay.addWidget(self.label)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide)

    def showEvent(self, event) -> None:
        from parakeet.screen_privacy import set_capture_protection

        set_capture_protection(self, self._content_protection)
        super().showEvent(event)

    def set_content_protection(self, enabled: bool) -> None:
        from parakeet.screen_privacy import set_capture_protection

        self._content_protection = enabled
        set_capture_protection(self, enabled)

    def _place(self) -> None:
        self.adjustSize()
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(
            screen.center().x() - self.width() // 2,
            screen.bottom() - self.height() - 48,
        )

    def show_state(self, text: str, auto_hide_ms: int = 0) -> None:
        self._hide_timer.stop()
        self.label.setText(text)
        self._place()
        self.show()  # WA_ShowWithoutActivating keeps focus in the user's app
        if auto_hide_ms:
            self._hide_timer.start(auto_hide_ms)

    def flash(self, text: str, ms: int = 1300) -> None:
        self.show_state(text, auto_hide_ms=ms)

    def listening(self) -> None:
        self.show_state("🎙  Listening… release to insert")

    def meeting(self) -> None:
        self.show_state("🔴  Recording meeting audio… release to ask")

    def transcribing(self) -> None:
        self.show_state("✍  Transcribing…")

    def done(self) -> None:
        self.show_state("✓  Inserted", auto_hide_ms=1200)

    def failed(self, message: str = "Didn't catch that") -> None:
        self.show_state(f"✗  {message}", auto_hide_ms=1800)
