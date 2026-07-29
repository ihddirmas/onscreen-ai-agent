import { NextRequest, NextResponse } from "next/server";
import { adminClient } from "@/lib/supabase";

const LITELLM_URL = process.env.LITELLM_URL!;
const LITELLM_MASTER_KEY = process.env.LITELLM_MASTER_KEY!;

/**
 * POST /api/usage/report
 * Desktop app calls this with { token: "sk-...", event_type: "session_start"|"inference", session_id: "..." }
 * to report usage. Resolves the LiteLLM key → user_id → writes to ledger.
 * Returns 403 if trial limit is reached.
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

  // Get current profile to determine tier
  const { data: profile } = await admin
    .from("profiles")
    .select("tier, trial_used, session_count")
    .eq("id", userId)
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
      user_id: userId,
      session_id,
      event_type,
      model_used: model_used ?? null,
      tokens_in: tokens_in ?? 0,
      tokens_out: tokens_out ?? 0,
      tier,
      cost_usd: 0,
    });

    if (error) throw error;

    // On first session_start for a free user, flip trial_used and increment
    if (event_type === "session_start") {
      if (profile && !profile.trial_used && profile.tier === "free") {
        await admin.from("profiles").update({
          trial_used: true,
          session_count: (profile.session_count ?? 0) + 1,
        }).eq("id", userId);
      } else {
        await admin.from("profiles").update({
          session_count: (profile?.session_count ?? 0) + 1,
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
