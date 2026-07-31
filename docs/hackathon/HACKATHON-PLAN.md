# OnCUE — Gemini XPRIZE Execution Plan

**Today:** July 31, 2026  
**Submission deadline:** August 17, 2026 (~17 days remaining)  
**Category:** Education & Human Potential

---

## Executive summary

OnCUE is a **real product** with a working desktop agent, web portal, hosted inference, and payment infrastructure. The codebase is strong; the gap is **submission packaging** — live deployment, demo video, financial/user evidence, and judge-ready documentation.

This plan prioritizes work by **judge impact** and **hackathon compliance risk**.

---

## Phase 1 — Compliance blockers (do first)

These are pass/fail requirements. Missing any one can disqualify the entry.

### 1.1 Gemini API in deployed application ✅ (code done)

**What:** At least one LLM call in the live deployed app must hit Gemini.

**Implementation:**
- Added `oncue-persona` model alias → `gemini/gemini-2.5-flash` in `backend/litellm-config.yaml`
- Document upload on the website (`website/app/api/documents/upload/route.ts`) calls `oncue-persona` to summarize user background into `profiles.persona`

**Your action:** Deploy LiteLLM with `GOOGLE_API_KEY` set. Upload a test PDF on the dashboard and verify `persona` updates in Supabase.

### 1.2 Google Cloud product ✅ (config done)

**What:** Use at least one Google Cloud product.

**Implementation:**
- `backend/cloudbuild.yaml` — Cloud Build → Artifact Registry → Cloud Run
- `backend/cloudrun-service.yaml` — Knative service spec
- Cloud Logging is automatic on Cloud Run

**Your action:**
```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
gcloud builds submit --config backend/cloudbuild.yaml backend/
# Set secrets (GROQ_API_KEY, GOOGLE_API_KEY, DATABASE_URL, LITELLM_MASTER_KEY)
# Point LITELLM_URL in website/webapp to the Cloud Run URL
```

### 1.3 Live demo for judges

**What:** Working URL + test credentials judges can use until judging ends.

**Stack to deploy (in order):**
1. Supabase (schema + RAG edge function) — `DEPLOY.md` §1
2. LiteLLM on Cloud Run — `DEPLOY.md` + `backend/cloudbuild.yaml`
3. Website on Vercel — `website/` with env vars
4. Webapp on Railway (payments) — `webapp/` with Stripe test mode
5. Windows `.exe` build — `pyinstaller packaging/oncue.spec`

**Deliverable:** Fill in `docs/hackathon/TESTING.md` with live URLs and a test account.

### 1.4 Repository access

**What:** Public repo OR private repo shared with `testing@devpost.com` and `judging@hacker.fund`.

**Your action:** Choose one and do it before submitting.

---

## Phase 2 — Submission materials (high judge impact)

### 2.1 Demo video (≤ 3 minutes)

**Script:** `docs/hackathon/VIDEO-OUTLINE.md`

**Must show:**
- AI running live in production (not mockups)
- Desktop agent on real Windows machine
- How AI makes decisions (screen Q&A, voice, document RAG)
- Gemini + Google Cloud mention (brief: "persona built with Gemini on Cloud Run")

**Recording tips:**
- Turn off screen-share hiding for recording (`GUIDE.md`)
- Use real screen capture, no stock footage
- Upload to YouTube as **public**
- Keep under 3:00 — judges may stop watching

### 2.2 Written narrative (500–1000 words)

**Draft:** `docs/hackathon/SUBMISSION-NARRATIVE.md`

**Must cover:**
- How AI runs the business day-to-day
- What humans do vs what AI does
- Jobs/economic opportunities created
- Category relevance (Education & Human Potential)
- Real users and revenue story

**Your action:** Replace `[PLACEHOLDER]` values with real numbers and customer quotes.

### 2.3 Revenue & expense evidence

**Template:** `docs/hackathon/EVIDENCE-TEMPLATES.md`

**Required:**
- Total revenue (arms-length customers, USD)
- Revenue by month: May, June, July, August 2026
- Total expenses + description
- Marketing/customer acquisition spend (even if $0)
- Related-party revenue (separate line item)

**Sources:**
- Stripe dashboard export (`webapp/` has Stripe integration)
- Razorpay dashboard (UPI subscriptions for India)
- Bank statements
- LiteLLM spend logs for API costs

### 2.4 User evidence

**Required:**
- Number of individual users
- Breakdown of who they are (students, developers, etc.)
- Testimonials (with consent)
- Customer contact info (name, email, phone) — judges may verify

**Your action:** Email 5–10 early users asking for a one-sentence testimonial and permission to share their first name + role.

