# Gemini API + Google Cloud Compliance

This document explains how OnCUE satisfies the two technical requirements of the Build with Gemini XPRIZE hackathon.

---

## Requirement 1: Gemini API in the deployed application

> *"Projects that include LLM functionality must use the Gemini API for at least one LLM call in the deployed application."*

### How OnCUE complies

**Deployed component:** Website (Next.js on Vercel) — `website/app/api/documents/upload/route.ts`

**Flow:**
1. User uploads a PDF/DOCX/TXT on the dashboard
2. Server extracts text, chunks it, embeds it (Supabase Edge Function)
3. Server calls LiteLLM proxy with model `oncue-persona`
4. LiteLLM routes to `gemini/gemini-2.5-flash` using `GOOGLE_API_KEY`
5. Gemini returns a 2–4 sentence persona summary
6. Summary stored in `profiles.persona` — used to personalize all future agent responses

**Config:** `backend/litellm-config.yaml`
```yaml
- model_name: oncue-persona
  litellm_params:
    model: gemini/gemini-2.5-flash
    api_key: os.environ/GOOGLE_API_KEY
```

**Code:** `website/app/api/documents/upload/route.ts` → `updatePersona()` function

**Verification:**
```bash
# Upload a test file, then check:
curl "$LITELLM_URL/model/info" -H "Authorization: Bearer $MASTER_KEY" | jq '.data[] | select(.model_name=="oncue-persona")'
```

### Additional Gemini access (Pro tier)

Pro users can also select `oncue-gemini` in the desktop Settings dropdown for screen Q&A inference. This is a second Gemini touchpoint but the persona pipeline alone satisfies the requirement.

---

## Requirement 2: At least one Google Cloud product

> *"A Project must use at least one product from Google Cloud."*

### How OnCUE complies

**Product:** Google Cloud Run  
**Service:** LiteLLM inference proxy (`oncue-litellm`)

**Deployment files:**
- `backend/Dockerfile` — LiteLLM container image
- `backend/cloudbuild.yaml` — Cloud Build → Artifact Registry → Cloud Run
- `backend/cloudrun-service.yaml` — Knative service specification

**Additional GCP services used:**
| Product | Purpose |
|---|---|
| **Cloud Run** | Hosts LiteLLM proxy (production inference) |
| **Cloud Build** | CI/CD — builds and deploys on git push |
| **Artifact Registry** | Stores Docker images |
| **Cloud Logging** | Automatic request/error logs from Cloud Run |
| **Secret Manager** | Stores API keys (GROQ, GOOGLE, DATABASE_URL) |

### Deploy commands
```bash
# Enable APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com \
  cloudbuild.googleapis.com secretmanager.googleapis.com

# Create Artifact Registry repo
gcloud artifacts repositories create oncue \
  --repository-format=docker --location=asia-south1

# Build and deploy
gcloud builds submit --config backend/cloudbuild.yaml backend/

# Set LITELLM_URL in website/webapp env to the Cloud Run URL
```

### Verification
```bash
# Health check
curl https://oncue-litellm-XXXXX.asia-south1.run.app/health/liveliness

# Cloud Console
# → Cloud Run → oncue-litellm → Metrics → Request count
```

---

## Architecture diagram

```
┌─────────────────────────────────────────────────────────┐
│  User's Windows PC                                        │
│  ┌──────────────┐                                        │
│  │ OnCUE Desktop │ ── screen Q&A, voice, dictation       │
│  │ (LangGraph)   │                                        │
│  └──────┬───────┘                                        │
└─────────┼───────────────────────────────────────────────┘
          │ HTTPS (virtual key)
          ▼
┌─────────────────────────────────────────────────────────┐
│  Google Cloud Run                                        │
│  ┌──────────────────────────────────────────┐           │
│  │ LiteLLM Proxy                             │           │
│  │  oncue-default  → Groq (free)            │           │
│  │  oncue-gemini   → Gemini 2.5 Flash  ◄────┼── Gemini  │
│  │  oncue-persona  → Gemini 2.5 Flash  ◄────┼── Gemini  │
│  │  oncue-claude   → Anthropic              │           │
│  │  oncue-gpt      → OpenAI                 │           │
│  └──────────────────────────────────────────┘           │
│  Cloud Logging ← all requests logged automatically      │
└─────────┬───────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│  Vercel (Website)                                        │
│  Document upload → calls oncue-persona (Gemini) ────────►│
│  Usage ledger → Supabase                                 │
│  Auth → Supabase (Google OAuth)                          │
└─────────────────────────────────────────────────────────┘
```

---

## What is NOT used (clarification)

| Service | Status | Notes |
|---|---|---|
| Vertex AI | Not used | We use Gemini API (AI Studio key) via LiteLLM, not Vertex |
| Google OAuth | Used | Via Supabase Auth — this is auth, not a GCP product for inference |
| Google Fonts | Used | Typography only — not a qualifying GCP product |
| `google_search` tool | Used | Opens google.com in browser — not an API call |

**Cloud Run is the qualifying Google Cloud product.** Gemini API is the qualifying LLM call.

---

## Environment variables required

| Variable | Where | Purpose |
|---|---|---|
| `GOOGLE_API_KEY` | Cloud Run (LiteLLM) | Gemini API access for `oncue-persona` and `oncue-gemini` |
| `GROQ_API_KEY` | Cloud Run (LiteLLM) | Default inference (free tier) |
| `LITELLM_MASTER_KEY` | Cloud Run + Vercel | Admin API for key minting |
| `LITELLM_URL` | Vercel (website) | Points to Cloud Run service URL |
| `DATABASE_URL` | Cloud Run (LiteLLM) | Postgres for virtual key storage (Supabase) |
