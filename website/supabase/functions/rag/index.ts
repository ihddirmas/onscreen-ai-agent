// Supabase Edge Function: RAG embedding + search, using the built-in, free
// `gte-small` model (384-dim). No model download, runs next to the database.
//
// Deploy:  supabase functions deploy rag --no-verify-jwt
// Secrets: supabase secrets set EMBED_SECRET=... SUPABASE_SERVICE_ROLE_KEY=...
//          (SUPABASE_URL is provided automatically)
//
// Actions:
//   { action: "embed",  texts: string[] }        + header x-embed-secret
//       -> { embeddings: number[][] }   (server-to-server, for uploads)
//   { action: "search", query: string }          + Authorization: Bearer <key>
//       -> { passages: string[] }       (desktop hot path: embed + match)

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// gte-small — swap here if a better free built-in model appears later.
const EMBED_MODEL = "gte-small";

// deno-lint-ignore no-explicit-any
const session = new (globalThis as any).Supabase.ai.Session(EMBED_MODEL);

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_ROLE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const EMBED_SECRET = Deno.env.get("EMBED_SECRET") ?? "";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-embed-secret, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...CORS },
  });
}

async function embedOne(text: string): Promise<number[]> {
  // mean-pooled + normalized sentence embedding (384-dim)
  const out = await session.run(text, { mean_pool: true, normalize: true });
  return Array.from(out as number[]);
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return json({ error: "POST only" }, 405);

  let body: { action?: string; texts?: string[]; query?: string };
  try {
    body = await req.json();
  } catch {
    return json({ error: "invalid JSON" }, 400);
  }

  // --- embed: server-to-server, used by the upload route -------------------
  if (body.action === "embed") {
    if (!EMBED_SECRET || req.headers.get("x-embed-secret") !== EMBED_SECRET) {
      return json({ error: "unauthorized" }, 401);
    }
    const texts = body.texts ?? [];
    const embeddings: number[][] = [];
    for (const t of texts) embeddings.push(await embedOne(t));
    return json({ embeddings });
  }

  // --- search: desktop hot path (auth by OnCUE key) ---------------------
  if (body.action === "search") {
    const key = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "").trim();
    if (!key) return json({ error: "unauthorized" }, 401);
    const query = (body.query || "").toString();
    if (!query) return json({ error: "missing query" }, 400);

    const admin = createClient(SUPABASE_URL, SERVICE_ROLE, {
      auth: { persistSession: false },
    });

    const { data: profile } = await admin
      .from("profiles")
      .select("id")
      .eq("litellm_key", key)
      .maybeSingle();
    if (!profile) return json({ error: "unauthorized" }, 401);

    const embedding = await embedOne(query);
    const { data, error } = await admin.rpc("match_doc_chunks", {
      p_user_id: profile.id,
      query_embedding: embedding,
      match_count: 5,
    });
    if (error) return json({ error: error.message }, 500);

    const passages = (data ?? []).map((r: { content: string }) => r.content);
    return json({ passages });
  }

  return json({ error: "unknown action" }, 400);
});
