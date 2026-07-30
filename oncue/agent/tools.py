"""Agent tools: web search, browser, and allowlisted read/open-only system tools.

Guardrails (do not weaken):
- File tools only touch folders in ALLOWED_DIRS (under the user's home).
  Paths outside are refused, not clamped.
- No delete/move/write tools in v1.
- Side-effecting tools (ACTION_TOOLS) go through a human confirmation gate:
  `_confirm()` raises a LangGraph interrupt; the UI shows Allow/Deny and the
  graph resumes with the user's answer. This also mitigates prompt injection
  from `browse` (untrusted web text can't silently open files/apps).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import webbrowser
from pathlib import Path
from urllib.parse import quote_plus

from langchain_core.tools import tool
from langgraph.types import interrupt

from oncue.config import get_config

# Tools with side effects — gated behind user confirmation.
ACTION_TOOLS = ["launch_app", "open_file", "open_website"]

# Known install locations for PREFERRED_BROWSER on Windows. On macOS/Linux
# only "default" and explicit paths are supported.
_BROWSER_PATHS: dict[str, list[str]] = {
    "chrome": [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ],
    "edge": [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ],
    "firefox": [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ],
    "brave": [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
    ],
}


def _open_url(url: str) -> None:
    """Open a URL in the user's preferred browser (config), else OS default."""
    choice = (get_config().preferred_browser or "default").strip()
    if choice.lower() not in ("", "default"):
        candidates = (
            [choice] if os.path.sep in choice or choice.lower().endswith(".exe")
            else _BROWSER_PATHS.get(choice.lower(), [])
        )
        for path in candidates:
            if os.path.exists(path):
                try:
                    subprocess.Popen([path, url])
                    return
                except OSError:
                    break
    webbrowser.open(url)


def _confirm(action: str) -> bool:
    """Human-in-the-loop gate. Pauses the graph until the overlay answers."""
    if not get_config().confirm_actions:
        return True
    answer = interrupt({"type": "confirm", "action": action})
    return bool(answer)


def _allowed(p: Path) -> bool:
    try:
        p = p.expanduser().resolve()
    except OSError:
        return False
    for root in get_config().allowed_roots():
        try:
            if p.is_relative_to(root.resolve()):
                return True
        except OSError:
            continue
    return False


# --- web + browser tools ---------------------------------------------------

