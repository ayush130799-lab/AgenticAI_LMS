"""Assessment Agent — grades submitted answers and generates practice
questions. Fully DB-agnostic: plain dicts in, plain dicts out.
"""

from __future__ import annotations

import json
import re

from ai_engine.llm.client import get_chat_model, is_llm_configured
from ai_engine.prompts.assessment import GRADING_SYSTEM_PROMPT, PRACTICE_GENERATION_SYSTEM_PROMPT

_WORD_RE = re.compile(r"[a-z0-9]{4,}")


def _strip_json_fences(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"```$", "", text.strip())
    return text.strip()


class AssessmentAgent:
    """`mcq`/`multi_select` are graded deterministically (no LLM needed).
    `short_answer`/`coding`/`scenario` always get a real heuristic score;
    when an LLM is configured, it additionally judges semantic/behavioral
    correctness and that judgment is preferred over the heuristic.
    """

    # -- Grading -------------------------------------------------------------

    def grade(self, questions: list[dict], answers: dict) -> dict:
        answers = answers or {}
        per_question: list[dict] = []
        skill_scores_raw: dict[str, list[float]] = {}
        skill_names: dict[str, str] = {}
        total_points = 0.0
        earned_points = 0.0

        for q in questions or []:
            qid = str(q.get("id"))
            qtype = q.get("question_type")
            points = float(q.get("points", 1.0) or 1.0)
            skill_slug = q.get("skill_slug")
            student_answer = answers.get(qid)

            if qtype == "mcq":
                score, correct, feedback = self._grade_mcq(q, student_answer)
            elif qtype == "multi_select":
                score, correct, feedback = self._grade_multi_select(q, student_answer)
            elif qtype == "short_answer":
                score, correct, feedback = self._grade_short_answer(q, student_answer)
            elif qtype in ("coding", "scenario"):
                score, correct, feedback = self._grade_open(q, student_answer)
            else:
                score, correct, feedback = 0.0, False, f"Unknown question type '{qtype}'; not graded."

            per_question.append(
                {"question_id": qid, "correct": bool(correct), "score": round(float(score), 4), "feedback": feedback}
            )
            total_points += points
            earned_points += score * points

            if skill_slug:
                skill_scores_raw.setdefault(skill_slug, []).append(score)
                skill_names[skill_slug] = q.get("skill_name") or skill_slug

        total_score = round(earned_points / total_points, 4) if total_points > 0 else 0.0
        skill_scores = {
            slug: round(sum(scores) / len(scores), 4) for slug, scores in skill_scores_raw.items()
        }
        weak_concepts = [skill_names[slug] for slug, score in skill_scores.items() if score < 0.5]
        strengths = [skill_names[slug] for slug, score in skill_scores.items() if score >= 0.85]

        return {
            "total_score": total_score,
            "per_question": per_question,
            "skill_scores": skill_scores,
            "weak_concepts": weak_concepts,
            "strengths": strengths,
        }

    @staticmethod
    def _grade_mcq(q: dict, student_answer) -> tuple[float, bool, str]:
        expected = (q.get("correct_answer") or {}).get("choice")
        given = student_answer.get("choice") if isinstance(student_answer, dict) else student_answer
        correct = given is not None and expected is not None and str(given) == str(expected)
        feedback = "Correct." if correct else f"Incorrect — the correct choice was '{expected}'."
        return (1.0 if correct else 0.0), correct, feedback

    @staticmethod
    def _grade_multi_select(q: dict, student_answer) -> tuple[float, bool, str]:
        expected = set((q.get("correct_answer") or {}).get("choices") or [])
        given_raw = student_answer.get("choices") if isinstance(student_answer, dict) else student_answer
        given = set(given_raw or [])
        correct = expected == given
        feedback = "Correct." if correct else f"Incorrect — the correct choices were {sorted(expected)}."
        return (1.0 if correct else 0.0), correct, feedback

    def _grade_short_answer(self, q: dict, student_answer) -> tuple[float, bool, str]:
        answer_text = str(student_answer or "").strip()
        if not answer_text:
            return 0.0, False, "No answer submitted."

        correct_answer = q.get("correct_answer") or {}
        keywords = [k.lower() for k in (correct_answer.get("keywords") or [])]
        expected = correct_answer.get("expected", "")
        answer_lower = answer_text.lower()

        if keywords:
            hits = sum(1 for kw in keywords if kw in answer_lower)
            score = hits / len(keywords)
            feedback = f"Matched {hits}/{len(keywords)} expected keywords/concepts."
        elif expected:
            score = 1.0 if expected.lower() in answer_lower else 0.4
            feedback = "Matched the reference answer." if score == 1.0 else "Partially overlaps the reference answer."
        else:
            score = 0.5
            feedback = "No reference keywords/answer configured; scored as a neutral partial credit."

        if is_llm_configured():
            try:
                llm_score, llm_feedback = self._llm_judge(q.get("prompt", ""), expected, answer_text, "short_answer")
                score, feedback = llm_score, llm_feedback
            except Exception as exc:  # noqa: BLE001
                print(
                    "[ai_engine.agents.assessment] WARNING: LLM short_answer grading failed, "
                    f"using keyword heuristic: {exc}"
                )

        return score, score >= 0.6, feedback

    def _grade_open(self, q: dict, student_answer) -> tuple[float, bool, str]:
        answer_text = str(student_answer or "").strip()
        if not answer_text:
            return 0.0, False, "No answer submitted."

        correct_answer = q.get("correct_answer") or {}
        expected_text = correct_answer.get("expected_behavior") or correct_answer.get("expected") or ""
        score = self._keyword_structure_score(expected_text, answer_text)
        feedback = f"Heuristic check: answer covers {score:.0%} of the expected key concepts."

        if is_llm_configured():
            try:
                llm_score, llm_feedback = self._llm_judge(
                    q.get("prompt", ""), expected_text, answer_text, q.get("question_type", "coding")
                )
                score, feedback = llm_score, llm_feedback
            except Exception as exc:  # noqa: BLE001
                print(
                    f"[ai_engine.agents.assessment] WARNING: LLM {q.get('question_type')} grading failed, "
                    f"using heuristic floor: {exc}"
                )

        return score, score >= 0.6, feedback

    @staticmethod
    def _keyword_structure_score(expected_text: str, answer_text: str) -> float:
        expected_words = set(_WORD_RE.findall(expected_text.lower()))
        if not expected_words:
            return 0.5 if answer_text.strip() else 0.0
        answer_words = set(_WORD_RE.findall(answer_text.lower()))
        overlap = len(expected_words & answer_words)
        return round(min(overlap / len(expected_words), 1.0), 4)

    @staticmethod
    def _llm_judge(prompt: str, expected: str, answer: str, qtype: str) -> tuple[float, str]:
        from langchain_core.messages import HumanMessage, SystemMessage

        model = get_chat_model(temperature=0.0)
        human = (
            f"Question type: {qtype}\nQuestion prompt (data): {prompt}\n"
            f"Reference/expected answer (data): {expected}\nStudent answer (data): {answer}\n"
            "Judge the student answer strictly against the reference and return the required JSON."
        )
        response = model.invoke([SystemMessage(content=GRADING_SYSTEM_PROMPT), HumanMessage(content=human)])
        raw = getattr(response, "content", None) or str(response)
        data = json.loads(_strip_json_fences(raw))
        score = max(0.0, min(1.0, float(data.get("score", 0.0))))
        feedback = data.get("feedback") or ("Correct." if data.get("correct") else "Incorrect.")
        return score, feedback

    # -- Practice question generation ----------------------------------------

    def generate_practice_questions(self, skill_slug: str, skill_name: str, level: str, n: int = 3) -> list[dict]:
        if is_llm_configured():
            try:
                questions = self._generate_practice_llm(skill_slug, skill_name, level, n)
                if questions:
                    return questions
            except Exception as exc:  # noqa: BLE001
                print(
                    "[ai_engine.agents.assessment] WARNING: LLM practice-question generation failed, "
                    f"using static fallback bank: {exc}"
                )

        return self._generate_practice_fallback(skill_slug, skill_name, level, n)

    def _generate_practice_llm(self, skill_slug: str, skill_name: str, level: str, n: int) -> list[dict]:
        from langchain_core.messages import HumanMessage, SystemMessage

        model = get_chat_model(temperature=0.5, max_tokens=2500)
        human = (
            f"Skill slug (data): {skill_slug}\nSkill name (data): {skill_name}\n"
            f"Student level (data): {level}\nGenerate exactly {n} new practice questions."
        )
        response = model.invoke(
            [SystemMessage(content=PRACTICE_GENERATION_SYSTEM_PROMPT), HumanMessage(content=human)]
        )
        raw = getattr(response, "content", None) or str(response)
        data = json.loads(_strip_json_fences(raw))
        if not isinstance(data, list):
            raise ValueError("expected a JSON array of questions")

        questions = []
        for item in data[:n]:
            if not isinstance(item, dict) or "prompt" not in item:
                continue
            item.setdefault("skill_slug", skill_slug)
            item.setdefault("difficulty", "medium")
            item.setdefault("points", 1.0)
            item.setdefault("options", [])
            item.setdefault("correct_answer", {})
            questions.append(item)
        return questions

    def _generate_practice_fallback(self, skill_slug: str, skill_name: str, level: str, n: int) -> list[dict]:
        bank = _STATIC_PRACTICE_BANK.get(skill_slug)
        skill_name = skill_name or skill_slug

        if bank:
            questions = [dict(q, skill_slug=skill_slug) for q in bank]
        else:
            questions = [
                {
                    "question_type": "short_answer",
                    "prompt": (
                        f"In your own words, explain what '{skill_name}' means in the context of building "
                        f"agentic AI systems, and give one concrete example of applying it."
                    ),
                    "options": [],
                    "correct_answer": {
                        "expected": f"A clear, accurate explanation of {skill_name} with a relevant example.",
                        "keywords": [w.lower() for w in skill_name.split() if len(w) > 3] or [skill_slug],
                    },
                    "explanation": (
                        f"This is a generic static fallback question for '{skill_slug}' — no hand-authored "
                        "practice bank exists for this skill yet, and no LLM is configured to generate one."
                    ),
                    "difficulty": "medium",
                    "points": 1.0,
                    "skill_slug": skill_slug,
                },
                {
                    "question_type": "short_answer",
                    "prompt": (
                        f"Describe one common mistake learners make with '{skill_name}', and how to avoid it."
                    ),
                    "options": [],
                    "correct_answer": {
                        "expected": f"A realistic pitfall related to {skill_name} and a concrete fix.",
                        "keywords": [w.lower() for w in skill_name.split() if len(w) > 3] or [skill_slug],
                    },
                    "explanation": (
                        f"Generic static fallback question for '{skill_slug}' (static bank / no LLM configured)."
                    ),
                    "difficulty": "medium",
                    "points": 1.0,
                    "skill_slug": skill_slug,
                },
            ]

        return questions[:n] if n else questions


