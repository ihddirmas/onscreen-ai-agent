#!/usr/bin/env bash
# One-command production stack bootstrap for OnCUE.
# Run from repo root after filling in .env.deploy (copy from .env.deploy.example).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT/.env.deploy}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing $ENV_FILE — copy .env.deploy.example and fill in values."
  exit 1
fi

# shellcheck disable=SC1090
source "$ENV_FILE"

need() {
  if [[ -z "${!1:-}" ]]; then
    echo "Required variable $1 is not set in $ENV_FILE"
    exit 1
  fi
}

echo "==> 1/4 Supabase schema"
need SUPABASE_DB_URL
if command -v psql >/dev/null 2>&1; then
  psql "$SUPABASE_DB_URL" -f "$ROOT/website/supabase/schema.sql"
  psql "$SUPABASE_DB_URL" -f "$ROOT/website/supabase/schema_ledger.sql"
  psql "$SUPABASE_DB_URL" -f "$ROOT/website/supabase/schema_payments.sql"
  echo "    Schema applied."
else
  echo "    psql not found — paste SQL files into Supabase SQL Editor manually:"
  echo "    - website/supabase/schema.sql"
  echo "    - website/supabase/schema_ledger.sql"
  echo "    - website/supabase/schema_payments.sql"
fi

echo "==> 2/4 LiteLLM on Google Cloud Run"
need GCP_PROJECT_ID
need LITELLM_MASTER_KEY
need GROQ_API_KEY
need GOOGLE_API_KEY
need DATABASE_URL
gcloud config set project "$GCP_PROJECT_ID"
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
gcloud builds submit --config "$ROOT/backend/cloudbuild.yaml" "$ROOT/backend/" \
  --substitutions="_REGION=${GCP_REGION:-asia-south1}"
echo "    Cloud Run URL:"
gcloud run services describe oncue-litellm --region "${GCP_REGION:-asia-south1}" \
  --format='value(status.url)'

echo "==> 3/4 Website on Vercel"
need VERCEL_TOKEN
need VERCEL_ORG_ID
need VERCEL_PROJECT_ID
(
  cd "$ROOT/website"
  npm ci
  npx vercel deploy --prod --token "$VERCEL_TOKEN" --yes
)

echo "==> 4/4 Post-deploy checklist"
cat <<EOF

Manual steps remaining:
  1. Set Vercel env vars (see website/.env.local.example)
  2. Stripe webhook → https://YOUR_SITE/api/webhooks/stripe
     Events: checkout.session.completed, customer.subscription.updated, customer.subscription.deleted
  3. Supabase Auth redirect URL → https://YOUR_SITE
  4. Deploy RAG edge function (DEPLOY.md §1)
  5. Tag a release to build Windows exe:
       git tag v0.1.0 && git push origin v0.1.0
  6. Share repo with testing@devpost.com (public repo: already done)

EOF
