# AGENTS.md

## Cursor Cloud specific instructions

### Repo layout

Monorepo with three independent subprojects (no root `package.json`):

| Path | Stack | Purpose |
|------|-------|---------|
| `oncue/` | Python 3.10+ (PySide6, LangGraph) | Desktop on-screen AI agent |
| `website/` | Next.js 14 + npm | Auth, dashboard, document RAG portal |
| `backend/` | LiteLLM (Docker) | Hosted-mode model proxy |

See `README.md` (desktop), `website/README.md` (web), and `DEPLOY.md` (full hosted stack).

### One-time VM system packages

The desktop app needs native build/runtime libs that are **not** installed by the update script:

```bash
sudo apt-get install -y python3.12-venv python3-dev build-essential libegl1 libgl1
```

### Python (desktop app)

Use the repo-local venv (`.venv/` is gitignored):

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
cp .env.example .env   # add GROQ_API_KEY for dev (console.groq.com)
```

Activate for interactive work: `source .venv/bin/activate`

**Smoke tests (no GUI):**

```bash
# Screenshot pipeline (needs Xvfb in headless Linux)
xvfb-run -a .venv/bin/python -c "from oncue.capture import screenshot_png; print(len(screenshot_png()))"

# Full spine: screenshot → Groq → stdout (requires GROQ_API_KEY in .env)
xvfb-run -a .venv/bin/python -m oncue.spine --now
```

The full tray/overlay app (`python -m oncue`) targets Windows/macOS and is not practical to run in this Linux cloud VM.

### Website (Next.js)

```bash
cd website
cp .env.local.example .env.local   # fill Supabase + LiteLLM for auth/dashboard
npm install
npm run dev      # http://localhost:3000
npm run build    # production build + typecheck (no separate test suite)
```

`npm run lint` prompts for ESLint setup on a fresh clone; `npm run build` already type-checks. Landing page (`/`) works with placeholder `.env.local`; login/dashboard need real Supabase credentials.

### Backend (LiteLLM)

Optional for full hosted E2E. Requires Docker and external Postgres (`DATABASE_URL`, often Supabase). See `DEPLOY.md` and `backend/Dockerfile`. Not needed for desktop-only dev with `DEFAULT_PROVIDER=groq`.

### Secrets for meaningful E2E

| Secret | Used by |
|--------|---------|
| `GROQ_API_KEY` | Desktop dev (`oncue.spine`, default provider) |
| `NEXT_PUBLIC_SUPABASE_*`, `SUPABASE_SERVICE_ROLE_KEY` | Website auth + RAG |
| `LITELLM_URL`, `LITELLM_MASTER_KEY` | Website key minting + credits |

### Gotchas

- `pip install -e .` on bare Ubuntu fails without `python3.12-venv` and `python3-dev` (for `evdev` / `pynput`).
- PySide6 screenshot downscaling needs `libegl1` on Linux; use `xvfb-run` when no real display is available.
- Do not commit `.env` or `website/.env.local` (gitignored).
- Do **not** `source .env` in bash — hotkey values like `<ctrl>+<shift>+<space>` break shell parsing. OnCUE reads `.env` via its own parser; export only the vars you need (e.g. `export GROQ_API_KEY=...`).
