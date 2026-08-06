/** OnCUE brand tokens — shared across v0-import landing sections. */
export const ONCUE = {
  /** Desktop HUD surface — matches oncue/ui/theme.py panel */
  surface: "#12121a",
  surfaceDeep: "#09090f",
  hudBorder: "rgba(255, 255, 255, 0.35)",
  hudText: "#e4e4e4",
  hudMuted: "rgba(255, 255, 255, 0.55)",
} as const;

export const HOTKEYS = [
  {
    keys: "Ctrl+Shift+Space",
    title: "Screen Q&A",
    description: "Capture your screen, type a question, get a streamed answer over any app.",
  },
  {
    keys: "Ctrl+Shift+H",
    title: "Chat",
    description: "Text-only follow-ups — no screenshot. Press again to hide the overlay.",
  },
  {
    keys: "Ctrl+Shift+V",
    title: "Voice + screen",
    description: "Hold while you speak; release to send with screen context.",
  },
  {
    keys: "Ctrl+Shift+D",
    title: "Dictate",
    description: "Hold to transcribe into the focused field — Hinglish supported.",
  },
  {
    keys: "Ctrl+Shift+M",
    title: "Meeting audio",
    description: "Hold during a call; ask about what was said after you release.",
  },
] as const;

/** Primary CTA — matches v0 monochrome editorial buttons */
export const BTN_PRIMARY =
  "bg-foreground hover:bg-foreground/90 text-background rounded-full";

/** Section eyebrow line — matches v0 landing sections */
export const SECTION_LINE = "bg-foreground/30";

/** Desktop HUD chrome — matches monochrome overlay theme */
export const HUD_PANEL =
  "rounded-2xl border border-white/25 bg-[#12121a]/95 shadow-2xl backdrop-blur-sm";
