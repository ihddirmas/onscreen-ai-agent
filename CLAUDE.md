# OnCUE — AI Desktop Agent

## Project layout

- `oncue/` — Python 3.10+ desktop agent (PySide6, LangGraph)
- `website/` — Next.js 14 web portal (auth, dashboard, RAG)
- `webapp/` — Reflex (Python) web app (landing, login, payments, legacy)
- `backend/` — LiteLLM model proxy (Docker)

## Quick start

```bash
# Desktop (requires .env with GROQ_API_KEY)
python3 -m venv .venv && source .venv/bin/activate && pip install -e .
python -m oncue.spine --now     # headless smoke test

# Website
cd website && npm install && npm run dev

# Reflex webapp
cd webapp && pip install -r requirements.txt && reflex run
```

## Key files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Full dev environment reference |
| `DEPLOY.md` | Hosted stack deployment guide |
| `README.md` | Project overview |
| `pyproject.toml` | Python package config |

## Secrets

`GROQ_API_KEY` for desktop dev. Supabase + LiteLLM keys for website. See `AGENTS.md`.
