import type { Metadata } from "next";

const SITE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://oncue.app";

export const siteConfig = {
  name: "OnCUE",
  tagline: "An AI buddy on your desktop",
  description:
    "OnCUE is a desktop AI buddy — press a hotkey and ask about anything on your screen, dictate in Hinglish, or get answers grounded in your documents. Private overlay, invisible on screen share.",
  url: SITE_URL,
  keywords: [
    "desktop AI assistant",
    "screen AI",
    "AI buddy",
    "on-screen copilot",
    "Hinglish dictation",
    "voice dictation Windows",
    "screen share invisible overlay",
    "hotkey AI assistant",
    "document grounded AI",
    "meeting audio AI",
  ],
} as const;

export const defaultMetadata: Metadata = {
  metadataBase: new URL(siteConfig.url),
  title: {
    default: `${siteConfig.name} — ${siteConfig.tagline}`,
    template: `%s — ${siteConfig.name}`,
  },
  description: siteConfig.description,
  keywords: [...siteConfig.keywords],
  authors: [{ name: "OnCUE" }],
  creator: "OnCUE",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: siteConfig.url,
    siteName: siteConfig.name,
    title: `${siteConfig.name} — ${siteConfig.tagline}`,
    description: siteConfig.description,
  },
  twitter: {
    card: "summary_large_image",
    title: `${siteConfig.name} — ${siteConfig.tagline}`,
    description: siteConfig.description,
  },
  robots: {
    index: true,
    follow: true,
  },
  alternates: {
    canonical: siteConfig.url,
  },
};

export const faqItems = [
  {
    question: "What is OnCUE?",
    answer:
      "OnCUE is an AI buddy that lives on your desktop. Press a hotkey and it sees what you see — ask about errors, charts, slides, or anything on screen. Dictate in Hinglish, chat without screenshots, or ground answers in your own documents.",
  },
  {
    question: "Is OnCUE watching my screen all the time?",
    answer:
      "No. OnCUE only captures your screen when you press a hotkey (e.g. Ctrl+Shift+Space). Nothing is sent until you trigger it.",
  },
  {
    question: "Is my data private during screen shares?",
    answer:
      "Yes. Enable “Hide from screen sharing” in Settings before Zoom, Meet, or Teams. Viewers won’t see the overlay — only you do.",
  },
  {
    question: "What can OnCUE actually do?",
    answer:
      "Screen Q&A on any visible app, Hinglish dictation into any text field, voice + screen questions, meeting-audio summaries, and document-grounded answers via RAG — all from a floating overlay without alt-tabbing to a browser.",
  },
  {
    question: "Which apps does it work with?",
    answer:
      "Anything on your screen. VS Code, Excel, slides, WhatsApp Web, browsers — if you can see it, OnCUE can answer about it. No plugins required.",
  },
  {
    question: "Do I need an API key?",
    answer:
      "Not for hosted trial mode. Sign in on the dashboard and click “Open OnCUE app” — your license and backend URLs are sent via deep link. Bring your own Groq, Claude, GPT, or Gemini keys anytime in Settings.",
  },
  {
    question: "Is it free?",
    answer:
      "Yes to start. Free tier includes hosted trial credits. Pro unlocks more credits and premium models. BYOK tier lets you use your own API keys with no hosted limits.",
  },
  {
    question: "Windows or Mac?",
    answer:
      "OnCUE ships for Windows and Linux today (Qt overlay + global hotkeys). macOS is on the roadmap.",
  },
] as const;

export function softwareApplicationJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: siteConfig.name,
    applicationCategory: "ProductivityApplication",
    operatingSystem: "Windows, Linux",
    description: siteConfig.description,
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "USD",
    },
  };
}

export function faqPageJsonLd() {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqItems.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    })),
  };
}
