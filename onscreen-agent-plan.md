# On-Screen AI Agent — Build Brief

A desktop AI assistant that listens to a voice command (or hotkey), captures the screen, and runs an **agent** that can answer directly or take actions — search the web, open/drive the browser, open apps and files, and search local documents — before streaming the answer onto a transparent always-on-top overlay. Cross-platform: **Windows 10/11 and macOS 12+**.

> This document is the build brief. Work through the phases in order. Each phase has acceptance criteria — do not move to the next phase until the current one passes.

---

## 1. Architecture

```
Voice command / hotkey ─┐
                        ├─► LangGraph agent (ReAct loop) ──► final answer ──► Overlay (streams tokens)
Screenshot ─────────────┘            │              ▲
                                     ▼              │
              Tools: web search · browser (open/search/read) · system (launch apps,
                     open files, find & search documents) · re-capture screen
                          (the model loops through tools until it can answer)
```

Two processes that talk over a local WebSocket:

- **Electron shell** (TypeScript/JS) — owns the transparent overlay window, the global hotkey, and the screenshot. Thin UI layer only.
- **Python backend** (FastAPI) — owns audio capture, speech-to-text, the **LangGraph agent**, the model router, and the tools. This is the "brain."

They communicate over `ws://127.0.0.1:8765`. The backend streams **status events** ("searching the web…", "opening YouTube…") and **answer tokens**; the overlay shows the status line while tools run, then types out the answer.

> Single-process alternative: everything can live in Electron/TypeScript with LangGraph.js. The Python split is recommended because the agent, STT, and system tools are cleaner in Python.

---

## 2. Tech stack

| Concern | Choice | Notes |
|---|---|---|
| UI shell / overlay | Electron + `electron-builder` | Transparent, click-through, always-on-top window |
| Global hotkey | Electron `globalShortcut` | `Ctrl+Shift+Space` (Win) / `Cmd+Shift+Space` (mac) |
| Screenshot | Python `mss` | Fast, cross-platform. macOS needs Screen Recording permission |
| Audio capture | Python `sounddevice` | Cross-platform mic capture |
| Speech-to-text | `faster-whisper` (local) | Push-to-talk first; wake-word later |
| Backend server | FastAPI + `uvicorn` | Streams status + tokens over WebSocket |
| **Agent orchestration** | **LangGraph** (`create_react_agent` or custom `StateGraph`) | ReAct loop, conditional tool routing, checkpointer for memory, interrupts for confirmations |
| Model layer | LangChain chat models (`ChatAnthropic`, `ChatOpenAI`) | One interface for Claude, GPT, local; `bind_tools` + streaming + vision |
| Web search tool | Tavily (`langchain-tavily`) | Text answers. Needs `TAVILY_API_KEY` |
| Browser tools | `webbrowser` (open/search) + Playwright (read/drive) | Playwright is cross-platform Chromium automation |
| **System tools** | stdlib `subprocess`/`os`; optional `AppOpener` (Windows) | Launch apps, open files, walk folders |
| Local doc search | filename walk + text grep (MVP) → FAISS/Chroma embeddings (upgrade) | Semantic "search my docs" is a RAG upgrade path |
| Local models | Ollama | OpenAI-compatible endpoint at `localhost:11434/v1` |

---

## 3. Cross-platform requirements

### Overlay window
- Both: `transparent`, `frame:false`, `alwaysOnTop`, `skipTaskbar`, `hasShadow:false`, no `backgroundColor`.
- macOS: `win.setAlwaysOnTop(true, "screen-saver")` to float above full-screen apps.
- Click-through on both: `win.setIgnoreMouseEvents(true, { forward: true })`; toggle off on hover of controls.

### Screen-capture exclusion
- `win.setContentProtection(true)` on both (macOS `NSWindowSharingNone`; Windows `WDA_EXCLUDEFROMCAPTURE`, needs Win10 2004+). **User toggle, default OFF.**

### Opening files, apps & URLs
This is the main OS-specific surface for the system tools:
- **Open file / URL with default app:** macOS `subprocess.run(["open", target])`; Windows `os.startfile(target)`; Linux `xdg-open`.
- **Launch app by name:** macOS `open -a "AppName"` (reliable). Windows has no clean built-in — use the optional `AppOpener` package or a small name→path map; expect this to be the flakiest tool on Windows and surface failures to the user.
- **Browser (Playwright):** cross-platform; one-time `playwright install chromium`. The `open_url`/search tools use stdlib `webbrowser` and need no install.

