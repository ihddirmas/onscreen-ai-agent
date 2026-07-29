import { NextRequest, NextResponse } from "next/server";
import { adminClient } from "@/lib/supabase";

const LITELLM_URL = process.env.LITELLM_URL!;
const LITELLM_MASTER_KEY = process.env.LITELLM_MASTER_KEY!;

/**
 * POST /api/usage/check
 * Desktop app calls this with { token: "sk-..." } to check session eligibility.
 * Resolves the LiteLLM virtual key → user_id → profile.
 */
export async function POST(req: NextRequest) {
  const { token } = await req.json();
  if (!token) {
    return NextResponse.json({ error: "token required" }, { status: 400 });
  }

  // Resolve the LiteLLM virtual key to get user_id from metadata
  let userId: string;
  try {
    const res = await fetch(`${LITELLM_URL}/key/info?key=${encodeURIComponent(token)}`, {
      headers: { Authorization: `Bearer ${LITELLM_MASTER_KEY}` },
    });
    if (!res.ok) {
      return NextResponse.json({ error: "invalid key" }, { status: 403 });
    }
    const data = await res.json();
    const info = data.info ?? data;
    userId = info.metadata?.user_id;
    if (!userId) {
      return NextResponse.json({ error: "key not linked to a user" }, { status: 403 });
    }
  } catch {
    return NextResponse.json({ error: "could not verify key" }, { status: 502 });
  }

  const admin = adminClient();
  const { data: profile } = await admin
    .from("profiles")
    .select("tier, session_count, trial_used")
    .eq("id", userId)
    .maybeSingle();

  if (!profile) {
    return NextResponse.json({
      can_start: true,
      tier: "free",
      session_count: 0,
      trial_remaining: 1,
    });
  }

  const isTrial = profile.tier === "free" && !profile.trial_used
    || profile.tier === "trial";
  const sessionCount = profile.session_count ?? 0;
  const canStart = profile.tier !== "trial" || sessionCount < 1;

  return NextResponse.json({
    can_start: canStart,
    tier: isTrial ? "trial" : profile.tier,
    session_count: sessionCount,
    trial_remaining: canStart && isTrial ? 1 - sessionCount : 0,
  });
}
