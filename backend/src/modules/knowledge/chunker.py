"""Text chunking for RAG.

Targets ~512-token chunks with ~50-token overlap. We approximate tokens with a
word window (≈0.75 words/token) to avoid a tokenizer dependency at ingest time.
"""

_WORDS_PER_CHUNK = 380  # ~512 tokens
_OVERLAP_WORDS = 40  # ~50 tokens


def chunk_text(
    text: str, *, words_per_chunk: int = _WORDS_PER_CHUNK, overlap: int = _OVERLAP_WORDS
) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks: list[str] = []
    step = max(1, words_per_chunk - overlap)
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + words_per_chunk]).strip()
        if chunk:
            chunks.append(chunk)
        if start + words_per_chunk >= len(words):
            break
    return chunks
