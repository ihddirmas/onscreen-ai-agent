// Per-model pricing in USD per 1K tokens (input / output).
// Used by the usage ledger to compute cost_usd at report time.
// Groq models are free via their API; Claude/GPT/Gemini have published rates.

const PRICING: Record<string, { in: number; out: number }> = {
  // Groq: free tier
  "llama-3.3-70b-versatile": { in: 0, out: 0 },
  "llama-3.1-8b-instant": { in: 0, out: 0 },
  "mixtral-8x7b-32768": { in: 0, out: 0 },
  "qwen-2.5-32b": { in: 0, out: 0 },
  "qwen-2.5-coder-32b": { in: 0, out: 0 },
  "deepseek-r1-distill-llama-70b": { in: 0, out: 0 },

  // Hosted defaults (LiteLLM proxy): tracked via LiteLLM spend if available;
  // fallback to $0 since most hosted backends chain through free APIs.
  "oncue-default": { in: 0, out: 0 },
  "oncue-groq": { in: 0, out: 0 },
};

export function computeCost(
  model: string | null | undefined,
  tokensIn: number,
  tokensOut: number,
): number {
  if (!model) return 0;
  const rates = PRICING[model];
  if (!rates) return 0;
  return (rates.in * tokensIn + rates.out * tokensOut) / 1000;
}
