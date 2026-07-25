# Parakeet — Deployment runbook

Deploy in this order. Each step produces a value the next one needs. Put
everything in the **same cloud region** for low latency.

Components:
- **Supabase** — database, auth, document storage, free embeddings (edge fn)
- **LiteLLM** on Render — model gateway (holds provider keys, per-user keys, spend)
- **Website** on Vercel — accounts, pricing, dashboard, uploads
- **Desktop app** — the client users install

---

## 1. Supabase (do this first)

1. Create a project at [supabase.com](https://supabase.com). Note the **region**.
2. **SQL Editor → New query →** paste all of `website/supabase/schema.sql` → Run.
   (Creates tables, pgvector, the `match_doc_chunks` function, RLS, and the
   `documents` storage bucket.)
3. **Deploy the `rag` edge function** (free `gte-small` embeddings + search).
   Pick ONE:

   **Option A — Dashboard, no CLI (easiest):**
   - Edge Functions → **Create a function** → name it `rag`.
   - Paste the code from `website/supabase/functions/rag/index.ts`.
   - Turn **Verify JWT = OFF** for this function → Deploy.
   - Edge Functions → **Secrets** → add:
     - `EMBED_SECRET` = a long random string (remember it — the website needs the same value)
     - `SUPABASE_SERVICE_ROLE_KEY` = Settings → API → `service_role` key

   **Option B — CLI:** Supabase has **no** global npm install. Use `npx` (you
   already have Node), or Scoop, or the release binary
   ([github.com/supabase/cli/releases](https://github.com/supabase/cli/releases)).
   From the `website/` folder:
   ```
   npx supabase login
   npx supabase link --project-ref <ref>
   npx supabase functions deploy rag --no-verify-jwt
   npx supabase secrets set EMBED_SECRET=<random> SUPABASE_SERVICE_ROLE_KEY=<service-role>
   ```

4. **Enable Google login (optional):** Auth → Providers → Google.
5. **Collect (Settings → API / General / Database):**
   - `Project URL`  ·  `anon` key  ·  `service_role` key
   - `Reference ID` (the `<ref>`)  ·  Postgres **Connection string** (for LiteLLM)

---

## 2. LiteLLM on Render

Render **builds the Docker image from `backend/Dockerfile`** — you do not build
or upload an image.

1. Render → **New + → Blueprint** → connect this repo. It reads
   `backend/render.yaml` and creates the `parakeet-litellm` web service.
   (Or: New Web Service → repo → **root dir `backend`**, runtime **Docker**.)
2. Set env vars:
   - `GROQ_API_KEY` = your Groq key
   - `LITELLM_MASTER_KEY` = a strong `sk-master-…` (the blueprint can auto-generate)
   - `DATABASE_URL` = **reuse Supabase's Postgres connection string** (no separate DB)
   - optional: `ANTHROPIC_API_KEY` / `OPENAI_API_KEY`
3. Deploy. **Collect:** the service URL (e.g. `https://parakeet-litellm.onrender.com`).
4. Smoke-test (replace URL + master key):
   ```
   # mint a test key
   curl -X POST https://<render-url>/key/generate \
     -H "Authorization: Bearer <LITELLM_MASTER_KEY>" -H "Content-Type: application/json" \
     -d '{"models":["parakeet-default"],"max_budget":1,"duration":"30d"}'
   # use it — should return a real answer
   curl https://<render-url>/v1/chat/completions \
     -H "Authorization: Bearer <the-key-from-above>" -H "Content-Type: application/json" \
     -d '{"model":"parakeet-default","messages":[{"role":"user","content":"hi"}]}'
   ```
   > The model is `groq/qwen/qwen3.6-27b` (current). The old llama-4-scout was retired.

---

## 3. Website on Vercel

1. Import the repo into Vercel → **root directory `website`** (same region as Supabase).
2. Environment variables:
   ```
   NEXT_PUBLIC_SUPABASE_URL       = Supabase Project URL
   NEXT_PUBLIC_SUPABASE_ANON_KEY  = Supabase anon key
   SUPABASE_SERVICE_ROLE_KEY      = Supabase service_role key
   EMBED_SECRET                   = same string as the Supabase secret
   LITELLM_URL                    = the Render URL
   LITELLM_MASTER_KEY             = from step 2
   NEXT_PUBLIC_SITE_URL           = your Vercel URL (e.g. https://parakeet.vercel.app)
   ```
3. Deploy. **Collect:** the live site URL.
4. Supabase → **Auth → URL Configuration** → add the site URL to the redirect allow-list.

---

## 4. Keep-warm (optional, lowest latency)

Add a Supabase scheduled job (pg_cron or a scheduled function) that pings the
`rag` function every ~5 min so the first document search isn't a cold start. Free.

---

## 5. Desktop app

- **For users:** they sign up on the site and click **"Open Parakeet app"** — the
  `parakeet://` link injects their key + your URLs automatically (hosted mode).
- **For your own testing:** in the app's Settings set provider `hosted`,
  `PARAKEET_BACKEND_URL` = Render URL, `PARAKEET_WEB_URL` = site URL,
  `PARAKEET_RAG_URL` = `<supabase-url>/functions/v1/rag`, and paste a key.
- **Build the installer:** `pip install pyinstaller && pyinstaller packaging/parakeet.spec`
  → `dist/Parakeet.exe`. Host it (GitHub Releases / Supabase Storage) and point the
  website's `/download` button at it.

---

## End-to-end sanity check (once live)

Sign up → dashboard shows a minted key + 0% credit meter → upload a resume (goes
`ready`) → click "Open Parakeet app" → ask a question → answer streams on the
overlay, the credit meter ticks up, and "search my documents" grounds answers in
your upload.