### Permissions
- **macOS:** Screen Recording (for `mss`), Microphone, possibly Accessibility (hotkeys). Detect missing Screen Recording on first launch (capture returns black frames until granted).
- **Windows:** Microphone permission via Settings. No special screen-capture permission.

### Packaging
- `electron-builder`: `dmg`/`zip` (macOS), `nsis` (Windows). Bundle the Python backend via PyInstaller as a sidecar (Phase 6).

---

## 4. Project structure

```
onscreen-agent/
├── package.json
├── .env.example
├── electron/
│   ├── main.js          # BrowserWindow, globalShortcut, spawns + connects to backend
│   ├── preload.js
│   ├── overlay.html     # status line + answer area
│   └── renderer.js      # WebSocket client; renders status events + streaming tokens
└── backend/
    ├── requirements.txt
    ├── server.py        # FastAPI + /ws; drives the agent, streams out, confirmation gate
    ├── router.py        # get_model(): LangChain chat model per provider (§5)
    ├── agent.py         # LangGraph ReAct agent: binds tools, streams (§6)
    ├── tools.py         # web / browser / system tools (§6)
    ├── capture.py       # screenshot (mss) + audio (sounddevice)
    └── stt.py           # faster-whisper transcription
```

---

## 5. Model router (`backend/router.py`)

Return LangChain chat models so the agent can bind tools uniformly. Keys read from env.

```python
from langchain_core.language_models.chat_models import BaseChatModel

def get_model(name: str) -> BaseChatModel:
    if name == "claude":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model="claude-sonnet-5", max_tokens=1024)
    if name == "gpt":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o")
    if name == "local":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="llama3.2-vision", api_key="ollama",
                          base_url="http://localhost:11434/v1")
    raise ValueError(f"unknown provider: {name}")
```

Build the initial user turn as a multimodal message so the screenshot rides along:

```python
import base64
from typing import Optional
from langchain_core.messages import HumanMessage

def build_message(instruction: str, screenshot_png: Optional[bytes]) -> HumanMessage:
    content = [{"type": "text", "text": instruction}]
    if screenshot_png:
        b64 = base64.standard_b64encode(screenshot_png).decode()
        content.append({"type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"}})
    return HumanMessage(content=content)
```

> Model IDs drift and LangChain's multimodal block format varies by version — verify both against the versions you pin.

---

## 6. Agent, tools & guardrails (`backend/agent.py` + `backend/tools.py`)

### 6a. Web + browser tools

```python
from urllib.parse import quote_plus
import webbrowser
from langchain_core.tools import tool

@tool
def web_search(query: str) -> str:
    """Search the web and return a text answer with sources (use when you need facts)."""
    from langchain_tavily import TavilySearch
    return str(TavilySearch(max_results=5).invoke(query))

@tool
def open_website(query: str) -> str:
    """Open a website in the browser. `query` may be a full URL or a known name
    (youtube, netflix, gmail, github). Use for 'open Netflix' / 'open YouTube'."""
    sites = {"youtube": "https://youtube.com", "netflix": "https://netflix.com",
             "gmail": "https://mail.google.com", "github": "https://github.com"}
    url = sites.get(query.lower().strip()) or (query if query.startswith("http") else f"https://{query}")
    webbrowser.open(url)
    return f"Opened {url}"

@tool
def google_search(query: str) -> str:
    """Open Google results for `query` in the browser (visual results, not a text answer)."""
    webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
    return f"Opened Google results for: {query}"

@tool
def youtube_search(query: str) -> str:
    """Open YouTube search results for `query` in the browser."""
    webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
    return f"Opened YouTube results for: {query}"

@tool
def browse(url: str, task: str) -> str:
    """Navigate a real browser to `url` and return page text relevant to `task`.
    Use to READ a page, not just open it. Playwright/Chromium."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        page = b.new_page(); page.goto(url, wait_until="domcontentloaded")
        text = page.inner_text("body"); b.close()
    return text[:4000]
```

### 6b. System tools (allowlisted, read/open-only)

