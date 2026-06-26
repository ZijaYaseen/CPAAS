"""Knowledge base ORM models for RAG: KnowledgeDocument, KnowledgeChunk.

Embeddings are stored in Postgres via pgvector (VECTOR(1536) for OpenAI
text-embedding-3-small), so retrieval is a single SQL query — no separate vector DB.
"""

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models import Base, TenantMixin, TimestampMixin, uuid_pk

EMBEDDING_DIM = 1536


class KnowledgeDocument(Base, TenantMixin, TimestampMixin):
    __tablename__ = "knowledge_documents"

    id: Mapped[uuid.UUID] = uuid_pk()
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pdf | text | url
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    # Processing lifecycle: pending -> processing -> ready | failed
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")


class KnowledgeChunk(Base, TenantMixin):
    __tablename__ = "knowledge_chunks"
    __table_args__ = (UniqueConstraint("document_id", "chunk_index", name="uq_chunk_doc_index"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
