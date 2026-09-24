"""OnCUE app: tray icon + global hotkeys + overlay + agent, one process.

Flow:
  capture hotkey -> screenshot frozen -> overlay input -> Enter -> agent streams
  voice hotkey (hold) -> screenshot + record -> release -> whisper -> agent streams
"""

from __future__ import annotations

import re
import sys
import threading
import uuid

from langgraph.checkpoint.memory import MemorySaver
from PySide6.QtCore import QObject, QThread, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from oncue.agent.router import build_message
from oncue.agent.worker import AgentWorker
from oncue.capture import screenshot_png
from oncue.config import CONFIG_FILE, get_config
from oncue.hotkeys import HotkeyManager
from oncue.ui.onboarding import OnboardingDialog
from oncue.ui.overlay import Overlay
from oncue.ui.pointer import PointingWidget, parse_point_tags
from oncue.ui.settings import SettingsDialog
from oncue.tts import TTSManager
from oncue.interview_mode import INTERVIEW_CONFIRMATION, InterviewSession
from oncue.meeting_memory import record_turn
from oncue.parakeet import PARAKEET_CONFIRMATION, ParakeetSession
from oncue.usage import check_session, report_inference, report_session_start

# Auto-analysis prompt for the screenshot hotkey — the user doesn't say what's
# on screen; the agent figures out what to do.
SCREEN_PROMPT = (
    "Look at my screen and help me directly — do not ask what I want. "
    "If it shows a coding or programming problem, give a correct, working "
    "solution with a short explanation. If it shows a question, quiz, or exam "
    "item, answer it and briefly say why. If it shows a concept, article, "
    "diagram, or topic, explain it clearly and concisely. Otherwise, describe "
    "what's on screen and what I most likely need. Keep it concise."
)


class HotkeyBridge(QObject):
    """pynput callbacks run on the listener thread; these signals hop to Qt."""

    capture_pressed = Signal()
    dictate_pressed = Signal()
    dictate_released = Signal()
    chat_pressed = Signal()
    voice_pressed = Signal()     # screenshot + mic + system audio
    voice_released = Signal()
    meeting_pressed = Signal()   # "listen" (mic + system audio only)
    meeting_released = Signal()
    agent_pressed = Signal()     # Parakeet instant agent (tap)


class TranscribeWorker(QThread):
    text = Signal(str)
    error = Signal(str)

    def __init__(self, audio, model_name: str, language_mode: str, backend: str, parent=None):
        super().__init__(parent)
        self._audio = audio
        self._model_name = model_name
        self._language_mode = language_mode
        self._backend = backend

    def run(self) -> None:
        try:
            from oncue.stt import transcribe

            self.text.emit(
                transcribe(
                    self._audio, self._model_name, self._language_mode, self._backend
                )
            )
        except Exception as e:
            self.error.emit(f"{type(e).__name__}: {e}")


def _tray_icon() -> QIcon:
    pm = QPixmap(64, 64)
    pm.fill(QColor(0, 0, 0, 0))
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(24, 130, 90))
    p.setPen(QColor(240, 240, 240))
    p.drawEllipse(4, 4, 56, 56)
    f = p.font()
    f.setPixelSize(34)
    p.setFont(f)
    p.drawText(pm.rect(), 0x84, "O")  # AlignCenter
    p.end()
    return QIcon(pm)


