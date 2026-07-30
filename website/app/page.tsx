import Link from "next/link";

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
      <div className="nav">
        <div className="brand">🦜 OnCUE</div>
        <div style={{ display: "flex", gap: 12 }}>
          <Link className="btn secondary" href="/login">Log in</Link>
          <Link className="btn" href="/login">Get started</Link>
        </div>
      </div>

      <div className="hero">
        <h1>Your on-screen AI assistant</h1>
        <p>
          Ask about anything on your screen, dictate anywhere, and get answers
          grounded in your own documents — resume, notes, study plans. Hidden
          from screen sharing, powered by fast models.
        </p>
        <Link className="btn" href="/login">Create your account</Link>
      </div>

      <div className="container">
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
      </div>
    </>
  );
}
