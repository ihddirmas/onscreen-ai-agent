import { NextResponse } from "next/server";
import { adminClient } from "@/lib/supabase";
import { userFromBearer } from "@/lib/keyauth";

// Desktop-facing: the app fetches the user's persona + preferences (by key)
// to inject into the agent's system prompt. Bearer auth = the Parakeet key.
export async function GET(req: Request) {
  const userId = await userFromBearer(req);
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const admin = adminClient();
  const { data } = await admin
    .from("profiles")
    .select("persona, preferences")
    .eq("id", userId)
    .maybeSingle();

  return NextResponse.json({
    persona: data?.persona ?? "",
    preferences: data?.preferences ?? "",
  });
}
