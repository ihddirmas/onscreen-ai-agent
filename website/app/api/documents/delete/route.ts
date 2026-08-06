import { NextResponse } from "next/server";
import { serverClient, adminClient } from "@/lib/supabase";

export async function POST(req: Request) {
  const supabase = serverClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { id } = await req.json().catch(() => ({ id: "" }));
  if (!id) return NextResponse.json({ error: "missing document id" }, { status: 400 });

  const admin = adminClient();

  const { data: doc } = await admin
    .from("documents")
    .select("storage_path")
    .eq("id", id)
    .eq("user_id", user.id)
    .maybeSingle();
  if (!doc) return NextResponse.json({ error: "not found" }, { status: 404 });

  await admin.storage.from("documents").remove([doc.storage_path]);
  await admin.from("doc_chunks").delete().eq("document_id", id);
  await admin.from("documents").delete().eq("id", id);

  return NextResponse.json({ deleted: true });
}
