# OnCUE feature guide

Desktop flows inspired by **Parakeet** (web session → desktop deep link, screen-share privacy) and **Clicky** (push-to-talk hotkeys, tray-first settings, per-feature tutorials).

## Connect (hosted)

1. Sign in at your OnCUE dashboard.
2. Click **Open OnCUE app** — fills license key, website URL, RAG URL, and LiteLLM backend via `oncue://connect`.
3. Or: tray → **Settings** → **OnCUE hosted** → paste manually.

## Settings sections

| Section | What it controls |
|---------|------------------|
| **Quick start** | Hotkey cheat sheet + link to in-app feature guide |
| **AI provider** | `hosted`, `groq`, `claude`, `gpt`, `gemini` |
| **API keys** | BYO provider keys + Tavily web search |
| **OnCUE hosted** | Backend URL, website URL, RAG URL, license key, model alias, trial status |
| **Speech** | Language (Hinglish/Hindi/English), STT backend, Groq/local models |
| **Behavior** | All hotkeys, allowed folders, browser, screen-share hiding, system tools |

## Hotkeys (default)

| Hotkey | Action |
|--------|--------|
| `Ctrl+Shift+Space` | Screen Q&A (screenshot + question) |
| `Ctrl+Shift+H` | Chat without screenshot |
| `Ctrl+Shift+V` (hold) | Voice about screen |
| `Ctrl+Shift+D` (hold) | Dictate at cursor |
| `Ctrl+Shift+M` (hold) | Meeting audio capture |

## Tray menu

- Ask about my screen
- Show overlay
- Settings…
- Feature guide…
- Reset overlay position
- Speak answers aloud
- Hide from screen sharing
- Allow system actions
- Pause agent (5 / 15 / 30 min)
- Quit

## Record a settings tour (dev)

```bash
bash scripts/record_gui_settings_tour.sh
```

## Automated tests

```bash
.venv/bin/pytest tests/test_settings_dialog.py -v
```
