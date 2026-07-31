# Judge Testing Instructions — OnCUE.ai

> **Before submitting:** Replace all `[PLACEHOLDER]` values with your deployed URLs and test credentials.

---

## Overview

OnCUE.ai is an on-screen AI agent for **Windows**. The web portal handles signup, document upload, and billing. The desktop app connects to our hosted inference backend.

**Category:** Education & Human Potential  
**Gemini API:** Used for persona summarization on document upload (`oncue-persona` → Gemini 2.5 Flash)  
**Google Cloud:** LiteLLM proxy hosted on Render (requires Starter plan — free tier OOMs at 512MB) or Cloud Run

---

## 1. Web portal (no install required)

**URL:** https://oncue-website.onrender.com

### Create a test account
1. Go to `[URL]/login`
2. Sign up with email/password OR Google OAuth
3. You'll land on the dashboard

### Test document upload (triggers Gemini)
1. Dashboard → Upload a PDF or TXT file (lecture notes, resume, any text document)
2. Wait for status → "ready"
3. Check that `persona` field updates (visible on dashboard or in Supabase `profiles` table)
4. This upload triggers a **Gemini 2.5 Flash** call via our LiteLLM proxy (`oncue-persona` model)

### Get your license key
1. Dashboard → "Your key" or visit `[URL]/api/me/key`
2. Copy the `sk-...` virtual key

### Test usage ledger
1. Dashboard should show credit usage meter
2. Every desktop session reports to `usage_ledger` in Supabase

---

## 2. Desktop app (Windows required)

**Download:** `[PLACEHOLDER: link to dist/OnCUE.exe or GitHub Releases]`

### Setup
1. Install and launch OnCUE (tray icon appears)
2. Right-click tray → Settings
3. Set Provider to **Hosted**
4. Paste your license key from step 1
5. Set Backend URL to `[PLACEHOLDER: https://your-litellm-cloudrun-url.run.app/v1]`
6. Click Save

### Test screen Q&A
1. Open any app (browser, VS Code, Notepad)
2. Press `Ctrl+Shift+Space`
3. Type a question (or press Enter for "describe my screen")
4. Answer streams onto the overlay

### Test Hinglish dictation
1. Click into any text field (browser, WhatsApp Web, Notepad)
2. Hold `Ctrl+Shift+D`
3. Speak in Hinglish: "kal ka weather check karo"
4. Release — text appears at cursor

### Test voice command
1. Hold `Ctrl+Shift+V`
2. Speak a question about your screen
3. Release — agent processes and answers on overlay

### Test document RAG (if you uploaded docs)
1. Press `Ctrl+Shift+Space`
2. Ask something related to your uploaded document
3. Agent should use `search_my_documents` tool and cite your content

---

## 3. Payments (optional test)

**Webapp URL:** `[PLACEHOLDER: https://your-webapp.railway.app]`

### Stripe test checkout
1. Log in with the same Supabase account
2. Go to Pricing → Choose Pro
3. Use Stripe test card: `4242 4242 4242 4242`, any future expiry, any CVC
4. Verify tier upgrades to "pro" on dashboard

### Razorpay (India)
- UPI Autopay test mode available if configured
- Contact us for test UPI credentials if needed

---

## 4. Verify Gemini + Google Cloud

### Gemini API usage
```bash
# After uploading a document, check LiteLLM logs for oncue-persona calls:
curl "[PLACEHOLDER: LITELLM_URL]/model/info" \
  -H "Authorization: Bearer [LITELLM_MASTER_KEY]"
```

Or check Google AI Studio / Cloud Console for `gemini-2.5-flash` request counts during your test window.

### Google Cloud Run
1. Google Cloud Console → Cloud Run → `oncue-litellm`
2. View request logs (Cloud Logging)
3. Confirm health check: `GET [LITELLM_URL]/health/liveliness` → 200

---

## 5. Pre-configured test account

For automated E2E (local stack or Supabase cloud):

| Field | Value |
|---|---|
| Email | `oncue-e2e-test@example.com` |
| Password | `OnCUE-E2E-Test-Only-2026!` |
| User ID | `00000000-0000-4000-8000-000000000001` |
| License key | Written to `.env.test` by `scripts/provision_test_user.py` |
| Tier | `free` (1 hosted trial session) |

**Setup:**

```bash
cp .env.test.example .env.test
# Optional: fill NEXT_PUBLIC_SUPABASE_* for cloud Supabase test user
bash scripts/start_local_e2e_stack.sh
.venv/bin/pytest tests/test_e2e_hosted_flow.py -v
bash scripts/record_gui_e2e.sh   # screen recording
```

See `.env.test.example` for all test-only variables. Never commit `.env.test`.

---

## 6. Repository

**GitHub (public):** https://github.com/ihddirmas/onscreen-ai-agent

Judges can clone and review without an invite. If the repo is made private later, add `testing@devpost.com` and `judging@hacker.fund` as collaborators.

Key paths for reviewers:
- `oncue/agent/` — LangGraph ReAct agent + tools
- `backend/litellm-config.yaml` — model routing (includes `oncue-persona` → Gemini)
- `backend/cloudbuild.yaml` — Google Cloud Run deployment
- `website/app/api/documents/upload/route.ts` — Gemini persona call
- `website/supabase/schema_ledger.sql` — usage tracking
- `webapp/webapp/services/payments.py` — Stripe + Razorpay

---

## 7. Known limitations

- Desktop app targets **Windows** (macOS build not yet shipped)
- Full tray/overlay app requires a real Windows machine (not runnable in headless Linux)
- Free tier has a 1-session trial cap; use the pre-configured Pro test account for unlimited testing
- Screen-share hiding is on by default; disable in Settings if you want to record the overlay

---

## Contact

For live demo requests or issues during judging:

| | |
|---|---|
| Name | `[PLACEHOLDER: Your name]` |
| Email | `[PLACEHOLDER: your@email.com]` |
| Response time | Within 2 business days |
