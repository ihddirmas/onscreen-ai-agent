# OnCUE — User Guide

Everything in one place: how to run, every key, every feature, every setting.

---

## ▶ Run

```powershell
cd c:\Users\yasht.ASUS\OneDrive\Desktop\hackthon\OnCUE.ai
python -m oncue
```

- Nothing visibly opens — look for the **green O icon in the system tray**
  (bottom-right corner; click `^` if collapsed). The overlay appears on hotkey.
- Detached (no terminal window):
  `Start-Process python -ArgumentList "-m","oncue" -WindowStyle Hidden`
- Terminal smoke test (no GUI): `python -m oncue.spine --now`

## ⏹ Close

- **Normal:** right-click the green O tray icon → **Quit**
- From a terminal that's running it: `Ctrl+C`
- Stuck / can't find the icon: `Get-Process python | Stop-Process -Force`

⚠ **Don't run it twice** — two instances fight over the same hotkeys.
If hotkeys fire twice, kill everything with the command above and start once.

---

## ⌨ Hotkeys

| Key | Hold or press | What it does |
|---|---|---|
| **Ctrl + Shift + Space** | press | **Auto-solve the screen** — screenshots and *immediately* figures it out: coding problem → solution, topic → explanation, question → answer. You type nothing. Then type follow-ups ("explain more", "in Hindi") — it still sees the screen. |
| **Ctrl + Shift + V** *or* **Ctrl + Shift + M** | **hold** while speaking / during a call | **Listen** — captures **your mic AND all system/call audio at the same time**, then answers. Works for a spoken question, a Meet/Zoom call, a YouTube video — anything you hear. Both keys do the same thing. Release → it answers; then keep asking by typing. No audio caught? The box opens so you can type. |
| **Ctrl + Shift + H** | press (toggles) | **Chat mode** — plain AI chat, no screen, no audio. Press again to hide. |
| **Ctrl + Shift + D** | **hold** while speaking | **Dictation** (Wispr Flow): click into any text box first (WhatsApp, ChatGPT, search bar), speak, release → text is pasted at your cursor. You press Enter. |
| **Esc** | press (overlay focused) | Hide the overlay |

**One interface for voice + text:** voice (V), call audio (M), and screenshot
(Space) all answer in the same overlay, and after every answer an input box
appears so you can keep asking by **typing** — no need to press a hotkey again.
Only the screenshot hotkey looks at your screen; voice and chat are screen-free.

**Overlay window:** drag it anywhere by its title/background. **Resize** by
dragging the right edge, bottom edge, or bottom-right corner (the cursor
changes to arrows near an edge; there's also a ◢ grip). Position and size are
remembered across restarts. Tray menu → *Reset overlay position* restores the
top-right default.

**Allow / Deny buttons** appear whenever the agent wants to open an
app/file/website — nothing side-effecting runs without your click.

---

## 🛡 Hidden from screen sharing

OnCUE's overlay is **invisible in any screen share or recording** — Zoom,
Google Meet, Teams, Discord, OBS, PowerPoint, PrintScreen. You still see it on
your own monitor; whoever you're sharing with does not. It works for any app or
website because it's done at the Windows compositor level
(`WDA_EXCLUDEFROMCAPTURE`, Windows 10 2004+).

- **On by default.** Toggle it from the tray → **"Hide from screen sharing"**,
  or Settings, or `.env` (`CONTENT_PROTECTION`).
- **To show OnCUE in a demo/recording** (e.g. your hackathon presentation),
  turn it **off** first.
- **Limit:** it can't hide from a physical camera pointed at your screen.

## 🔒 Turning off system actions

By default OnCUE can open apps, files, and the browser and search your local
files (always behind an Allow/Deny prompt). To switch that off:

- **In the overlay:** untick the **"System actions (apps · files · browser)"**
  checkbox at the bottom. Now OnCUE only answers and searches the web — it
  can't touch your computer.
- **Tray icon:** toggle **"Allow system actions"**, or **"Pause system actions →
  for 15 / 30 / 60 minutes"** to disable it temporarily (it re-enables itself
  automatically).
- **Settings / `.env`:** `SYSTEM_TOOLS_ENABLED=false`.

## 🧠 What you can ask (agent features)

| Say / type | What happens | Needs |
|---|---|---|
| "what's on my screen?" / "solve this" | Vision answer directly | nothing |
| "search the web for X" / any current-info question | Real web results with sources (keyless DuckDuckGo, ~3–4s) | nothing — works out of the box. Add a `TAVILY_API_KEY` for higher-quality results if you want |
| "open youtube and search lofi" | Opens results in your browser | Allow click |
| "google the weather in Delhi" | Opens Google results | nothing |
| "read this article: <url>" | Fetches page text into the answer | `pip install playwright` + `playwright install chromium` |
| "open spotify" / "open calculator" | Launches the app | Allow click |
| "find my files about resume" | Filename search in allowed folders | nothing |
| "search my notes for X" | Text search inside documents | nothing |
| "open my resume" | Opens the file | Allow click |

