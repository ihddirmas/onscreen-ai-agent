"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { browserClient } from "@/lib/supabase-browser";

export default function LoginPage() {
  const supabase = browserClient();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState<"in" | "up">("in");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMsg("");
    const fn =
      mode === "in"
        ? supabase.auth.signInWithPassword({ email, password })
        : supabase.auth.signUp({ email, password });
    const { error } = await fn;
    setBusy(false);
    if (error) {
      setMsg(error.message);
      return;
    }
    if (mode === "up") {
      setMsg("Account created. If email confirmation is on, check your inbox — otherwise you're in.");
    }
    router.push("/dashboard");
    router.refresh();
  }

  async function google() {
    await supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${location.origin}/dashboard` },
    });
  }

  return (
    <div className="container" style={{ maxWidth: 420, marginTop: 60 }}>
      <div className="brand" style={{ textAlign: "center", marginBottom: 20 }}>🦜 Parakeet</div>
      <div className="card">
        <h2>{mode === "in" ? "Log in" : "Create your account"}</h2>
        <form onSubmit={submit}>
          <label>Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <label>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
          <button className="btn" style={{ width: "100%", marginTop: 16 }} disabled={busy}>
            {busy ? "…" : mode === "in" ? "Log in" : "Sign up"}
          </button>
        </form>
        <button className="btn secondary" style={{ width: "100%", marginTop: 10 }} onClick={google}>
          Continue with Google
        </button>
        {msg && <p className="muted" style={{ marginTop: 12 }}>{msg}</p>}
        <p className="muted" style={{ marginTop: 16, textAlign: "center" }}>
          {mode === "in" ? "No account?" : "Already have one?"}{" "}
          <a onClick={() => setMode(mode === "in" ? "up" : "in")} style={{ cursor: "pointer" }}>
            {mode === "in" ? "Sign up" : "Log in"}
          </a>
        </p>
      </div>
    </div>
  );
}
