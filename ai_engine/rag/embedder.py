"""Text embedding for the RAG pipeline.

`embed_text` always returns a 1024-dim vector (matches
`DocumentChunk.embedding`, a pgvector `Vector(1024)` column), so the caller
never needs to know which mode produced it.

- Real mode: if an embedding API key is configured (`EMBEDDING_API_KEY` or
  `VOYAGE_API_KEY`), we call the embedding provider (Voyage AI, Anthropic's
  recommended embeddings partner) for a genuine semantic embedding.
- Fallback mode: a deterministic pseudo-embedding computed via the hashing
  trick over word uni/bi-grams, L2-normalized. It has no real semantic
  understanding, but text sharing vocabulary hashes into the same
  dimensions, so cosine similarity still meaningfully clusters similar text.
  This keeps RAG functionally testable end-to-end with no API key.
"""

from __future__ import annotations

import hashlib
import math
import os
import re

EMBED_DIM = 1024
_EMBEDDING_API_KEY_ENV_VARS = ("EMBEDDING_API_KEY", "VOYAGE_API_KEY")
_WORD_RE = re.compile(r"[a-z0-9]+")


def _get_embedding_api_key() -> str | None:
    for var in _EMBEDDING_API_KEY_ENV_VARS:
        value = os.environ.get(var)
        if value:
            return value
    return None


def is_embedding_configured() -> bool:
    return _get_embedding_api_key() is not None


def embed_text(text: str) -> list[float]:
    """Return a 1024-dim embedding vector for `text`."""

    text = text or ""

    if is_embedding_configured():
        try:
            return _real_embedding(text)
        except Exception as exc:  # noqa: BLE001 - never let embedding fail the caller
            print(f"[ai_engine.rag.embedder] WARNING: real embedding call failed, "
                  f"falling back to deterministic pseudo-embedding: {exc}")

    return _hashing_embedding(text)


def _real_embedding(text: str) -> list[float]:
    import voyageai  # optional dependency, only imported when a key is configured

    api_key = _get_embedding_api_key()
    model = os.environ.get("EMBEDDING_MODEL", "voyage-3")
    client = voyageai.Client(api_key=api_key)
    result = client.embed([text], model=model, input_type="document")
    vector = list(result.embeddings[0])

    if len(vector) != EMBED_DIM:
        vector = _resize(vector, EMBED_DIM)
    return vector


def _resize(vector: list[float], dim: int) -> list[float]:
    """Pad or truncate a vector to exactly `dim` entries (defensive only)."""

    if len(vector) == dim:
        return vector
    if len(vector) > dim:
        return vector[:dim]
    return vector + [0.0] * (dim - len(vector))


def _tokenize(text: str) -> list[str]:
    words = _WORD_RE.findall(text.lower())
    if not words:
        return []
    bigrams = [f"{a}_{b}" for a, b in zip(words, words[1:])]
    return words + bigrams


def _hashing_embedding(text: str) -> list[float]:
    """Deterministic seeded feature-hashing embedding (the "hashing trick").

    Each token (word unigram/bigram) is hashed with SHA-256; the hash picks
    a target dimension and a sign, and contributes +/-1 to that dimension.
    The result is L2-normalized so cosine similarity behaves sensibly.
    Same input text always produces the same vector (deterministic).
    """

    vector = [0.0] * EMBED_DIM
    tokens = _tokenize(text) or ["__empty__"]

    for token in tokens:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % EMBED_DIM
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign

    norm = math.sqrt(sum(v * v for v in vector))
    if norm > 0:
        vector = [v / norm for v in vector]
    return vector