@tool
def search_my_documents(query: str) -> str:
    """Search the user's OWN uploaded reference documents (their resume, notes,
    study plans) for material relevant to `query`. Call this whenever the user's
    own background, projects, or notes could improve the answer. Use the results
    silently to give a better, personalized answer — do not cite the document."""
    cfg = get_config()
    if not cfg.oncue_token or not (cfg.rag_url or cfg.web_url):
        return (
            "No documents connected. Sign in and upload documents at the OnCUE "
            "website, then paste your key in Settings."
        )
    # Prefer the Supabase edge function directly (lowest latency: embed + vector
    # match in one hop next to the DB); fall back to the website API.
    if cfg.rag_url:
        url = cfg.rag_url.rstrip("/")
        payload = {"action": "search", "query": query}
    else:
        url = f"{cfg.web_url.rstrip('/')}/api/documents/search"
        payload = {"query": query}
    try:
        import urllib.request

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {cfg.oncue_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        return f"Could not search your documents: {e}"
    passages = data.get("passages") or []
    if not passages:
        return "No relevant passages found in your documents."
    return "\n\n---\n\n".join(passages)


@tool
def web_search(query: str) -> str:
    """Search the web for CURRENT information and return top results with sources.
    Use this whenever the answer depends on recent or real-world facts (news,
    prices, releases, people, events) rather than answering from memory."""
    # Tavily if a key is set (highest quality); otherwise keyless DuckDuckGo.
    if os.environ.get("TAVILY_API_KEY"):
        try:
            from langchain_tavily import TavilySearch

            return str(TavilySearch(max_results=5).invoke({"query": query}))
        except Exception:
            pass  # fall through to keyless search
    return _ddg_search(query)


def _ddg_search(query: str, max_results: int = 5) -> str:
    try:
        from ddgs import DDGS
    except ImportError:
        return "web_search unavailable: run `pip install ddgs`."
    try:
        with DDGS(timeout=8) as ddgs:
            results = ddgs.text(query, max_results=max_results)
    except Exception as e:
        return f"web_search failed: {e}"
    if not results:
        return "No web results found."
    blocks = []
    for r in results:
        title = (r.get("title") or "").strip()
        body = (r.get("body") or "").strip()
        href = (r.get("href") or "").strip()
        blocks.append(f"{title}\n{body}\n(source: {href})")
    return "\n\n".join(blocks)


@tool
def open_website(query: str) -> str:
    """Open a website in the user's browser. `query` may be a full URL or a known name
    (youtube, netflix, gmail, github). Use for requests like 'open Netflix'."""
    sites = {
        "youtube": "https://youtube.com",
        "netflix": "https://netflix.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
    }
    url = sites.get(query.lower().strip()) or (
        query if query.startswith("http") else f"https://{query}"
    )
    if not _confirm(f"Open {url} in your browser?"):
        return "User declined to open the website."
    _open_url(url)
    return f"Opened {url}"


@tool
def google_search(query: str) -> str:
    """Open Google results for `query` in the browser (visual results, not a text answer)."""
    _open_url(f"https://www.google.com/search?q={quote_plus(query)}")
    return f"Opened Google results for: {query}"


@tool
def youtube_search(query: str) -> str:
    """Open YouTube search results for `query` in the browser."""
    _open_url(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
    return f"Opened YouTube results for: {query}"


@tool
def browse(url: str, task: str) -> str:
    """Navigate a real browser to `url` and return page text relevant to `task`.
    Use to READ a page, not just open it."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return (
            "browse unavailable: Playwright is not installed. "
            "Tell the user to run: pip install playwright && playwright install chromium"
        )
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True)
            page = b.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            text = page.inner_text("body")
            b.close()
    except Exception as e:
        return f"browse failed: {e}"
    return text[:4000]


# --- system tools (allowlisted, read/open-only) ----------------------------

@tool
def launch_app(name: str) -> str:
    """Launch a desktop application by name, e.g. 'Spotify', 'Calculator', 'Notepad'."""
    if not _confirm(f"Launch the app '{name}'?"):
        return "User declined to launch the app."
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", "-a", name], check=True)
        elif sys.platform == "win32":
            from AppOpener import open as app_open

            app_open(name, match_closest=True, throw_error=True, output=False)
        else:
            subprocess.run([name.lower()], check=True)
        return f"Launched {name}"
    except Exception as e:
        return f"Could not launch {name}: {e}"


@tool
def open_file(path: str) -> str:
    """Open a file with its default app. Only files inside the allowed folders."""
    p = Path(path).expanduser()
    if not _allowed(p):
        return "Refused: path is outside the allowed folders."
    if not p.exists():
        return f"No such file: {p}"
    if not _confirm(f"Open the file '{p.name}'?"):
        return "User declined to open the file."
    if sys.platform == "darwin":
        subprocess.run(["open", str(p)])
    elif sys.platform == "win32":
        os.startfile(str(p))  # type: ignore[attr-defined]
    else:
        subprocess.run(["xdg-open", str(p)])
    return f"Opened {p.name}"


@tool
def find_files(name_query: str, subfolder: str = "") -> str:
    """Find files by NAME within the allowed folders. Returns up to 25 paths."""
    hits: list[str] = []
    for root in get_config().allowed_roots():
        base = (root / subfolder) if subfolder else root
        if not _allowed(base) or not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and name_query.lower() in p.name.lower():
                hits.append(str(p))
                if len(hits) >= 25:
                    return "\n".join(hits)
    return "\n".join(hits) or "No matching files."


@tool
def search_documents(text_query: str, subfolder: str = "") -> str:
    """Search INSIDE text-based docs (.txt .md .csv .py .json .log) for `text_query`.
    Returns file:line matches."""
    exts = {".txt", ".md", ".csv", ".py", ".json", ".log"}
    out: list[str] = []
    for root in get_config().allowed_roots():
        base = (root / subfolder) if subfolder else root
        if not _allowed(base) or not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in exts:
                try:
                    for i, line in enumerate(
                        p.read_text(errors="ignore").splitlines(), 1
                    ):
                        if text_query.lower() in line.lower():
                            out.append(f"{p.name}:{i}: {line.strip()[:120]}")
                            if len(out) >= 25:
                                return "\n".join(out)
                except Exception:
                    pass
    return "\n".join(out) or "No matches in documents."


# Tools that only fetch information — always safe, no computer side effects.
SAFE_TOOLS = [web_search, search_my_documents]

# Tools that act on the computer: open apps/files/browser, read local files.
# These are what the "System actions" toggle disables.
SYSTEM_TOOLS = [
    open_website,
    google_search,
    youtube_search,
    browse,
    launch_app,
    open_file,
    find_files,
    search_documents,
]

ALL_TOOLS = SAFE_TOOLS + SYSTEM_TOOLS


def tools_for(allow_system: bool) -> list:
    return ALL_TOOLS if allow_system else SAFE_TOOLS
