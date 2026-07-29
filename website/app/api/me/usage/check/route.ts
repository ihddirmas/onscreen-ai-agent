import { NextResponse } from "next/server";
import { serverClient, adminClient } from "@/lib/supabase";

/**
 * GET /api/me/usage/check
 * Returns whether the user can start a new session + remaining trial info.
 * Called by the desktop app on startup (via hosted backend proxy or directly).
 */
export async function GET() {
  const supabase = serverClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const admin = adminClient();
  const { data: profile } = await admin
    .from("profiles")
    .select("tier, session_count, trial_used")
    .eq("id", user.id)
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
  const trialUsed = profile.trial_used || profile.tier === "trial";
  const sessionCount = profile.session_count ?? 0;
  const canStart = profile.tier !== "trial" || sessionCount < 1;

  return NextResponse.json({
    can_start: canStart,
    tier: isTrial ? "trial" : profile.tier,
    session_count: sessionCount,
    trial_remaining: canStart && isTrial ? 1 - sessionCount : 0,
  });
}
