import { NextRequest, NextResponse } from "next/server";
import { serverClient, adminClient } from "@/lib/supabase";
import { computeCost } from "@/lib/pricing";

/**
 * POST /api/me/usage/report
 * Browser-authenticated usage reporting (session_start or inference).
 * Body: { event_type: "session_start" | "inference", session_id, model_used?, tokens_in?, tokens_out? }
 *
 * Trial cap is enforced by the check_trial_session_limit DB trigger, not
 * by a read-then-write check in this handler (avoids TOCTOU races).
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

  // Read profile for the row-level tier label only — NOT for a
  // read-then-write session cap check (the DB trigger handles that
  // atomically).
  const { data: profile } = await admin
    .from("profiles")
    .select("tier, trial_used")
    .eq("id", user.id)
    .maybeSingle();

  const isTrialUser = profile
    ? (profile.tier === "trial" || (profile.tier === "free" && !profile.trial_used))
    : true;
  const tier = isTrialUser ? "trial" : (profile?.tier ?? "free");

  const cost_usd = computeCost(model_used, tokens_in ?? 0, tokens_out ?? 0);

  try {
    const { error } = await admin.from("usage_ledger").insert({
      user_id: user.id,
      session_id,
      event_type,
      model_used: model_used ?? null,
      tokens_in: tokens_in ?? 0,
      tokens_out: tokens_out ?? 0,
      tier,
      cost_usd,
    });

    if (error) throw error;

    // Increment session_count for non-trial users. Trial users' session_count
    // is already managed atomically by the check_trial_session_limit trigger;
    // updating it here too would double-count.
    if (event_type === "session_start" && profile && profile.tier !== "trial") {
      if (!profile.trial_used && profile.tier === "free") {
        await admin.from("profiles").update({
          trial_used: true,
          session_count: (profile.session_count ?? 0) + 1,
        }).eq("id", user.id);
      } else {
        await admin.from("profiles").update({
          session_count: (profile.session_count ?? 0) + 1,
        }).eq("id", user.id);
      }
    }

    return NextResponse.json({ ok: true });
  } catch (e: any) {
    if (e?.message?.includes("trial_session_limit_reached")) {
      return NextResponse.json({ error: "trial_limit_reached" }, { status: 403 });
    }
    return NextResponse.json({ error: `ledger insert failed: ${e.message}` }, { status: 500 });
  }
}
