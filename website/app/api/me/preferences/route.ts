import { NextResponse } from "next/server";
import { serverClient, adminClient } from "@/lib/supabase";

// Save the user's editable preferences ("answer coding questions in Python").
export async function POST(req: Request) {
  const supabase = serverClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const { preferences } = await req.json().catch(() => ({ preferences: "" }));
  await adminClient()
    .from("profiles")
    .update({ preferences: String(preferences ?? "").slice(0, 2000) })
    .eq("id", user.id);
  return NextResponse.json({ ok: true });
}
