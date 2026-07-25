// Document RAG helpers. Chunking stays in Node; embedding is delegated to the
// Supabase Edge Function `rag` (built-in gte-small, 384-dim, free, no model
// download) so there is no cold-start penalty and nothing to run in this bundle.

export const EMBED_DIM = 384; // gte-small — matches vector(384) in schema.sql

function edgeUrl(): string {
  // e.g. https://<project>.supabase.co/functions/v1/rag
  const base =
    process.env.SUPABASE_FUNCTIONS_URL ||
    `${process.env.NEXT_PUBLIC_SUPABASE_URL}/functions/v1`;
  return `${base.replace(/\/$/, "")}/rag`;
}

/** Split text into ~500-word chunks with a small overlap for context. */
export function chunk(text: string, size = 500, overlap = 60): string[] {
  const words = text.split(/\s+/).filter(Boolean);
  if (words.length === 0) return [];
  const chunks: string[] = [];
  for (let i = 0; i < words.length; i += size - overlap) {
    chunks.push(words.slice(i, i + size).join(" "));
    if (i + size >= words.length) break;
  }
  return chunks;
}

/** Embed strings via the edge function (server-to-server, shared secret). */
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

/** Embed a single query string. */
export async function embedOne(text: string): Promise<number[]> {
  const [v] = await embed([text]);
  return v;
}
