"""Settings: process env > user config file > defaults.

The config file is a simple KEY=VALUE file in the platform user-config dir
(e.g. %APPDATA%/OnCUE/config.env on Windows), written by the settings UI.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, fields
from pathlib import Path

from platformdirs import user_config_dir

CONFIG_DIR = Path(user_config_dir("OnCUE", appauthor=False))
CONFIG_FILE = CONFIG_DIR / "config.env"

# config attribute -> env var name
_ENV_MAP = {
    "provider": "DEFAULT_PROVIDER",
    "groq_api_key": "GROQ_API_KEY",
    "anthropic_api_key": "ANTHROPIC_API_KEY",
    "openai_api_key": "OPENAI_API_KEY",
    "gemini_api_key": "GOOGLE_API_KEY",
    "tavily_api_key": "TAVILY_API_KEY",
    "groq_model": "GROQ_MODEL",
    "claude_model": "CLAUDE_MODEL",
    "gpt_model": "GPT_MODEL",
    "gemini_model": "GEMINI_MODEL",
    "backend_url": "ONCUE_BACKEND_URL",
    "oncue_token": "ONCUE_TOKEN",
    "hosted_model": "HOSTED_MODEL",
    "web_url": "ONCUE_WEB_URL",
    "rag_url": "ONCUE_RAG_URL",
    "capture_hotkey": "CAPTURE_HOTKEY",
    "voice_hotkey": "VOICE_HOTKEY",
    "dictate_hotkey": "DICTATE_HOTKEY",
    "chat_hotkey": "CHAT_HOTKEY",
    "meeting_hotkey": "MEETING_HOTKEY",
    "allowed_dirs": "ALLOWED_DIRS",
    "confirm_actions": "CONFIRM_ACTIONS",
    "system_tools_enabled": "SYSTEM_TOOLS_ENABLED",
    "content_protection": "CONTENT_PROTECTION",
    "whisper_model": "WHISPER_MODEL",
    "stt_language": "STT_LANGUAGE",
    "stt_backend": "STT_BACKEND",
    "groq_stt_model": "GROQ_STT_MODEL",
    "preferred_browser": "PREFERRED_BROWSER",
    "click_through": "CLICK_THROUGH",
    "overlay_geometry": "OVERLAY_GEOMETRY",
}

_BOOL_FIELDS = {
    "confirm_actions",
    "click_through",
    "system_tools_enabled",
    "content_protection",
}


@dataclass
class Config:
    # "hosted" so a fresh install with no key configured hits the router's
    # clean, actionable ValueError ("open Settings and sign in...") instead of
    # a raw ChatGroq validation error — the onboarding dialog is the primary
    # path, this default is defense-in-depth if it's dismissed/skipped.
    provider: str = "hosted"
    groq_api_key: str = ""
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    gemini_api_key: str = ""
    tavily_api_key: str = ""
    groq_model: str = "qwen/qwen3.6-27b"  # vision-capable on Groq's free tier
    claude_model: str = "claude-opus-4-8"
    gpt_model: str = "gpt-4o"
    gemini_model: str = "gemini-2.5-flash"
    backend_url: str = ""
    oncue_token: str = ""
    hosted_model: str = "oncue-default"
    web_url: str = ""  # OnCUE website base URL (for documents + profile)
    rag_url: str = ""  # Supabase edge `rag` function URL (fast direct doc search)
    capture_hotkey: str = "<ctrl>+<shift>+<space>"
    voice_hotkey: str = "<ctrl>+<shift>+v"
    dictate_hotkey: str = "<ctrl>+<shift>+d"
    chat_hotkey: str = "<ctrl>+<shift>+h"  # chat agent, no screenshot; toggles
    meeting_hotkey: str = "<ctrl>+<shift>+m"  # hold: record system + mic audio
    allowed_dirs: str = "Documents,Downloads,Desktop"
    confirm_actions: bool = True
    system_tools_enabled: bool = True  # open apps/files/browser + file search
    content_protection: bool = True    # hide overlay from screen sharing/recording
    whisper_model: str = "small"
    stt_language: str = "hinglish"  # hinglish | hindi | english | auto
    stt_backend: str = "auto"  # auto (Groq if key set) | groq | local
    # whisper-large-v3 = most accurate (best for Hindi/Hinglish);
    # whisper-large-v3-turbo = faster, less accurate
    groq_stt_model: str = "whisper-large-v3"
    preferred_browser: str = "default"  # default | chrome | edge | firefox | brave | <path>
    click_through: bool = False
    overlay_geometry: str = ""  # "x,y,w,h" — saved when the user moves/resizes

    def allowed_roots(self) -> list[Path]:
        home = Path.home()
        return [home / d.strip() for d in self.allowed_dirs.split(",") if d.strip()]

    def apply_env(self) -> None:
        """Export API keys so LangChain integrations pick them up."""
        for attr, env in (
            ("groq_api_key", "GROQ_API_KEY"),
            ("anthropic_api_key", "ANTHROPIC_API_KEY"),
            ("openai_api_key", "OPENAI_API_KEY"),
            ("tavily_api_key", "TAVILY_API_KEY"),
        ):
            value = getattr(self, attr)
            if value:
                os.environ[env] = value

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        lines = []
        for f in fields(self):
            env_name = _ENV_MAP[f.name]
            value = getattr(self, f.name)
            if isinstance(value, bool):
                value = "true" if value else "false"
            lines.append(f"{env_name}={value}")
        CONFIG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values


def load_config() -> Config:
    cfg = Config()
    file_values = _parse_env_file(CONFIG_FILE)
    # also honor a local .env when running from a source checkout
    file_values = {**_parse_env_file(Path(".env")), **file_values}
    for attr, env_name in _ENV_MAP.items():
        raw = os.environ.get(env_name) or file_values.get(env_name)
        if raw is None or raw == "":
            continue
        if attr in _BOOL_FIELDS:
            setattr(cfg, attr, raw.strip().lower() in ("1", "true", "yes", "on"))
        else:
            setattr(cfg, attr, raw)
    return cfg


_current: Config | None = None


def get_config() -> Config:
    global _current
    if _current is None:
        _current = load_config()
    return _current


def set_config(cfg: Config) -> None:
    global _current
    _current = cfg
    cfg.apply_env()
