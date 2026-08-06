import { NextResponse } from "next/server";
import { serverClient, adminClient } from "@/lib/supabase";
import { userFromBearer } from "@/lib/keyauth";
import { embedOne } from "@/lib/rag";

export async function POST(req: Request) {
  const cookieUser = await serverClient().auth.getUser().then((r) => r.data.user);
  const bearerUser = await userFromBearer(req);
  const userId = cookieUser?.id ?? bearerUser;
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
