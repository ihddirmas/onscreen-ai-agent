# mymind-inspired aesthetic: webapp "How it works" section + desktop GUI light theme

Date: 2026-07-29
Status: approved, pending implementation plan

## Background

Reference: https://mymind.com/how — colorful gradient-blob hero with a serif
speech-bubble headline, a "so that's really it?" pull-quote break, and
alternating full-bleed colored panels (one per persona), each with a tag,
serif headline, body copy, checkmark bullets, and a product screenshot mockup.

Two independent surfaces adopt this aesthetic, scoped separately because they
are different tech stacks with different constraints:

1. **Webapp** (`webapp/webapp/`, Reflex/Python→React) — the "How it works"
   section on the landing page.
2. **Desktop GUI** (`parakeet/ui/`, PySide6/Qt) — the settings and onboarding
   dialogs only.

The always-on-top overlay/indicator HUD (`parakeet/ui/overlay.py`,
`parakeet/ui/indicator.py`, themed via `parakeet/ui/theme.py`) is explicitly
**out of scope**. `theme.py`'s existing docstring already establishes why:
it's dark/translucent/minimal-chrome by functional necessity — it must stay
legible over arbitrary screen content and consistent with the
screen-share-invisible positioning. A colorful mymind-style panel there would
actively hurt both properties. This is a constraint, not a stylistic
preference, and this spec does not touch those two files or `theme.py`.

## Part 1 — Webapp: "How it works" section redesign

Scope: `webapp/webapp/components/how_it_works.py` only. No new route — this
replaces the section in place on `landing.py` (same `id="how-it-works"`
anchor, same file). `webapp/webapp/styles/tokens.py` gains new scoped tokens
described below; nothing else in the site (nav, hero, pricing, login, etc.)
changes.

### Layout

1. **Speech-bubble header** — a rounded white/surface bubble reading
   "How OnCUE works?" with a bubble tail, sitting on a soft gradient-blob
   background. Mirrors mymind's hero treatment.
2. **3-step mechanism strip** — the existing 3 numbered steps (hotkey →
   capture → overlay) are kept, restyled as compact cards directly under the
   header rather than removed. Copy is unchanged (already sourced from the
   copy-reviewed campaign doc).
3. **Pull-quote break** — a short, center-aligned "That's really it?" beat:
   - Heading: "That's really it?"
   - Body: "Yes. No new workflow to learn — just the hotkeys you already
     reach for. Press, ask, or dictate, and the answer streams in before
     you'd have finished alt-tabbing."
4. **4 alternating audience panels**, full-bleed, each with: a small
   all-caps tag pill, a serif headline, 2-3 sentences of body copy, 2-3
   checkmark bullets, and a CSS-built overlay mockup on the opposite side (see
   "Screenshot mockups" below — no fabricated product screenshots).
5. **Closing CTA** — center pill button reusing the existing "Get started
   free" link treatment and href (`/login`). No new claims, no new copy.

### Persona panels (content, grounded in
`.claude/campaigns/parakeet-launch/landing-page.md` and `positioning.md` —
no new marketing claims invented)

