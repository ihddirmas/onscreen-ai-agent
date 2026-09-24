import numpy as np

from oncue.ring_buffer import RingAudioBuffer, SAMPLE_RATE
from oncue.parakeet import ParakeetSession, default_agent_hotkey


def test_ring_buffer_keeps_tail():
    ring = RingAudioBuffer(max_seconds=1.0)
    ring.append(np.ones(SAMPLE_RATE // 2, dtype=np.float32))
    ring.append(np.zeros(SAMPLE_RATE // 2, dtype=np.float32) + 2.0)
    snap = ring.snapshot()
    assert snap.size == SAMPLE_RATE
    assert float(snap[-1]) == 2.0


def test_ring_buffer_snapshot_window():
    ring = RingAudioBuffer(max_seconds=2.0)
    ring.append(np.ones(SAMPLE_RATE, dtype=np.float32))
    ring.append(np.zeros(SAMPLE_RATE, dtype=np.float32))
    snap = ring.snapshot(seconds=0.5)
    assert snap.size == SAMPLE_RATE // 2
    assert float(np.mean(snap)) == 0.0


def test_parakeet_lock_phrase():
    session = ParakeetSession()
    assert session.wants_lock("lock the mode permanently for this session")
    assert not session.enabled
    msg = session.lock()
    assert session.enabled
    assert "Parakeet mode" in msg


def test_parakeet_enrich_question():
    session = ParakeetSession()
    session.lock()
    session._context.window_title = "Chrome"
    out = session.enrich_question("What is on screen?")
    assert "Chrome" in out
    assert "What is on screen?" in out


def test_default_agent_hotkey_nonempty():
    assert default_agent_hotkey().strip()
