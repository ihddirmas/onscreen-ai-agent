import { NextRequest, NextResponse } from "next/server";
import { serverClient, adminClient } from "@/lib/supabase";

/**
 * POST /api/me/usage/report
 * Desktop app calls this to report a session start or inference event.
 * Body: { event_type: "session_start" | "inference", session_id: string, model_used?: string, tokens_in?: number, tokens_out?: number }
 *
 * Returns 403 with { error: "trial_limit_reached" } if a trial user hits the cap.
 */
export async function POST(req: NextRequest) {
  const supabase = serverClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const admin = adminClient();
  const body = await req.json();
  const { event_type, session_id, model_used, tokens_in, tokens_out } = body;

  if (!event_type || !session_id) {
    return NextResponse.json({ error: "event_type and session_id required" }, { status: 400 });
  }

  // Get current profile to determine tier
  const { data: profile } = await admin
    .from("profiles")
    .select("tier, trial_used, session_count")
    .eq("id", user.id)
    .maybeSingle();

  const isTrialUser = profile
    ? (profile.tier === "trial" || (profile.tier === "free" && !profile.trial_used))
    : true;
  const tier = isTrialUser ? "trial" : (profile?.tier ?? "free");

  // Enforce trial cap server-side
  if (event_type === "session_start" && isTrialUser && (profile?.session_count ?? 0) >= 1) {
    return NextResponse.json({ error: "trial_limit_reached" }, { status: 403 });
  }

  try {
    const { error } = await admin.from("usage_ledger").insert({
      user_id: user.id,
      session_id,
      event_type,
      model_used: model_used ?? null,
      tokens_in: tokens_in ?? 0,
      tokens_out: tokens_out ?? 0,
      tier,
      cost_usd: 0, // computed async via LiteLLM spend data
    });

    if (error) throw error;

    // On first session_start for a free user, flip trial_used
    if (event_type === "session_start" && profile && !profile.trial_used && profile.tier === "free") {
      await admin.from("profiles").update({
        trial_used: true,
        session_count: (profile.session_count ?? 0) + 1,
      }).eq("id", user.id);
    } else if (event_type === "session_start") {
      await admin.from("profiles").update({
        session_count: (profile?.session_count ?? 0) + 1,
      }).eq("id", user.id);
    }

    return NextResponse.json({ ok: true });
  } catch (e: any) {
    if (e?.message?.includes("trial_session_limit_reached")) {
      return NextResponse.json({ error: "trial_limit_reached" }, { status: 403 });
    }
    return NextResponse.json({ error: `ledger insert failed: ${e.message}` }, { status: 500 });
  }
}
