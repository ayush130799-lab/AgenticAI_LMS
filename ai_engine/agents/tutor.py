"""AI Tutor Agent — answers a student's question, grounded in retrieved
lesson content (RAG). Fully DB-agnostic: takes plain dicts/lists in, returns
a plain dict out.
"""

from __future__ import annotations

import re

from ai_engine.llm.client import get_chat_model, is_llm_configured
from ai_engine.memory.conversation_memory import to_langchain_messages
from ai_engine.orchestration.graph import build_tutor_graph

_HISTORY_LIMIT = 10


class TutorAgent:
    """LLM mode: LangGraph graph (build_context -> generate -> extract_citations),
    see `ai_engine.orchestration.graph.build_tutor_graph`.

    Fallback mode: a real, content-driven answer templated from the top
    retrieved chunks (quotes/paraphrases the most question-relevant
    sentences and names the source lesson) — not a generic apology.
    """

    def respond(self, question: str, context: dict, history: list[dict], retrieved_chunks: list[dict]) -> dict:
        question = (question or "").strip()
        context = context or {}
        retrieved_chunks = retrieved_chunks or []

        if not question:
            return {"reply": "I didn't receive a question — could you ask again?", "citations": []}

        if is_llm_configured():
            try:
                return self._respond_llm(question, context, history or [], retrieved_chunks)
            except Exception as exc:  # noqa: BLE001 - never raise out to the caller
                print(
                    "[ai_engine.agents.tutor] WARNING: LLM tutor call failed, "
                    f"falling back to templated answer: {exc}"
                )

        return self._respond_fallback(question, context, retrieved_chunks)

    # -- LLM mode ----------------------------------------------------------

    def _respond_llm(self, question: str, context: dict, history: list[dict], retrieved_chunks: list[dict]) -> dict:
        model = get_chat_model(temperature=0.3)
        graph = build_tutor_graph(model)
        history_messages = to_langchain_messages(history, limit=_HISTORY_LIMIT)

        result = graph.invoke(
            {
                "question": question,
                "context": context,
                "history_messages": history_messages,
                "retrieved_chunks": retrieved_chunks,
            }
        )
        reply = result.get("raw_reply") or "I wasn't able to generate a response — please try again."
        citations = result.get("citations") or []
        return {"reply": reply, "citations": citations}

    # -- Fallback mode -------------------------------------------------------

    def _respond_fallback(self, question: str, context: dict, retrieved_chunks: list[dict]) -> dict:
        student_level = context.get("student_level")
        top_chunks = retrieved_chunks[:2]

        if not top_chunks:
            location = self._location_str(context)
            where = f" for {location}" if location else ""
            reply = (
                f'I don\'t have any retrieved lesson content to ground an answer to "{question}"{where}. '
                "This tutor is currently running without an LLM connected, so it can only answer from "
                "retrieved course excerpts. Try asking about a specific lesson topic, or check that the "
                "relevant lesson content has been indexed."
            )
            return {"reply": reply, "citations": []}

        pieces = []
        citations = []
        seen_lessons: set = set()
        for chunk in top_chunks:
            title = chunk.get("title") or "this lesson"
            snippet = self._best_sentences(chunk.get("content") or "", question)
            pieces.append(f'From "{title}": {snippet}')
            lesson_id = chunk.get("lesson_id")
            if lesson_id and lesson_id not in seen_lessons:
                citations.append({"lesson_id": lesson_id, "title": title})
                seen_lessons.add(lesson_id)

        level_note = f" (adapted for a {student_level} level)" if student_level else ""
        reply = (
            f"Based on the course material{level_note}:\n\n"
            + "\n\n".join(pieces)
            + (
                "\n\n(The AI model could not be reached just now, so this answer is assembled directly from the "
                "retrieved lesson excerpts above instead of being explained in the model's own words. "
                "Please try again in a moment.)"
                if is_llm_configured()
                else "\n\n(No LLM is currently configured, so this answer is assembled directly from the "
                "retrieved lesson excerpts above rather than freely explained — ask a follow-up if you need "
                "more detail on a specific part.)"
            )
        )
        return {"reply": reply, "citations": citations}

    @staticmethod
    def _location_str(context: dict) -> str:
        bits = [context.get(k) for k in ("course_title", "module_title", "lesson_title") if context.get(k)]
        return " > ".join(bits)

    @staticmethod
    def _best_sentences(content: str, question: str, max_sentences: int = 2) -> str:
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", content.strip()) if s]
        if not sentences:
            return content.strip()[:400]

        question_words = set(re.findall(r"[a-z0-9]{3,}", question.lower()))
        scored = [
            (len(set(re.findall(r"[a-z0-9]{3,}", s.lower())) & question_words), i, s)
            for i, s in enumerate(sentences)
        ]
        scored.sort(key=lambda triple: triple[0], reverse=True)
        top_indices = sorted(i for _, i, _ in scored[:max_sentences])
        if not top_indices or scored[0][0] == 0:
            # No lexical overlap with the question — just lead with the
            # opening sentences, which is usually the concept definition.
            return " ".join(sentences[:max_sentences])
        return " ".join(sentences[i] for i in top_indices)
