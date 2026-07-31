"""Settings dialog: provider picker, API keys / license token, guardrails."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from oncue.agent.router import PROVIDERS
from oncue.config import Config, get_config, set_config
from oncue.ui.theme import COLOR, DIALOG_STYLE, RADIUS

_LANGUAGES = [
    ("hinglish", "Hinglish — Roman (kal milte hain)"),
    ("hindi", "Hindi — देवनागरी"),
    ("english", "English"),
    ("auto", "Auto-detect"),
]

_STT_BACKENDS = [
    ("auto", "Auto — Groq cloud when key set (best)"),
    ("groq", "Groq cloud (whisper-large-v3-turbo)"),
    ("local", "Local (offline, private, slower)"),
]


class SettingsDialog(QDialog):
    saved = Signal()  # app.py rebuilds the agent when this fires

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OnCUE Settings")
        self.setMinimumWidth(500)
        self.setStyleSheet(DIALOG_STYLE)
        cfg = get_config()

        root = QVBoxLayout(self)

        # provider
        form = QFormLayout()
        self.provider = QComboBox()
        self.provider.addItems(PROVIDERS)
        self.provider.setCurrentText(cfg.provider)
        form.addRow("Provider", self.provider)
        root.addLayout(form)

        # BYO keys
        keys_box = QGroupBox("API keys (bring-your-own providers)")
        keys = QFormLayout(keys_box)
        self.groq_key = self._secret(cfg.groq_api_key)
        self.anthropic_key = self._secret(cfg.anthropic_api_key)
        self.openai_key = self._secret(cfg.openai_api_key)
        self.gemini_key = self._secret(cfg.gemini_api_key)
        self.tavily_key = self._secret(cfg.tavily_api_key)
        keys.addRow("Groq (free — console.groq.com)", self.groq_key)
        keys.addRow("Anthropic", self.anthropic_key)
        keys.addRow("OpenAI", self.openai_key)
        keys.addRow("Gemini (Google AI Studio)", self.gemini_key)
        keys.addRow("Tavily (web search)", self.tavily_key)
        root.addWidget(keys_box)

        # hosted mode
        hosted_box = QGroupBox("OnCUE hosted (no provider keys needed)")
        hosted = QFormLayout(hosted_box)
        self.backend_url = QLineEdit(cfg.backend_url)
        self.backend_url.setPlaceholderText("https://api.yourdomain.com/v1")
        self.web_url = QLineEdit(cfg.web_url)
        self.web_url.setPlaceholderText("https://your-oncue-site.com")
        self.rag_url = QLineEdit(cfg.rag_url)
        self.rag_url.setPlaceholderText("https://xxx.supabase.co/functions/v1/rag")
        self.token = self._secret(cfg.oncue_token)
        self.hosted_model = QComboBox()
        self.hosted_model.setEditable(True)  # a licensed alias not in this list still works
        self.hosted_model.addItems(
            ["oncue-default", "oncue-groq", "oncue-claude", "oncue-gpt", "oncue-gemini"]
        )
        self.hosted_model.setCurrentText(cfg.hosted_model)
        hosted.addRow("Backend URL", self.backend_url)
        hosted.addRow("Website URL", self.web_url)
        hosted.addRow("RAG URL", self.rag_url)
        hosted.addRow("License key", self.token)
        hosted.addRow("Hosted model", self.hosted_model)
        hosted_note = QLabel(
            "Free-tier keys are only allowed \"oncue-groq\" server-side —\n"
            "picking another alias here does nothing without a Pro key."
        )
        hosted_note.setStyleSheet(f"color: {COLOR['text_muted']}; font-size: 11px;")
        hosted.addRow("", hosted_note)
        self._trial_label = QLabel("")
        self._trial_label.setStyleSheet(f"color: {COLOR['status_green']}; font-size: 11px;")
        hosted.addRow("", self._trial_label)
        root.addWidget(hosted_box)

        # speech
        speech_box = QGroupBox("Speech")
        speech = QFormLayout(speech_box)
        self.stt_language = QComboBox()
        for value, label in _LANGUAGES:
            self.stt_language.addItem(label, value)
        idx = self.stt_language.findData(cfg.stt_language)
        self.stt_language.setCurrentIndex(idx if idx >= 0 else 0)
        self.stt_backend = QComboBox()
        for value, label in _STT_BACKENDS:
            self.stt_backend.addItem(label, value)
        idx = self.stt_backend.findData(cfg.stt_backend)
        self.stt_backend.setCurrentIndex(idx if idx >= 0 else 0)
        self.groq_stt_model = QComboBox()
        self.groq_stt_model.addItems(["whisper-large-v3", "whisper-large-v3-turbo"])
        self.groq_stt_model.setCurrentText(cfg.groq_stt_model)
        self.whisper_model = QComboBox()
        self.whisper_model.addItems(["base", "small", "medium"])
        self.whisper_model.setCurrentText(cfg.whisper_model)
        speech.addRow("Language", self.stt_language)
        speech.addRow("Recognition", self.stt_backend)
        speech.addRow("Groq model (accuracy)", self.groq_stt_model)
        speech.addRow("Local model (offline)", self.whisper_model)
        root.addWidget(speech_box)

        # behavior
        behavior_box = QGroupBox("Behavior")
        behavior = QFormLayout(behavior_box)
        self.capture_hotkey = QLineEdit(cfg.capture_hotkey)
        self.voice_hotkey = QLineEdit(cfg.voice_hotkey)
        self.dictate_hotkey = QLineEdit(cfg.dictate_hotkey)
        self.meeting_hotkey = QLineEdit(cfg.meeting_hotkey)
        self.allowed_dirs = QLineEdit(cfg.allowed_dirs)
        self.browser = QComboBox()
        self.browser.setEditable(True)  # allows a custom .exe path too
        self.browser.addItems(["default", "chrome", "edge", "firefox", "brave"])
        self.browser.setCurrentText(cfg.preferred_browser)
        self.content_protection = QCheckBox(
            "Hide overlay from screen sharing / recording"
        )
        self.content_protection.setChecked(cfg.content_protection)
        self.system_tools_enabled = QCheckBox(
            "Enable system actions (open apps/files/browser, search local files)"
        )
        self.system_tools_enabled.setChecked(cfg.system_tools_enabled)
        self.confirm_actions = QCheckBox("Ask before opening apps/files/websites")
        self.confirm_actions.setChecked(cfg.confirm_actions)
        behavior.addRow("Browser for searches", self.browser)
        self.chat_hotkey = QLineEdit(cfg.chat_hotkey)
        behavior.addRow("Capture hotkey", self.capture_hotkey)
        behavior.addRow("Chat hotkey (no screenshot)", self.chat_hotkey)
        behavior.addRow("Voice hotkey (hold)", self.voice_hotkey)
        behavior.addRow("Dictation hotkey (hold)", self.dictate_hotkey)
        behavior.addRow("Meeting audio hotkey (hold)", self.meeting_hotkey)
        behavior.addRow("Allowed folders", self.allowed_dirs)
        behavior.addRow("", self.content_protection)
        behavior.addRow("", self.system_tools_enabled)
        behavior.addRow("", self.confirm_actions)
        root.addWidget(behavior_box)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def showEvent(self, event):
        from oncue.screen_privacy import set_capture_protection

        set_capture_protection(self, get_config().content_protection)
        self._refresh_trial_label()
        super().showEvent(event)

    def _refresh_trial_label(self) -> None:
        cfg = get_config()
        if cfg.provider != "hosted" or not cfg.web_url or not cfg.oncue_token:
            self._trial_label.setText("")
            return
        from oncue.usage import check_session

        result = check_session()
        remaining = result.get("trial_remaining", 0)
        if remaining > 0:
            self._trial_label.setText(f"Hosted trial: {remaining} session(s) remaining")
        elif not result.get("can_start", True):
            self._trial_label.setText("Trial ended — upgrade on your dashboard")
        else:
            self._trial_label.setText("Hosted mode connected")

    @staticmethod
    def _secret(value: str) -> QLineEdit:
        box = QLineEdit(value)
        box.setEchoMode(QLineEdit.EchoMode.Password)
        return box

    def _save(self) -> None:
        old = get_config()
        cfg = Config(
            provider=self.provider.currentText(),
            groq_api_key=self.groq_key.text().strip(),
            anthropic_api_key=self.anthropic_key.text().strip(),
            openai_api_key=self.openai_key.text().strip(),
            gemini_api_key=self.gemini_key.text().strip(),
            tavily_api_key=self.tavily_key.text().strip(),
            groq_model=old.groq_model,
            claude_model=old.claude_model,
            gpt_model=old.gpt_model,
            gemini_model=old.gemini_model,
            backend_url=self.backend_url.text().strip(),
            oncue_token=self.token.text().strip(),
            web_url=self.web_url.text().strip(),
            rag_url=self.rag_url.text().strip(),
            hosted_model=self.hosted_model.currentText().strip() or old.hosted_model,
            capture_hotkey=self.capture_hotkey.text().strip() or old.capture_hotkey,
            voice_hotkey=self.voice_hotkey.text().strip() or old.voice_hotkey,
            dictate_hotkey=self.dictate_hotkey.text().strip() or old.dictate_hotkey,
            chat_hotkey=self.chat_hotkey.text().strip() or old.chat_hotkey,
            meeting_hotkey=self.meeting_hotkey.text().strip() or old.meeting_hotkey,
            allowed_dirs=self.allowed_dirs.text().strip() or old.allowed_dirs,
            confirm_actions=self.confirm_actions.isChecked(),
            system_tools_enabled=self.system_tools_enabled.isChecked(),
            content_protection=self.content_protection.isChecked(),
            whisper_model=self.whisper_model.currentText(),
            stt_language=self.stt_language.currentData(),
            stt_backend=self.stt_backend.currentData(),
            groq_stt_model=self.groq_stt_model.currentText(),
            preferred_browser=self.browser.currentText().strip() or "default",
            click_through=old.click_through,
            overlay_geometry=old.overlay_geometry,
        )
        cfg.save()
        set_config(cfg)
        self.saved.emit()
        self.accept()
