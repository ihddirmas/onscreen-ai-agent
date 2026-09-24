"""Parakeet mode — session-scoped always-on listening + instant agent hotkey."""

from __future__ import annotations

import re

from oncue.desktop_context import DesktopContext, capture_desktop_context

PARAKEET_CONFIRMATION = (
    "OnCUE is now permanently in Parakeet mode. Always recording. Always synced. Ready."
)

PARAKEET_STATUS_LABEL = "Parakeet · always on"

_LOCK_PATTERNS = (
    re.compile(r"lock\s+(?:the\s+)?mode\s+permanently", re.I),
    re.compile(r"permanently\s+in\s+parakeet\s+mode", re.I),
    re.compile(r"\bparakeet\s+mode\b.*\balways\s+recording\b", re.I),
    re.compile(r"full\s+parakeet\s+mode", re.I),
)

_UNLOCK_PATTERNS = (
    re.compile(r"exit\s+parakeet", re.I),
    re.compile(r"disable\s+parakeet", re.I),
    re.compile(r"turn\s+off\s+parakeet", re.I),
)


class ParakeetSession:
    """Runtime-only session state (not persisted to config.env)."""

    def __init__(self) -> None:
        self.enabled = False
        self._context: DesktopContext | None = None

    def lock(self) -> str:
        self.enabled = True
        self.refresh_context()
        return PARAKEET_CONFIRMATION

    def unlock(self) -> None:
        self.enabled = False
        self._context = None

    def refresh_context(self) -> DesktopContext:
        self._context = capture_desktop_context()
        return self._context

    @property
    def context(self) -> DesktopContext:
        if self._context is None:
            self.refresh_context()
        return self._context or DesktopContext()

    def enrich_question(self, question: str) -> str:
        if not self.enabled:
            return question
        prefix = self.context.as_prompt_prefix()
        if not prefix:
            return question
        return prefix + question

    def wants_lock(self, text: str) -> bool:
        t = text.strip()
        if not t:
            return False
        if any(p.search(t) for p in _UNLOCK_PATTERNS):
            return False
        return any(p.search(t) for p in _LOCK_PATTERNS)

    def wants_unlock(self, text: str) -> bool:
        return any(p.search(text) for p in _UNLOCK_PATTERNS)


def default_agent_hotkey() -> str:
    import sys

    if sys.platform == "win32":
        return "<cmd>+k"
    if sys.platform == "darwin":
        return "<cmd>+k"
    return "<ctrl>+<shift>+v"
