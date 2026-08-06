"""Text-to-speech for spoken answers. Uses edge-tts (free, no API key, works
offline, cross-platform). Plays audio in a background thread so the UI never
blocks."""

from __future__ import annotations

import os
import sys
import tempfile
import threading

from PySide6.QtCore import QThread, Signal

try:
    import edge_tts

    _HAVE_EDGE_TTS = True
except ImportError:
    _HAVE_EDGE_TTS = False

_VOICE = "en-US-JennyNeural"  # natural American English female voice
_SPEAK_RATE = "+0%"           # can adjust: "+10%" faster, "-10%" slower


class TTSWorker(QThread):
    """Speak text in a background thread. Emits done() when finished."""

    done = Signal()
    error = Signal(str)

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self._text = text
        self._cancelled = threading.Event()

    def cancel(self) -> None:
        self._cancelled.set()

    def run(self) -> None:
        if not _HAVE_EDGE_TTS or not self._text.strip():
            self.done.emit()
            return

        try:
            import asyncio
            import pygame

            # Generate speech to a temp file using edge-tts
            communicate = edge_tts.Communicate(self._text, _VOICE, rate=_SPEAK_RATE)
            tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            tmp_path = tmp.name
            tmp.close()

            # Run the async communicate in a fresh event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(communicate.save(tmp_path))
            loop.close()

            if self._cancelled.is_set():
                self._cleanup(tmp_path)
                self.done.emit()
                return

            # Play the audio file
            if sys.platform == "win32":
                os.environ.setdefault("SDL_AUDIODRIVER", "directsound")
            pygame.mixer.init()
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()

            # Wait for playback to finish (check every 100ms for cancel)
            while pygame.mixer.music.get_busy():
                if self._cancelled.is_set():
                    pygame.mixer.music.stop()
                    break
                QThread.msleep(100)

            pygame.mixer.quit()
            self._cleanup(tmp_path)
            self.done.emit()

        except Exception as e:
            self.error.emit(f"TTS failed: {e}")
            self.done.emit()

    @staticmethod
    def _cleanup(path: str) -> None:
        try:
            if os.path.exists(path):
                os.unlink(path)
        except OSError:
            pass


class TTSManager:
    """Manages the TTS worker: ensures only one speaks at a time, and new
    speech cancels the previous."""

    def __init__(self):
        self._worker: TTSWorker | None = None

    def speak(self, text: str, error_callback=None, done_callback=None) -> None:
        """Cancel any in-progress TTS and start speaking `text`.
        `error_callback` / `done_callback` are connected to the worker's signals."""
        self.stop()
        if not text.strip():
            if done_callback:
                done_callback()
            return
        self._worker = TTSWorker(text)
        if error_callback:
            self._worker.error.connect(error_callback)
        if done_callback:
            self._worker.done.connect(done_callback)
        self._worker.start()

    def stop(self) -> None:
        """Cancel any in-progress TTS immediately."""
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(2000)
        self._worker = None
