"""Reference-document upload: rx.upload wiring around the extract -> chunk ->
embed -> index pipeline in webapp.services.documents. Failed
extraction/embedding flips the row to 'error' and leaves it retryable."""
from __future__ import annotations

import uuid

import reflex as rx

from webapp.services.documents import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, chunk, embed, extract_text
from webapp.services.supabase import admin_client
from webapp.states.dashboard_state import DashboardState


class UploadState(DashboardState):
    uploading: bool = False
    upload_error: str = ""

    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            return
        self.uploading = True
        self.upload_error = ""
        yield
        file = files[0]
        ext = "." + file.name.rsplit(".", 1)[-1].lower() if "." in file.name else ""
        if ext not in ALLOWED_EXTENSIONS:
            self.upload_error = f"Unsupported file type: {ext}. Allowed: pdf, docx, txt, md, csv, json"
            self.uploading = False
            return
        data = await file.read()
        if len(data) > MAX_FILE_SIZE:
            self.upload_error = f"File too large (max {MAX_FILE_SIZE // 1024 // 1024} MB)"
            self.uploading = False
            return
        admin = admin_client()
        # Server-generated object key, not the user-supplied filename — a
        # filename containing "/", "..", or similar could otherwise escape
        # the per-user storage prefix. The original filename is kept as a
        # separate metadata column for display, never used as a path.
        storage_path = f"{self.user_id}/{uuid.uuid4()}"
        doc_row = None
        try:
            admin.storage.from_("documents").upload(
                storage_path, data,
                {"content-type": file.content_type or "application/octet-stream"},
            )
            doc_row = (
                admin.table("documents")
                .insert({
                    "user_id": self.user_id,
                    "filename": file.name,
                    "storage_path": storage_path,
                    "status": "processing",
                })
                .execute()
                .data[0]
            )
            self._index_document(admin, doc_row["id"], data, file.name)
        except Exception as exc:  # noqa: BLE001 - surfaced via upload_error, never swallowed
            self.upload_error = f"Upload failed: {exc}"
            if doc_row is not None:
                admin.table("documents").update({"status": "error"}).eq("id", doc_row["id"]).execute()
        finally:
            self.uploading = False
        await self.load_dashboard()

    async def retry_document(self, document_id: str):
        admin = admin_client()
        # admin_client() bypasses RLS, so this lookup MUST be scoped to the
        # caller's own user_id — otherwise any signed-in user could pass
        # another user's document_id and read/re-index their document.
        result = (
            admin.table("documents")
            .select("storage_path, filename")
            .eq("id", document_id)
            .eq("user_id", self.user_id)
            .execute()
        )
        rows = result.data or []
        if not rows:
            self.upload_error = "Document not found."
            return
        row = rows[0]
        self.uploading = True
        self.upload_error = ""
        yield
        try:
            data = admin.storage.from_("documents").download(row["storage_path"])
            admin.table("doc_chunks").delete().eq("document_id", document_id).eq(
                "user_id", self.user_id
            ).execute()
            self._index_document(admin, document_id, data, row["filename"])
        except Exception as exc:  # noqa: BLE001
            self.upload_error = f"Retry failed: {exc}"
            admin.table("documents").update({"status": "error"}).eq("id", document_id).eq(
                "user_id", self.user_id
            ).execute()
        finally:
            self.uploading = False
        await self.load_dashboard()

    def _index_document(self, admin, document_id: str, data: bytes, filename: str) -> None:
        """Shared extract -> chunk -> embed -> insert -> mark-ready path used
        by both a fresh upload and a retry."""
        text = extract_text(data, filename)
        chunks = chunk(text)
        if not chunks:
            raise ValueError("no readable text in this file")
        vectors = embed(chunks)
        rows = [
            {"document_id": document_id, "user_id": self.user_id, "content": c, "embedding": v}
            for c, v in zip(chunks, vectors)
        ]
        admin.table("doc_chunks").insert(rows).execute()
        admin.table("documents").update({"status": "ready"}).eq("id", document_id).execute()
