"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { browserClient } from "@/lib/supabase-browser";

type Doc = { id: string; filename: string; status: string; created_at: string };

export default function Dashboard(props: {
  email: string;
  tier: string;
  parakeetKey: string | null;
  spend: number;
  maxBudget: number;
  persona: string;
  preferences: string;
  docs: Doc[];
  siteUrl: string;
  ragUrl: string;
}) {
  const router = useRouter();
  const supabase = browserClient();
  const [prefs, setPrefs] = useState(props.preferences);
  const [prefsMsg, setPrefsMsg] = useState("");
  const [uploading, setUploading] = useState(false);
  const [copyMsg, setCopyMsg] = useState("Copy");

  const pct =
    props.maxBudget > 0 ? Math.min(100, (props.spend / props.maxBudget) * 100) : 0;

  const deepLink = props.parakeetKey
    ? `parakeet://connect?token=${encodeURIComponent(props.parakeetKey)}` +
      `&web=${encodeURIComponent(props.siteUrl)}` +
      `&rag=${encodeURIComponent(props.ragUrl)}`
    : "#";

  async function signOut() {
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  }

  async function savePrefs() {
    setPrefsMsg("Saving…");
    await fetch("/api/me/preferences", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ preferences: prefs }),
    });
    setPrefsMsg("Saved ✓");
    setTimeout(() => setPrefsMsg(""), 1500);
  }

  async function upload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const fd = new FormData();
    fd.append("file", file);
    const res = await fetch("/api/documents/upload", { method: "POST", body: fd });
    setUploading(false);
    e.target.value = "";
    if (res.ok) router.refresh();
    else alert("Upload failed: " + (await res.text()));
  }

  function copyKey() {
    if (!props.parakeetKey) return;
    navigator.clipboard.writeText(props.parakeetKey);
    setCopyMsg("Copied ✓");
    setTimeout(() => setCopyMsg("Copy"), 1500);
  }

  return (
    <>
      <div className="nav">
        <div className="brand">🦜 Parakeet</div>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <span className="muted">{props.email}</span>
          <button className="btn secondary" onClick={signOut}>Sign out</button>
        </div>
      </div>

      <div className="container">
        {/* Open in app */}
        <div className="card">
          <h2>Use Parakeet on your computer</h2>
          <p className="muted">
            Launch the desktop app already signed in — no key to paste.
          </p>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 8 }}>
            <a className="btn" href={deepLink}>Open Parakeet app</a>
            <a className="btn secondary" href="/download">Don&apos;t have the app? Download</a>
          </div>
        </div>

        {/* Key + credits */}
        <div className="grid">
          <div className="card">
            <h2>Your Parakeet key <span className="tier-badge">{props.tier}</span></h2>
            <p className="muted">Paste this into the desktop app&apos;s Settings (hosted mode).</p>
            {props.parakeetKey ? (
              <div className="keybox">
                <span>{props.parakeetKey}</span>
                <button className="btn secondary" onClick={copyKey}>{copyMsg}</button>
              </div>
            ) : (
              <p className="muted">Key will appear once the backend is connected.</p>
            )}
          </div>

          <div className="card">
            <h2>Credit usage</h2>
            <div className="meter"><span style={{ width: `${pct}%` }} /></div>
            <p className="muted">
              ${props.spend.toFixed(3)} of ${props.maxBudget.toFixed(2)} used this month
            </p>
          </div>
        </div>

        {/* Documents */}
        <div className="card">
          <h2>Reference documents</h2>
          <p className="muted">
            Upload your resume, notes, or study plan. Parakeet uses them to give
            better, personalized answers.
          </p>
          <label className="btn" style={{ marginTop: 8, cursor: "pointer" }}>
            {uploading ? "Uploading…" : "Upload document"}
            <input type="file" hidden accept=".pdf,.docx,.txt,.md,.csv,.json" onChange={upload} disabled={uploading} />
          </label>
          <ul className="docs" style={{ marginTop: 14 }}>
            {props.docs.length === 0 && <li className="muted">No documents yet.</li>}
            {props.docs.map((d) => (
              <li key={d.id}>
                <span>{d.filename}</span>
                <span className={`pill ${d.status}`}>{d.status}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Preferences */}
        <div className="card">
          <h2>Preferences</h2>
          <p className="muted">
            How should Parakeet answer you? This shapes every answer.
          </p>
          <textarea
            rows={3}
            value={prefs}
            onChange={(e) => setPrefs(e.target.value)}
            placeholder="e.g. Answer coding questions in Python. Keep explanations concise."
          />
          <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 10 }}>
            <button className="btn" onClick={savePrefs}>Save preferences</button>
            <span className="muted">{prefsMsg}</span>
          </div>
          {props.persona && (
            <p className="muted" style={{ marginTop: 14 }}>
              <strong>What Parakeet knows about you:</strong> {props.persona}
            </p>
          )}
        </div>
      </div>
    </>
  );
}
