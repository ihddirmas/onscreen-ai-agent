import { NextResponse } from "next/server";
import { createServerClient, type CookieOptions } from "@supabase/ssr";
import { cookies } from "next/headers";
import { getSiteUrl } from "@/lib/site-url";

type CookieItem = { name: string; value: string; options?: CookieOptions };

/**
 * Supabase PKCE OAuth callback (Google, etc.).
 * Add this URL to Supabase → Auth → URL Configuration → Redirect URLs:
 *   https://YOUR-VERCEL-DOMAIN.vercel.app/auth/callback
 */
export async function GET(request: Request) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");
  let next = requestUrl.searchParams.get("next") ?? "/dashboard";
  if (!next.startsWith("/") || next.startsWith("//")) {
    next = "/dashboard";
  }

  const siteUrl = getSiteUrl();
  const loginError = `${siteUrl}/login?error=auth`;

  if (!code) {
    return NextResponse.redirect(loginError);
  }

  const cookieStore = cookies();
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll: () => cookieStore.getAll(),
        setAll: (items: CookieItem[]) => {
          items.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          );
        },
      },
    }
  );

  const { error } = await supabase.auth.exchangeCodeForSession(code);
  if (error) {
    console.error("auth callback:", error.message);
    return NextResponse.redirect(`${loginError}&message=${encodeURIComponent(error.message)}`);
  }

  return NextResponse.redirect(`${siteUrl}${next}`);
}
