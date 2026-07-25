"""`parakeet://` deep-link support so the website can launch/configure the app.

Website button → parakeet://connect?token=<key>&web=<url>
→ OS launches the app with that URL as argv → we parse it, save token + web
URL into config, and switch to hosted mode. Registration is done on Windows via
a per-user registry key pointing back at this app.
"""

from __future__ import annotations

import sys
from urllib.parse import parse_qs, urlparse

from parakeet.config import get_config, set_config

SCHEME = "parakeet"


def url_in_argv() -> str | None:
    for arg in sys.argv[1:]:
        if arg.startswith(f"{SCHEME}://"):
            return arg
    return None


def apply_url(url: str) -> str | None:
    """Parse a parakeet:// URL and apply it. Returns a short status string
    (for the UI) or None if it wasn't a connect link."""
    parsed = urlparse(url)
    if parsed.scheme != SCHEME:
        return None
    action = parsed.netloc or parsed.path.lstrip("/")
    if action != "connect":
        return None
    q = parse_qs(parsed.query)
    token = (q.get("token") or [""])[0]
    web = (q.get("web") or [""])[0]
    rag = (q.get("rag") or [""])[0]
    if not token:
        return None
    cfg = get_config()
    cfg.parakeet_token = token
    if web:
        cfg.web_url = web
    if rag:
        cfg.rag_url = rag
    cfg.provider = "hosted"
    try:
        cfg.save()
    except OSError:
        pass
    set_config(cfg)
    return "Connected to your Parakeet account"


def register_windows(target_cmd: str | None = None) -> bool:
    """Register the parakeet:// scheme for the current user (Windows).
    `target_cmd` is the launch command; defaults to `pythonw -m parakeet "%1"`
    for dev. The installer passes the exe path in packaging."""
    if sys.platform != "win32":
        return False
    import winreg

    if target_cmd is None:
        pyw = sys.executable.replace("python.exe", "pythonw.exe")
        target_cmd = f'"{pyw}" -m parakeet "%1"'
    try:
        base = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\parakeet")
        winreg.SetValueEx(base, "", 0, winreg.REG_SZ, "URL:Parakeet Protocol")
        winreg.SetValueEx(base, "URL Protocol", 0, winreg.REG_SZ, "")
        cmd = winreg.CreateKey(
            winreg.HKEY_CURRENT_USER, r"Software\Classes\parakeet\shell\open\command"
        )
        winreg.SetValueEx(cmd, "", 0, winreg.REG_SZ, target_cmd)
        return True
    except OSError:
        return False
