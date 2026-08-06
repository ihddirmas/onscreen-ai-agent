"""Speech-to-text: Groq-hosted Whisper (fast, accurate) with local fallback.

Backends (config STT_BACKEND):
  auto  — Groq cloud when GROQ_API_KEY is set, else local. Default.
  groq  — Groq's `whisper-large-v3-turbo`: near-instant and far better at
          Hindi/Hinglish than any model that fits on a laptop CPU. Uses the
          same free API key as the chat model.
  local — faster-whisper on-device (private/offline; slower, weaker Hinglish).

Language modes (config STT_LANGUAGE):
  hinglish — Roman Hinglish output ("kal ka weather check karo"). Forces
             Latin script + a code-switched Roman prompt so Hindi words are
             transliterated, not translated or dropped. Default.
  hindi    — Devanagari output.   english — plain English.   auto — detect.
"""

from __future__ import annotations

import io
import os
import wave

import numpy as np

SAMPLE_RATE = 16000

_HINGLISH_PROMPT = (
    "Haan bhai, kal ka weather check karo aur WhatsApp pe message bhej dena. "
    "Screen pe kya likha hai batao, phir YouTube pe lofi songs chala do."
)

_MODES: dict[str, dict] = {
    "hinglish": {"language": "en", "initial_prompt": _HINGLISH_PROMPT},
    "hindi": {"language": "hi"},
    "english": {"language": "en"},
    "auto": {"language": None},
}

_local_model = None
_local_model_name = None


def transcribe(
    audio: np.ndarray,
    model_name: str = "small",
    language_mode: str = "hinglish",
    backend: str = "auto",
) -> str:
    """Transcribe 16 kHz mono float32 audio to text."""
    if audio.size < 4800:  # < 0.3 s — nothing useful was said
        return ""
    # silence gate: whisper hallucinates on silence/noise (it can even echo our
    # Hinglish prompt back) — never send audio with no speech energy in it
    if float(np.sqrt(np.mean(audio**2))) < 0.005:
        return ""
    use_groq = backend == "groq" or (backend == "auto" and os.environ.get("GROQ_API_KEY"))
    if use_groq:
        try:
            return _guard(_transcribe_groq(audio, language_mode))
        except Exception:
            if backend == "groq":
                raise
            # auto mode: fall back to local (offline, key revoked, etc.)
    return _guard(_transcribe_local(audio, model_name, language_mode))


def _guard(text: str) -> str:
    """Drop transcripts that are just the bias prompt hallucinated back
    (whisper does this on silence/noise). Word-overlap, not exact match —
    hallucinations paraphrase slightly ("song" vs "songs")."""

    def words(s: str) -> list[str]:
        return "".join(c if c.isalnum() or c == " " else " " for c in s.lower()).split()

    w = words(text)
    if len(w) >= 4:
        prompt_words = set(words(_HINGLISH_PROMPT))
        overlap = sum(1 for x in w if x in prompt_words) / len(w)
        if overlap >= 0.8:
            return ""
    return text


def _wav_bytes(audio: np.ndarray) -> bytes:
    pcm = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


def _transcribe_groq(audio: np.ndarray, language_mode: str) -> str:
    import groq

    params = _MODES.get(language_mode, _MODES["auto"])
    kwargs: dict = {}
    if params.get("language"):
        kwargs["language"] = params["language"]
    if params.get("initial_prompt"):
        kwargs["prompt"] = params["initial_prompt"]
    from oncue.config import get_config

    client = groq.Groq()  # reads GROQ_API_KEY from env
    result = client.audio.transcriptions.create(
        file=("speech.wav", _wav_bytes(audio)),
        model=get_config().groq_stt_model,
        temperature=0.0,
        **kwargs,
    )
    return (result.text or "").strip()


def _transcribe_local(audio: np.ndarray, model_name: str, language_mode: str) -> str:
    global _local_model, _local_model_name
    if _local_model is None or _local_model_name != model_name:
        from faster_whisper import WhisperModel

        _local_model = WhisperModel(model_name, device="cpu", compute_type="int8")
        _local_model_name = model_name
    params = _MODES.get(language_mode, _MODES["auto"])
    segments, _info = _local_model.transcribe(
        audio,
        beam_size=1,
        vad_filter=True,
        language=params.get("language"),
        initial_prompt=params.get("initial_prompt"),
    )
    return " ".join(seg.text.strip() for seg in segments).strip()
