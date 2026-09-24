from __future__ import annotations

import numpy as np

SAMPLE_RATE = 16000


class RingAudioBuffer:
    """Fixed-duration rolling buffer of mono float32 @ 16 kHz (no I/O)."""

    def __init__(self, max_seconds: float = 30.0) -> None:
        self._max_samples = int(max_seconds * SAMPLE_RATE)
        self._chunks: list[np.ndarray] = []
        self._total = 0

    def append(self, chunk: np.ndarray) -> None:
        flat = chunk.reshape(-1).astype(np.float32)
        if flat.size == 0:
            return
        self._chunks.append(flat)
        self._total += flat.size
        while self._total > self._max_samples and self._chunks:
            drop = self._chunks.pop(0)
            self._total -= drop.size

    def snapshot(self, seconds: float | None = None) -> np.ndarray:
        if not self._chunks:
            return np.zeros(0, dtype=np.float32)
        audio = np.concatenate(self._chunks, axis=0)
        if seconds is not None:
            n = int(seconds * SAMPLE_RATE)
            if audio.size > n:
                audio = audio[-n:]
        return audio.astype(np.float32)
