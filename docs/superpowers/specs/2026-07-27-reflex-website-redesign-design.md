# Reflex website redesign — conversion, retention, tutorial

Status: approved for planning
Branch: `reflex-website`

## Problem

Parakeet's marketing/account site (`website/`, Next.js + Supabase JS) is
functionally complete but has three gaps:

1. **UI/UX** reads as a generic dark dashboard template — flat cards, no
   hierarchy, no product visuals.
2. **Conversion**: the landing page asks visitors to create an account
   without ever showing them the product. No social proof.
3. **Tutorial**: nothing in the funnel explains how Parakeet works — not on
   the landing page, and not inside the desktop app on first launch.
4. **Retention**: the dashboard is a blank slate after signup — no guided
   next step, so activation (download → connect → first real use) has no
   scaffolding.

## Scope

**In scope (this spec):**
- A new Reflex (Python) app, `webapp/`, built **alongside** the existing
  `website/` — not a cutover. `website/` keeps running until `webapp/`
  reaches parity and a separate decision is made to switch.
- Same Supabase project and schema, accessed via `supabase-py` (auth,
  Postgres, storage) instead of the Supabase JS client. No data migration.
- Full functional parity with today's site (landing, login/signup incl.
  Google OAuth, download, dashboard: key/credits, document upload,
  preferences) plus:
  - A real product demo and "how it works" section on the landing page
    (conversion + website-side tutorial content)
  - Honest social proof (use-case quotes, not fabricated reviews)
  - An onboarding checklist on the dashboard (retention)
- Visual direction: **light editorial / product-led** (Linear/Raycast-style
  light SaaS), confirmed via mockup comparison — see
  `.superpowers/brainstorm/28195-1785074682/content/visual-style.html`.

**Explicitly deferred (separate specs):**
- The in-app PySide6 first-run tutorial for the desktop overlay app
  (`parakeet/ui/`) — different codebase, own design pass.
- Actually cutting `website/` over to `webapp/` in production.
- Payments (stays a placeholder, as today).
- Backend-verified "first hotkey used" signal for the onboarding checklist
  (would require changes to `backend/`, the LiteLLM proxy) — the checklist
  uses a simpler client-side signal instead (see below).

## Architecture

```
webapp/
├── rxconfig.py
├── webapp/
│   ├── webapp.py               # app entrypoint, page registration
│   ├── states/
│   │   ├── auth_state.py       # session, sign in/up/out, Google OAuth
│   │   ├── dashboard_state.py  # key, spend, docs, preferences, checklist
│   │   └── upload_state.py     # rx.upload handler + pipeline
│   ├── pages/
│   │   ├── landing.py
│   │   ├── login.py
│   │   ├── download.py
│   │   └── dashboard.py
│   ├── components/             # nav, hero, pricing_card, checklist, demo
│   ├── styles/
│   │   └── tokens.py           # colors, fonts, radius, shadow tokens
│   └── services/
│       ├── supabase.py         # supabase-py client factory (server-side)
│       ├── litellm.py          # httpx: mint_key, get_spend (mirrors lib/litellm.ts)
│       └── documents.py        # extract text, chunk, call Edge Function to embed
```

**Auth & session:** `supabase-py`'s client handles sign-up / sign-in /
Google OAuth against the existing Supabase project. The session (access +
refresh token) is stored in an `rx.Cookie`, not `localStorage` — not
reachable from JS, a security improvement over the current browser-side
Supabase client.

**No separate API routes.** Reflex event handlers (async `State` methods)
replace the four Next.js API routes directly:

| Today (Next.js) | Reflex equivalent |
|---|---|
| `app/api/documents/upload/route.ts` | `UploadState.handle_upload` (`rx.upload`) |
| `app/api/documents/search/route.ts` | `DashboardState.search_documents` |
| `app/api/me/key/route.ts` | `DashboardState.get_or_mint_key` |
| `app/api/me/preferences/route.ts`, `.../profile/route.ts` | `DashboardState.save_preferences` / profile methods |

The upload pipeline (extract → chunk → embed → index → refresh persona)
keeps calling the **existing Supabase Edge Function** for embeddings
unchanged — it's already a language-agnostic HTTP endpoint. Only the
calling language changes (Python `httpx`/`pypdf`/`python-docx` instead of
Node). The LiteLLM admin API calls (`mint_key`, `get_spend`) are a
line-for-line port of `lib/litellm.ts` using `httpx`.

## Visual design system

