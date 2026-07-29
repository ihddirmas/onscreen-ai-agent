# Parakeet — Deployment runbook

Deploy in this order. Each step produces a value the next one needs. Put
everything in the **same cloud region** for low latency.

Components:
- **Supabase** — database, auth, document storage, free embeddings (edge fn)
- **LiteLLM** on Render — model gateway (holds provider keys, per-user keys, spend)
- **Webapp** on Render — Reflex app: accounts, pricing, dashboard, uploads, payments
- **Desktop app** — the client users install

---

## 1. Supabase (do this first)

1. Create a project at [supabase.com](https://supabase.com). Note the **region**.
2. **SQL Editor → New query →** paste all of `website/supabase/schema.sql` → Run.
   (Creates tables, pgvector, the `match_doc_chunks` function, RLS, and the
   `documents` storage bucket.)
3. **Run the payments schema** — `webapp/supabase/schema_payments.sql` in the same
   SQL editor (adds billing columns to `profiles` + the `payment_events` table).
4. **Deploy the `rag` edge function** (free `gte-small` embeddings + search).
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

5. **Enable Google login (optional):** Auth → Providers → Google.
6. **Collect (Settings → API / General / Database):**
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

## 3. Webapp on Render

The webapp is a Reflex app wrapped in a single Docker container with Caddy
(reverse proxy for the static frontend) + redis (production state backend).
The Stripe and Razorpay webhook routes live at `/api/webhooks/stripe` and
`/api/webhooks/razorpay` respectively.

1. **Create a Render Blueprint:**
   - Render → **New + → Blueprint** → connect this repo.
   - It reads `webapp/render.yaml` and creates the `oncue-webapp` service.
   - (Or: **New Web Service** → repo → root dir `webapp`, runtime **Docker**.)

2. **Set the 14 environment variables** in the Render dashboard (all `sync: false`,
   filled manually — never commit secrets):

   `SUPABASE_URL` · `SUPABASE_ANON_KEY` · `SUPABASE_SERVICE_ROLE_KEY` ·
   `SUPABASE_FUNCTIONS_URL` · `EMBED_SECRET` · `LITELLM_URL` ·
   `LITELLM_MASTER_KEY` · `STRIPE_SECRET_KEY` · `STRIPE_WEBHOOK_SECRET` ·
   `STRIPE_PRICE_ID_PRO` · `RAZORPAY_KEY_ID` · `RAZORPAY_KEY_SECRET` ·
   `RAZORPAY_WEBHOOK_SECRET` · `RAZORPAY_PLAN_ID_PRO`

   > **Tip:** Start with Stripe in test mode so you can verify the full
   > checkout flow without real charges. Same for Razorpay test mode.

3. Deploy. **Collect:** the service URL (e.g. `https://oncue-webapp.onrender.com`).

4. **Register webhooks** — this is the step most deployments miss. Both Stripe
   and Razorpay must send events to your live Render URL:

   **Stripe Dashboard → Developers → Webhooks → Add endpoint:**
   - Endpoint URL: `https://<your-url>/api/webhooks/stripe`
   - Events to listen for:
     - `checkout.session.completed`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
   - After creation, Reveal the **Signing secret** → paste into Render's
     `STRIPE_WEBHOOK_SECRET` env var and redeploy.

   **Razorpay Dashboard → Settings → Webhooks → Add webhook:**
   - URL: `https://<your-url>/api/webhooks/razorpay`
   - Events: `subscription.activated` + `subscription.cancelled`
   - After creation, copy the **Webhook Secret** → paste into Render's
     `RAZORPAY_WEBHOOK_SECRET` env var and redeploy.

5. Verify webhooks work:
   ```
   # Stripe test — should return 400 (bad signature), NOT 404
   curl -X POST https://<your-url>/api/webhooks/stripe
   # Razorpay test — should return 400
   curl -X POST https://<your-url>/api/webhooks/razorpay
   ```
   Then use Stripe's Dashboard "Send test webhook" and Razorpay's "Send test"
   feature to fire real events and confirm they produce a `200` + a new row
   in `payment_events`.

6. **Supabase Auth redirect:** In Supabase → Auth → URL Configuration, add
   `https://<your-url>` to the redirect allow-list (or the full path
   `https://<your-url>/login`).

> **Known tradeoff:** Render's free/starter plan cold-starts containers when
> idle. Acceptable for the hackathon submission window — add a keep-warm ping
> (e.g. a scheduled Supabase pg_cron job or a simple Uptime Robot monitor)
> in production.

---

## 4. Keep-warm (optional, lowest latency)

Add a Supabase scheduled job (pg_cron or a scheduled function) that pings the
`rag` function every ~5 min so the first document search isn't a cold start. Free.

---

## 5. Desktop app

- **For users:** they sign up on the site and click **"Open Parakeet app"** — the
  `parakeet://` link injects their key + your URLs automatically (hosted mode).
- **For your own testing:** in the app's Settings set provider `hosted`,
  `PARAKEET_BACKEND_URL` = LiteLLM Render URL,
  `PARAKEET_WEB_URL` = webapp Render URL,
  `PARAKEET_RAG_URL` = `<supabase-url>/functions/v1/rag`, and paste a key.
- **Build the installer:** `pip install pyinstaller && pyinstaller packaging/parakeet.spec`
  → `dist/Parakeet.exe`. Host it (GitHub Releases / Supabase Storage) and point the
  website's `/download` button at it.

---

## End-to-end sanity check (once live)

Sign up → dashboard shows a minted key + 0% credit meter → upload a resume (goes
`ready`) → click "Open Parakeet app" → ask a question → answer streams on the
overlay, the credit meter ticks up, and "search my documents" grounds answers in
your upload. Subscribe to Pro → checkout completes → tier flips in the dashboard
→ provider choice unlocks — all without leaving the app.
