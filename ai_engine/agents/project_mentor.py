"""Project Mentor Agent — reviews a capstone-style project submission.

This is a TEXT-REVIEW mentor only: it reasons over the project's stated
requirements/evaluation_criteria and the student's submission notes as
text. It never fetches, clones, executes, or otherwise inspects the code at
`submission["repo_url"]` — that URL is treated as an opaque reference the
student included in their notes, not something this agent visits.
"""

from __future__ import annotations

import json
import re

from ai_engine.llm.client import get_chat_model, is_llm_configured
from ai_engine.prompts.project_mentor import PROJECT_MENTOR_SYSTEM_PROMPT

_WORD_RE = re.compile(r"[a-z0-9]{4,}")


def _strip_json_fences(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"```$", "", text.strip())
    return text.strip()


class ProjectMentorAgent:
    def review(self, project: dict, submission: dict) -> dict:
        project = project or {}
        submission = submission or {}
        notes = (submission.get("submission_notes") or "").strip()

        if is_llm_configured():
            try:
                return self._review_llm(project, submission, notes)
            except Exception as exc:  # noqa: BLE001
                print(
                    "[ai_engine.agents.project_mentor] WARNING: LLM project review failed, "
                    f"using rubric heuristic: {exc}"
                )

        return self._review_fallback(project, notes)

    # -- LLM mode --------------------------------------------------------

    def _review_llm(self, project: dict, submission: dict, notes: str) -> dict:
        from langchain_core.messages import HumanMessage, SystemMessage

        model = get_chat_model(temperature=0.3, max_tokens=2500)
        criteria = project.get("evaluation_criteria") or []
        skills = [s.get("slug") for s in (project.get("skills") or []) if s.get("slug")]

        human = (
            f"Project title (data): {project.get('title')}\n"
            f"Objective (data): {project.get('objective')}\n"
            f"Requirements (data): {json.dumps(project.get('requirements') or [])}\n"
            f"Evaluation criteria (data): {json.dumps(criteria)}\n"
            f"Project skills (data, skill_updates keys must match exactly): {json.dumps(skills)}\n"
            f"Student repo_url (data, reference only — do not fetch or execute): {submission.get('repo_url')}\n"
            f"Student submission notes (data): {notes}\n"
            "Evaluate the submission notes against each evaluation criterion and return the required JSON."
        )
        response = model.invoke([SystemMessage(content=PROJECT_MENTOR_SYSTEM_PROMPT), HumanMessage(content=human)])
        raw = getattr(response, "content", None) or str(response)
        data = json.loads(_strip_json_fences(raw))

        score = max(0.0, min(1.0, float(data.get("score", 0.0))))
        skill_updates_raw = data.get("skill_updates") or {}
        skill_updates = {
            slug: max(0.0, min(1.0, float(skill_updates_raw.get(slug, score)))) for slug in skills
        } or {slug: score for slug in skills}

        return {
            "score": round(score, 4),
            "feedback": data.get("feedback") or "Reviewed.",
            "strengths": list(data.get("strengths") or []),
            "improvements": list(data.get("improvements") or []),
            "skill_updates": skill_updates,
        }

    # -- Fallback mode -----------------------------------------------------

    def _review_fallback(self, project: dict, notes: str) -> dict:
        """Real rubric-driven heuristic: scores notes length/specificity and
        how many evaluation_criteria keywords are actually addressed in the
        submission notes, then builds feedback text from the actual project
        title and criteria labels (never generic boilerplate).
        """

        title = project.get("title") or "this project"
        criteria = project.get("evaluation_criteria") or []
        skills = [s.get("slug") for s in (project.get("skills") or []) if s.get("slug")]

        if not notes:
            feedback = (
                f'No submission notes were provided for "{title}", so this review can\'t assess it. '
                "Please describe what you built, how it satisfies each requirement, and any tradeoffs you made."
            )
            return {
                "score": 0.0,
                "feedback": feedback,
                "strengths": [],
                "improvements": [f"Add notes describing how the submission meets: {c.get('criterion')}" for c in criteria]
                or ["Add submission notes describing your work."],
                "skill_updates": {slug: 0.0 for slug in skills},
            }

        notes_words = set(_WORD_RE.findall(notes.lower()))
        notes_word_count = len(notes.split())

        met_criteria = []
        unmet_criteria = []
        for c in criteria:
            criterion_text = c.get("criterion", "")
            criterion_words = set(_WORD_RE.findall(criterion_text.lower()))
            overlap = len(criterion_words & notes_words) if criterion_words else 0
            coverage = overlap / len(criterion_words) if criterion_words else 0.0
            if coverage >= 0.3:
                met_criteria.append((c, coverage))
            else:
                unmet_criteria.append(c)

        # Weighted coverage score across criteria (falls back to a
        # length/specificity heuristic if no criteria were given at all).
        if criteria:
            total_weight = sum(c.get("weight", 1.0 / len(criteria)) for c in criteria) or 1.0
            covered_weight = sum(c.get("weight", 1.0 / len(criteria)) for c, _ in met_criteria)
            coverage_score = covered_weight / total_weight
        else:
            coverage_score = 0.0

        # Specificity bonus: longer, more detailed notes score a bit higher,
        # capped so verbosity alone can't fake a strong review.
        specificity_bonus = min(notes_word_count / 300.0, 1.0) * 0.2

        score = max(0.0, min(1.0, coverage_score * 0.8 + specificity_bonus))

        strengths = [f'Addressed: "{c.get("criterion")}"' for c, _ in met_criteria] or [
            "Notes were submitted, though they don't clearly address the listed evaluation criteria yet."
        ]
        improvements = [f'Add detail on: "{c.get("criterion")}"' for c in unmet_criteria]
        if not criteria:
            improvements = [
                f'No evaluation criteria were configured for "{title}"; scored on notes length/specificity only.'
            ]
        if notes_word_count < 40:
            improvements.append("Submission notes are quite short — add more detail on your implementation and decisions.")

        feedback = (
            f'Reviewed "{title}" against {len(criteria)} evaluation criteria (no LLM configured — this is a '
            f"rubric/keyword heuristic review, not a semantic one). Addressed {len(met_criteria)}/{len(criteria)} "
            f"criteria based on keyword coverage in your notes."
            if criteria
            else f'Reviewed "{title}" (no evaluation criteria configured; scored on notes length/specificity).'
        )

        skill_updates = {slug: round(score, 4) for slug in skills}

        return {
            "score": round(score, 4),
            "feedback": feedback,
            "strengths": strengths,
            "improvements": improvements,
            "skill_updates": skill_updates,
        }