```python
# webapp/webapp/styles/tokens.py
COLOR = {
    "bg": "#fbfaf8",
    "surface": "#ffffff",
    "border": "#ececea",
    "text": "#1a1a1a",
    "text_muted": "#6b6b6b",
    "accent": "#1a1a1a",
    "accent_soft": "#f2f1ee",
    "success": "#2f9e5c",
    "warning": "#c98a2c",
    "error": "#c94f4f",
}
FONT = {
    "sans": "'Inter', system-ui, sans-serif",
    "mono": "'JetBrains Mono', Consolas, monospace",  # hotkeys/keys only
}
RADIUS = {"sm": "8px", "md": "14px", "pill": "999px"}
SHADOW_CARD = "0 12px 30px rgba(0,0,0,0.06)"
```

Design qualities this targets: scale contrast (26px→48px headline vs 13px
body), intentional spacing rhythm (not uniform card padding everywhere),
depth via soft shadow + layered white-on-off-white surfaces, a deliberate
type pairing (monospace reserved for hotkeys/keys so it reads purposeful),
semantic color (status pills colored by meaning, not decoration), and
designed hover/focus states (pill buttons lift + darken on hover, visible
focus rings for keyboard nav). The 🦜 wordmark and "always-on-top overlay"
positioning are kept — this re-executes the brand, it doesn't replace it.

## Pages

**Landing (`/`)**
- Nav: wordmark, Log in, Get started (pill button)
- Hero: headline + subhead + primary CTA + a **real demo** — screen-recorded
  GIF/video of the overlay in actual use, autoplay muted + looping. Replaces
  the current text-only hero; this is the single highest-leverage conversion
  change (visitors currently never see the product before being asked to
  sign up).
- **How it works** (website-side tutorial content): 3-step strip — press
  hotkey → Parakeet reads screen → answer appears in overlay — each step
  with a short clip or annotated screenshot.
- **Social proof**: honest placeholders since no real testimonials exist
  yet — a "Built for" row (student / developer / researcher use-cases, one
  quote each) rather than fabricated star ratings. Swap for real
  testimonials once collected.
- Pricing: existing Free/Pro cards, restyled, same content/logic.
- Footer: minimal.

**Login (`/login`)** — same email/password + Google OAuth flow, restyled as
a centered card. No functional change.

**Download (`/download`)** — same flow, restyled.

**Dashboard (`/dashboard`)** — retention lives here:
- **Onboarding checklist**, shown only while incomplete, dismisses once all
  steps are done:
  1. Download the app
  2. Open Parakeet app (deep link) — marked done on click
  3. Upload a reference document — marked done when a doc reaches `ready`
  4. Try your first hotkey — marked done via the deep-link click itself
     (simplified per scope decision above; no backend signal)
- Existing cards (key + credit meter, documents, preferences) restyled to
  the new tokens, same functionality, same tables. No schema changes.

## Error handling

- Auth errors (bad password, existing email, OAuth denial) surface inline
  on the login card, matching today's behavior.
- Upload pipeline failures flip `documents.status` to `error` (existing
  behavior) and the dashboard adds a **retry action** on the error pill
  (new — today it only displays the error with no recourse).
- Edge Function / LiteLLM network or 5xx errors are caught in the service
  layer and surfaced as a toast ("Couldn't reach Parakeet's servers — try
  again"), never a raw stack trace.
- Deep link with no app installed: if clicking "Open Parakeet app" doesn't
  trigger a visibility change within ~1.5s, show a contextual "Don't have
  the app yet? Download" prompt inline.

## Testing

**Hard requirement: nothing is committed without having actually been run
and clicked through — not just type-checked or lint-clean.**

- Every page manually exercised via `reflex run` in a real browser before
  any commit: signup, login, Google OAuth, upload, checklist progression,
  error states (bad upload, wrong password).
- Playwright E2E for the critical path: land → sign up → see checklist →
  upload a doc → see it reach `ready` → checklist step ticks.
- Unit tests for `services/documents.py` (chunking) and `services/litellm.py`
  (key mint / spend parsing) — pure functions, no live network in unit
  tests.
- No screenshots or "looks right" claims stand in for actually running the
  flow.

## Out of scope reminders

- No changes to `backend/` (LiteLLM proxy) or the Supabase Edge Function.
- No changes to `parakeet/` (desktop app) — that's the next spec.
- No production cutover — `website/` keeps serving traffic until a separate
  decision is made.
