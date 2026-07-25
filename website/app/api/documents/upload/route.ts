import { NextResponse } from "next/server";
import { serverClient, adminClient } from "@/lib/supabase";
import { extractText } from "@/lib/extract";
import { chunk, embed } from "@/lib/rag";

export const maxDuration = 60; // embedding can take a bit

// Upload a reference document: store → extract → chunk → embed → index,
// then refresh the user's persona summary.
export async function POST(req: Request) {
  const supabase = serverClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const form = await req.formData();
  const file = form.get("file") as File | null;
  if (!file) return NextResponse.json({ error: "no file" }, { status: 400 });

  const admin = adminClient();
  const buffer = Buffer.from(await file.arrayBuffer());
  const storagePath = `${user.id}/${Date.now()}-${file.name}`;

  // 1. store the raw file
  await admin.storage.from("documents").upload(storagePath, buffer, {
    contentType: file.type || "application/octet-stream",
    upsert: false,
  });

  // 2. document row (processing)
  const { data: doc } = await admin
    .from("documents")
    .insert({ user_id: user.id, filename: file.name, storage_path: storagePath, status: "processing" })
    .select("id")
    .single();

  try {
    // 3. extract + chunk + embed
    const text = await extractText(buffer, file.name);
    const chunks = chunk(text);
    if (chunks.length === 0) throw new Error("no readable text");
    const vectors = await embed(chunks);
    const rows = chunks.map((content, i) => ({
      document_id: doc!.id,
      user_id: user.id,
      content,
      embedding: vectors[i] as unknown as string,
    }));
    await admin.from("doc_chunks").insert(rows);
    await admin.from("documents").update({ status: "ready" }).eq("id", doc!.id);

    // 4. refresh persona (best-effort; don't fail the upload if it errors)
    updatePersona(user.id, text).catch(() => {});

    return NextResponse.json({ id: doc!.id, chunks: chunks.length, status: "ready" });
  } catch (e: any) {
    await admin.from("documents").update({ status: "error" }).eq("id", doc!.id);
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}

// One cheap LLM call (via LiteLLM) to summarize the user from a new document,
// merged into profiles.persona.
async function updatePersona(userId: string, text: string) {
  const admin = adminClient();
  const { data: profile } = await admin
    .from("profiles")
    .select("persona, litellm_key")
    .eq("id", userId)
    .maybeSingle();

  const res = await fetch(`${process.env.LITELLM_URL}/chat/completions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.LITELLM_MASTER_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "parakeet-default",
      max_tokens: 200,
      messages: [
        {
          role: "system",
          content:
            "Summarize who this person is for personalizing an AI assistant: " +
            "background, skills, tech stack, notable projects, and how they'd " +
            "likely want answers. 2-4 sentences. Merge with any existing summary.",
        },
        {
          role: "user",
          content: `Existing summary: ${profile?.persona || "(none)"}\n\nNew document:\n${text.slice(0, 6000)}`,
        },
      ],
    }),
  });
  if (!res.ok) return;
  const data = await res.json();
  const persona = data.choices?.[0]?.message?.content?.trim();
  if (persona) await admin.from("profiles").update({ persona }).eq("id", userId);
}