```python
import os, sys, subprocess
from pathlib import Path

# Configurable via ALLOWED_DIRS; defaults to the user's doc folders. NEVER the whole disk.
ALLOWED_ROOTS = [Path.home() / d for d in
                 os.getenv("ALLOWED_DIRS", "Documents,Downloads,Desktop").split(",")]

def _allowed(p: Path) -> bool:
    p = p.expanduser().resolve()
    return any(str(p).startswith(str(r.resolve())) for r in ALLOWED_ROOTS)

@tool
def launch_app(name: str) -> str:
    """Launch a desktop application by name, e.g. 'Spotify', 'Calculator', 'Notes'."""
    try:
        if sys.platform == "darwin":
            subprocess.run(["open", "-a", name], check=True)
        elif sys.platform == "win32":
            from AppOpener import open as app_open          # pip install AppOpener
            app_open(name, match_closest=True, throw_error=True)
        else:
            subprocess.run([name.lower()], check=True)
        return f"Launched {name}"
    except Exception as e:
        return f"Could not launch {name}: {e}"

@tool
def open_file(path: str) -> str:
    """Open a file with its default app. Only files inside the allowed folders."""
    p = Path(path).expanduser()
    if not _allowed(p):  return "Refused: path is outside the allowed folders."
    if not p.exists():   return f"No such file: {p}"
    if sys.platform == "darwin":   subprocess.run(["open", str(p)])
    elif sys.platform == "win32":  os.startfile(str(p))       # type: ignore[attr-defined]
    else:                          subprocess.run(["xdg-open", str(p)])
    return f"Opened {p.name}"

@tool
def find_files(name_query: str, subfolder: str = "") -> str:
    """Find files by NAME within the allowed folders. Returns up to 25 paths."""
    hits = []
    for root in ALLOWED_ROOTS:
        base = (root / subfolder) if subfolder else root
        if not _allowed(base) or not base.exists(): continue
        for p in base.rglob("*"):
            if p.is_file() and name_query.lower() in p.name.lower():
                hits.append(str(p))
                if len(hits) >= 25: return "\n".join(hits)
    return "\n".join(hits) or "No matching files."

@tool
def search_documents(text_query: str, subfolder: str = "") -> str:
    """Search INSIDE text-based docs (.txt .md .csv .py .json .log) for `text_query`.
    Returns file:line matches. For PDFs/Word or semantic search, see the RAG note."""
    exts, out = {".txt", ".md", ".csv", ".py", ".json", ".log"}, []
    for root in ALLOWED_ROOTS:
        base = (root / subfolder) if subfolder else root
        if not _allowed(base) or not base.exists(): continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in exts:
                try:
                    for i, line in enumerate(p.read_text(errors="ignore").splitlines(), 1):
                        if text_query.lower() in line.lower():
                            out.append(f"{p.name}:{i}: {line.strip()[:120]}")
                            if len(out) >= 25: return "\n".join(out)
                except Exception: pass
    return "\n".join(out) or "No matches in documents."
```

### 6c. The agent (`backend/agent.py`)

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from router import get_model
from tools import (web_search, open_website, google_search, youtube_search, browse,
                   launch_app, open_file, find_files, search_documents)

SYSTEM = (
    "You are an on-screen desktop assistant. You can see the user's screen via a "
    "screenshot on their message. Answer directly when you can. Use web_search for "
    "facts; open_website/google_search/youtube_search to open things in the browser; "
    "browse to read a page; launch_app to open apps; open_file/find_files/"
    "search_documents to work with local files (limited to allowed folders). "
    "Keep answers concise for an overlay."
)

# Side-effecting tools get a confirmation gate (see §6d).
ACTION_TOOLS = ["launch_app", "open_file", "open_website"]

def build_agent(provider: str):
    tools = [web_search, open_website, google_search, youtube_search, browse,
             launch_app, open_file, find_files, search_documents]
    return create_react_agent(get_model(provider), tools=tools,
                              checkpointer=MemorySaver(), prompt=SYSTEM)