### 2.5 Product evidence (AI in production)

**Guide:** `docs/hackathon/PRODUCT-EVIDENCE.md`

**Collect:**
- Screenshots of Supabase `usage_ledger` table
- LiteLLM spend dashboard (`/key/info` API)
- Cloud Run request logs in Google Cloud Console
- Gemini API usage from Google AI Studio / Cloud Console
- 2–3 redacted agent execution examples (screen Q&A sessions)

---

## Phase 3 — Product polish (differentiation)

Lower priority than submission materials, but strengthens judging scores.

### 3.1 Unify payments

**Current state:** `website/` says "Payments coming soon"; `webapp/` has working Stripe + Razorpay.

**Options:**
- A) Point website Pro CTA to webapp checkout URL
- B) Port payment routes from webapp to website
- C) Deploy webapp as primary portal, website as marketing site

**Recommendation:** Option A is fastest — link `/pricing` "Choose Pro" to the Railway webapp checkout.

### 3.2 Name consistency

**Current state:** OnCUE (product) vs Parakeet (campaign docs).

**Recommendation:** Standardize on **OnCUE** for submission. Update campaign docs later.

### 3.3 Free tier Gemini access

**Current state:** Gemini is server-side (persona) + Pro-tier user-facing.

**Optional:** Add `oncue-gemini` to free tier allowlist so judges can test Gemini inference directly. Costs ~$0.01/session on Flash.

### 3.4 Marketing push (last 2 weeks)

From `refineplan.md` — position as:
- "Invisible teleprompter" for presentations (not cheating)
- Hinglish-first dictation for Indian students
- Screen Q&A without alt-tabbing

**Channels:** Reddit (r/India, r/learnprogramming), Twitter/X, LinkedIn, college discords, Product Hunt.

---

## Phase 4 — Devpost form checklist

Copy-paste ready fields for [xprize.devpost.com](https://xprize.devpost.com):

| Field | Source |
|---|---|
| Project name | OnCUE.ai |
| Tagline | On-screen AI agent — Hinglish-first screen Q&A, voice, and dictation |
| Category | Education & Human Potential |
| Repository URL | https://github.com/ihddirmas/onscreen-ai-agent |
| Demo URL | Vercel website + test account in TESTING.md |
| Video URL | YouTube link |
| Description | SUBMISSION-NARRATIVE.md |
| Built with | Gemini API, Google Cloud Run, LangGraph, Supabase, Next.js |
| What it does | See narrative |
| How we built it | See narrative § "Architecture" |
| Challenges | See narrative § "Challenges" |
| Revenue evidence | EVIDENCE-TEMPLATES.md (attach or paste) |
| User evidence | EVIDENCE-TEMPLATES.md § Users |

---

## Risk register

| Risk | Mitigation |
|---|---|
| No real revenue yet | Launch Pro tier on webapp immediately; offer early-bird pricing to 10 users |
| No real users yet | Ship Windows exe to 20 beta testers from your network this week |
| Gemini not verifiable | Document upload → persona is a clear, auditable Gemini call |
| GCP not deployed | Cloud Run deploy takes ~30 min; do it before recording video |
| Video too long | Script is 2:45; practice once with a timer |
| Payments not live on website | Use webapp for checkout; mention in testing instructions |

---

## Week-by-week sprint

### Week 1 (Jul 31 – Aug 6)
- [ ] Deploy full stack (Supabase + Cloud Run + Vercel + Railway)
- [ ] Share repo with judges
- [ ] Get 5 paying or committed users
- [ ] Record demo video

### Week 2 (Aug 7 – Aug 13)
- [ ] Collect revenue/user evidence
- [ ] Fill evidence templates
- [ ] Finalize narrative
- [ ] Get 2–3 testimonials

### Week 3 (Aug 14 – Aug 17)
- [ ] Submit on Devpost
- [ ] Double-check all links work
- [ ] Respond to any judge verification requests within 2 business days

---

## What AI does vs what humans do (for narrative)

| Task | Who |
|---|---|
| Screen analysis + answer generation | AI agent (LangGraph ReAct) |
| Voice transcription | AI (faster-whisper) |
| Document embedding + RAG search | AI (gte-small embeddings + vector search) |
| Persona summarization from uploads | AI (Gemini 2.5 Flash) |
| Web search + browse | AI agent with tools |
| Customer support first response | AI (can draft; human reviews) |
| Pricing, refunds, legal | Human |
| Product roadmap | Human |
| Marketing copy drafts | AI assists; human approves |
| Infrastructure deploys | Human triggers; Cloud Build/Run automates |
| Payment processing | Stripe/Razorpay (automated) |
