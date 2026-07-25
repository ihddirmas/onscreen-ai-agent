// LiteLLM admin API: mint per-user virtual keys and read their spend.
// Uses the master key server-side only.

const BASE = process.env.LITELLM_URL!;
const MASTER = process.env.LITELLM_MASTER_KEY!;

const TIER_BUDGET: Record<string, number> = {
  free: 1, // USD/month
  pro: 15,
};

function headers() {
  return {
    Authorization: `Bearer ${MASTER}`,
    "Content-Type": "application/json",
  };
}

/** Create a virtual key for a user with a monthly budget for their tier. */
export async function mintKey(userId: string, tier: string): Promise<string> {
  const res = await fetch(`${BASE}/key/generate`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({
      models: ["parakeet-default"],
      max_budget: TIER_BUDGET[tier] ?? TIER_BUDGET.free,
      budget_duration: "30d",
      metadata: { user_id: userId },
    }),
  });
  if (!res.ok) throw new Error(`LiteLLM key/generate failed: ${res.status}`);
  const data = await res.json();
  return data.key as string;
}

/** Spend + budget for a key, for the dashboard credit meter. */
export async function getSpend(
  key: string
): Promise<{ spend: number; maxBudget: number }> {
  const res = await fetch(`${BASE}/key/info?key=${encodeURIComponent(key)}`, {
    headers: headers(),
  });
  if (!res.ok) return { spend: 0, maxBudget: 0 };
  const data = await res.json();
  const info = data.info ?? data;
  return {
    spend: Number(info.spend ?? 0),
    maxBudget: Number(info.max_budget ?? 0),
  };
}