```

### 6d. Guardrails (build these in, don't defer)
- **Filesystem allowlist.** `open_file` / `find_files` / `search_documents` only touch `ALLOWED_DIRS` (default Documents, Downloads, Desktop). Never the whole disk or system paths. Paths outside are refused, not clamped.
- **Read/open-only.** No delete, move, or write tools in v1. Keep it that way — it removes the worst failure modes.
- **Prompt-injection gate.** The `browse` tool feeds untrusted web text into the loop; a malicious page could tell the agent to open files or launch apps. Mitigate with a human-in-the-loop confirmation before any tool in `ACTION_TOOLS` — compile the graph with `interrupt_before=["tools"]` (or a custom `ToolNode` that checks the tool name), pause, ask the user via the overlay ("Open /path/resume.pdf? y/n"), and resume from the checkpointer. Always gate action tools when the same turn already called `browse`.
- **Streaming still applies.** Emit a status event per tool call so the user sees what the agent is about to do before it happens.

### 6e. Streaming (in `server.py`)
Use `stream_mode=["updates", "messages"]`: `updates` → emit `{"type":"status", "text":"Using <tool>…"}` from tool calls (and pause for confirmation on action tools); `messages` → stream final answer tokens as `{"type":"token"}`.

> **Local models + tools:** reliable on Claude/GPT, weak on local vision models — and vision+tools together is weakest locally. Let the `local` provider degrade gracefully and say so in the UI.
>
> **Document search upgrade (your RAG lane):** replace `search_documents`' grep with a local embedding index (chunk Documents → embeddings → FAISS/Chroma) for semantic "find my notes about X" across PDFs and Word docs. MVP is grep; this is the natural v2.

---

## 7. Build phases

### Phase 0 — Spine (no UI, no tools)
Hotkey → `mss` screenshot → `get_model("claude")` → stream to stdout via `build_message`.
- **Acceptance:** hotkey prints a streaming answer about what's on screen.

### Phase 1 — Overlay
FastAPI `/ws` streams tokens; Electron overlay (§3) renders them.
- **Acceptance:** a floating, click-through panel types the answer over any focused app, both OSes.

### Phase 2 — Voice
Push-to-talk via `sounddevice`, transcribe with `faster-whisper`.
- **Acceptance:** holding the voice hotkey and speaking a request produces an overlay answer.

### Phase 3 — Agent + web/browser tools (LangGraph)
Wrap the model in `create_react_agent` with `web_search`, `open_website`, `google_search`, `youtube_search`, `browse`. Stream status + tokens.
- **Acceptance:** "search the web for X and summarise" shows a status line then a grounded answer; "open YouTube and search lofi" and "google the weather" open the browser correctly; multi-turn memory works via the checkpointer.

### Phase 4 — System actions + guardrails
Add `launch_app`, `open_file`, `find_files`, `search_documents` with the §6b allowlist and the §6d confirmation gate.
- **Acceptance:** "open Netflix" / "open Spotify" / "open my resume" / "find files about invoices" / "search my notes for the API key" all work within allowed folders; a request to open anything outside those folders is refused; action tools prompt for confirmation before executing.

### Phase 5 — Provider switching
Tray/settings to pick `claude` / `gpt` / `local`, rebuilding the agent. Persist choice + keys.
- **Acceptance:** switching provider mid-session changes the model with no restart; local degrades gracefully on tool tasks.

### Phase 6 — Polish & packaging
Wake-word (Porcupine), content-protection toggle (default OFF), macOS permission check, PyInstaller sidecar, `electron-builder` installers.
- **Acceptance:** installable `.dmg` and `.exe` that auto-launch the backend, no terminal.

---

## 8. Configuration (`.env.example`)

```
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
TAVILY_API_KEY=
DEFAULT_PROVIDER=claude              # claude | gpt | local
BACKEND_PORT=8765
CAPTURE_HOTKEY=CmdOrCtrl+Shift+Space
VOICE_HOTKEY=CmdOrCtrl+Shift+V
CONTENT_PROTECTION=false
ALLOWED_DIRS=Documents,Downloads,Desktop   # folders the file tools may touch
CONFIRM_ACTIONS=true                        # human-in-the-loop for launch/open tools
```

`CmdOrCtrl` resolves to Cmd on macOS and Ctrl on Windows.

---

## 9. Out of scope (for now)
- Destructive file operations (delete, move, overwrite) — read/open-only in v1.
- Full autonomous multi-step app/browser control (clicking through flows, form-filling). Phase 4 opens and searches; a `browser-use`-style sub-agent is a later extension.
- Feeding fresh mid-loop screenshots back to the model (multimodal ToolMessage) — deferred.
- Semantic document index (embeddings/RAG) — grep MVP now, vector index later.
- Proctoring/exam evasion. Content-protection defaults off.
- Cloud sync, accounts, TTS output.

---

## 10. First tasks for Claude Code
1. Scaffold §4 with `package.json`, `.env.example`, and `requirements.txt` including: `langgraph`, `langchain-anthropic`, `langchain-openai`, `langchain-tavily`, `playwright`, `AppOpener` (Windows only), `mss`, `sounddevice`, `faster-whisper`, `fastapi`, `uvicorn`.
2. Implement `router.py` (§5) and `tools.py` (§6a–6b).
3. Complete **Phase 0** end to end before writing overlay or agent-graph code.
4. Then implement `agent.py` (§6c), the confirmation gate (§6d), and `/ws` streaming (§6e), satisfying each phase's acceptance criteria in order.
