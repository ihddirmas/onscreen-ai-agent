# Parakeet — Web app

Login, pricing, credit usage, and **reference documents** for the Parakeet
desktop assistant. Next.js (App Router) + Supabase (auth + Postgres + storage +
pgvector). Documents you upload here become knowledge the desktop agent uses to
give better, personalized answers.

## What it does

- **Auth** — email + Google (Supabase).
- **One Parakeet key per user** — minted from the LiteLLM proxy (`backend/`); it
  authenticates both model calls *and* the document/profile APIs the desktop
  calls. Shown on the dashboard; also handed to the app via the "Open Parakeet
  app" button (`parakeet://` deep link) so there's nothing to paste.
- **Pricing + credit usage** — tiers page; the dashboard meter reads the user's
  spend/budget from LiteLLM.
- **Reference documents (RAG)** — upload a resume/notes/study plan → extracted →
  chunked → embedded **free** on a **Supabase Edge Function** using the built-in
  `gte-small` model (384-dim; the model is resident in the edge runtime, so there
  is **no model download and no cold-start penalty**) → stored in pgvector. The
  desktop agent's `search_my_documents` tool hits the edge function **directly**
  (embed + vector match in one hop next to the DB) for minimum latency; it falls
  back to the website API if not configured.
- **Profile / preferences** — an auto-derived persona (from your docs) plus an
  editable Preferences box are injected into the agent's system prompt, so e.g.
  a Python user gets coding answers in Python.

## Setup

1. Create a **Supabase** project. In the SQL editor, run `supabase/schema.sql`
   (creates tables, pgvector, the `match_doc_chunks` function, RLS, and the
   `documents` storage bucket). Then deploy the embedding/search edge function:
   ```
   supabase functions deploy rag --no-verify-jwt
   supabase secrets set EMBED_SECRET=<same as .env.local> SUPABASE_SERVICE_ROLE_KEY=<service role>
   ```
   Uses the built-in free `gte-small` model — no embedding API key.
2. Deploy the **LiteLLM proxy** (`../backend/`) and note its URL + master key.
3. Copy `.env.local.example` → `.env.local` and fill in:
   Supabase URL/anon/service-role, `LITELLM_URL`, `LITELLM_MASTER_KEY`,
   `NEXT_PUBLIC_SITE_URL`. (No embedding key needed — it's open-source/local.)
4. `npm install && npm run dev` → http://localhost:3000

## How the desktop connects

The dashboard "Open Parakeet app" button opens
`parakeet://connect?token=<key>&web=<site>`; the desktop app registers that
scheme, saves the token + site URL, and switches to hosted mode. Or paste the
key + set `PARAKEET_WEB_URL` manually in the app's Settings.

## Routes

| Route | Purpose |
|---|---|
| `/` | Landing + pricing |
| `/login` | Auth |
| `/dashboard` | Key · credits · documents · preferences · Open-in-app |
| `POST /api/documents/upload` | Ingest a document (auth: session) |
| `POST /api/documents/search` | RAG retrieval (auth: Bearer Parakeet key — desktop) |
| `GET /api/me/key` | Get/mint the user's key (session) |
| `GET /api/me/profile` | Persona + preferences (Bearer key — desktop) |
| `POST /api/me/preferences` | Save preferences (session) |

Deploy to Vercel; set the same env vars there.
