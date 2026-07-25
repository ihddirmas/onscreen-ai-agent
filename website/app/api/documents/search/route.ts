import { NextResponse } from "next/server";
import { adminClient } from "@/lib/supabase";
import { userFromBearer } from "@/lib/keyauth";
import { embedOne } from "@/lib/rag";

// Desktop-facing RAG retrieval. The agent's search_my_documents tool calls this
// with the user's Parakeet key. Returns the top relevant passages (used
// silently by the agent — no citation needed).
export async function POST(req: Request) {
  const userId = await userFromBearer(req);
  if (!userId) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { query } = await req.json().catch(() => ({ query: "" }));
  if (!query || typeof query !== "string") {
    return NextResponse.json({ error: "missing query" }, { status: 400 });
  }

  let embedding: number[];
  try {
    embedding = await embedOne(query);
  } catch (e: any) {
    return NextResponse.json({ error: `embed failed: ${e.message}` }, { status: 502 });
  }

  const admin = adminClient();
  const { data, error } = await admin.rpc("match_doc_chunks", {
    p_user_id: userId,
    query_embedding: embedding as unknown as string,
    match_count: 5,
  });
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  const passages = (data ?? []).map((r: { content: string }) => r.content);
  return NextResponse.json({ passages });
}
