"""Insert text into whatever app/text-box currently has focus (dictation mode).

Strategy: clipboard paste — instant for long text and safe for Hindi/emoji in
every app. The user's previous clipboard text is restored afterwards.

Must be called from the Qt main thread (QClipboard requirement).
"""

from __future__ import annotations

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from pynput.keyboard import Controller, Key

_kbd = Controller()


def paste_text(text: str) -> None:
    if not text:
        return
    clipboard = QApplication.clipboard()
    previous = clipboard.text()
    clipboard.setText(text)

    def _send_paste() -> None:
        modifier = Key.cmd if sys.platform == "darwin" else Key.ctrl
        with _kbd.pressed(modifier):
            _kbd.press("v")
            _kbd.release("v")
        # give the target app time to read the clipboard before restoring
        QTimer.singleShot(500, lambda: clipboard.setText(previous))

    # small settle delay so the clipboard write lands before Ctrl+V
    QTimer.singleShot(120, _send_paste)
