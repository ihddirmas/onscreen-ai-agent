"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { browserClient } from "@/lib/supabase-browser";

type Doc = { id: string; filename: string; status: string; created_at: string };

export default function Dashboard(props: {
  email: string;
  tier: string;
  oncueKey: string | null;
  spend: number;
  maxBudget: number;
  persona: string;
  preferences: string;
  sessionCount: number;
  trialUsed: boolean;
  trialRemaining: number;
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
  const [deleting, setDeleting] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<string[] | null>(null);
  const [searching, setSearching] = useState(false);

  const pct =
    props.maxBudget > 0 ? Math.min(100, (props.spend / props.maxBudget) * 100) : 0;

  const deepLink = props.oncueKey
    ? `oncue://connect?token=${encodeURIComponent(props.oncueKey)}` +
      `&web=${encodeURIComponent(props.siteUrl)}` +
      `&rag=${encodeURIComponent(props.ragUrl)}`
    : "#";

  async function signOut() {
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  }

  async function savePrefs() {
    setPrefsMsg("Saving...");
    await fetch("/api/me/preferences", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ preferences: prefs }),
    });
    setPrefsMsg("Saved ok");
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
    else {
      const err = await res.json().catch(() => ({ error: res.statusText }));
      alert("Upload failed: " + (err.error || res.statusText));
    }
  }

  async function deleteDoc(id: string) {
    setDeleting(id);
    await fetch("/api/documents/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });
    setDeleting(null);
    router.refresh();
  }

  async function searchDocs() {
    if (!searchQuery.trim()) return;
    setSearching(true);
    setSearchResults(null);
    try {
      const res = await fetch("/api/documents/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: res.statusText }));
        alert("Search failed: " + (err.error || res.statusText));
        return;
      }
      const data = await res.json();
      setSearchResults(data.passages || []);
    } catch (e: any) {
      alert("Search failed: " + e.message);
    } finally {
      setSearching(false);
    }
  }

  function copyKey() {
    if (!props.oncueKey) return;
    navigator.clipboard.writeText(props.oncueKey);
    setCopyMsg("Copied");
    setTimeout(() => setCopyMsg("Copy"), 1500);
  }

  return (
    <>
      <div className="nav">
        <div className="brand">OnCUE</div>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <span className="muted">{props.email}</span>
          <button className="btn secondary" onClick={signOut}>Sign out</button>
        </div>
      </div>

      <div className="container">
        <div className="card">
          <h2>Use OnCUE on your computer</h2>
          <p className="muted">
            Launch the desktop app already signed in.
          </p>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 8 }}>
            <a className="btn" href={deepLink}>Open OnCUE app</a>
            <a className="btn secondary" href="/download">Download the app</a>
          </div>
        </div>

        <div className="grid">
          <div className="card">
            <h2>Your OnCUE key <span className="tier-badge">{props.tier}</span></h2>
            <p className="muted">Paste this into the desktop app Settings.</p>
            {props.oncueKey ? (
              <div className="keybox">
                <span>{props.oncueKey}</span>
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

          {props.trialRemaining > 0 && (
            <div className="card">
              <h2>Trial status</h2>
              <p className="muted">
                You have <strong>{props.trialRemaining} trial session{props.trialRemaining > 1 ? "s" : ""}</strong> remaining.
              </p>
              <a className="btn secondary" href="/pricing" style={{ marginTop: 8, display: "inline-block" }}>View pricing</a>
            </div>
          )}
        </div>

        <div className="card">
          <h2>Reference documents</h2>
          <p className="muted">
            Upload your resume, notes, or study plan. OnCUE uses them to give better personalized answers.
          </p>
          <label className="btn" style={{ marginTop: 8, cursor: "pointer" }}>
            {uploading ? "Uploading..." : "Upload document"}
            <input type="file" hidden accept=".pdf,.docx,.txt,.md,.csv,.json" onChange={upload} disabled={uploading} />
          </label>
          <ul className="docs" style={{ marginTop: 14 }}>
            {props.docs.length === 0 && <li className="muted">No documents yet.</li>}
            {props.docs.map((d) => (
              <li key={d.id}>
                <span>{d.filename}</span>
                <span style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <span className={`pill ${d.status}`}>{d.status}</span>
                  <button
                    className="btn secondary"
                    style={{ padding: "4px 10px", fontSize: 12 }}
                    onClick={() => deleteDoc(d.id)}
                    disabled={deleting === d.id}
                  >
                    {deleting === d.id ? "..." : "Delete"}
                  </button>
                </span>
              </li>
            ))}
          </ul>
        </div>

        <div className="card">
          <h2>Search your documents</h2>
          <p className="muted">
            Find relevant passages from your uploaded reference documents.
          </p>
          <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
            <input
              type="text"
              placeholder="e.g. What projects have I worked on?"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && searchDocs()}
            />
            <button className="btn" onClick={searchDocs} disabled={searching || !searchQuery.trim()}>
              {searching ? "Searching..." : "Search"}
            </button>
          </div>
          {searchResults !== null && (
            <div style={{ marginTop: 14 }}>
              {searchResults.length === 0 ? (
                <p className="muted">No relevant passages found.</p>
              ) : (
                searchResults.map((p, i) => (
                  <div
                    key={i}
                    style={{
                      background: "#0b0b12",
                      border: "1px solid rgba(255,255,255,0.06)",
                      borderRadius: 8,
                      padding: "10px 12px",
                      marginBottom: 8,
                      fontSize: 13,
                      lineHeight: 1.5,
                      whiteSpace: "pre-wrap",
                    }}
                  >
                    {p}
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        <div className="card">
          <h2>Preferences</h2>
          <p className="muted">
            How should OnCUE answer you?
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
              <strong>What OnCUE knows about you:</strong> {props.persona}
            </p>
          )}
        </div>
      </div>
    </>
  );
}