class OnCUEApp(QObject):
    def __init__(self, app: QApplication):
        super().__init__()
        self._qapp = app
        self._agent = None
        self._worker: AgentWorker | None = None
        self._stt_worker: TranscribeWorker | None = None
        self._pending_png: bytes | None = None
        self._pending_png_gen = 0
        self._capture_gen = 0
        self._recording_meeting = False
        self._thread_id = str(uuid.uuid4())
        self._session_reported = False
        self._tts_enabled = True
        self._tts = TTSManager()
        self._pointer = PointingWidget()
        # One checkpointer for the whole process lifetime: the agent graph
        # gets rebuilt on settings changes, system-tools toggles, and
        # protocol-URL handling, but conversation memory should survive
        # those rebuilds — a fresh MemorySaver has no history even if the
        # thread_id is unchanged.
        self._checkpointer = MemorySaver()
        self._parakeet = ParakeetSession()
        self._interview = InterviewSession()
        self._agent_stt = False  # STT from instant agent hotkey (not hold-to-talk)

        cfg = get_config()
        cfg.apply_env()

        self.overlay = Overlay(
            click_through=cfg.click_through,
            geometry=cfg.overlay_geometry,
            system_enabled=cfg.system_tools_enabled,
            content_protection=cfg.content_protection,
        )
        self.overlay.submitted.connect(self._on_question)
        self.overlay.confirmed.connect(self._on_confirmed)
        self.overlay.system_toggled.connect(self._set_system_enabled)
        self.overlay.cancelled.connect(self._on_cancel)
        self._pause_timer: object | None = None

        from oncue.ui.indicator import DictationIndicator

        self.indicator = DictationIndicator(content_protection=cfg.content_protection)
        self._dictating = False

        self._build_tray()
        self._start_hotkeys(cfg)

        from oncue.audio import AlwaysOnRecorder, MeetingRecorder, Recorder, warmup_system_audio

        self._recorder = Recorder()
        self._meeting_recorder = MeetingRecorder()
        self._always_on = AlwaysOnRecorder(max_seconds=30.0)
        self._parakeet_sync = QTimer(self)
        self._parakeet_sync.setInterval(45_000)
        self._parakeet_sync.timeout.connect(self._parakeet.refresh_context)
        # prime the audio stack so the first meeting capture isn't a cold start
        threading.Thread(target=warmup_system_audio, daemon=True).start()

        self._maybe_check_trial()
        self._maybe_show_onboarding()

    def _maybe_check_trial(self) -> None:
        """Hosted mode only: check session cap on startup."""
        cfg = get_config()
        if cfg.provider != "hosted" or not cfg.web_url:
            return
        result = check_session()
        if not result.get("can_start", True):
            self.overlay.show_error(
                "Your trial session has ended. Sign in at "
                f"{cfg.web_url.rstrip('/')}/login to continue using OnCUE."
            )
        else:
            remaining = result.get("trial_remaining", 0)
            if remaining > 0:
                self.overlay.set_trial_status(remaining)

    def _maybe_show_onboarding(self) -> None:
        """First launch only (detected by the config file not existing yet) —
        offer the free hosted trial before silently falling back to an
        unconfigured BYOK provider."""
        if CONFIG_FILE.exists():
            return
        dialog = OnboardingDialog()
        dialog.open_settings.connect(self._open_settings)
        dialog.exec()

    # --- tray ---------------------------------------------------------------

    def _build_tray(self) -> None:
        self.tray = QSystemTrayIcon(_tray_icon())
        self.tray.setToolTip("OnCUE — on-screen AI agent")
        menu = QMenu()
        ask = QAction("Ask about my screen", menu)
        ask.triggered.connect(self._on_capture)
        settings = QAction("Settings…", menu)
        settings.triggered.connect(self._open_settings)
        reset_pos = QAction("Reset overlay position", menu)
        reset_pos.triggered.connect(lambda: self.overlay.reset_position())

        # Speak answers toggle
        self._tray_tts_action = QAction("Speak answers aloud", menu)
        self._tray_tts_action.setCheckable(True)
        self._tray_tts_action.setChecked(True)
        self._tray_tts_action.toggled.connect(self._set_tts_enabled)

        # Hide-from-screen-sharing toggle
        self._tray_hide_action = QAction("Hide from screen sharing", menu)
        self._tray_hide_action.setCheckable(True)
        self._tray_hide_action.setChecked(get_config().content_protection)
        self._tray_hide_action.toggled.connect(self._set_content_protection)

        self._tray_parakeet_action = QAction("Parakeet mode (session)", menu)
        self._tray_parakeet_action.setCheckable(True)
        self._tray_parakeet_action.toggled.connect(self._set_parakeet_mode)

        self._tray_interview_action = QAction("Interview & Meeting mode (session)", menu)
        self._tray_interview_action.setCheckable(True)
        self._tray_interview_action.toggled.connect(self._set_interview_mode)

        # System-actions toggle + timed pause
        self._tray_system_action = QAction("Allow system actions", menu)
        self._tray_system_action.setCheckable(True)
        self._tray_system_action.setChecked(get_config().system_tools_enabled)
        self._tray_system_action.toggled.connect(self._set_system_enabled)
        pause_menu = QMenu("Pause system actions", menu)
        for minutes in (15, 30, 60):
            act = QAction(f"for {minutes} minutes", pause_menu)
            act.triggered.connect(lambda _=False, m=minutes: self._pause_system(m))
            pause_menu.addAction(act)

        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(self._qapp.quit)
        menu.addAction(ask)
        menu.addAction(self._tray_parakeet_action)
        menu.addAction(self._tray_interview_action)
        menu.addAction(settings)
        menu.addAction(reset_pos)
        menu.addSeparator()
        menu.addAction(self._tray_tts_action)
        menu.addAction(self._tray_hide_action)
        menu.addAction(self._tray_system_action)
        menu.addMenu(pause_menu)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.show()

    # --- hotkeys ------------------------------------------------------------

    def _start_hotkeys(self, cfg) -> None:
        self._bridge = HotkeyBridge()
        self._bridge.capture_pressed.connect(self._on_capture)
        self._bridge.dictate_pressed.connect(self._on_dictate_press)
        self._bridge.dictate_released.connect(self._on_dictate_release)
        self._bridge.chat_pressed.connect(self._on_chat)
        self._bridge.voice_pressed.connect(self._on_voice_press)
        self._bridge.voice_released.connect(self._on_voice_release)
        self._bridge.meeting_pressed.connect(self._on_listen_press)
        self._bridge.meeting_released.connect(self._on_listen_release)
        self._bridge.agent_pressed.connect(self._on_agent_hotkey)

        self._hotkeys = HotkeyManager()
        self._hotkeys.register(cfg.capture_hotkey, self._bridge.capture_pressed.emit)
        self._hotkeys.register(
            cfg.voice_hotkey,
            self._bridge.voice_pressed.emit,
            self._bridge.voice_released.emit,
        )
        self._hotkeys.register(
            cfg.meeting_hotkey,
            self._bridge.meeting_pressed.emit,
            self._bridge.meeting_released.emit,
        )
        self._hotkeys.register(
            cfg.dictate_hotkey,
            self._bridge.dictate_pressed.emit,
            self._bridge.dictate_released.emit,
        )
        self._hotkeys.register(cfg.chat_hotkey, self._bridge.chat_pressed.emit)
        if cfg.agent_hotkey.strip():
            self._hotkeys.register(cfg.agent_hotkey, self._bridge.agent_pressed.emit)
        self._hotkeys.start()

    def _restart_hotkeys(self) -> None:
        self._hotkeys.stop()
        self._start_hotkeys(get_config())

    # --- Parakeet mode (session) --------------------------------------------

    def _set_parakeet_mode(self, enabled: bool) -> None:
        if enabled:
            self._enable_parakeet()
        else:
            self._disable_parakeet()

    def _enable_parakeet(self) -> None:
        self._parakeet.lock()
        self._always_on.start()
        self._parakeet_sync.start()
        self.overlay.set_parakeet_active(True)
        if hasattr(self, "_tray_parakeet_action"):
            self._tray_parakeet_action.setChecked(True)
        self.indicator.flash("🎙 Parakeet · always listening", 2200)

    def _disable_parakeet(self) -> None:
        self._parakeet.unlock()
        self._always_on.stop()
        self._parakeet_sync.stop()
        self.overlay.set_parakeet_active(False)
        if hasattr(self, "_tray_parakeet_action"):
            self._tray_parakeet_action.setChecked(False)
        self.indicator.flash("Parakeet mode off", 1600)

    def _set_interview_mode(self, enabled: bool) -> None:
        if enabled:
            self._enable_interview_mode()
        else:
            self._disable_interview_mode()

    def _enable_interview_mode(self) -> None:
        self._interview.lock()
        self._enable_parakeet()
        self.overlay.set_interview_active(True)
        if hasattr(self, "_tray_interview_action"):
            self._tray_interview_action.setChecked(True)
        self.indicator.flash("🎤 Interview & Meeting mode", 2400)

    def _disable_interview_mode(self) -> None:
        self._interview.unlock()
        self.overlay.set_interview_active(False)
        if hasattr(self, "_tray_interview_action"):
            self._tray_interview_action.setChecked(False)
        self.indicator.flash("Interview mode off", 1600)

    def _stream_static_answer(self, answer: str, question: str = "") -> None:
        self.overlay.begin_answer("")
        if question:
            self.overlay.show_question(question)
        self.overlay.append_token(answer)
        self.overlay.finish()

    def _consume_interview_commands(self, text: str) -> str | None:
        if self._interview.wants_unlock(text):
            self._disable_interview_mode()
            self._stream_static_answer("Interview & Meeting mode off for this session.")
            return None
        if self._interview.wants_lock(text):
            self._enable_interview_mode()
            remainder = re.sub(
                r"interview\s*(?:&|and)\s*meeting\s*mode[^.]*\.?",
                "",
                text,
                flags=re.I,
            ).strip()
            remainder = re.sub(
                r"switch\s+to\s+interview[^.]*\.?",
                "",
                remainder,
                flags=re.I,
            ).strip()
            if len(remainder) < 28:
                self._stream_static_answer(
                    INTERVIEW_CONFIRMATION, question="Interview & Meeting"
                )
                return None
            return remainder
        return text

    def _consume_parakeet_commands(self, text: str) -> str | None:
        """Handle lock/unlock voice or typed commands. None = stop processing."""
        text = self._consume_interview_commands(text)
        if text is None:
            return None
        if self._parakeet.wants_unlock(text):
            self._disable_parakeet()
            self._stream_static_answer("Parakeet mode disabled for this session.")
            return None
        if self._parakeet.wants_lock(text):
            self._enable_parakeet()
            remainder = text
            for pat in (
                r"lock\s+(?:the\s+)?mode\s+permanently[^.]*\.?",
                r"full\s+parakeet\s+mode[^.]*\.?",
                r"always\s+recording[^.]*\.?",
                r"always\s+synced[^.]*\.?",
            ):
                remainder = re.sub(pat, "", remainder, flags=re.I).strip()
            if len(remainder) < 24:
                self._stream_static_answer(
                    PARAKEET_CONFIRMATION, question="Parakeet mode"
                )
                return None
            return remainder
        return text

    def _on_agent_hotkey(self) -> None:
        if self._busy():
            return
        self._parakeet.refresh_context()
        self._pending_png = screenshot_png()
        self._pending_png_gen = self._capture_gen
        if self._parakeet.enabled and self._always_on.active:
            from oncue.audio import SAMPLE_RATE

            audio = self._always_on.snapshot(seconds=18.0)
            if audio.size > int(SAMPLE_RATE * 0.35):
                self.overlay.begin_answer("Transcribing…")
                cfg = get_config()
                self._agent_stt = True
                self._stt_worker = TranscribeWorker(
                    audio, cfg.whisper_model, cfg.stt_language, cfg.stt_backend
                )
                self._stt_worker.text.connect(self._on_agent_hotkey_text)
                self._stt_worker.error.connect(self.overlay.show_error)
                self._stt_worker.start()
                return
        self._ask(SCREEN_PROMPT, display="⚡ Agent")

    def _on_agent_hotkey_text(self, text: str) -> None:
        self._agent_stt = False
        cleaned = (text or "").strip()
        if cleaned:
            cleaned = self._consume_parakeet_commands(cleaned)
            if cleaned is None:
                return
            if cleaned:
                self._ask(cleaned)
                return
        self._ask(SCREEN_PROMPT, display="⚡ Agent")

    # --- capture + typed question flow --------------------------------------

    def _on_capture(self) -> None:
        if self._busy():
            return
        self._pending_png = screenshot_png()
        self._pending_png_gen = self._capture_gen
        self._ask(SCREEN_PROMPT, display="📸 What's on my screen?")

    def _on_chat(self) -> None:
        """Chat agent mode — no screenshot. Same key toggles it hidden."""
        if self.overlay.isVisible():
            self.overlay.hide()
            return
        if self._busy():
            return
        self._pending_png = None
        self.overlay.show_for_input(chat=True)

    def _on_question(self, question: str) -> None:
        if not question:
            return
        question = self._consume_parakeet_commands(question)
        if question is None:
            return
        self._ask(question)

    # --- dictation flow (Wispr Flow style) -----------------------------------
    # Hold the dictate hotkey with your cursor in ANY text box; on release the
    # transcript is pasted at the cursor. Focus is never stolen.

    def _on_dictate_press(self) -> None:
        if self._recorder.recording:
            return
        try:
            self._recorder.start()
        except Exception as e:
            self.indicator.failed(f"Mic error: {e}")
            return
        self._dictating = True
        self.indicator.listening()

    def _on_dictate_release(self) -> None:
        if not self._dictating:
            return
        audio = self._recorder.stop()
        self.indicator.transcribing()
        cfg = get_config()
        self._stt_worker = TranscribeWorker(
            audio, cfg.whisper_model, cfg.stt_language, cfg.stt_backend
        )
        self._stt_worker.text.connect(self._on_dictation_text)
        self._stt_worker.error.connect(self._on_dictation_error)
        self._stt_worker.start()

    def _on_dictation_text(self, text: str) -> None:
        self._dictating = False
        if not text:
            self.indicator.failed()
            return
        from oncue.inject import paste_text

        paste_text(text)  # queued signal → we're on the main thread; safe
        self.indicator.done()

    def _on_dictation_error(self, message: str) -> None:
        self._dictating = False
        self.indicator.failed(message)

    # --- voice flow: screenshot + mic/system audio, then answer ----------------
    # Hold the voice hotkey, speak about what's on screen, release → transcribed
    # and sent to the agent with the frozen screenshot.

    def _on_voice_press(self) -> None:
        if self._busy() or self._recording_meeting or self._recorder.recording:
            return
        self._pending_png = screenshot_png()
        self._pending_png_gen = self._capture_gen
        try:
            self._meeting_recorder.start()
        except Exception as e:
            self.overlay.show_error(f"Audio capture error: {e}")
            return
        self._recording_meeting = True
        self.overlay.begin_answer("🔴 Listening (screenshot + audio)… release to answer")

    def _on_voice_release(self) -> None:
        if not self._recording_meeting:
            return
        audio = self._meeting_recorder.stop()
        self.overlay.set_status("Transcribing…")
        cfg = get_config()
        self._stt_worker = TranscribeWorker(
            audio, cfg.whisper_model, cfg.stt_language, cfg.stt_backend
        )
        self._stt_worker.text.connect(self._on_voice_text)
        self._stt_worker.error.connect(self.overlay.show_error)
        self._stt_worker.start()

    def _on_voice_text(self, text: str) -> None:
        self._recording_meeting = False
        if not text:
            self.overlay.show_for_input()
            self.overlay.set_status("Didn't catch any audio — type your question")
            return
        text = self._consume_parakeet_commands(text)
        if text is None:
            return
        self._ask(text)

    # --- listen flow: mic + all system/call audio at once, then answer -------

    def _on_listen_press(self) -> None:
        if self._busy() or self._recording_meeting or self._recorder.recording:
            return
        self._pending_png = None  # audio only
        try:
            self._meeting_recorder.start()
        except Exception as e:
            self.overlay.show_error(f"Audio capture error: {e}")
            return
        self._recording_meeting = True
        self.overlay.begin_answer("🔴 Listening (you + system audio)… release to answer")

    def _on_listen_release(self) -> None:
        if not self._recording_meeting:
            return
        audio = self._meeting_recorder.stop()
        self.overlay.set_status("Transcribing…")
        cfg = get_config()
        self._stt_worker = TranscribeWorker(
            audio, cfg.whisper_model, cfg.stt_language, cfg.stt_backend
        )
        self._stt_worker.text.connect(self._on_listen_text)
        self._stt_worker.error.connect(self.overlay.show_error)
        self._stt_worker.start()

    def _on_listen_text(self, text: str) -> None:
        self._recording_meeting = False
        self._pending_png = None
        if not text:
            # nothing captured — open the box so they can type instead
            self.overlay.show_for_input()
            self.overlay.set_status("Didn't catch any audio — type your question")
            return
        self._ask(text)

    # --- agent ----------------------------------------------------------------

    def _ensure_agent(self) -> bool:
        if self._agent is not None:
            return True
        try:
            from oncue.agent.agent import build_agent

            self._agent = build_agent(
                allow_system=get_config().system_tools_enabled,
                checkpointer=self._checkpointer,
            )
            return True
        except Exception as e:
            self.overlay.show_error(
                f"Couldn't start the model provider:\n{e}\n\nOpen Settings from the tray icon."
            )
            return False

    def _ask(self, question: str, display: str | None = None) -> None:
        """Run the agent. A generation counter tags every turn so that
        out-of-order / stale worker completions are silently discarded."""
        if self._interview.enabled and not self._interview.should_invoke_agent(
            question
        ):
            self._stream_static_answer(
                self._interview.filler_acknowledgment(),
                question=display or question,
            )
            return
        if not self._ensure_agent():
            return
        if self._parakeet.enabled:
            self._parakeet.refresh_context()
            question = self._parakeet.enrich_question(question)
            if self._pending_png is None:
                self._pending_png = screenshot_png()
                self._pending_png_gen = self._capture_gen
        if self._interview.enabled:
            question = self._interview.enrich_question(question)
        self._capture_gen += 1
        gen = self._capture_gen
        cfg = get_config()
        if not self._session_reported and cfg.provider == "hosted" and cfg.web_url:
            report_session_start()
            self._session_reported = True
        png = self._pending_png
        self.overlay.begin_answer("Thinking…")
        self.overlay.show_question(display or question)
        self._worker = AgentWorker(
            self._agent, build_message(question, png), self._thread_id
        )
        self._worker._gen = gen
        self._worker.status.connect(self.overlay.set_status)
        self._worker.token.connect(lambda t, g=gen: self._on_token(t, g))
        self._worker.confirm_request.connect(self.overlay.show_confirm)
        self._worker.done.connect(lambda g=gen: self._on_done(g))
        self._worker.error.connect(lambda e, g=gen: self._on_error(e, g))
        self._worker.start()

    def _on_token(self, text: str, gen: int) -> None:
        if gen != self._capture_gen:
            return
        self.overlay.set_status("")
        self.overlay.append_token(text)
        points = parse_point_tags(text)
        for pt in points:
            self._pointer.point_at(pt)

    def _on_confirmed(self, allowed: bool) -> None:
        if self._worker:
            self._worker.provide_confirmation(allowed)

    def _on_done(self, gen: int) -> None:
        if gen != self._capture_gen:
            return
        self._pending_png = None
        self.overlay.finish()
        cfg = get_config()
        if cfg.provider == "hosted" and cfg.web_url:
            answer = self.overlay._answer_buffer or ""
            report_inference(
                model_used=cfg.hosted_model,
                tokens_out=len(answer) // 4,
            )
        if self._interview.enabled:
            from oncue.ui.pointer import strip_point_tags

            q = self._interview.last_question
            a = strip_point_tags(self.overlay._answer_buffer).strip()
            if q and a:
                record_turn(q, a)
        if self._tts_enabled:
            from oncue.ui.pointer import strip_point_tags

            clean = strip_point_tags(self.overlay._answer_buffer).strip()
            if clean:
                self.overlay.set_tts_speaking(True)
                self._tts.speak(
                    clean,
                    error_callback=self.overlay.show_error,
                    done_callback=lambda: self.overlay.set_tts_speaking(False),
                )

    def _on_error(self, message: str, gen: int) -> None:
        if gen != self._capture_gen:
            return
        self.overlay.show_error(message)

    def _on_cancel(self) -> None:
        """Cancel the in-flight agent turn (Esc pressed on overlay)."""
        self._capture_gen += 1
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
        self._worker = None
        self._pointer.clear_points()
        self._tts.stop()
        self.overlay._reset()

    def _busy(self) -> bool:
        running = self._worker is not None and self._worker.isRunning()
        stt = self._stt_worker is not None and self._stt_worker.isRunning()
        return (
            running
            or stt
            or self._recording_meeting
            or self._recorder.recording
        )

    # --- settings ---------------------------------------------------------------

    # --- TTS toggle ---------------------------------------------------------

    def _set_tts_enabled(self, enabled: bool) -> None:
        self._tts_enabled = enabled
        if not enabled:
            self._tts.stop()

    # --- hide from screen sharing -------------------------------------------

    def _set_content_protection(self, enabled: bool) -> None:
        cfg = get_config()
        cfg.content_protection = enabled
        try:
            cfg.save()
        except OSError:
            pass
        self.overlay.set_content_protection(enabled)
        self.indicator.set_content_protection(enabled)
        if hasattr(self, "_tray_hide_action"):
            self._tray_hide_action.setChecked(enabled)
        self.indicator.flash(
            "🛡 Hidden from screen sharing" if enabled else "👁 Visible in screen sharing",
            1600,
        )

    # --- system-actions toggle (open apps/files/browser) ---------------------

    def _set_system_enabled(self, enabled: bool, from_timer: bool = False) -> None:
        cfg = get_config()
        if cfg.system_tools_enabled == enabled and not from_timer:
            self.overlay.set_system_enabled(enabled)
            return
        cfg.system_tools_enabled = enabled
        try:
            cfg.save()
        except OSError:
            pass
        self._agent = None  # rebuilt lazily with the new tool set
        self.overlay.set_system_enabled(enabled)
        if hasattr(self, "_tray_system_action"):
            self._tray_system_action.setChecked(enabled)
        if enabled and self._pause_timer is not None:
            self._pause_timer.stop()
            self._pause_timer = None

    def _pause_system(self, minutes: int) -> None:
        from PySide6.QtCore import QTimer

        self._set_system_enabled(False)
        if self._pause_timer is not None:
            self._pause_timer.stop()
        self._pause_timer = QTimer(self)
        self._pause_timer.setSingleShot(True)
        self._pause_timer.timeout.connect(
            lambda: self._set_system_enabled(True, from_timer=True)
        )
        self._pause_timer.start(minutes * 60 * 1000)
        self.indicator.flash(f"🔒 System actions paused for {minutes} min", 1800)

    def _open_settings(self) -> None:
        dialog = SettingsDialog()
        dialog.saved.connect(self._on_settings_saved)
        dialog.exec()

    def handle_protocol_url(self, url: str) -> None:
        """Apply a oncue:// deep link (from the website 'Open app' button)."""
        from oncue.protocol import apply_url

        status = apply_url(url)
        if status:
            self._agent = None  # rebuild with the new token/profile
            self.indicator.flash(f"🔗 {status}", 2200)

    def _on_settings_saved(self) -> None:
        self._agent = None            # rebuilt lazily with the new provider
        # thread_id and self._checkpointer are intentionally left alone so
        # conversation memory survives a settings change instead of silently
        # resetting.
        self._restart_hotkeys()
        cfg = get_config()
        # re-apply toggles that other UI (tray) mirrors
        self.overlay.set_content_protection(cfg.content_protection)
        self.indicator.set_content_protection(cfg.content_protection)
        self._tray_hide_action.setChecked(cfg.content_protection)
        self._tray_system_action.setChecked(cfg.system_tools_enabled)
        self.overlay.set_system_enabled(cfg.system_tools_enabled)