Multi-turn works: follow up with "ab usko Hindi mein samjhao" etc.

**Hinglish is the default speech language** — speak naturally ("kal ka
weather check karo") and it transcribes to Roman Hinglish. Speech recognition
runs on Groq's `whisper-large-v3-turbo` (fast + accurate) and falls back to a
local model when offline.

---

## 🔑 Configuration keys

Edit `.env` in the project folder, or use tray → **Settings…** (same knobs).

| Key | Default | Meaning |
|---|---|---|
| `DEFAULT_PROVIDER` | `groq` | Brain: `groq` (free) / `claude` / `gpt` / `hosted` (license key, production) |
| `GROQ_API_KEY` | — | Free key from console.groq.com — chat **and** voice recognition |
| `GROQ_MODEL` | `qwen/qwen3.6-27b` | Only vision-capable model on Groq's free tier right now |
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` | — | Only for `claude` / `gpt` providers |
| `CLAUDE_MODEL` / `GPT_MODEL` | `claude-opus-4-8` / `gpt-4o` | Model overrides |
| `TAVILY_API_KEY` | — | Optional — upgrades web_search to Tavily quality. Web search works keyless (DuckDuckGo) without it. |
| `ONCUE_BACKEND_URL` / `ONCUE_TOKEN` / `HOSTED_MODEL` | — | Hosted mode (deployed `backend/` LiteLLM proxy) |
| `CAPTURE_HOTKEY` | `<ctrl>+<shift>+<space>` | Rebindable (pynput syntax) |
| `CHAT_HOTKEY` | `<ctrl>+<shift>+h` | Chat mode (no screenshot); press again to hide |
| `VOICE_HOTKEY` | `<ctrl>+<shift>+v` | Rebindable |
| `DICTATE_HOTKEY` | `<ctrl>+<shift>+d` | Rebindable |
| `MEETING_HOTKEY` | `<ctrl>+<shift>+m` | Hold: record system audio + mic, then ask |
| `STT_LANGUAGE` | `hinglish` | `hinglish` (Roman) / `hindi` (देवनागरी) / `english` / `auto` |
| `STT_BACKEND` | `auto` | `auto` (Groq cloud when key set) / `groq` / `local` (offline/private) |
| `GROQ_STT_MODEL` | `whisper-large-v3` | `whisper-large-v3` = most accurate (best for Hindi/Hinglish); `whisper-large-v3-turbo` = faster |
| `WHISPER_MODEL` | `small` | Local fallback model: `base` / `small` / `medium` |
| `PREFERRED_BROWSER` | `default` | `default` / `chrome` / `edge` / `firefox` / `brave` / path to a browser .exe |
| `ALLOWED_DIRS` | `Documents,Downloads,Desktop` | The ONLY folders file tools may touch |
| `CONFIRM_ACTIONS` | `true` | The Allow/Deny gate — keep on |
| `SYSTEM_TOOLS_ENABLED` | `true` | Allow opening apps/files/browser + file search. Toggle in overlay/tray. |
| `CONTENT_PROTECTION` | `true` | Hide the overlay from screen shares/recordings. Toggle in tray/Settings. |
| `OVERLAY_GEOMETRY` | — | Saved overlay position/size (managed automatically; delete the line to reset) |

Settings saved from the dialog live in `%APPDATA%\OnCUE\config.env`.

---

## ⚠ Known limits & troubleshooting

- **Groq free tier: 8,000 tokens/minute.** 2–3 rapid screenshot questions can
  hit it — the overlay shows "wait about a minute". It recovers by itself.
- **First local-whisper use** (offline fallback only) downloads ~250 MB.
- **"Didn't catch that"** = silence gate — no speech energy detected, or the
  transcript looked like a hallucination. Speak a little louder/longer.
- **Model not found error** → Groq rotated its catalog again. List models at
  console.groq.com and update `GROQ_MODEL` in `.env`.
- **Hotkeys stop working** → probably two instances running. Kill all python
  processes and start once.

---

## 📦 Build the .exe (distribution)

```powershell
pip install pyinstaller
pyinstaller packaging/oncue.spec     # → dist/OnCUE.exe
```

For end users without API keys: deploy `backend/` (LiteLLM proxy — see
comments in `backend/litellm-config.yaml`), issue license keys, and users pick
provider `hosted` in Settings.
