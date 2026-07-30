import { NextResponse } from "next/server";
import { serverClient, adminClient } from "@/lib/supabase";
import { extractText } from "@/lib/extract";
import { chunk, embed } from "@/lib/rag";

export const maxDuration = 60;

const ALLOWED_EXTENSIONS = new Set([".pdf", ".docx", ".txt", ".md", ".csv", ".json"]);
const MAX_FILE_SIZE = 25 * 1024 * 1024;

export async function POST(req: Request) {
  const supabase = serverClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "unauthorized" }, { status: 401 });

  const form = await req.formData();
  const file = form.get("file") as File | null;
  if (!file) return NextResponse.json({ error: "no file" }, { status: 400 });

  if (file.size > MAX_FILE_SIZE) {
    return NextResponse.json(
      { error: `file too large (max ${MAX_FILE_SIZE / 1024 / 1024} MB)` },
      { status: 413 },
    );
  }

  const ext = "." + file.name.split(".").pop()?.toLowerCase();
  if (!ALLOWED_EXTENSIONS.has(ext)) {
    return NextResponse.json(
      {
        error: `unsupported file type: ${ext}. Allowed: pdf, docx, txt, md, csv, json`,
      },
      { status: 415 },
    );
  }

  const admin = adminClient();
  const buffer = Buffer.from(await file.arrayBuffer());
  const storagePath = `${user.id}/${Date.now()}-${file.name}`;

  await admin.storage.from("documents").upload(storagePath, buffer, {
    contentType: file.type || "application/octet-stream",
    upsert: false,
  });

  const { data: doc } = await admin
    .from("documents")
    .insert({ user_id: user.id, filename: file.name, storage_path: storagePath, status: "processing" })
    .select("id")
    .single();

  try {
    const text = await extractText(buffer, file.name);
    const chunks = chunk(text, 500, 100);
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

    updatePersona(user.id, text).catch(() => {});

    return NextResponse.json({ id: doc!.id, chunks: chunks.length, status: "ready" });
  } catch (e: any) {
    await admin.from("documents").update({ status: "error" }).eq("id", doc!.id);
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}

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
      model: "oncue-default",
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
