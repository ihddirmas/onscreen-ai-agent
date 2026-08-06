import Link from "next/link";

const MARQUEE = [
  { stat: "1 hotkey", label: "replaces the alt-tab cycle", tag: "DEVELOPERS" },
  { stat: "Hinglish", label: "dictation at your cursor", tag: "STUDENTS" },
  { stat: "<1s", label: "to first token on screen", tag: "CALLS" },
  { stat: "Private", label: "invisible on screen share", tag: "DEMOS" },
];

const FEATURES = [
  {
    num: "01",
    title: "Screen-aware answers",
    body: "Press a hotkey and ask about whatever is on your screen — errors, diagrams, slides. No screenshot → paste → alt-tab back.",
  },
  {
    num: "02",
    title: "Hinglish-native dictation",
    body: "Hold a key and speak the way you actually talk. Text lands in WhatsApp, Gmail, or any focused field — no translating to English first.",
  },
  {
    num: "03",
    title: "Grounded in your documents",
    body: "Upload your resume, notes, or study plan. Answers pull from your reference docs via RAG, not generic web fluff.",
  },
  {
    num: "04",
    title: "Invisible when it matters",
    body: "The overlay stays off screen recordings and shares by default — private during your own demos, calls, and presentations.",
  },
];

const STEPS = [
  {
    num: "I",
    title: "Press your hotkey",
    body: "Ctrl+Shift+Space for screen Q&A, Ctrl+Shift+D to dictate, Ctrl+Shift+M during a call.",
  },
  {
    num: "II",
    title: "OnCUE captures context",
    body: "A screenshot, your voice, or meeting audio — whichever mode you triggered.",
  },
  {
    num: "III",
    title: "Answer streams on the overlay",
    body: "A floating transparent window with follow-ups, or text typed straight into your app.",
  },
];

const TIERS = [
  {
    num: "01",
    name: "Free",
    desc: "For trying hosted mode",
    price: "$0",
    period: "/month",
    badge: null,
    features: [
      "On-screen AI overlay",
      "Voice + screenshot answers",
      "~$1 hosted credits / month",
      "1 reference document",
    ],
    cta: "Start free",
    href: "/login",
    highlight: false,
  },
  {
    num: "02",
    name: "Pro",
    desc: "For daily power users",
    price: "$9",
    period: "/month",
    badge: "Most popular",
    features: [
      "Everything in Free",
      "~$15 hosted credits / month",
      "Unlimited reference documents",
      "Claude, GPT & Gemini models",
    ],
    cta: "Get Pro",
    href: "/login",
    highlight: true,
  },
];

function OverlayMockup() {
  return (
    <div className="w-full max-w-md rounded-xl border border-foreground/10 bg-[#121218] p-4 shadow-2xl">
      <div className="mb-3 flex items-center gap-2 text-[10px] font-mono text-white/40">
        <span className="h-2 w-2 rounded-full bg-red-500" />
        <span className="h-2 w-2 rounded-full bg-yellow-500" />
        <span className="h-2 w-2 rounded-full bg-green-500" />
        <span className="ml-auto">Ctrl+Shift+Space</span>
      </div>
      <p className="text-sm text-white/50">summarize this chart for my standup</p>
      <p className="mt-2 text-sm leading-relaxed text-[#e4e4e4]">
        Signups dipped 18% after Tuesday — mostly mobile onboarding at the verify-phone step.
        Consider shortening OTP or adding WhatsApp login.
      </p>
    </div>
  );
}

