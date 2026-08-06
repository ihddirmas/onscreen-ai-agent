export const EMBED_DIM = 384;

function edgeUrl(): string {
  const base =
    process.env.SUPABASE_FUNCTIONS_URL ||
    `${process.env.NEXT_PUBLIC_SUPABASE_URL}/functions/v1`;
  return `${base.replace(/\/$/, "")}/rag`;
}

export function chunk(text: string, size = 500, overlap = 100): string[] {
  const words = text.split(/\s+/).filter(Boolean);
  if (words.length === 0) return [];
  const step = Math.max(1, size - overlap);
  const chunks: string[] = [];
  for (let i = 0; i < words.length; i += step) {
    chunks.push(words.slice(i, i + size).join(" "));
    if (i + size >= words.length) break;
  }
  return chunks;
}

export async function embed(texts: string[]): Promise<number[][]> {
  if (texts.length === 0) return [];
  const res = await fetch(edgeUrl(), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-embed-secret": process.env.EMBED_SECRET || "",
    },
    body: JSON.stringify({ action: "embed", texts }),
  });
  if (!res.ok) throw new Error(`embed failed: ${res.status} ${await res.text()}`);
  const data = await res.json();
  return data.embeddings as number[][];
}

export async function embedOne(text: string): Promise<number[]> {
  const [v] = await embed([text]);
  return v;
}
