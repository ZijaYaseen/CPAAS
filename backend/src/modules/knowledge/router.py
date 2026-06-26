"""Knowledge base API routes (tenant-scoped, authenticated)."""

import io
import uuid

from fastapi import APIRouter, File, UploadFile

from src.core.logging import get_logger
from src.modules.auth.dependencies import CurrentUser, TenantDB
from src.modules.knowledge import service
from src.modules.knowledge.schemas import (
    DocumentCreateRequest,
    DocumentResponse,
    SearchRequest,
    SearchResult,
)

logger = get_logger("knowledge.router")
router = APIRouter(prefix="/knowledge", tags=["knowledge"])


def _enqueue_processing(tenant_id: str, document_id: str) -> None:
    try:
        from src.celery_app import celery_app

        celery_app.send_task(
            "src.workers.document_processor.process",
            args=[tenant_id, document_id],
            queue="ai",
        )
    except Exception:  # noqa: BLE001
        pass


@router.post("/documents", response_model=DocumentResponse, status_code=201)
async def create_document(payload: DocumentCreateRequest, db: TenantDB, user: CurrentUser):
    doc = await service.create_document(
        db,
        tenant_id=user.tenant_id,
        title=payload.title,
        source_type=payload.source_type,
        content=payload.content,
        source_url=payload.source_url,
    )
    _enqueue_processing(str(user.tenant_id), str(doc.id))
    return DocumentResponse.model_validate(doc)


@router.post("/documents/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(db: TenantDB, user: CurrentUser, file: UploadFile = File(...)):
    raw = await file.read()
    text = _extract_text(file.filename or "upload", raw)
    doc = await service.create_document(
        db,
        tenant_id=user.tenant_id,
        title=file.filename or "Uploaded document",
        source_type="pdf" if (file.filename or "").lower().endswith(".pdf") else "text",
        content=text,
    )
    _enqueue_processing(str(user.tenant_id), str(doc.id))
    return DocumentResponse.model_validate(doc)


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(db: TenantDB, _user: CurrentUser):
    docs = await service.list_documents(db)
    return [DocumentResponse.model_validate(d) for d in docs]


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(document_id: uuid.UUID, db: TenantDB, _user: CurrentUser):
    await service.delete_document(db, document_id)


@router.post("/search", response_model=list[SearchResult])
async def search(payload: SearchRequest, db: TenantDB, _user: CurrentUser):
    results = await service.search(db, query=payload.query, top_k=payload.top_k)
    return [SearchResult(**r) for r in results]


def _extract_text(filename: str, raw: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(raw))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return raw.decode("utf-8", errors="replace")