export default function LandingPage() {
  return (
    <main className="noise-overlay relative min-h-screen overflow-x-hidden">
      {/* Nav */}
      <header className="fixed top-0 left-0 right-0 z-50 border-b border-transparent bg-background/80 backdrop-blur-md">
        <nav className="mx-auto flex h-20 max-w-[1400px] items-center justify-between px-6 lg:px-8">
          <Link href="/" className="font-display text-2xl tracking-tight">
            OnCUE
          </Link>
          <div className="hidden items-center gap-10 md:flex">
            <a href="#features" className="text-sm text-foreground/70 transition hover:text-foreground">
              Features
            </a>
            <a href="#how-it-works" className="text-sm text-foreground/70 transition hover:text-foreground">
              How it works
            </a>
            <a href="#pricing" className="text-sm text-foreground/70 transition hover:text-foreground">
              Pricing
            </a>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/login" className="hidden text-sm text-foreground/70 hover:text-foreground sm:block">
              Sign in
            </Link>
            <Link href="/login" className="btn-primary !h-10 !px-6 !text-sm">
              Get started
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero */}
      <section className="relative flex min-h-screen flex-col justify-center overflow-hidden pt-20">
        <div className="pointer-events-none absolute inset-0 opacity-30">
          {Array.from({ length: 8 }).map((_, i) => (
            <div
              key={`h-${i}`}
              className="absolute h-px bg-foreground/10"
              style={{ top: `${(i + 1) * 12.5}%`, left: 0, right: 0 }}
            />
          ))}
          {Array.from({ length: 12 }).map((_, i) => (
            <div
              key={`v-${i}`}
              className="absolute w-px bg-foreground/10"
              style={{ left: `${(i + 1) * 8.33}%`, top: 0, bottom: 0 }}
            />
          ))}
        </div>

        <div className="relative z-10 mx-auto max-w-[1400px] px-6 py-32 lg:px-12 lg:py-40">
          <div className="mb-8 animate-in">
            <span className="section-label">The on-screen AI copilot</span>
          </div>
          <h1 className="font-display text-[clamp(2.5rem,10vw,7rem)] leading-[0.95] tracking-tight animate-in">
            <span className="block">Ask your screen.</span>
            <span className="block text-muted-foreground">Skip the alt-tab.</span>
          </h1>
          <div className="mt-12 grid items-end gap-12 lg:grid-cols-2 lg:gap-24">
            <p className="max-w-xl text-xl leading-relaxed text-muted-foreground lg:text-2xl animate-in">
              Dictate in Hinglish, ask about anything visible, and get answers grounded in your own
              documents — from a private overlay that stays off screen shares.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row animate-in">
              <Link href="/login" className="btn-primary">
                Start free
                <span aria-hidden>→</span>
              </Link>
              <a href="#how-it-works" className="btn-secondary">
                See how it works
              </a>
            </div>
          </div>
          <div className="mt-16 flex justify-center lg:justify-end animate-in">
            <OverlayMockup />
          </div>
        </div>

        {/* Marquee */}
        <div className="absolute bottom-8 left-0 right-0 overflow-hidden border-t border-foreground/10 py-6">
          <div className="flex animate-marquee gap-16 whitespace-nowrap">
            {[...MARQUEE, ...MARQUEE].map((item, i) => (
              <div key={i} className="flex shrink-0 items-baseline gap-4">
                <span className="font-display text-4xl lg:text-5xl">{item.stat}</span>
                <span className="text-sm text-muted-foreground">
                  {item.label}
                  <span className="mt-1 block font-mono text-xs">{item.tag}</span>
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 lg:py-32">
        <div className="mx-auto max-w-[1400px] px-6 lg:px-12">
          <div className="mb-16 lg:mb-24">
            <span className="section-label mb-6">Capabilities</span>
            <h2 className="font-display text-4xl tracking-tight lg:text-6xl">
              Everything you need.
              <br />
              <span className="text-muted-foreground">Nothing you don&apos;t.</span>
            </h2>
          </div>
          <div>
            {FEATURES.map((f) => (
              <div key={f.num} className="group feature-row">
                <span className="shrink-0 font-mono text-sm text-muted-foreground">{f.num}</span>
                <div className="grid flex-1 items-center gap-8 lg:grid-cols-2">
                  <div>
                    <h3 className="mb-4 font-display text-3xl transition group-hover:translate-x-2 lg:text-4xl">
                      {f.title}
                    </h3>
                    <p className="text-lg leading-relaxed text-muted-foreground">{f.body}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Process */}
      <section id="how-it-works" className="bg-foreground py-24 text-background lg:py-32">
        <div className="mx-auto max-w-[1400px] px-6 lg:px-12">
          <div className="mb-16">
            <span className="inline-flex items-center gap-3 font-mono text-sm text-background/50">
              <span className="h-px w-8 bg-background/30" />
              Process
            </span>
            <h2 className="mt-6 font-display text-4xl tracking-tight lg:text-6xl">
              Three steps.
              <br />
              <span className="text-background/50">Zero context switching.</span>
            </h2>
          </div>
          <div className="grid gap-12 lg:grid-cols-3">
            {STEPS.map((s) => (
              <div key={s.num} className="border-t border-background/20 pt-8">
                <span className="font-mono text-sm text-background/50">{s.num}</span>
                <h3 className="mt-4 font-display text-2xl">{s.title}</h3>
                <p className="mt-3 leading-relaxed text-background/60">{s.body}</p>
              </div>
            ))}
          </div>
          <div className="mt-16 rounded-xl border border-background/20 bg-background/5 p-6 font-mono text-sm">
            <div className="text-background/40">oncue://connect</div>
            <pre className="mt-2 overflow-x-auto text-background/80">
{`# One click from your dashboard — no API keys to paste
oncue://connect?token=…&web=…&rag=…&backend=…`}
            </pre>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 lg:py-32">
        <div className="mx-auto max-w-[1400px] px-6 lg:px-12">
          <div className="mb-16 text-center">
            <span className="section-label mb-6 justify-center">Pricing</span>
            <h2 className="font-display text-4xl tracking-tight lg:text-6xl">
              Simple, transparent pricing
            </h2>
            <p className="mx-auto mt-4 max-w-lg text-muted-foreground">
              Start free with hosted models. Upgrade when you need Claude, GPT, or Gemini.
            </p>
          </div>
          <div className="mx-auto grid max-w-4xl gap-8 md:grid-cols-2">
            {TIERS.map((t) => (
              <div
                key={t.name}
                className={`relative rounded-2xl border p-8 ${
                  t.highlight
                    ? "border-foreground bg-foreground text-background"
                    : "border-foreground/10 bg-background"
                }`}
              >
                {t.badge && (
                  <span className="absolute -top-3 left-8 rounded-full bg-background px-3 py-1 text-xs font-medium text-foreground">
                    {t.badge}
                  </span>
                )}
                <span className="font-mono text-sm opacity-60">{t.num}</span>
                <h3 className="mt-2 font-display text-3xl">{t.name}</h3>
                <p className="mt-1 text-sm opacity-70">{t.desc}</p>
                <div className="mt-6 flex items-baseline gap-1">
                  <span className="font-display text-5xl">{t.price}</span>
                  <span className="text-sm opacity-60">{t.period}</span>
                </div>
                <ul className="mt-8 space-y-3 text-sm">
                  {t.features.map((f) => (
                    <li key={f} className="flex gap-2">
                      <span className="opacity-50">—</span>
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href={t.href}
                  className={`mt-8 inline-flex w-full items-center justify-center rounded-full py-3 text-sm font-medium ${
                    t.highlight
                      ? "bg-background text-foreground hover:bg-background/90"
                      : "bg-foreground text-background hover:bg-foreground/90"
                  }`}
                >
                  {t.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-foreground/10 py-24 lg:py-32">
        <div className="mx-auto max-w-[1400px] px-6 text-center lg:px-12">
          <h2 className="font-display text-4xl tracking-tight lg:text-6xl">
            Ready to stay in flow?
          </h2>
          <p className="mx-auto mt-4 max-w-lg text-muted-foreground">
            Download the desktop app, sign in once, and press your first hotkey.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link href="/login" className="btn-primary">
              Start building free
            </Link>
            <Link href="/download" className="btn-secondary">
              Download app
            </Link>
          </div>
          <p className="mt-6 text-sm text-muted-foreground">No API key required for hosted mode</p>
        </div>
      </section>

      <footer className="border-t border-foreground/10 py-8 text-center text-sm text-muted-foreground">
        © OnCUE
      </footer>
    </main>
  );
}
