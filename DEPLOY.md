# OnCUE — Deployment runbook

Deploy in this order. Each step produces a value the next one needs. Put
everything in the **same cloud region** for low latency.

Components:
- **Supabase** — database, auth, document storage, free embeddings (edge fn)
- **LiteLLM** on Render — model gateway (holds provider keys, per-user keys, spend)
- **Webapp** on Railway — Reflex app: accounts, pricing, dashboard, uploads, payments
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

## 2. LiteLLM proxy (Render or Google Cloud Run)

The LiteLLM proxy holds provider keys server-side and mints per-user virtual
keys. Pick **one** host — Cloud Run is recommended for the Gemini XPRIZE
hackathon (satisfies the Google Cloud product requirement).

### Option A — Google Cloud Run (recommended for hackathon)

Uses `backend/cloudbuild.yaml` and `backend/cloudrun-service.yaml`.

1. Enable APIs:
   ```
   gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
     cloudbuild.googleapis.com secretmanager.googleapis.com
   ```
2. Create an Artifact Registry repo:
   ```
   gcloud artifacts repositories create oncue \
     --repository-format=docker --location=asia-south1
   ```
3. Store secrets in Secret Manager:
   ```
   echo -n "gsk_..." | gcloud secrets create groq-api-key --data-file=-
   echo -n "AIza..." | gcloud secrets create google-api-key --data-file=-
   echo -n "postgresql://..." | gcloud secrets create litellm-database-url --data-file=-
   echo -n "sk-master-..." | gcloud secrets create litellm-master-key --data-file=-
   ```
   `GOOGLE_API_KEY` is **required** — it powers the `oncue-persona` model
   (Gemini 2.5 Flash) called on every document upload.
4. Build and deploy:
   ```
   gcloud builds submit --config backend/cloudbuild.yaml backend/
   ```
5. **Collect:** the Cloud Run URL (e.g. `https://oncue-litellm-xxxxx.asia-south1.run.app`).
6. Smoke-test — same curl commands as Render below, replacing the URL.

See `docs/hackathon/GCP-GEMINI.md` for compliance details.

### Option B — Render

Render **builds the Docker image from `backend/Dockerfile`** — you do not build
or upload an image.

1. Render → **New + → Blueprint** → connect this repo. It reads
   `backend/render.yaml` and creates the `oncue-litellm` web service.
   (Or: New Web Service → repo → **root dir `backend`**, runtime **Docker**.)
2. Set env vars:
   - `GROQ_API_KEY` = your Groq key
   - `GOOGLE_API_KEY` = your Gemini API key (required for `oncue-persona`)
   - `LITELLM_MASTER_KEY` = a strong `sk-master-…` (the blueprint can auto-generate)
   - `DATABASE_URL` = **reuse Supabase's Postgres connection string** (no separate DB)
   - optional: `ANTHROPIC_API_KEY` / `OPENAI_API_KEY`
3. Deploy. **Collect:** the service URL (e.g. `https://oncue-litellm.onrender.com`).
4. Smoke-test (replace URL + master key):
   ```
   # mint a test key
   curl -X POST https://<render-url>/key/generate \
     -H "Authorization: Bearer <LITELLM_MASTER_KEY>" -H "Content-Type: application/json" \
      -d '{"models":["oncue-default"],"max_budget":1,"duration":"30d"}'
   # use it — should return a real answer
   curl https://<render-url>/v1/chat/completions \
     -H "Authorization: Bearer <the-key-from-above>" -H "Content-Type: application/json" \
      -d '{"model":"oncue-default","messages":[{"role":"user","content":"hi"}]}'
   ```
   > The model is `groq/qwen/qwen3.6-27b` (current). The old llama-4-scout was retired.

---

## 3. Webapp on Railway

The webapp is a Reflex app wrapped in a single Docker container with Caddy
(reverse proxy for the static frontend). Railway auto-detects the Dockerfile
and builds it on every push. The Stripe and Razorpay webhook routes live at
`/api/webhooks/stripe` and `/api/webhooks/razorpay` respectively.

