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
    </div>
  );
}
