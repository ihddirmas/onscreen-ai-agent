# Gemini XPRIZE — OnCUE Submission Package

**Deadline:** August 17, 2026, 1:00 pm Pacific  
**Hackathon:** [Build with Gemini XPRIZE](https://xprize.devpost.com)  
**Category:** Education & Human Potential

This folder contains everything needed to complete the Devpost submission for OnCUE.ai.

## Status dashboard

| Requirement | Status | Owner / next step |
|---|---|---|
| **Gemini API in deployed app** | ✅ Wired | `oncue-persona` model (Gemini 2.5 Flash) runs on every document upload → persona summarization. See `backend/litellm-config.yaml`. |
| **Google Cloud product** | ✅ Config ready | LiteLLM proxy deploys to **Google Cloud Run** via `backend/cloudbuild.yaml`. Deploy and set `LITELLM_URL` to the Cloud Run URL. |
| **Public repo + judge access** | ✅ Done | Public: https://github.com/ihddirmas/onscreen-ai-agent. Judges: `testing@devpost.com`, `judging@hacker.fund` can clone directly. |
| **Live demo URL** | ⬜ TODO | Follow `DEPLOY-NOW.md` — deploy Supabase + Cloud Run + Vercel. |
| **Stripe Pro checkout** | ✅ Wired | Website `/pricing` → `/api/checkout/stripe` → webhook at `/api/webhooks/stripe`. |
| **Windows .exe distribution** | ✅ CI ready | Tag `v0.1.0` to trigger `.github/workflows/release-windows.yml`. |
| **3-minute demo video** | ⬜ TODO | Record using `VIDEO-OUTLINE.md`. Upload to YouTube (public). |
| **Written narrative (500–1000 words)** | ✅ Draft | `SUBMISSION-NARRATIVE.md` — customize with your real numbers. |
| **Revenue evidence** | ⬜ TODO | Fill `EVIDENCE-TEMPLATES.md` with Stripe/Razorpay exports. |
| **Expense / marketing spend** | ⬜ TODO | Fill P&L section in `EVIDENCE-TEMPLATES.md`. |
| **User evidence** | ⬜ TODO | Add user count, testimonials, contact info (with consent). |
| **Product evidence (agent logs)** | ⬜ TODO | Export usage ledger + LiteLLM spend. See `PRODUCT-EVIDENCE.md`. |
| **Testing instructions** | ✅ Draft | `TESTING.md` — add live URLs and test credentials before submit. |

## Files in this folder

| File | Purpose |
|---|---|
| [HACKATHON-PLAN.md](./HACKATHON-PLAN.md) | Prioritized execution plan — what to do and in what order |
| [SUBMISSION-NARRATIVE.md](./SUBMISSION-NARRATIVE.md) | Devpost description (500–1000 words) |
| [TESTING.md](./TESTING.md) | Judge testing instructions |
| [VIDEO-OUTLINE.md](./VIDEO-OUTLINE.md) | 3-minute demo script |
| [EVIDENCE-TEMPLATES.md](./EVIDENCE-TEMPLATES.md) | Revenue, expenses, users, P&L templates |
| [PRODUCT-EVIDENCE.md](./PRODUCT-EVIDENCE.md) | How to export agent logs and API usage |
| [GCP-GEMINI.md](./GCP-GEMINI.md) | Technical proof of Gemini + Google Cloud compliance |

## Quick technical proof (for judges)

1. **Gemini call:** Upload a PDF on the dashboard → server calls `oncue-persona` → Gemini 2.5 Flash summarizes your background into `profiles.persona`.
2. **Google Cloud:** LiteLLM proxy runs on Cloud Run (`backend/cloudbuild.yaml`). Cloud Logging captures request logs.
3. **AI-native operations:** Desktop agent (LangGraph ReAct) handles screen Q&A, voice, dictation, and tool use autonomously. Humans set policy; AI executes.

## Suggested submission order

1. Deploy production stack (Supabase → Cloud Run LiteLLM → Vercel website → Railway webapp)
2. Record demo video on a real Windows machine
3. Collect revenue/user evidence from Stripe/Razorpay dashboards
4. Fill evidence templates with real numbers
5. Copy narrative into Devpost form
6. Share repo with judges
7. Submit before August 17 deadline