_SINGLE_INSTANCE = "oncue-single-instance"


def main() -> None:
    from PySide6.QtNetwork import QLocalServer, QLocalSocket

    from oncue.protocol import register_windows, url_in_argv

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("OnCUE")

    # Single instance: if one is already running, forward any oncue:// URL to
    # it and exit — so clicking "Open app" twice doesn't spawn a duplicate.
    probe = QLocalSocket()
    probe.connectToServer(_SINGLE_INSTANCE)
    if probe.waitForConnected(300):
        probe.write((url_in_argv() or "").encode())
        probe.flush()
        probe.waitForBytesWritten(300)
        probe.disconnectFromServer()
        return

    QLocalServer.removeServer(_SINGLE_INSTANCE)  # clear any stale socket
    server = QLocalServer()
    server.listen(_SINGLE_INSTANCE)

    oncue_app = OnCUEApp(app)

    def _on_conn():
        conn = server.nextPendingConnection()
        if conn and conn.waitForReadyRead(300):
            url = bytes(conn.readAll()).decode()
            if url:
                oncue_app.handle_protocol_url(url)

    server.newConnection.connect(_on_conn)

    # apply a URL we were launched with, and register the scheme for next time
    launch_url = url_in_argv()
    if launch_url:
        oncue_app.handle_protocol_url(launch_url)
    register_windows()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
