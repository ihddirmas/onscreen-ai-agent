# 🦜 Parakeet.ai

An on-screen AI agent for Windows/macOS: press a hotkey (or hold the voice
hotkey and speak), Parakeet screenshots your screen and runs a tool-using
agent — web search, opening sites/apps/files, searching your documents — then
streams the answer onto a transparent always-on-top overlay.

Pure Python. One process. No Electron.

## Quick start (dev)

```bash
# Python 3.10+
pip install -e .
copy .env.example .env        # then put your free Groq key in it (console.groq.com)
python -m parakeet.spine --now   # phase-0 smoke test: screenshot -> Groq -> stdout
python -m parakeet               # full app: tray icon + overlay + hotkeys
```

Default hotkeys:

| Hotkey | Action |
|---|---|
| `Ctrl+Shift+Space` | Capture & ask — type your question, Enter (empty = "describe my screen") |
| hold `Ctrl+Shift+V` | Push-to-talk: speak a command about your screen |
| hold `Ctrl+Shift+D` | **Dictation** (Wispr Flow style): cursor in any text box — browser, ChatGPT, WhatsApp — speak, release, and the text is pasted at your cursor. You press Enter. |

First voice use downloads the whisper `small` model (~250 MB).

**Hinglish built in:** speech defaults to Roman Hinglish output — say
"kal ka weather check karo" and that's what gets typed/understood. Switch to
Hindi (देवनागरी), English, or auto-detect in Settings.

Optional: `pip install playwright && playwright install chromium` enables the
`browse` (read-a-webpage) tool. A `TAVILY_API_KEY` enables `web_search`.

## Providers

| Provider | Model | Who it's for |
|---|---|---|
| `groq` (default) | Llama 4 Scout — free tier, vision + tools | dev/testing |
| `claude` | `claude-opus-4-8` | production, BYO key |
| `gpt` | `gpt-4o` | production, BYO key |
| `hosted` | whatever our backend maps `parakeet-default` to | end users — **no provider key needed** |

Switch in the tray → Settings dialog; takes effect immediately.

## Hosted mode (how shipped exes connect)

The exe never contains API keys. It talks to our LiteLLM proxy
(`backend/litellm-config.yaml` + `backend/Dockerfile`), which holds the real
provider keys, issues per-user license keys with budgets, and maps the
`parakeet-default` alias to Groq today / Claude-GPT at production — a
server-side switch, no app update. Users paste their license key in Settings.

## Guardrails

- File tools only touch `ALLOWED_DIRS` (Documents/Downloads/Desktop by
  default) — never the whole disk. Read/open-only; no delete/move/write.
- Opening apps/files/websites requires an Allow/Deny confirmation on the
  overlay (also the prompt-injection defense for the `browse` tool).

## Build the exe

```bash
pip install pyinstaller
pyinstaller packaging/parakeet.spec
# -> dist/Parakeet.exe
```

## Repo layout

```
parakeet/            the app (UI, hotkeys, capture, voice, agent)
├── agent/           router (providers), tools, LangGraph agent, Qt worker
├── ui/              overlay + settings dialog
└── spine.py         phase-0 CLI smoke test
backend/             hosted-mode LiteLLM proxy (Docker)
packaging/           PyInstaller spec
onscreen-agent-plan.md   original build brief
```
