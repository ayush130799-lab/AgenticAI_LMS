"""pgvector-backed retrieval over `DocumentChunk` rows.

DB-read-only: takes a SQLAlchemy `AsyncSession` owned and passed in by the
backend. This module never writes to the database and never opens its own
session/connection.
"""

from __future__ import annotations

import re
import uuid

from sqlalchemy import func, literal_column, select

from ai_engine.rag.embedder import embed_text, is_embedding_configured


def _load_document_chunk_model():
    # Imported lazily (not at module load time) so ai_engine stays importable
    # even outside the backend process / before the backend package is on
    # PYTHONPATH (e.g. in isolated unit tests of chunk_text/embed_text).
    from app.models.rag import DocumentChunk

    return DocumentChunk


_STOPWORDS = frozenset(
    "a an the and or but if then so of to in on at by for with about from into over under as is are was were be been being "
    "do does did doing done have has had having can could should would may might will shall this that these those it its "
    "i me my we our you your he she they them their what which who whom whose when where why how not no yes than too very "
    "just also more most some any each other such only own same tell explain describe give show simply please example "
    "examples mean means meaning define definition difference between vs versus works work use used using".split()
)

_CANDIDATES = 30  # candidates taken from each ranking before fusion
_RRF_K = 60  # standard reciprocal-rank-fusion constant
_MAX_PER_LESSON = 2  # keep the context diverse instead of five chunks from one lesson


def _query_terms(query: str) -> list[str]:
    """Significant search terms: lowercase alphanumerics minus stopwords (safe to inline in a tsquery)."""
    seen: list[str] = []
    for token in re.findall(r"[a-z0-9]+", query.lower()):
        if len(token) > 1 and token not in _STOPWORDS and token not in seen:
            seen.append(token)
    return seen[:12]


async def retrieve_relevant_chunks(
    session,
    query: str,
    lesson_id: str | None = None,
    k: int = 5,
) -> list[dict]:
    """Return the top-k most relevant chunks for `query` using hybrid retrieval.

    Two rankings are computed over `document_chunks` and fused with reciprocal
    rank fusion:
      1. lexical: Postgres full-text search (English stemming; lesson title
         weighted above body; rank normalised by chunk length), OR-ing the
         significant query terms so a short question still matches.
      2. vector: pgvector cosine distance on `embed_text(query)`. Without a
         real embedding provider the built-in embedding is only a weak
         lexical signal, so it gets a lower weight than the full-text rank.
    Chunks from `lesson_id` (the lesson the student is viewing) get a boost,
    and at most `_MAX_PER_LESSON` chunks per lesson are returned.

    Returns `[{"content", "title", "lesson_id", "score"}, ...]`, `score`
    being the fused relevance normalised to [0, 1] (higher = more relevant).
    """

    if not query or not query.strip() or k <= 0:
        return []

    DocumentChunk = _load_document_chunk_model()

    lesson_uuid = None
    if lesson_id:
        try:
            lesson_uuid = uuid.UUID(str(lesson_id))
        except ValueError:
            lesson_uuid = None

    by_id: dict = {}
    fused: dict = {}
    vector_weight = 1.0 if is_embedding_configured() else 0.5
    lexical_weight = 1.0

    # 1) lexical ranking
    terms = _query_terms(query)
    if terms:
        tsquery = func.to_tsquery("english", " | ".join(terms))
        doc_vector = func.setweight(func.to_tsvector("english", DocumentChunk.title), literal_column("'A'")).op("||")(
            func.setweight(func.to_tsvector("english", DocumentChunk.content), literal_column("'B'"))
        )
        rank = func.ts_rank_cd(doc_vector, tsquery, 1)
        stmt = select(DocumentChunk).where(doc_vector.op("@@")(tsquery)).order_by(rank.desc()).limit(_CANDIDATES)
        for position, chunk in enumerate((await session.execute(stmt)).scalars().all()):
            by_id[chunk.id] = chunk
            fused[chunk.id] = fused.get(chunk.id, 0.0) + lexical_weight / (_RRF_K + position + 1)

    # 1b) chunks that contain *all* the key terms (a strong signal for multi-word topics
    # like "prompt injection", where "prompt" alone matches half the curriculum)
    all_terms_match = len(terms) >= 2
    if all_terms_match:
        strict_query = func.to_tsquery("english", " & ".join(terms))
        strict_rank = func.ts_rank_cd(doc_vector, strict_query, 1)
        stmt = (
            select(DocumentChunk).where(doc_vector.op("@@")(strict_query)).order_by(strict_rank.desc()).limit(_CANDIDATES // 2)
        )
        for position, chunk in enumerate((await session.execute(stmt)).scalars().all()):
            by_id[chunk.id] = chunk
            fused[chunk.id] = fused.get(chunk.id, 0.0) + 1.0 / (_RRF_K + position + 1)

    # 2) vector ranking
    distance = DocumentChunk.embedding.cosine_distance(embed_text(query))
    stmt = select(DocumentChunk).order_by(distance).limit(_CANDIDATES)
    for position, chunk in enumerate((await session.execute(stmt)).scalars().all()):
        by_id[chunk.id] = chunk
        fused[chunk.id] = fused.get(chunk.id, 0.0) + vector_weight / (_RRF_K + position + 1)

    # 3) chunks of the lesson being viewed
    if lesson_uuid is not None:
        stmt = select(DocumentChunk).where(DocumentChunk.lesson_id == lesson_uuid).order_by(distance).limit(k)
        for chunk in (await session.execute(stmt)).scalars().all():
            by_id[chunk.id] = chunk
            fused[chunk.id] = fused.get(chunk.id, 0.0) + 1.0 / (_RRF_K + 1)  # as if ranked first

    ordered = sorted(fused, key=fused.get, reverse=True)
    best_possible = (
        (lexical_weight + vector_weight) / (_RRF_K + 1)
        + (1.0 / (_RRF_K + 1) if all_terms_match else 0.0)
        + (1.0 / (_RRF_K + 1) if lesson_uuid else 0.0)
    )

    results: list[dict] = []
    per_lesson: dict = {}
    for chunk_id in ordered:
        chunk = by_id[chunk_id]
        if per_lesson.get(chunk.lesson_id, 0) >= _MAX_PER_LESSON:
            continue
        per_lesson[chunk.lesson_id] = per_lesson.get(chunk.lesson_id, 0) + 1
        results.append(
            {
                "content": chunk.content,
                "title": chunk.title,
                "lesson_id": str(chunk.lesson_id) if chunk.lesson_id else None,
                "score": round(fused[chunk_id] / best_possible, 4),
            }
        )
        if len(results) >= k:
            break
    return results
