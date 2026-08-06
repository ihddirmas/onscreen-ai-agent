/**
 * Canonical public site URL for OAuth redirects, deep links, and Stripe.
 * Prefer NEXT_PUBLIC_SITE_URL on Vercel (set to your production domain).
 */
export function getSiteUrl(): string {
  const fromEnv = process.env.NEXT_PUBLIC_SITE_URL?.replace(/\/$/, "");
  if (fromEnv) return fromEnv;

  // Vercel injects VERCEL_URL without protocol (e.g. optimus-the-ai-platform-to-bu.vercel.app)
  const vercel = process.env.VERCEL_URL?.replace(/\/$/, "");
  if (vercel) return `https://${vercel}`;

  if (typeof window !== "undefined") {
    return window.location.origin;
  }

  return "http://localhost:3000";
}

/** OAuth callback — must match Supabase Auth → URL Configuration redirect allow-list. */
export function getAuthCallbackUrl(next = "/dashboard"): string {
  const base = getSiteUrl();
  const path = next.startsWith("/") ? next : `/${next}`;
  return `${base}/auth/callback?next=${encodeURIComponent(path)}`;
}
