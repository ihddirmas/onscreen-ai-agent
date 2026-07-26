"""Design tokens for the light-editorial visual direction (confirmed via
mockup comparison, see docs/superpowers/specs/2026-07-27-reflex-website-redesign-design.md).
Every component pulls colors/fonts/radius/shadow from here — no ad hoc values."""

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
    "mono": "'JetBrains Mono', Consolas, monospace",
}

RADIUS = {"sm": "8px", "md": "14px", "pill": "999px"}

SHADOW_CARD = "0 12px 30px rgba(0,0,0,0.06)"
