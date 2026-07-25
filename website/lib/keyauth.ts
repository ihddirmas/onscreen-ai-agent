// Resolve the desktop app's Bearer key (the user's litellm_key) to a user id.
import { adminClient } from "@/lib/supabase";

export async function userFromBearer(req: Request): Promise<string | null> {
  const auth = req.headers.get("authorization") || "";
  const key = auth.replace(/^Bearer\s+/i, "").trim();
  if (!key) return null;
  const admin = adminClient();
  const { data } = await admin
    .from("profiles")
    .select("id")
    .eq("litellm_key", key)
    .maybeSingle();
  return data?.id ?? null;
}
