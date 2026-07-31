# OnCUE.ai — Devpost Submission Narrative

> **Instructions:** Replace all `[PLACEHOLDER]` values with your real data before submitting. Target length: 500–1000 words.

---

## What we built

OnCUE.ai is an on-screen AI agent for Windows that eliminates the "alt-tab tax" — the dozens of times per day students and early-career workers screenshot an error, switch to ChatGPT, paste, wait, and switch back. One hotkey (`Ctrl+Shift+Space`) captures the screen, runs a tool-using AI agent, and streams the answer onto a transparent overlay — without leaving the app you're in.

We built OnCUE for **Education & Human Potential**: Hinglish-speaking students in India who think in Roman Hinglish but are forced to translate into English before any dictation or AI tool will understand them. OnCUE defaults to Hinglish speech-to-text, screen Q&A in the language you speak, and document-grounded answers from your own study materials.

## How AI runs our business

OnCUE is AI-native by design — not a wrapper with a chatbot bolted on.

**Production AI workflows:**

1. **Desktop agent (LangGraph ReAct):** Every user session triggers an autonomous agent that decides whether to search the web, browse a page, open a file, search uploaded documents (RAG), or answer directly from the screenshot. The agent executes these decisions without human intervention. Humans set guardrails (allowed directories, confirmation for side-effecting actions); AI executes.

2. **Voice pipeline:** Push-to-talk captures mic + system audio → faster-whisper transcribes → agent processes the command. Dictation mode pastes Hinglish text at the cursor. Zero human in the loop during a session.

3. **Document RAG:** Users upload PDFs/DOCX on the web portal. Chunks are embedded (gte-small via Supabase Edge Function), stored in pgvector, and retrieved by the desktop agent's `search_my_documents` tool during screen Q&A.

4. **Persona engine (Gemini):** On every document upload, our deployed backend calls **Gemini 2.5 Flash** (via the `oncue-persona` model on our LiteLLM proxy hosted on **Google Cloud Run**) to summarize who the user is — background, skills, projects — and stores it in their profile. This persona personalizes every subsequent agent response.

5. **Hosted inference:** End users never need API keys. Our LiteLLM proxy on Cloud Run holds provider keys, mints per-user virtual keys with monthly budgets, and routes requests. Usage is metered in a `usage_ledger` table; the desktop app reports every session and inference event.

**What humans do:**
- Set product direction and pricing
- Handle payment disputes and legal
- Review flagged support escalations
- Deploy infrastructure (one-click Cloud Build → Cloud Run)
- Approve marketing copy (AI drafts, human publishes)

**What AI does:**
- Every screen Q&A, voice command, and dictation session
- Document processing, embedding, and retrieval
- Persona summarization (Gemini)
- Web search and page browsing for answers
- First-draft customer support responses
- Marketing copy drafts and social post variants

## Real business, real users

We launched OnCUE during the hackathon period (May 2026) as a freemium SaaS:

- **Free tier:** ~$1/month of model credits, 1 reference document, screen Q&A + voice
- **Pro tier ($9/month):** ~$15 credits, unlimited documents, priority models (Claude, GPT, Gemini)

**Revenue:** `[PLACEHOLDER: total USD revenue May–Aug 2026]`  
**Arms-length customers:** `[PLACEHOLDER: number]`  
**Related-party revenue:** `[PLACEHOLDER: $0 or amount with explanation]`  

**Monthly breakdown:**
| Month | Revenue (USD) |
|---|---|
| May 2026 | `[PLACEHOLDER]` |
| June 2026 | `[PLACEHOLDER]` |
| July 2026 | `[PLACEHOLDER]` |
| August 2026 | `[PLACEHOLDER]` |

**Expenses:** `[PLACEHOLDER: total USD]` — hosting (Cloud Run, Vercel, Railway, Supabase), AI API usage (Groq free tier + Gemini), domain, `[other]`.

**Marketing spend:** `[PLACEHOLDER: $0 or amount]`

**Users:** `[PLACEHOLDER: total count]` — primarily Hinglish-speaking students and early-career developers in India. `[PLACEHOLDER: 1-2 sentence user breakdown]`.

**Testimonial:** *"[PLACEHOLDER: customer quote]"* — `[Name]`, `[role]`

## Category impact: Education & Human Potential

Students in India face a specific friction: they learn in Hinglish, but every AI tool expects English input. OnCUE removes that translation step. A student debugging code can hold `Ctrl+Shift+Space`, ask "yeh error kya hai" in Hinglish, and get an answer overlaid on their IDE — without leaving VS Code, without re-screenshotting, without switching languages.

Upload lecture notes or textbook chapters, and the agent grounds answers in *your* materials during exams and assignments. This isn't generic ChatGPT — it's your study context, on your screen, in your language.

We believe this redefines how 300M+ Hinglish speakers learn and work: AI that meets them where they are, not where Silicon Valley assumes they should be.

## Technical architecture

```
Desktop (Python/PySide6/LangGraph)
  → LiteLLM proxy (Google Cloud Run)
    → Groq / Gemini / Claude / GPT
  → Website (Next.js on Vercel)
    → Supabase (auth, pgvector RAG, usage ledger)
    → Gemini (persona summarization on document upload)
  → Webapp (Reflex on Railway)
    → Stripe + Razorpay payments
```

**Google Cloud:** Cloud Run hosts the LiteLLM inference proxy. Cloud Build deploys on every push. Cloud Logging captures all API requests.

**Gemini API:** `oncue-persona` model uses `gemini-2.5-flash` for every document upload persona update. Pro users can also select `oncue-gemini` for screen Q&A.

## Challenges we solved

1. **Screen-share privacy:** Windows `WDA_EXCLUDEFROMCAPTURE` hides the overlay from screen shares — useful for client calls, not for cheating (we explicitly avoid that positioning).

2. **Hosted mode without shipping keys:** The desktop exe never contains API keys. Per-user virtual keys with monthly budgets are minted server-side and auto-configured via `oncue://` deep link after web signup.

3. **Multi-provider parity:** LiteLLM aliases (`oncue-default`, `oncue-gemini`, etc.) with server-side tier enforcement — free users can't access Pro models even if they guess the alias name.

4. **Hinglish STT:** Default whisper prompt biases output toward Roman Hinglish. Users can switch to Devanagari Hindi or English in Settings.

## Economic opportunity

OnCUE creates opportunity beyond our founding team:

- **For users:** Saves 30–60 minutes/day of context-switching — time redirected to learning and building
- **For future hires:** As we grow, we'll need customer success, localization (regional Indian languages), and Windows installer support
- **For the ecosystem:** Open-source desktop agent code; developers can extend tools and providers

We pre-existed no generic template — we built the overlay, hotkey system, voice pipeline, RAG integration, and hosted billing from scratch during the hackathon period, using open-source libraries (LangGraph, PySide6, Supabase) as foundations.

---

*OnCUE.ai — skip the alt-tab tax.*