| # | Tag | Headline | Angle | Source |
|---|-----|----------|-------|--------|
| 1 | FOR STUDENTS | "For late-night study sessions" | Screen Q&A for problem sets + Hinglish dictation for notes, no alt-tab, no translating to English first | Problem #1, #2; Solution #1, #2 |
| 2 | FOR EARLY-CAREER DEVELOPERS | "Debug without losing the thread" | The screenshot → alt-tab → ChatGPT → paste → alt-tab-back cycle, replaced by one hotkey; follow-ups keep screen context; keyless cited web search | Problem #1; Solution #1; Features #2, #4 |
| 3 | FOR INTERVIEW & CALL DAYS | "Vivas, interviews, client demos" | Reuses the exact copy-reviewed line: needing to look something up mid-call without going silent or looking away. Privacy framed as "stays private to you on your own calls" (matches `hero.py`'s existing phrasing) — explicitly NOT interview/exam-evasion framing, per the positioning doc's standing guardrail | Problem #3; Solution #3; positioning.md guardrail |
| 4 | FOR ANYONE WHO THINKS IN HINGLISH | "Dictate the way you actually talk" | Hinglish is the default output, not a workaround; text lands at the cursor in any app | Solution #2; Features #1 |

Panel background colors alternate: `panel_navy`, `panel_pink`,
`panel_lavender`, `panel_mint` (defined below), in that order. Text color
flips per panel (light text on `panel_navy`, dark `tokens.COLOR["text"]` on
the three light panels).

### Screenshot mockups

No real product screenshots exist yet (`webapp/webapp/assets/` is empty, and
`hero.py` already establishes the "don't reference a fabricated/broken asset"
rule with its "Demo video coming soon" placeholder). Each panel's mockup side
is a CSS-built stand-in: a small rounded "window" with a title bar reading
the relevant hotkey (e.g. "Ctrl+Shift+Space") and a couple of lines of
placeholder chat-style text, styled with the existing `tokens.RADIUS` /
`tokens.SHADOW_CARD` values. Not a real screenshot, not claimed to be one.

### New tokens (`webapp/webapp/styles/tokens.py`)

```python
HOW_ACCENT = {
    "gradient": "radial-gradient(circle at 30% 30%, #ffd7c2 0%, #f3c9e6 35%, #c9c2f2 60%, transparent 80%)",
    "panel_navy": "#1c2230",
    "panel_pink": "#fbe4e6",
    "panel_lavender": "#eceaf7",
    "panel_mint": "#e3f2ea",
    "tag_text": "#c65b3d",  # warm terracotta
}
HOW_SERIF = "'Georgia', 'Iowan Old Style', serif"  # display accent, headline only
```

These are scoped additions alongside the existing `COLOR`/`FONT`/`RADIUS`
dicts — not a replacement of them. Only the bubble headline and panel
headlines use `HOW_SERIF`; body copy, nav, buttons, and the rest of the site
keep `tokens.FONT["sans"]` and the existing monochrome `tokens.COLOR` system
untouched.

`HOW_ACCENT`'s `panel_navy` / `tag_text` values are shared **by literal
value** with the desktop GUI's `light_theme.py` (Part 2) so the two surfaces
read as the same product, even though they live in different tech stacks and
can't share an import.

## Part 2 — Desktop GUI: settings & onboarding light theme

Scope: `parakeet/ui/settings.py` and `parakeet/ui/onboarding.py` only. New
file `parakeet/ui/light_theme.py`. Does **not** touch `parakeet/ui/theme.py`,
`overlay.py`, or `indicator.py` (see Background — functional constraint, not
a style choice).

### New module: `parakeet/ui/light_theme.py`

```python
"""Light theme for regular (non-HUD) dialogs: settings and onboarding.

Deliberately separate from theme.py (the dark/translucent overlay HUD theme)
— these are normal top-level windows with no legibility-over-arbitrary-
content or screen-share-invisibility constraints, so they're free to carry
the product's mymind-inspired brand identity. Palette values are shared BY
VALUE (not import — different tech stack) with webapp/webapp/styles/tokens.py's
HOW_ACCENT dict; keep the two in sync if either changes.
"""

LIGHT_COLOR = {
    "bg": "#fbf6f1",
    "surface": "#ffffff",
    "border": "#ece5dc",
    "text": "#1a1a1a",
    "text_muted": "#6b6b6b",
    "accent": "#c65b3d",       # matches webapp HOW_ACCENT["tag_text"]
    "accent_hover": "#b04f34",
    "panel_navy": "#1c2230",   # matches webapp HOW_ACCENT["panel_navy"]
}

LIGHT_FONT_HEADING = "Georgia"  # Windows-only build; safe per positioning.md guardrail

LIGHT_QSS = """
QDialog { background-color: %(bg)s; }
QGroupBox {
    border: 1px solid %(border)s; border-radius: 10px;
    margin-top: 10px; padding-top: 12px; font-weight: 600;
}
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
QLineEdit, QComboBox {
    border: 1px solid %(border)s; border-radius: 6px; padding: 4px 8px;
    background-color: %(surface)s;
}
QPushButton {
    border-radius: 8px; padding: 8px 16px; font-weight: 600;
}
QPushButton#primary {
    background-color: %(accent)s; color: white; border: none;
}
QPushButton#primary:hover { background-color: %(accent_hover)s; }
QPushButton#secondary {
    background-color: transparent; color: %(text)s; border: 1px solid %(border)s;
}
""" % LIGHT_COLOR
```

Exact QSS selectors/properties may be adjusted during implementation to fit
what PySide6's QSS subset actually supports — the palette values and the
primary/secondary button distinction are the parts that must be preserved.

### `onboarding.py` changes

- `self.setStyleSheet(LIGHT_QSS)` in `__init__`.
- Title label (`"How do you want to get started?"`) gets
  `font-family: Georgia; font-size: 20px; font-weight: 600;` — the serif
  accent, echoing the webapp bubble headline, since this is the first-run
  brand moment.
- `self._trial_btn` gets `setObjectName("primary")` (filled terracotta pill —
  it's the recommended path, no API key needed).
- `key_btn` gets `setObjectName("secondary")` (outline button).
- No copy changes, no behavior changes — `_start_trial` / `_use_own_key`
  logic untouched.

### `settings.py` changes

- `self.setStyleSheet(LIGHT_QSS)` in `__init__`.
- No per-widget object names beyond the Save button
  (`QDialogButtonBox.StandardButton.Save` gets `setObjectName("primary")`
  where accessible) — deliberately calmer than onboarding since this is a
  dense config form, not a brand moment.
- All functional widgets (hotkey fields, checkboxes, password-masked key
  fields, provider/model combo boxes) unchanged — styling only.

## Testing / verification

- **Webapp**: start the Reflex dev server (`reflex run`, per the
  `reflex-process-management` skill) and visually check the redesigned
  section at both mobile (375px) and desktop (1440px) widths, plus confirm
  the rest of the landing page (hero, social proof, pricing) is visually
  unaffected.
- **Desktop GUI**: launch the app (or a minimal script that constructs
  `SettingsDialog`/`OnboardingDialog` standalone) and visually confirm both
  dialogs render with the new theme, all fields remain functional (typing,
  combo selection, save round-trip), and the overlay/indicator HUD is
  unchanged (spot-check `overlay.py`/`indicator.py` still import only from
  `theme.py`, not `light_theme.py`).
- No unit tests are needed for pure QSS styling or Reflex `rx.box`/`rx.text`
  layout — this is a visual-only change to non-critical-path UI. Existing
  `settings.py`/`onboarding.py`/`how_it_works.py` behavior (config save,
  onboarding signal emission, hotkey copy accuracy) must not regress —
  verify by re-reading the diffed files against this spec's "no behavior
  change" notes above.
