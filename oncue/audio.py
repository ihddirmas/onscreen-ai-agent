"""Audio capture.

- Recorder: push-to-talk microphone (sounddevice).
- MeetingRecorder: mic + system/loopback audio at once (soundcard), for
  "record what someone is saying and ask my agent about it". Mixed to one
  16 kHz mono stream for whisper.
"""

from __future__ import annotations

import sys
import threading

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000  # what faster-whisper expects


def _com_init() -> None:
    """WASAPI/COM (used by soundcard) requires CoInitialize on every thread
    that touches it, or record() raises 0x800401f0 (CO_E_NOTINITIALIZED).
    Worker threads must call this before using soundcard."""
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.ole32.CoInitializeEx(None, 0)  # 0 = MULTITHREADED
        except Exception:
            pass


def _com_uninit() -> None:
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.ole32.CoUninitialize()
        except Exception:
            pass


class Recorder:
    def __init__(self) -> None:
        self._chunks: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()

    @property
    def recording(self) -> bool:
        return self._stream is not None

    def start(self) -> None:
        with self._lock:
            if self._stream is not None:
                return
            self._chunks = []

            def _callback(indata, frames, time, status):
                self._chunks.append(indata.copy())

            self._stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="float32",
                callback=_callback,
            )
            self._stream.start()

    def stop(self) -> np.ndarray:
        """Stop recording and return mono float32 audio at 16 kHz."""
        with self._lock:
            if self._stream is None:
                return np.zeros(0, dtype=np.float32)
            self._stream.stop()
            self._stream.close()
            self._stream = None
            if not self._chunks:
                return np.zeros(0, dtype=np.float32)
            audio = np.concatenate(self._chunks, axis=0)
            return audio.reshape(-1).astype(np.float32)


def _silence_soundcard_del_warning() -> None:
    """soundcard's _COMLibrary.__del__ raises a harmless AttributeError at
    interpreter shutdown ('object has no attribute com_loaded'). Wrap it so the
    ignored-exception traceback doesn't clutter the console."""
    try:
        from soundcard import mediafoundation as _mf

        _orig = _mf._COMLibrary.__del__

        def _safe(self):
            try:
                _orig(self)
            except Exception:
                pass

        _mf._COMLibrary.__del__ = _safe
    except Exception:
        pass


def warmup_system_audio() -> None:
    """Prime soundcard's WASAPI/COM stack so the first meeting capture isn't a
    cold start (the first-ever recorder init in a process can be slow). Safe to
    call in a background thread at app startup; errors are ignored."""
    _com_init()
    try:
        import soundcard as sc

        _silence_soundcard_del_warning()

        spk = sc.default_speaker()
        loop = sc.get_microphone(spk.name, include_loopback=True)
        with loop.recorder(samplerate=SAMPLE_RATE, channels=1) as rec:
            rec.record(numframes=256)
        with sc.default_microphone().recorder(samplerate=SAMPLE_RATE, channels=1) as rec:
            rec.record(numframes=256)
    except Exception:
        pass
    finally:
        _com_uninit()


def _to_mono(chunks: list[np.ndarray]) -> np.ndarray:
    """Concatenate recorded chunks and downmix any channel count to mono.
    Recording the loopback at its NATIVE channel count (then averaging) is
    more reliable than asking soundcard for channels=1, which can grab a
    single (sometimes silent) channel and miss the actual audio."""
    if not chunks:
        return np.zeros(0, dtype=np.float32)
    data = np.concatenate(chunks, axis=0).astype(np.float32)
    if data.ndim == 2 and data.shape[1] > 1:
        data = data.mean(axis=1)
    return data.reshape(-1)


def _pad(a: np.ndarray, n: int) -> np.ndarray:
    if a.size >= n:
        return a[:n]
    return np.concatenate([a, np.zeros(n - a.size, dtype=np.float32)])


class MeetingRecorder:
    """Records the microphone AND system (loopback) audio simultaneously via
    the `soundcard` library, then mixes them into one 16 kHz mono stream.

    `system_ok` reports whether loopback capture actually started (it may not
    on machines without a WASAPI loopback endpoint) — in that case you still
    get mic-only audio.
    """

    def __init__(self) -> None:
        self._stop = threading.Event()
        self._threads: list[threading.Thread] = []
        self._mic: list[np.ndarray] = []
        self._sys_buffers: list[list[np.ndarray]] = []
        self.recording = False
        self.system_ok = False

    def start(self) -> None:
        import soundcard as sc

        self._stop.clear()
        self._mic = []
        self.system_ok = False
        self._threads = []

        def mic_worker():
            _com_init()
            try:
                with sc.default_microphone().recorder(samplerate=SAMPLE_RATE) as rec:
                    while not self._stop.is_set():
                        self._mic.append(rec.record(numframes=1024))
            except Exception:
                pass
            finally:
                _com_uninit()

        self._threads.append(threading.Thread(target=mic_worker, daemon=True))

        # Capture EVERY loopback endpoint, not just the default speaker — audio
        # (e.g. a browser tab) may be routed to a different device than the OS
        # default, and Bluetooth defaults sometimes don't loopback at all.
        # Whichever device is actually playing gets recorded; the rest are silent.
        try:
            loopbacks = [
                m
                for m in sc.all_microphones(include_loopback=True)
                if getattr(m, "isloopback", False)
            ]
        except Exception:
            loopbacks = []
        self._sys_buffers = [[] for _ in loopbacks]

        def make_sys_worker(device, buf):
            def worker():
                _com_init()
                try:
                    with device.recorder(samplerate=SAMPLE_RATE) as rec:
                        self.system_ok = True
                        while not self._stop.is_set():
                            buf.append(rec.record(numframes=1024))
                except Exception:
                    pass
                finally:
                    _com_uninit()

            return worker

        for device, buf in zip(loopbacks, self._sys_buffers):
            self._threads.append(
                threading.Thread(target=make_sys_worker(device, buf), daemon=True)
            )

        for t in self._threads:
            t.start()
        self.recording = True

    def stop(self) -> np.ndarray:
        self._stop.set()
        for t in self._threads:
            t.join(timeout=2)
        self._threads = []
        self.recording = False
        tracks = [_to_mono(self._mic)]
        tracks += [_to_mono(buf) for buf in self._sys_buffers]
        tracks = [t for t in tracks if t.size]
        if not tracks:
            return np.zeros(0, dtype=np.float32)
        n = max(t.size for t in tracks)
        mix = np.zeros(n, dtype=np.float32)
        for t in tracks:
            mix += _pad(t, n)
        peak = float(np.max(np.abs(mix)))
        if peak > 1.0:
            mix = mix / peak
        return mix.astype(np.float32)
