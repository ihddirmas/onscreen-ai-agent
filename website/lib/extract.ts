// Extract plain text from an uploaded file buffer by type.

export async function extractText(
  buffer: Buffer,
  filename: string
): Promise<string> {
  const lower = filename.toLowerCase();
  if (lower.endsWith(".pdf")) {
    const pdf = (await import("pdf-parse")).default;
    const data = await pdf(buffer);
    return data.text ?? "";
  }
  if (lower.endsWith(".docx")) {
    const mammoth = await import("mammoth");
    const { value } = await mammoth.extractRawText({ buffer });
    return value ?? "";
  }
  // txt / md / csv / json and anything else — treat as UTF-8 text
  return buffer.toString("utf-8");
}
