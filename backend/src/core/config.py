"""Application configuration loaded from environment variables.

All settings come from the environment (`.env` in dev). No secrets are hardcoded.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo root = .../CPAAS (config.py is at backend/src/core/config.py).
_REPO_ROOT = Path(__file__).resolve().parents[3]
# Load the root .env first, then an optional backend/.env override. Works whether
# the app runs from the repo root, from backend/, or in Docker (env injected too).
_ENV_FILES = (_REPO_ROOT / ".env", _REPO_ROOT / "backend" / ".env")


def to_sync_url(async_url: str) -> str:
    """Derive the sync (psycopg) DB URL from the async (asyncpg) one.

    Same database, different driver: asyncpg → psycopg, and the SSL query param
    name differs (asyncpg uses ``ssl=...``, psycopg uses ``sslmode=...``).
    """
    url = async_url
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "+psycopg")
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    return url.replace("ssl=require", "sslmode=require").replace("ssl=true", "sslmode=require")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ---- Core ----
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    secret_key: str = "change-me"

    # ---- Database ----
    # The ONLY database setting. Async URL (asyncpg) used by the app; the sync URL
    # for Alembic is exposed as the `database_url_sync` property (derived, not an env var).
    database_url: str = "postgresql+asyncpg://user:password@localhost/ucaas"

    @field_validator("database_url", "redis_url", "secret_key", mode="before")
    @classmethod
    def strip_bom_and_whitespace(cls, v: str) -> str:
        # Strip UTF-8 BOM (﻿) that Windows tools may prepend, plus any whitespace.
        return str(v).strip().lstrip("﻿")

    # ---- Redis ----
    redis_url: str = "redis://localhost:6379/0"

    # ---- Auth / Sessions ----
    session_cookie_name: str = "ucaas_session"
    session_ttl_seconds: int = 604800  # 7 days
    session_cookie_secure: bool = False
    session_cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    # ---- CORS ----
    frontend_origin: str = "http://localhost:3000"

    # ---- Security / Rate limiting ----
    rate_limit_per_minute: int = 120  # requests per identifier (user/IP) per minute
    rate_limit_enabled: bool = True
    csrf_protection_enabled: bool = True

    # ---- Observability ----
    sentry_dsn: str = ""
    otel_exporter_endpoint: str = ""  # e.g. http://otel-collector:4317
    slow_query_ms: int = 500  # log queries slower than this

    # ---- AI / LLM provider (OpenAI Agents SDK via OpenAI-compatible endpoint) ----
    # Default config targets Google Gemini through its OpenAI-compatible API.
    # Accepts either LLM_API_KEY or GEMINI_API_KEY in the env.
    llm_api_key: str = Field(
        default="", validation_alias=AliasChoices("LLM_API_KEY", "GEMINI_API_KEY")
    )
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    llm_model: str = "gemini-2.5-flash"           # override with your exact model id
    llm_tracing_disabled: bool = True             # OpenAI platform tracing off (no OpenAI key)

    # ---- Embeddings (RAG) — Gemini native embedContent + Matryoshka truncation ----
    # gemini-embedding-001 defaults to 3072 dims; we request 1536 (lossless via MRL) to
    # fit the pgvector column + ivfflat index (migration 0003 uses VECTOR(1536)).
    embedding_api_key: str = Field(
        default="", validation_alias=AliasChoices("EMBEDDING_API_KEY", "GEMINI_API_KEY")
    )
    embedding_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    embedding_model: str = "gemini-embedding-001"
    embedding_dim: int = 1536

    @property
    def effective_embedding_api_key(self) -> str:
        return self.embedding_api_key or self.llm_api_key

    # ---- Channels ----
    whatsapp_verify_token: str = ""
    whatsapp_app_secret: str = ""
    whatsapp_access_token: str = ""
    sendgrid_api_key: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    @property
    def database_url_sync(self) -> str:
        """Sync (psycopg) URL for Alembic, derived from the async DATABASE_URL."""
        return to_sync_url(self.database_url)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


settings = get_settings()