**Why Railway instead of Render:** better cold-start performance (critical for
webhook delivery — Stripe won't wait 20s for a container to wake up), managed
Redis add-on (no fragile in-container redis-server), and a Mumbai region
datacenter that matches your Hinglish-first India audience.

1. **Create a Railway project and deploy:**
   - [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**.
   - Select this repo, set **Root Directory** to `webapp`, **Build Command** is
     auto-detected from `webapp/Dockerfile` + `webapp/railway.json`.
   - Railway injects `PORT` automatically — the Dockerfile and Caddyfile both
     use `$PORT`, so no port configuration is needed.

2. **Add a managed Redis add-on** (optional but recommended):
   - In the Railway project → **New** → **Database** → **Redis**.
   - Railway creates a Redis instance and injects `REDIS_URL` into the webapp.
   - In the webapp's **Variables** tab, add:
     ```
     REFLEX_REDIS_URL = ${{Redis.REDIS_URL}}
     ```
   - This skips the in-container redis-server (the Dockerfile checks for this
     env var and only starts redis-server when REFLEX_REDIS_URL is not set).
   - **Without managed Redis** the app still works — it runs redis-server in
     the same container as a fallback.

3. **Set the 15 environment variables** in the webapp's **Variables** tab
   (never commit secrets):

   `SUPABASE_URL` · `SUPABASE_ANON_KEY` · `SUPABASE_SERVICE_ROLE_KEY` ·
   `SUPABASE_FUNCTIONS_URL` · `EMBED_SECRET` · `SITE_URL` · `LITELLM_URL` ·
   `LITELLM_MASTER_KEY` · `STRIPE_SECRET_KEY` · `STRIPE_WEBHOOK_SECRET` ·
   `STRIPE_PRICE_ID_PRO` · `RAZORPAY_KEY_ID` · `RAZORPAY_KEY_SECRET` ·
   `RAZORPAY_WEBHOOK_SECRET` · `RAZORPAY_PLAN_ID_PRO`

   > **Tip:** Start with Stripe in test mode so you can verify the full
   > checkout flow without real charges. Same for Razorpay test mode.

   `SITE_URL` is your public Railway URL (same as step 4 below). The dashboard
   embeds it in the `oncue://connect` deep link so the desktop app knows where
   to call `/api/usage/*` and profile endpoints.

   `LITELLM_URL` should point to where your LiteLLM instance runs. If it's on
   Render (see §2 above), use its Render URL. If you move LiteLLM to Railway
   too in the same project, use the private reference:
   ```
   LITELLM_URL = ${{litellm.RAILWAY_PRIVATE_DOMAIN}}:4000
   ```

4. **Generate a public domain** → **Networking** tab → **Generate Domain**.
   **Collect:** the Railway-provided URL (e.g. `https://oncue-webapp.up.railway.app`).

5. **Register webhooks** — both Stripe and Razorpay must send events to your
   live Railway URL:

   **Stripe Dashboard → Developers → Webhooks → Add endpoint:**
   - Endpoint URL: `https://<your-url>/api/webhooks/stripe`
   - Events to listen for:
     - `checkout.session.completed`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
   - After creation, Reveal the **Signing secret** → paste into Railway's
     `STRIPE_WEBHOOK_SECRET` variable and redeploy.

   **Razorpay Dashboard → Settings → Webhooks → Add webhook:**
   - URL: `https://<your-url>/api/webhooks/razorpay`
   - Events: `subscription.activated` + `subscription.cancelled`
   - After creation, copy the **Webhook Secret** → paste into Railway's
     `RAZORPAY_WEBHOOK_SECRET` variable and redeploy.

6. Verify webhooks work:
   ```
   # Stripe test — should return 400 (bad signature), NOT 404
   curl -X POST https://<your-url>/api/webhooks/stripe
   # Razorpay test — should return 400
   curl -X POST https://<your-url>/api/webhooks/razorpay
   ```
   Then use Stripe's Dashboard "Send test webhook" and Razorpay's "Send test"
   feature to fire real events and confirm they produce a `200` + a new row
   in `payment_events`.

7. **Supabase Auth redirect:** In Supabase → Auth → URL Configuration, add
   `https://<your-url>` to the redirect allow-list (or the full path
   `https://<your-url>/login`).

> **Mumbai region:** Railway supports Mumbai (ap-south-1) for deployment
> regions — select it in your project's settings to minimize latency for
> India-based users and LiteLLM proximity.

---

## 4. Keep-warm (optional, lowest latency)

Add a Supabase scheduled job (pg_cron or a scheduled function) that pings the
`rag` function every ~5 min so the first document search isn't a cold start. Free.

---

## 5. Desktop app

- **For users:** they sign up on the site and click **"Open OnCUE app"** — the
  `oncue://` link injects their key + your URLs automatically (hosted mode).
- **For your own testing:** in the app's Settings set provider `hosted`,
  `ONCUE_BACKEND_URL` = LiteLLM URL (Render or Railway),
  `ONCUE_WEB_URL` = webapp Railway URL,
  `ONCUE_RAG_URL` = `<supabase-url>/functions/v1/rag`, and paste a key.
- **Build the installer:** `pip install pyinstaller && pyinstaller packaging/oncue.spec`
  → `dist/OnCUE.exe`. Host it (GitHub Releases / Supabase Storage) and point the
  website's `/download` button at it.

---

## End-to-end sanity check (once live)

Sign up → dashboard shows a minted key + 0% credit meter → upload a resume (goes
`ready`) → click "Open OnCUE app" → ask a question → answer streams on the
overlay, the credit meter ticks up, and "search my documents" grounds answers in
your upload. Subscribe to Pro → checkout completes → tier flips in the dashboard
→ provider choice unlocks — all without leaving the app.
