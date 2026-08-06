"""Design tokens for the light-editorial visual direction (confirmed via
mockup comparison, see docs/superpowers/specs/2026-07-27-reflex-website-redesign-design.md).
Every component pulls colors/fonts/radius/shadow from here — no ad hoc values.

Depth/color pass (2026-07-29): the original palette was flat and monochrome
— one accent color, no gradient, no illustration, full-bleed white
throughout. Real user feedback compared it unfavorably against mymind.com's
"How it works" page (colorful gradient hero, alternating full-bleed color
bands, floating app-mockup screenshots with real shadow/depth). This adds a
hero gradient, alternating section-band backgrounds, and a display serif for
headlines — adapting mymind's structural principles (color, depth, layering)
without cloning its exact palette, since OnCUE is a different product with
its own identity."""

# Single source of truth for the product name — every page renders this
# constant, never a literal name string, so a rename is a one-line change.
BRAND_NAME = "OnCUE"

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

# Alternating full-bleed section bands (the mymind-style structural device):
# each band is a dark or tinted panel that content sits inside, giving the
# page real color and rhythm instead of one long white scroll. "dark" reuses
# the ACTUAL desktop overlay's real palette (oncue/ui/theme.py) rather
# than inventing a new dark color — the marketing site's mockups should look
# like the real product, not an approximation of it.
BAND = {
    "dark_bg": "#121218",
    "dark_text": "#f0f0f0",
    "dark_text_muted": "rgba(255, 255, 255, 0.6)",
    "dark_border": "rgba(255, 255, 255, 0.1)",
    "mint_bg": "#e8f3ec",
    "mint_tag_bg": "#cfe8d8",
    "mint_tag_text": "#1f6b42",
    "violet_bg": "#efecf7",
    "violet_tag_bg": "#ded6f2",
    "violet_tag_text": "#4c3a8f",
    "peach_bg": "#faece3",
    "peach_tag_bg": "#f3d6c2",
    "peach_tag_text": "#8a4a1f",
}

# The real desktop-overlay colors (oncue/ui/theme.py), duplicated
# intentionally: the floating "product mockup" cards on the marketing site
# render an actual likeness of the overlay, so they need its real colors,
# not the webapp's own light-editorial palette.
OVERLAY_MOCKUP = {
    "panel_bg": "rgba(18, 18, 24, 0.95)",
    "border": "rgba(120, 200, 120, 0.55)",
    "text": "#f0f0f0",
    "text_muted": "rgba(255, 255, 255, 0.55)",
    "status_green": "#8fd48f",
    "input_bg": "rgba(255, 255, 255, 0.08)",
}

# Soft multi-color blur blobs behind the hero headline — the single biggest
# "premium vs. generic" signal on mymind's page. Cooler/tech-toned (violet /
# teal / green) rather than mymind's warm pink/orange, to fit an AI-copilot
# product and to echo the real overlay's green accent.
HERO_GRADIENT = (
    "radial-gradient(circle at 22% 30%, rgba(143,212,143,0.55), transparent 55%), "
    "radial-gradient(circle at 78% 25%, rgba(124,131,240,0.5), transparent 55%), "
    "radial-gradient(circle at 50% 75%, rgba(94,196,196,0.45), transparent 60%)"
)

FONT = {
    "sans": "'Inter', system-ui, sans-serif",
    "mono": "'JetBrains Mono', Consolas, monospace",
    # Display serif for large headlines only (hero, band section titles) —
    # paired with Inter body text, the classic editorial pairing that reads
    # as considered rather than a single-typeface default.
    "serif": "'Fraunces', Georgia, 'Times New Roman', serif",
}

RADIUS = {"sm": "8px", "md": "14px", "lg": "22px", "pill": "999px"}

SHADOW_CARD = "0 12px 30px rgba(0,0,0,0.06)"
# Stronger shadow for content that should visually float above a colored
# band (the overlay mockups) — a flat drop shadow reads as pasted-on, this
# one has a tighter near shadow plus a soft far one for real depth.
SHADOW_FLOAT = "0 2px 8px rgba(0,0,0,0.12), 0 24px 48px rgba(0,0,0,0.18)"
