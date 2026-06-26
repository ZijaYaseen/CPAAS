"""Gemini embeddings (native ``embedContent`` API).

Uses ``gemini-embedding-001`` and requests ``outputDimensionality=1536`` so the
vectors fit the pgvector ``VECTOR(1536)`` column + ivfflat index (the OpenAI-compat
endpoint doesn't expose a dimensions param, so we call the native API directly).
For any dimensionality other than 3072, Google recommends L2-normalizing the result.
"""

import math

import httpx

from src.core.config import settings
from src.core.exceptions import AppError


def _normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vec))
    return [x / norm for x in vec] if norm > 0 else vec


async def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    api_key = settings.effective_embedding_api_key
    if not api_key:
        raise AppError("No embedding API key configured (set GEMINI_API_KEY)")

    url = f"{settings.embedding_base_url}/models/{settings.embedding_model}:batchEmbedContents"
    model_path = f"models/{settings.embedding_model}"
    body = {
        "requests": [
            {
                "model": model_path,
                "content": {"parts": [{"text": text}]},
                "outputDimensionality": settings.embedding_dim,
            }
            for text in texts
        ]
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, params={"key": api_key}, json=body)
        resp.raise_for_status()
        data = resp.json()

    embeddings = [item["values"] for item in data.get("embeddings", [])]
    # Truncated MRL embeddings should be normalized for correct cosine distance.
    return [_normalize(vec) for vec in embeddings]


async def embed_text(text: str) -> list[float]:
    result = await embed_texts([text])
    return result[0]
