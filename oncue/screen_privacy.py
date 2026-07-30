"""Hide a window from screen capture / screen sharing.

Windows: SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE) makes the window
render on the physical display but be excluded from ALL screen-capture APIs
(Zoom, Meet, Teams, Discord, OBS, PrintScreen…). It works at the OS compositor
level, so it's app-agnostic. Requires Windows 10 2004 (build 19041)+.

Note: this cannot hide the window from a physical camera pointed at the screen.
"""

from __future__ import annotations

import sys

_WDA_NONE = 0x00000000
_WDA_EXCLUDEFROMCAPTURE = 0x00000011


def set_capture_protection(widget, enabled: bool) -> bool:
    """Exclude (or re-include) a top-level Qt widget from screen capture.
    Returns True on success. No-op (False) on unsupported platforms."""
    if sys.platform == "win32":
        return _win(widget, enabled)
    if sys.platform == "darwin":
        return _mac(widget, enabled)
    return False


def _win(widget, enabled: bool) -> bool:
    import ctypes

    try:
        hwnd = int(widget.winId())
    except (TypeError, ValueError):
        return False
    if not hwnd:
        return False
    affinity = _WDA_EXCLUDEFROMCAPTURE if enabled else _WDA_NONE
    try:
        return bool(ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, affinity))
    except Exception:
        return False


def _mac(widget, enabled: bool) -> bool:
    # macOS equivalent is NSWindow.sharingType = NSWindowSharingNone, which
    # needs pyobjc to reach the NSWindow behind the Qt view. Not wired yet.
    return False
