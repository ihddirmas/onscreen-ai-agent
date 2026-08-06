import "server-only";
import {
  createServerClient,
  type CookieOptions,
} from "@supabase/ssr";
import { cookies } from "next/headers";
import { createClient } from "@supabase/supabase-js";

const URL = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const ANON = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

type CookieItem = { name: string; value: string; options?: CookieOptions };

/** Server client bound to the request cookies (auth-aware, respects RLS). */
export function serverClient() {
  const store = cookies();
  return createServerClient(URL, ANON, {
    cookies: {
      getAll: () => store.getAll(),
      setAll: (items: CookieItem[]) => {
        try {
          items.forEach(({ name, value, options }) => store.set(name, value, options));
        } catch {
          // called from a Server Component — ignore; middleware refreshes cookies
        }
      },
    },
  });
}

/** Service-role client — bypasses RLS. Server-only (never send to the browser). */
export function adminClient() {
  return createClient(URL, process.env.SUPABASE_SERVICE_ROLE_KEY!, {
    auth: { persistSession: false },
  });
}
