import { NextRequest, NextResponse } from "next/server";
import { adminClient } from "@/lib/supabase";
import { computeCost } from "@/lib/pricing";

const LITELLM_URL = process.env.LITELLM_URL!;
const LITELLM_MASTER_KEY = process.env.LITELLM_MASTER_KEY!;

/**
 * POST /api/usage/report
 * Desktop app calls this with { token: "sk-...", event_type: "session_start"|"inference", session_id: "..." }
 * to report usage. Resolves the LiteLLM key → user_id → writes to ledger.
 *
 * Trial cap is enforced by the check_trial_session_limit DB trigger, not by
 * a read-then-write check in this handler (avoids TOCTOU races).
 */
export async function POST(req: NextRequest) {
  const body = await req.json();
  const { token, event_type, session_id, model_used, tokens_in, tokens_out } = body;

  if (!token || !event_type || !session_id) {
    return NextResponse.json({ error: "token, event_type, session_id required" }, { status: 400 });
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

  // Read profile for the row-level tier label only — NOT for a
  // read-then-write session cap check (the DB trigger handles that
  // atomically).
  const { data: profile } = await admin
    .from("profiles")
    .select("tier, trial_used, session_count")
    .eq("id", userId)
    .maybeSingle();

  const isTrialUser = profile
    ? (profile.tier === "trial" || (profile.tier === "free" && !profile.trial_used))
    : true;
  const tier = isTrialUser ? "trial" : (profile?.tier ?? "free");

  const cost_usd = computeCost(model_used, tokens_in ?? 0, tokens_out ?? 0);

  try {
    const { error } = await admin.from("usage_ledger").insert({
      user_id: userId,
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
        }).eq("id", userId);
      } else {
        await admin.from("profiles").update({
          session_count: (profile.session_count ?? 0) + 1,
        }).eq("id", userId);
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
