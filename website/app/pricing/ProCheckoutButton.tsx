"use client";

import { useState } from "react";
import Link from "next/link";

export function ProCheckoutButton() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function startCheckout() {
    setBusy(true);
    setError("");
    try {
      const res = await fetch("/api/checkout/stripe", { method: "POST" });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Checkout failed");
      window.location.href = data.url;
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Checkout failed");
      setBusy(false);
    }
  }

  return (
    <div>
      <button className="btn" onClick={startCheckout} disabled={busy} style={{ marginTop: 8 }}>
        {busy ? "Redirecting..." : "Subscribe to Pro — $9/mo"}
      </button>
      {error && (
        <p className="muted" style={{ marginTop: 8, color: "#f59e0b" }}>
          {error}
        </p>
      )}
      <p className="muted" style={{ marginTop: 8, fontSize: "0.85em" }}>
        Not signed in? <Link href="/login">Log in first</Link>
      </p>
    </div>
  );
}
