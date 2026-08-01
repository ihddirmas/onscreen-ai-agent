# Secrets checklist — add these before deploying

Copy values into Vercel (website), Cloud Run (LiteLLM), and optionally GitHub Actions secrets.

## Vercel (website) — Settings → Environment Variables

| Variable | Source |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase → Settings → API |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase → Settings → API |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Settings → API (server only) |
| `EMBED_SECRET` | Generate random string (same as Supabase edge fn secret) |
| `LITELLM_URL` | Cloud Run service URL |
| `LITELLM_MASTER_KEY` | You generate (`sk-master-...`) |
| `STRIPE_SECRET_KEY` | Stripe → Developers → API keys (test: `sk_test_`) |
| `STRIPE_WEBHOOK_SECRET` | Stripe → Webhooks → signing secret |
| `STRIPE_PRICE_ID_PRO` | Stripe → Products → Pro price ID (`price_...`) |
| `NEXT_PUBLIC_SITE_URL` | Your Vercel URL |

## Cloud Run (LiteLLM)

| Variable | Source |
|---|---|
| `GROQ_API_KEY` | console.groq.com |
| `GOOGLE_API_KEY` | aistudio.google.com (Gemini) |
| `DATABASE_URL` | Supabase → Database → connection string |
| `LITELLM_MASTER_KEY` | Same as Vercel |

## GitHub Actions (optional — for automated deploy)

| Secret / variable | Purpose |
|---|---|
| `VERCEL_TOKEN` | vercel.com → Account → Tokens |
| `VERCEL_ORG_ID` | Vercel project settings (`.vercel/project.json`) |
| `VERCEL_PROJECT_ID` | Vercel project settings |
| `RENDER_API_KEY` | render.com → Account → API Keys |
| `RENDER_SERVICE_ID_WEBSITE` | `srv-d9mhghlbedkc73dp482g` (oncue-website) |
| `RENDER_SERVICE_ID_LITELLM` | `srv-d9mhfn5bedkc73dp292g` (oncue-litellm) |
| `GCP_SA_KEY` | GCP service account JSON (Cloud Run deploy) |
| `GCP_REGION` (repo variable) | Optional; defaults to `asia-south1` |

Workflow: **Actions → Deploy production → Run workflow**. Choose `website-vercel`, `website-render`, `litellm-cloudrun`, `litellm-render`, or `all`.

CI workflow (`.github/workflows/ci.yml`) runs on every push/PR to `main` and validates the website production build.

## Stripe setup (test mode)

1. Create product "OnCUE Pro" — $9/month recurring
2. Copy price ID → `STRIPE_PRICE_ID_PRO`
3. Webhook endpoint: `https://YOUR-SITE.vercel.app/api/webhooks/stripe`
4. Events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
5. Test card: `4242 4242 4242 4242`

## Available in this cloud agent environment

These are pre-injected for dev/testing only (do NOT commit):

- `GROQ_API_KEY`
- `GEMINI_API_KEY` (maps to `GOOGLE_API_KEY` for LiteLLM)
- `ANTHROPIC_API_KEY`

You still need Supabase, Stripe, Vercel, and GCP credentials from your own accounts.
