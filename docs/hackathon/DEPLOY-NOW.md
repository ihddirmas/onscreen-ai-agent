# Deploy Now — step-by-step production setup

**Time:** ~2 hours if you have accounts ready  
**Result:** Live website + LiteLLM on Cloud Run + Stripe Pro checkout + Windows exe via GitHub Releases

---

## MCP deployment status (2026-07-31)

| Component | Status | URL / notes |
|-----------|--------|-------------|
| **Supabase** (`oncue`) | ✅ Live | `https://jttumhkqzpfhpamwlxtr.supabase.co` — schemas + RAG edge function deployed; 67 LiteLLM tables applied |
| **Website (Render)** | ✅ Live | https://oncue-website.onrender.com |
| **LiteLLM (Render)** | ❌ Blocked | Free tier OOM at 512MB — use **Cloud Run** or Render **Starter** ($7/mo) |
| **Vercel** | ⏸ MCP auth timeout | Use Render website or authenticate Vercel MCP |
| **Railway webapp** | ⏸ MCP error | Manual deploy via dashboard |
| **Stripe** | ⏸ Not configured | Needs keys + webhook |

### Manual step required (blocks dashboard)

Copy `SUPABASE_SERVICE_ROLE_KEY` from [Supabase API settings](https://supabase.com/dashboard/project/jttumhkqzpfhpamwlxtr/settings/api) and set on Render `oncue-website`:

```
SUPABASE_SERVICE_ROLE_KEY=<service_role JWT>
```

Also set edge function secrets (CLI):

```bash
npx supabase secrets set --project-ref jttumhkqzpfhpamwlxtr \
  EMBED_SECRET=kXxc1417DNJ9JVMwI1x1UXEJ6AwvdteRSiuup1Sdims \
  SUPABASE_SERVICE_ROLE_KEY=<same service role key>
```

Add auth redirect URL in Supabase Dashboard → Auth → URL Configuration:

```
https://oncue-website.onrender.com/**
```

---

## Prerequisites

Create accounts (all have free tiers):

| Service | URL | What you need |
|---|---|---|
| Supabase | supabase.com | Project URL, anon key, service role key, DB connection string |
| Google Cloud | console.cloud.google.com | Project ID, enable billing, Gemini API key |
| Vercel | vercel.com | Account linked to GitHub |
| Stripe | stripe.com | Test mode keys + Pro price ($9/mo subscription) |
| Groq | console.groq.com | Free API key |

---

## Step 1: Supabase (15 min)

1. Create project (pick **Mumbai** or closest region to India).
2. SQL Editor → run these files in order:
   - `website/supabase/schema.sql`
   - `website/supabase/schema_ledger.sql`
   - `website/supabase/schema_payments.sql`
3. Deploy RAG edge function — see `DEPLOY.md` §1 Option A.
4. Auth → URL Configuration → add your Vercel URL to redirect allow-list.
5. (Optional) Auth → Providers → enable Google OAuth.

---

## Step 2: LiteLLM on Cloud Run (20 min)

```bash
# Install gcloud CLI, then:
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

# Store secrets
echo -n "gsk_..." | gcloud secrets create groq-api-key --data-file=-
echo -n "AIza..." | gcloud secrets create google-api-key --data-file=-
echo -n "postgresql://..." | gcloud secrets create litellm-database-url --data-file=-
echo -n "sk-master-..." | gcloud secrets create litellm-master-key --data-file=-

# Deploy
gcloud builds submit --config backend/cloudbuild.yaml backend/

# Get URL
gcloud run services describe oncue-litellm --region asia-south1 --format='value(status.url)'
```

Smoke test:
```bash
curl https://YOUR-CLOUD-RUN-URL/health/liveliness
```

Set env vars on Cloud Run for `GROQ_API_KEY`, `GOOGLE_API_KEY`, `DATABASE_URL`, `LITELLM_MASTER_KEY`.

---

## Step 3: Website on Vercel (15 min)

1. vercel.com → Import `ihddirmas/onscreen-ai-agent` → root directory: `website`
2. Set environment variables (from `website/.env.local.example`):

```
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
EMBED_SECRET
LITELLM_URL          ← Cloud Run URL
LITELLM_MASTER_KEY
STRIPE_SECRET_KEY    ← sk_test_... to start
STRIPE_WEBHOOK_SECRET
STRIPE_PRICE_ID_PRO
NEXT_PUBLIC_SITE_URL ← your Vercel URL
```

3. Deploy. Visit `/pricing` and `/login`.

### Stripe webhook
1. Stripe Dashboard → Developers → Webhooks → Add endpoint
2. URL: `https://YOUR-SITE.vercel.app/api/webhooks/stripe`
3. Events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
4. Copy signing secret → `STRIPE_WEBHOOK_SECRET` in Vercel → redeploy

---

## Step 4: Windows exe release (10 min)

On your Windows machine OR via GitHub Actions:

```bash
git tag v0.1.0
git push origin v0.1.0
```

This triggers `.github/workflows/release-windows.yml` which builds `OnCUE.exe` and attaches it to the GitHub Release. The `/download` page links to it automatically.

---

## Step 5: Verify end-to-end (10 min)

1. Sign up on your live site
2. Dashboard shows a minted `sk-...` key
3. Upload a PDF → status "ready" → persona updates (Gemini call)
4. Download `.exe`, install, paste key, set provider "hosted"
5. Press `Ctrl+Shift+Space` → answer streams on overlay
6. Subscribe to Pro (Stripe test card `4242 4242 4242 4242`) → tier flips to "pro"

---

## Step 6: Judge access

Repo is **already public**: https://github.com/ihddirmas/onscreen-ai-agent

Judges can also be invited as collaborators if you make it private later:
- `testing@devpost.com`
- `judging@hacker.fund`

Fill `docs/hackathon/TESTING.md` with your live URLs and a test account.

---

## Automated deploy (all steps)

```bash
cp .env.deploy.example .env.deploy
# fill in all values
chmod +x scripts/deploy-stack.sh
./scripts/deploy-stack.sh
```

Requires: `gcloud`, `psql`, `vercel` CLI, and all credentials in `.env.deploy`.
