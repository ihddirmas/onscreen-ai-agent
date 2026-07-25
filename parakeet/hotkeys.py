"""Global hotkeys via pynput, with press *and* release detection.

pynput's GlobalHotKeys only reports activation, but push-to-talk needs the
release of the chord too, so we track pressed keys ourselves.

Callbacks fire on the pynput listener thread — bridge to Qt with signals.
"""

from __future__ import annotations

import sys
from typing import Callable, Optional

from pynput import keyboard

# Windows virtual-key codes for chord modifiers — used to double-check the
# PHYSICAL key state before firing. pynput's press/release tracking can go
# stale (a missed release leaves e.g. Ctrl+Shift "held" forever, after which
# plain Space would wrongly complete a Ctrl+Shift+Space chord).
_VK = {
    keyboard.Key.ctrl: 0x11,
    keyboard.Key.shift: 0x10,
    keyboard.Key.alt: 0x12,
    keyboard.Key.cmd: 0x5B,
}


def _stale_keys(keys) -> set:
    """Return chord keys whose modifiers are NOT physically down right now."""
    if sys.platform != "win32":
        return set()
    import ctypes

    stale = set()
    for k in keys:
        vk = _VK.get(k)
        if vk is not None and not (ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000):
            stale.add(k)
    return stale


class _Chord:
    def __init__(
        self,
        combo: str,
        on_press: Callable[[], None],
        on_release: Optional[Callable[[], None]] = None,
    ):
        self.keys = set(keyboard.HotKey.parse(combo))
        self.on_press = on_press
        self.on_release = on_release
        self._down: set = set()
        self._active = False

    def press(self, key) -> None:
        if key in self.keys:
            self._down.add(key)
            if not self._active and self._down == self.keys:
                stale = _stale_keys(self.keys)
                if stale:
                    # missed release(s) — resync instead of firing spuriously
                    self._down -= stale
                    return
                self._active = True
                self.on_press()

    def release(self, key) -> None:
        if key in self.keys:
            self._down.discard(key)
            if self._active:
                self._active = False
                if self.on_release:
                    self.on_release()


class HotkeyManager:
    """Owns the pynput listener; register chords before start()."""

    def __init__(self) -> None:
        self._chords: list[_Chord] = []
        self._listener: keyboard.Listener | None = None

    def register(
        self,
        combo: str,
        on_press: Callable[[], None],
        on_release: Optional[Callable[[], None]] = None,
    ) -> None:
        self._chords.append(_Chord(combo, on_press, on_release))

    def start(self) -> None:
        def _on_press(key):
            k = self._listener.canonical(key)
            for chord in self._chords:
                chord.press(k)

        def _on_release(key):
            k = self._listener.canonical(key)
            for chord in self._chords:
                chord.release(k)

        self._listener = keyboard.Listener(on_press=_on_press, on_release=_on_release)
        self._listener.daemon = True
        self._listener.start()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()
            self._listener = None
