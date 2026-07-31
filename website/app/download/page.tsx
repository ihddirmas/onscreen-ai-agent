import Link from "next/link";

const REPO = "https://github.com/ihddirmas/onscreen-ai-agent";
const RELEASES =
  process.env.NEXT_PUBLIC_RELEASES_URL ||
  `${REPO}/releases/latest/download/OnCUE.exe`;

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
          <a className="btn" href={RELEASES}>Windows (.exe)</a>
          <a className="btn secondary" href={REPO}>macOS (build from source)</a>
        </div>
        <p className="muted" style={{ marginTop: 8, fontSize: "0.85em" }}>
          Linux: run <code>pip install -e .</code> after cloning the repo
        </p>
        <p className="muted" style={{ marginTop: 16 }}>
          <Link href="/dashboard">← Back to dashboard</Link>
        </p>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <span className="tier-badge">Hosted mode</span>
        <h2 style={{ marginTop: 10 }}>No API key needed</h2>
        <p className="muted">
          Log in and OnCUE mints a free license key for you automatically.
          Paste it into Settings and pick &quot;hosted&quot; as your provider.
        </p>
        <Link className="btn" href="/login" style={{ marginTop: 8 }}>
          Log in to get your free key
        </Link>
      </div>
    </div>
  );
}
