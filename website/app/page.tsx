import Link from "next/link";

function MockupWindow({ hotkey }: { hotkey: string }) {
  return (
    <div className="mockup-window">
      <div className="mockup-titlebar">
        <span className="mockup-dot red" />
        <span className="mockup-dot yellow" />
        <span className="mockup-dot green" />
        <span className="mockup-hotkey">{hotkey}</span>
      </div>
      <div className="mockup-content">
        <div className="mockup-line">What does this error mean?</div>
        <div className="mockup-line accent">
          The TypeError on line 42 means you&apos;re passing a string where a
          number is expected — check the function signature.
        </div>
        <div className="mockup-line" style={{ marginTop: 10 }}>
          And how do I fix it?
        </div>
        <div className="mockup-line accent">
          Wrap the input with <code>Number()</code> or parse it at the call
          site.
        </div>
      </div>
    </div>
  );
}

const PERSONAS = [
  {
    tag: "FOR STUDENTS",
    headline: "For late-night study sessions",
    body: "Stuck on a problem set at 2 AM? Ask about anything on your screen — diagrams, equations, code — and get answers grounded in your own notes and reference docs. Dictate in Hinglish, get text at the cursor.",
    bullets: [
      "Screen Q&A for problem sets and readings",
      "Hinglish dictation, no translating to English first",
      "Answers grounded in your uploaded documents",
    ],
    hotkey: "Ctrl+Shift+Space",
  },
  {
    tag: "FOR EARLY-CAREER DEVELOPERS",
    headline: "Debug without losing the thread",
    body: "No more screenshot → alt-tab → ChatGPT → paste → alt-tab-back. Press a hotkey, ask about the error on your screen, and follow up naturally — context stays intact.",
    bullets: [
      "One hotkey replaces the 5-step context-switch cycle",
      "Follow-ups keep your screen context",
      "Keyless cited web search included",
    ],
    hotkey: "Ctrl+Shift+D",
  },
  {
    tag: "FOR INTERVIEW & CALL DAYS",
    headline: "Vivas, interviews, client demos",
    body: "Need to look something up mid-call without going silent or looking away? OnCUE stays invisible to screen sharing and answers in your ear. Private to you on your own calls.",
    bullets: [
      "Invisible on screen share and recordings",
      "Answers via voice, no typing needed",
      "Your data stays yours — not interview evasion, just privacy",
    ],
    hotkey: "Ctrl+Shift+M",
  },
  {
    tag: "FOR ANYONE WHO THINKS IN HINGLISH",
    headline: "Dictate the way you actually talk",
    body: "Hinglish isn't a workaround — it's the default. Speak naturally, and text lands at the cursor in any app. Notes, drafts, replies, all in the mix you actually use.",
    bullets: [
      "Hinglish as the default output, not a mode to enable",
      "Types directly into any app at the cursor",
      "No translation layer — what you say is what you get",
    ],
    hotkey: "Ctrl+Shift+H",
  },
];

const TIERS = [
  {
    name: "Free",
    price: "$0",
    badge: "Get started",
    features: [
      "On-screen AI overlay",
      "Voice + screenshot answers",
      "~$1 of model credits / month",
      "1 reference document",
    ],
  },
  {
    name: "Pro",
    price: "$9",
    badge: "Most popular",
    features: [
      "Everything in Free",
      "~$15 of model credits / month",
      "Unlimited reference documents",
      "Priority models (Claude / GPT)",
    ],
  },
];

export default function Home() {
  return (
    <>
      <nav className="nav">
        <div className="brand">🦜 OnCUE</div>
        <div style={{ display: "flex", gap: 12 }}>
          <Link className="btn secondary" href="/login">Log in</Link>
          <Link className="btn" href="/login">Get started</Link>
        </div>
      </nav>

      <section className="hero">
        <h1>Your on-screen AI assistant</h1>
        <p>
          Ask about anything on your screen, dictate anywhere, and get answers
          grounded in your own documents — resume, notes, study plans. Hidden
          from screen sharing, powered by fast models.
        </p>
        <Link className="btn" href="/login">Create your account</Link>
      </section>

      <section className="container" style={{ textAlign: "center", paddingTop: 80, paddingBottom: 40 }}>
        <div className="speech-bubble">
          <h2>How does OnCUE work?</h2>
        </div>

        <div className="steps">
          <div className="step-card">
            <div className="step-number">01</div>
            <h3>Press a hotkey</h3>
            <p>Ctrl+Shift+Space opens the overlay from any app — no clicking, no searching.</p>
          </div>
          <div className="step-card">
            <div className="step-number">02</div>
            <h3>Ask or dictate</h3>
            <p>Type your question or speak naturally. OnCUE sees your screen and your uploaded docs.</p>
          </div>
          <div className="step-card">
            <div className="step-number">03</div>
            <h3>Get answers instantly</h3>
            <p>The overlay shows cited answers. Dictate follow-ups. Done in seconds, not tabs.</p>
          </div>
        </div>
      </section>

      <section className="pull-quote">
        <h2>That&apos;s really it?</h2>
        <p>
          Yes. No new workflow to learn — just the hotkeys you already reach for.
          Press, ask, or dictate, and the answer streams in before you&apos;d have
          finished alt-tabbing.
        </p>
      </section>

      <section className="container" style={{ paddingBottom: 60 }}>
        {PERSONAS.map((p) => (
          <div className="persona-panel" key={p.tag}>
            <div>
              <span className="persona-tag">{p.tag}</span>
              <h3>{p.headline}</h3>
              <p>{p.body}</p>
              <ul>
                {p.bullets.map((b) => (
                  <li key={b}>{b}</li>
                ))}
              </ul>
            </div>
            <MockupWindow hotkey={p.hotkey} />
          </div>
        ))}
      </section>

      <section className="container">
        <h2 style={{ textAlign: "center", marginBottom: 20 }}>Pricing</h2>
        <div className="grid">
          {TIERS.map((t) => (
            <div className="card" key={t.name}>
              <span className="tier-badge">{t.badge}</span>
              <h2 style={{ marginTop: 10 }}>{t.name}</h2>
              <div className="price">{t.price}<span className="muted" style={{ fontSize: 14 }}> / mo</span></div>
              <ul style={{ paddingLeft: 18, marginTop: 12 }}>
                {t.features.map((f) => (
                  <li key={f} style={{ marginBottom: 6 }}>{f}</li>
                ))}
              </ul>
              <Link className="btn" href="/login" style={{ marginTop: 8 }}>
                {t.name === "Free" ? "Start free" : "Choose Pro"}
              </Link>
            </div>
          ))}
        </div>
        <p className="muted" style={{ textAlign: "center", marginTop: 24 }}>
          Credits are metered by actual model usage. Payments coming soon — Pro
          is a placeholder for now.
        </p>
      </section>

      <section style={{ textAlign: "center", padding: "60px 24px 80px" }}>
        <Link
          className="btn"
          href="/login"
          style={{ fontSize: 16, padding: "14px 32px" }}
        >
          Get started free
        </Link>
      </section>
    </>
  );
}
