"""Chunking helpers used to build `DocumentChunk` rows for the RAG index.

Pure functions only — nothing here touches the database. The backend's
seed/ingestion service calls `build_lesson_chunks`, embeds each chunk's
`content` with `ai_engine.rag.embedder.embed_text`, and inserts the rows.
"""

from __future__ import annotations

import re

_PARAGRAPH_RE = re.compile(r"\n\s*\n")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(paragraph: str) -> list[str]:
    return [s for s in _SENTENCE_RE.split(paragraph.strip()) if s]


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Word-based chunking with overlap.

    Prefers to break on paragraph/sentence boundaries: text is split into
    paragraphs, then sentences, and sentences are packed into chunks of up
    to `chunk_size` words. Each new chunk starts with the last `overlap`
    words of the previous chunk so retrieval doesn't lose context at chunk
    edges. A single sentence longer than `chunk_size` is hard-split on word
    count as a fallback.
    """

    if not text or not text.strip():
        return []
    if chunk_size <= 0:
        return [text.strip()]
    overlap = max(0, min(overlap, chunk_size - 1))

    sentences: list[str] = []
    for paragraph in _PARAGRAPH_RE.split(text.strip()):
        if paragraph.strip():
            sentences.extend(_split_sentences(paragraph))

    chunks: list[str] = []
    current: list[str] = []

    def flush():
        if current:
            chunks.append(" ".join(current))

    for sentence in sentences:
        words = sentence.split()
        if not words:
            continue

        if current and len(current) + len(words) > chunk_size:
            flush()
            current = current[-overlap:] if overlap else []

        current.extend(words)

        # Hard-split an over-long run (e.g. one giant sentence/code block).
        while len(current) > chunk_size:
            chunks.append(" ".join(current[:chunk_size]))
            step = chunk_size - overlap if chunk_size > overlap else chunk_size
            current = current[step:]

    flush()
    return chunks


def build_lesson_chunks(lesson: dict) -> list[dict]:
    """Build retrieval-ready chunks for a lesson dict.

    `lesson` keys: id, title, content_markdown, examples (optional).
    Returns `[{"content": str, "chunk_index": int, "title": str}, ...]`
    ready for embedding + insertion by the backend.
    """

    title = lesson.get("title") or "Untitled Lesson"
    content_markdown = (lesson.get("content_markdown") or "").strip()
    examples = lesson.get("examples") or []

    parts: list[str] = []
    if content_markdown:
        parts.append(content_markdown)

    for example in examples:
        ex_title = (example or {}).get("title", "Example")
        ex_explanation = (example or {}).get("explanation", "")
        ex_code = (example or {}).get("code", "")
        example_text = f"{ex_title}\n{ex_explanation}".strip()
        if ex_code:
            example_text = f"{example_text}\n```\n{ex_code}\n```"
        if example_text.strip():
            parts.append(example_text)

    full_text = "\n\n".join(parts)
    chunks = chunk_text(full_text)

    return [
        {"content": chunk, "chunk_index": index, "title": title}
        for index, chunk in enumerate(chunks)
    ]
