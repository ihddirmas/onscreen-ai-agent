import Link from "next/link";
import { ProCheckoutButton } from "./ProCheckoutButton";

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
    cta: (
      <Link className="btn" href="/login" style={{ marginTop: 8 }}>
        Start free
      </Link>
    ),
  },
  {
    name: "Pro",
    price: "$9",
    badge: "Most popular",
    features: [
      "Everything in Free",
      "~$15 of model credits / month",
      "Unlimited reference documents",
      "Priority models (Claude / GPT / Gemini)",
    ],
    cta: <ProCheckoutButton />,
  },
];

export const metadata = {
  title: "Pricing — OnCUE",
  description: "OnCUE pricing plans: Free and Pro tiers for your on-screen AI assistant.",
};

export default function PricingPage() {
  return (
    <>
      <div className="nav">
        <div className="brand">OnCUE</div>
        <div style={{ display: "flex", gap: 12 }}>
          <Link className="btn secondary" href="/login">Log in</Link>
          <Link className="btn" href="/login">Get started</Link>
        </div>
      </div>

      <div className="hero">
        <h1>Simple, transparent pricing</h1>
        <p>Start free with 1 trial session. Upgrade when you need more.</p>
      </div>

      <div className="container">
        <div className="grid">
          {TIERS.map((t) => (
            <div className="card" key={t.name}>
              <span className="tier-badge">{t.badge}</span>
              <h2 style={{ marginTop: 10 }}>{t.name}</h2>
              <div className="price">
                {t.price}
                <span className="muted" style={{ fontSize: 14 }}> / mo</span>
              </div>
              <ul style={{ paddingLeft: 18, marginTop: 12 }}>
                {t.features.map((f) => (
                  <li key={f} style={{ marginBottom: 6 }}>{f}</li>
                ))}
              </ul>
              {t.cta}
            </div>
          ))}
        </div>
        <p className="muted" style={{ textAlign: "center", marginTop: 24 }}>
          Credits are metered by actual model usage. Pro checkout is powered by Stripe.
        </p>
        <p className="muted" style={{ textAlign: "center", marginTop: 8 }}>
          Already have an account? <Link href="/login">Log in</Link> to get your key.
        </p>
      </div>
    </>
  );
}