# --------------------------------------------------------------------------
# Static practice-question bank used by the no-LLM fallback for the core
# skill categories, so the feature is genuinely useful offline.
# --------------------------------------------------------------------------

_STATIC_PRACTICE_BANK: dict[str, list[dict]] = {
    "python": [
        {
            "question_type": "mcq",
            "prompt": "What does the following return? `len({1: 'a', 2: 'b', 2: 'c'})`",
            "options": [{"id": "a", "text": "1"}, {"id": "b", "text": "2"}, {"id": "c", "text": "3"}, {"id": "d", "text": "Error"}],
            "correct_answer": {"choice": "b"},
            "explanation": "Dict keys are unique; the second `2: 'c'` overwrites `2: 'b'`, leaving 2 keys.",
            "difficulty": "easy",
            "points": 1.0,
        },
        {
            "question_type": "short_answer",
            "prompt": "Explain the difference between a Python list and a tuple, and give one situation where you'd prefer a tuple.",
            "options": [],
            "correct_answer": {
                "expected": "Lists are mutable and ordered; tuples are immutable and ordered. Prefer tuples for fixed, hashable records (e.g. dict keys) or to signal data shouldn't change.",
                "keywords": ["mutable", "immutable", "hashable"],
            },
            "explanation": "Immutability is the key distinguishing property and drives when tuples are the right choice.",
            "difficulty": "medium",
            "points": 1.0,
        },
    ],
    "llm": [
        {
            "question_type": "mcq",
            "prompt": "Why do LLMs have a fixed 'context window'?",
            "options": [
                {"id": "a", "text": "Training data cutoff date"},
                {"id": "b", "text": "Self-attention cost scales with sequence length"},
                {"id": "c", "text": "Licensing restrictions"},
                {"id": "d", "text": "Tokenizer vocabulary size"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Self-attention compute/memory grows with sequence length, so models are trained and served with a bounded context window.",
            "difficulty": "medium",
            "points": 1.0,
        },
        {
            "question_type": "short_answer",
            "prompt": "What is 'temperature' when sampling from an LLM, and what happens as it approaches 0?",
            "options": [],
            "correct_answer": {
                "expected": "Temperature scales the randomness of next-token sampling; near 0 it becomes close to greedy/deterministic, always picking the highest-probability token.",
                "keywords": ["randomness", "deterministic", "sampling"],
            },
            "explanation": "Lower temperature sharpens the probability distribution toward the most likely token.",
            "difficulty": "easy",
            "points": 1.0,
        },
    ],
    "rag": [
        {
            "question_type": "mcq",
            "prompt": "In a RAG pipeline, what is the primary purpose of the retrieval step?",
            "options": [
                {"id": "a", "text": "Fine-tune the model weights"},
                {"id": "b", "text": "Fetch relevant grounding content to include in the prompt"},
                {"id": "c", "text": "Compress the model for faster inference"},
                {"id": "d", "text": "Tokenize the user query"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Retrieval finds relevant chunks so the LLM can generate an answer grounded in real content instead of relying only on parametric memory.",
            "difficulty": "easy",
            "points": 1.0,
        },
        {
            "question_type": "short_answer",
            "prompt": "Why does chunk size matter in a RAG system, and what's the tradeoff between small and large chunks?",
            "options": [],
            "correct_answer": {
                "expected": "Small chunks retrieve more precisely but can lose surrounding context; large chunks preserve context but dilute relevance and use more tokens.",
                "keywords": ["precision", "context", "tradeoff"],
            },
            "explanation": "Chunk size directly affects retrieval precision versus contextual completeness.",
            "difficulty": "medium",
            "points": 1.0,
        },
    ],
    "agents": [
        {
            "question_type": "mcq",
            "prompt": "What primarily distinguishes an 'agent' from a single-shot LLM call?",
            "options": [
                {"id": "a", "text": "It uses a larger model"},
                {"id": "b", "text": "It can plan, use tools, and take multi-step actions toward a goal"},
                {"id": "c", "text": "It only works with images"},
                {"id": "d", "text": "It has no system prompt"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Agents reason iteratively, decide when to call tools, and adapt across multiple steps rather than answering once.",
            "difficulty": "easy",
            "points": 1.0,
        },
        {
            "question_type": "short_answer",
            "prompt": "Why should an agent's tools be narrowly scoped and explicit rather than giving the agent broad system access?",
            "options": [],
            "correct_answer": {
                "expected": "Narrow, explicit tools limit the blast radius of mistakes or prompt injection, make behavior auditable, and let permissions be reasoned about per-action.",
                "keywords": ["safety", "permission", "scope"],
            },
            "explanation": "This is a core AI-safety principle: least-privilege tool access reduces the risk and impact of agent errors or manipulation.",
            "difficulty": "medium",
            "points": 1.0,
        },
    ],
    "langchain": [
        {
            "question_type": "mcq",
            "prompt": "In LangChain, what does the `@tool` decorator primarily do?",
            "options": [
                {"id": "a", "text": "Trains a new model"},
                {"id": "b", "text": "Wraps a Python function so an LLM can call it with structured arguments"},
                {"id": "c", "text": "Deletes unused imports"},
                {"id": "d", "text": "Compiles a LangGraph state machine"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "`@tool` turns a typed Python function into a LangChain Tool the model can invoke with structured arguments.",
            "difficulty": "easy",
            "points": 1.0,
        },
        {
            "question_type": "short_answer",
            "prompt": "What problem do LangChain's prompt template abstractions solve?",
            "options": [],
            "correct_answer": {
                "expected": "They let you parameterize and reuse prompt text safely, keeping variable substitution, formatting, and versioning consistent across calls.",
                "keywords": ["reuse", "parameterize", "template"],
            },
            "explanation": "Templates decouple prompt structure from runtime values, improving reuse and consistency.",
            "difficulty": "medium",
            "points": 1.0,
        },
    ],
    "langgraph": [
        {
            "question_type": "mcq",
            "prompt": "What is the core unit of state in a LangGraph `StateGraph`?",
            "options": [
                {"id": "a", "text": "A single global variable"},
                {"id": "b", "text": "A typed state object (e.g. TypedDict) threaded through nodes"},
                {"id": "c", "text": "A database row"},
                {"id": "d", "text": "An environment variable"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "LangGraph nodes read and return updates to a shared typed state object, which the graph merges between steps.",
            "difficulty": "medium",
            "points": 1.0,
        },
        {
            "question_type": "short_answer",
            "prompt": "Why would you model a multi-step agent workflow as a LangGraph graph instead of a single long prompt?",
            "options": [],
            "correct_answer": {
                "expected": "A graph makes each reasoning step independently testable, supports branching/looping/conditional edges, and lets you inspect or checkpoint state between steps.",
                "keywords": ["state", "branching", "testable"],
            },
            "explanation": "Explicit graph structure gives control flow, observability, and testability that a single prompt can't.",
            "difficulty": "medium",
            "points": 1.0,
        },
    ],
}
