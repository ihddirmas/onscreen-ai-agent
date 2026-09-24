"""Lightweight desktop context for Parakeet mode (foreground window + screen)."""

from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass
class DesktopContext:
    window_title: str = ""
    note: str = ""

    def as_prompt_prefix(self) -> str:
        parts: list[str] = []
        if self.window_title:
            parts.append(f'Active window: "{self.window_title}"')
        if self.note:
            parts.append(self.note)
        if not parts:
            return ""
        return "[Desktop context — " + "; ".join(parts) + "]\n\n"


def foreground_window_title() -> str:
    if sys.platform == "win32":
        try:
            import ctypes

            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return ""
            length = user32.GetWindowTextLengthW(hwnd) + 1
            buf = ctypes.create_unicode_buffer(length)
            user32.GetWindowTextW(hwnd, buf, length)
            return (buf.value or "").strip()
        except Exception:
            return ""
    if sys.platform == "darwin":
        try:
            from AppKit import NSWorkspace  # type: ignore[import-untyped]

            app = NSWorkspace.sharedWorkspace().frontmostApplication()
            if app is None:
                return ""
            return str(app.localizedName() or "")
        except Exception:
            return ""
    return ""


def capture_desktop_context() -> DesktopContext:
    title = foreground_window_title()
    note = (
        "You share this session with the user's live desktop; the latest screenshot "
        "shows their screen. Keep continuity with earlier turns in this thread."
    )
    return DesktopContext(window_title=title, note=note)
