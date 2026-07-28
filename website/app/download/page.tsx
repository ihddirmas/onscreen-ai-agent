import Link from "next/link";

export default function DownloadPage() {
  return (
    <div className="container" style={{ maxWidth: 560, marginTop: 60 }}>
      <div className="card">
        <h2>Download Parakeet</h2>
        <p className="muted">
          Install the desktop app, then click &quot;Open Parakeet app&quot; on your
          dashboard to sign in automatically.
        </p>
        <div style={{ display: "flex", gap: 12, marginTop: 12 }}>
          <a className="btn" href="#">Windows (.exe)</a>
          <a className="btn secondary" href="#">macOS (soon)</a>
        </div>
        <p className="muted" style={{ marginTop: 16 }}>
          <Link href="/dashboard">← Back to dashboard</Link>
        </p>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <span className="tier-badge">Hosted cohort</span>
        <h2 style={{ marginTop: 10 }}>Want the meeting copilot without your own API key?</h2>
        <p className="muted">
          Log in and Parakeet mints a free license key for you automatically —
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
