"""Knowledge base services: ingestion pipeline + pgvector semantic search."""

import uuid

import httpx
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError
from src.core.logging import get_logger
from src.modules.knowledge.chunker import chunk_text
from src.modules.knowledge.embeddings import embed_text, embed_texts
from src.modules.knowledge.models import KnowledgeChunk, KnowledgeDocument

logger = get_logger("knowledge")


async def create_document(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    title: str,
    source_type: str,
    content: str | None = None,
    source_url: str | None = None,
) -> KnowledgeDocument:
    doc = KnowledgeDocument(
        tenant_id=tenant_id,
        title=title,
        source_type=source_type,
        content=content,
        source_url=source_url,
        status="pending",
    )
    db.add(doc)
    await db.flush()
    return doc


async def list_documents(db: AsyncSession, *, tenant_id: uuid.UUID) -> list[KnowledgeDocument]:
    stmt = (
        select(KnowledgeDocument)
        .where(KnowledgeDocument.tenant_id == tenant_id, KnowledgeDocument.is_active.is_(True))
        .order_by(KnowledgeDocument.created_at.desc())
    )
    return list((await db.scalars(stmt)).all())


async def delete_document(db: AsyncSession, document_id: uuid.UUID, *, tenant_id: uuid.UUID) -> None:
    doc = await db.scalar(
        select(KnowledgeDocument).where(
            KnowledgeDocument.id == document_id, KnowledgeDocument.tenant_id == tenant_id
        )
    )
    if doc is None:
        raise NotFoundError("Document not found")
    await db.delete(doc)  # chunks cascade


async def _resolve_text(doc: KnowledgeDocument) -> str:
    if doc.source_type == "url" and doc.source_url:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(doc.source_url)
            resp.raise_for_status()
            return resp.text
    return doc.content or ""


async def process_document(db: AsyncSession, *, document_id: uuid.UUID) -> int:
    """Chunk + embed a document and store its vectors. Returns chunk count."""
    doc = await db.scalar(select(KnowledgeDocument).where(KnowledgeDocument.id == document_id))
    if doc is None:
        raise NotFoundError("Document not found")
    doc.status = "processing"
    await db.flush()

    try:
        text = await _resolve_text(doc)
        chunks = chunk_text(text)
        # Replace any existing chunks (re-processing / versioning).
        await db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.document_id == doc.id))

        embeddings = await embed_texts(chunks)
        for idx, (chunk, vector) in enumerate(zip(chunks, embeddings, strict=False)):
            db.add(
                KnowledgeChunk(
                    tenant_id=doc.tenant_id,
                    document_id=doc.id,
                    chunk_index=idx,
                    content=chunk,
                    embedding=vector,
                )
            )
        doc.status = "ready"
        await db.flush()
        return len(chunks)
    except Exception as exc:  # noqa: BLE001
        doc.status = "failed"
        await db.flush()
        logger.warning("document_process_failed", document_id=str(document_id), error=str(exc))
        raise


async def search(
    db: AsyncSession, *, query: str, tenant_id: uuid.UUID, top_k: int = 5
) -> list[dict]:
    """Semantic search over the tenant's knowledge chunks (cosine distance)."""
    query_vec = await embed_text(query)
    distance = KnowledgeChunk.embedding.cosine_distance(query_vec)
    stmt = (
        select(KnowledgeChunk.content, distance.label("distance"))
        .where(KnowledgeChunk.tenant_id == tenant_id, KnowledgeChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(top_k)
    )
    rows = (await db.execute(stmt)).all()
    return [{"content": content, "score": 1.0 - float(dist)} for content, dist in rows]
