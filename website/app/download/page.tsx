import Link from "next/link";

export default function DownloadPage() {
  return (
    <div className="container" style={{ maxWidth: 560, marginTop: 60 }}>
      <div className="card">
        <h2>Download OnCUE</h2>
        <p className="muted">
          Install the desktop app, then click &quot;Open OnCUE app&quot; on your
          dashboard to sign in automatically.
        </p>
        <div style={{ display: "flex", gap: 12, marginTop: 12 }}>
          <a className="btn" href="https://github.com/yashthenuia/onscreen-ai-agent/releases">Windows (.exe)</a>
          <a className="btn secondary" href="https://github.com/yashthenuia/onscreen-ai-agent">macOS (build from source)</a>
        </div>
        <p className="muted" style={{ marginTop: 8, fontSize: "0.85em" }}>
          Linux: run <code>pip install -e .</code> after cloning the repo
        </p>
        <p className="muted" style={{ marginTop: 16 }}>
          <Link href="/dashboard">← Back to dashboard</Link>
        </p>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <span className="tier-badge">Hosted cohort</span>
        <h2 style={{ marginTop: 10 }}>Want the meeting copilot without your own API key?</h2>
        <p className="muted">
          Log in and OnCUE mints a free license key for you automatically —
          no provider key, no separate signup. Paste it into Settings and
          pick &quot;hosted&quot; as your provider.
        </p>
        <p className="muted">
          Priority models and a larger usage budget (Pro) are opening to a
          limited first cohort as we finish billing — log in now and you&apos;ll
          be first in line when it&apos;s ready.
        </p>
        <Link className="btn" href="/login" style={{ marginTop: 8 }}>
          Log in to get your free key
        </Link>
      </div>
    </div>
  );
}
