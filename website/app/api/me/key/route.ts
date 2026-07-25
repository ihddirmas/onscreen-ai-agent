import { NextResponse } from "next/server";
import { serverClient, adminClient } from "@/lib/supabase";
import { mintKey } from "@/lib/litellm";

// GET: return the logged-in user's Parakeet key, minting one on first call.
export async function GET() {
  const supabase = serverClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const admin = adminClient();
  const { data: profile } = await admin
    .from("profiles")
    .select("litellm_key, tier")
    .eq("id", user.id)
    .maybeSingle();

  if (profile?.litellm_key) {
    return NextResponse.json({ key: profile.litellm_key });
  }

  // mint on first request
  let key: string;
  try {
    key = await mintKey(user.id, profile?.tier ?? "free");
  } catch (e: any) {
    return NextResponse.json({ error: `could not create key: ${e.message}` }, { status: 502 });
  }
  await admin.from("profiles").update({ litellm_key: key }).eq("id", user.id);
  return NextResponse.json({ key });
}
