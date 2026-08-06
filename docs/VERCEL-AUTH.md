# Vercel + Google OAuth fix

If you see **"The app redirect URL is invalid"** when clicking **Continue with Google**, the OAuth callback URLs are not registered in Supabase and/or Google Cloud.

Your Vercel project: **optimus-the-ai-platform-to-bu**  
Production URL (typical): `https://optimus-the-ai-platform-to-bu.vercel.app`

---

## 1. Vercel environment variables

In [Vercel → Project → Settings → Environment Variables](https://vercel.com/samr1ddh1s-projects/optimus-the-ai-platform-to-bu/settings/environment-variables), set:

| Variable | Value |
|----------|--------|
| `NEXT_PUBLIC_SUPABASE_URL` | `https://jttumhkqzpfhpamwlxtr.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | from Supabase → Settings → API |
| `SUPABASE_SERVICE_ROLE_KEY` | from Supabase → Settings → API (server only) |
| `NEXT_PUBLIC_SITE_URL` | `https://optimus-the-ai-platform-to-bu.vercel.app` |

Redeploy after saving env vars.

---

## 2. Supabase Auth URL configuration

[Supabase Dashboard → Auth → URL Configuration](https://supabase.com/dashboard/project/jttumhkqzpfhpamwlxtr/auth/url-configuration)

| Field | Value |
|-------|--------|
| **Site URL** | `https://optimus-the-ai-platform-to-bu.vercel.app` |
| **Redirect URLs** (add each line) | |
| | `https://optimus-the-ai-platform-to-bu.vercel.app/**` |
| | `https://optimus-the-ai-platform-to-bu.vercel.app/auth/callback` |
| | `https://*-samr1ddh1s-projects.vercel.app/**` *(preview deploys)* |

---

## 3. Google Cloud OAuth (required for "Continue with Google")

[Google Cloud Console → APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)

1. Open your **OAuth 2.0 Client ID** (the one whose Client ID is pasted in Supabase → Auth → Providers → Google).
2. Under **Authorized redirect URIs**, add **exactly**:

```
https://jttumhkqzpfhpamwlxtr.supabase.co/auth/v1/callback
```

This is Supabase’s callback — **not** your Vercel URL. Google redirects to Supabase first; Supabase then sends the user to `/auth/callback` on your site.

3. Save. Changes can take a few minutes to propagate.

### Supabase Google provider

[Supabase → Auth → Providers → Google](https://supabase.com/dashboard/project/jttumhkqzpfhpamwlxtr/auth/providers)

- Enable Google
- Paste **Client ID** and **Client Secret** from the same Google OAuth client
- Save

---

## 4. How auth works (after this PR)

```
User → Google → Supabase (/auth/v1/callback) → your site (/auth/callback) → /dashboard
```

The app now uses `/auth/callback` (PKCE code exchange). Older builds redirected straight to `/dashboard`, which breaks SSR sessions.

---

## 5. Quick test

1. Open `https://optimus-the-ai-platform-to-bu.vercel.app/login`
2. **Email/password** should work if Supabase env vars are set.
3. **Continue with Google** should work after steps 2–3 above.

If it still fails, check Vercel **Runtime Logs** on `/auth/callback` and Supabase **Auth → Logs**.

---

## Custom domain

If you add a custom domain in Vercel, update:

- `NEXT_PUBLIC_SITE_URL`
- Supabase Site URL + Redirect URLs
- (Google redirect URI stays the Supabase URL — no change)
