"""Learning Planner Agent — builds a short, personalized next-steps plan for
one student from their skill mastery data and the available curriculum.
Fully DB-agnostic: plain dicts/lists in, a plain dict out.
"""

from __future__ import annotations

from ai_engine.llm.client import get_chat_model, is_llm_configured
from ai_engine.orchestration.graph import build_planner_graph

_UNLOCK_DEFAULT_THRESHOLD = 0.5
_REVISION_THRESHOLD = 0.4
_ASSESSMENT_RANGE = (0.5, 0.85)
_PROJECT_READY_THRESHOLD = 0.6
_MAX_STEPS = 8
_MIN_STEPS = 4


class PlannerAgent:
    """LLM mode: LangGraph graph (analyze_skills -> identify_gaps ->
    select_content -> write_plan), see
    `ai_engine.orchestration.graph.build_planner_graph`.

    Fallback mode: real rule-based planning over the given skill/curriculum
    data (prerequisite-aware mastery ranking, revision/assessment/project
    step heuristics) — never a generic placeholder plan.
    """

    def generate_plan(self, student_context: dict, curriculum_summary: list[dict]) -> dict:
        student_context = student_context or {}
        curriculum_summary = curriculum_summary or []

        if is_llm_configured():
            try:
                return self._generate_plan_llm(student_context, curriculum_summary)
            except Exception as exc:  # noqa: BLE001 - never raise out to the caller
                print(
                    "[ai_engine.agents.planner] WARNING: LLM planner failed, "
                    f"falling back to rule-based plan: {exc}"
                )

        return self._generate_plan_fallback(student_context, curriculum_summary)

    # -- LLM mode ----------------------------------------------------------

    def _generate_plan_llm(self, student_context: dict, curriculum_summary: list[dict]) -> dict:
        model = get_chat_model(temperature=0.4, max_tokens=3500)  # a full JSON plan; reasoning models spend tokens thinking first
        graph = build_planner_graph(model)
        result = graph.invoke({"student_context": student_context, "curriculum_summary": curriculum_summary})
        plan = result.get("plan")
        if not plan:
            raise RuntimeError("planner graph completed without producing a plan")
        return plan

    # -- Fallback mode -------------------------------------------------------

    def _generate_plan_fallback(self, student_context: dict, curriculum_summary: list[dict]) -> dict:
        skills = student_context.get("skills") or []
        prereqs = student_context.get("skill_prereqs") or {}
        career_goal = student_context.get("career_goal")
        target_role = student_context.get("target_role")

        skills_by_slug = {s.get("slug"): s for s in skills if s.get("slug")}
        unlocked_sorted = self._rank_unlocked_skills(skills, skills_by_slug, prereqs)

        steps: list[dict] = []
        primary_skill = unlocked_sorted[0] if unlocked_sorted else (
            sorted(skills, key=lambda s: s.get("mastery", 0.0))[0] if skills else None
        )

        lesson_step = self._find_lesson_step(primary_skill, curriculum_summary) if primary_skill else None
        if lesson_step:
            steps.append(lesson_step)

        steps.extend(self._revision_steps(skills, limit=_MAX_STEPS - len(steps)))
        steps.extend(self._assessment_steps(skills, limit=_MAX_STEPS - len(steps)))

        if primary_skill and not lesson_step and len(steps) < _MAX_STEPS:
            steps.append(self._practice_step(primary_skill))

        strong_skills = [s for s in skills if s.get("mastery", 0.0) >= _PROJECT_READY_THRESHOLD]
        if len(strong_skills) >= 2 and len(steps) < _MAX_STEPS:
            steps.append(self._project_step(strong_skills))

        if not steps:
            steps.append(
                {
                    "step_type": "lesson",
                    "target_id": None,
                    "title": "Start the curriculum",
                    "reason": "No skill history was found for this student yet, so this plan starts from the "
                    "beginning of the curriculum.",
                    "skill_focus": [],
                }
            )

        steps = self._pad_to_minimum(steps, unlocked_sorted, curriculum_summary)[:_MAX_STEPS]

        summary = self._build_summary(skills, unlocked_sorted, strong_skills, career_goal, target_role, steps)
        reasoning = self._build_reasoning(skills, unlocked_sorted)

        return {"summary": summary, "reasoning": reasoning, "recommended_path": steps}

    @staticmethod
    def _rank_unlocked_skills(skills: list[dict], skills_by_slug: dict, prereqs: dict) -> list[dict]:
        def is_unlocked(skill: dict) -> bool:
            for req_slug, req_mastery in prereqs.get(skill.get("slug")) or []:
                req_skill = skills_by_slug.get(req_slug)
                actual = req_skill.get("mastery", 0.0) if req_skill else 0.0
                threshold = req_mastery if req_mastery is not None else _UNLOCK_DEFAULT_THRESHOLD
                if actual < threshold:
                    return False
            return True

        unlocked = [s for s in skills if is_unlocked(s)]
        return sorted(unlocked, key=lambda s: s.get("mastery", 0.0))

    @staticmethod
    def _find_lesson_step(skill: dict, curriculum_summary: list[dict]) -> dict | None:
        slug = skill.get("slug")
        for item in curriculum_summary:
            if item.get("completed"):
                continue
            if slug in (item.get("skills") or []):
                return {
                    "step_type": "lesson",
                    "target_id": item.get("lesson_id"),
                    "title": item.get("lesson_title") or "Next lesson",
                    "reason": (
                        f"'{skill.get('name', slug)}' is your lowest-mastery unlocked skill "
                        f"(mastery {skill.get('mastery', 0.0):.2f}); this lesson directly builds it."
                    ),
                    "skill_focus": [slug],
                }
        return None

    @staticmethod
    def _revision_steps(skills: list[dict], limit: int) -> list[dict]:
        steps = []
        for s in skills:
            if len(steps) >= max(limit, 0):
                break
            if s.get("mastery", 0.0) < _REVISION_THRESHOLD and s.get("attempts", 0) > 0:
                steps.append(
                    {
                        "step_type": "revision",
                        "target_id": None,
                        "title": f"Revisit {s.get('name', s.get('slug'))}",
                        "reason": (
                            f"'{s.get('name', s.get('slug'))}' is at {s.get('mastery', 0.0):.2f} mastery after "
                            f"{s.get('attempts', 0)} attempt(s) — below the {_REVISION_THRESHOLD} threshold, "
                            "so revision is recommended before moving on."
                        ),
                        "skill_focus": [s.get("slug")],
                    }
                )
        return steps

    @staticmethod
    def _assessment_steps(skills: list[dict], limit: int) -> list[dict]:
        low, high = _ASSESSMENT_RANGE
        steps = []
        for s in skills:
            if len(steps) >= max(limit, 0):
                break
            mastery = s.get("mastery", 0.0)
            if low <= mastery <= high and not s.get("last_assessed_at"):
                steps.append(
                    {
                        "step_type": "assessment",
                        "target_id": None,
                        "title": f"Check readiness: {s.get('name', s.get('slug'))}",
                        "reason": (
                            f"'{s.get('name', s.get('slug'))}' is at {mastery:.2f} mastery, in the "
                            f"ready-to-verify range ({low}-{high}), with no recent assessment recorded."
                        ),
                        "skill_focus": [s.get("slug")],
                    }
                )
        return steps

    @staticmethod
    def _practice_step(skill: dict) -> dict:
        return {
            "step_type": "practice",
            "target_id": None,
            "title": f"Practice: {skill.get('name', skill.get('slug'))}",
            "reason": (
                f"No incomplete lesson was found in the given curriculum for '{skill.get('name')}'; "
                "targeted practice is recommended instead."
            ),
            "skill_focus": [skill.get("slug")],
        }

    @staticmethod
    def _project_step(strong_skills: list[dict]) -> dict:
        top = strong_skills[:3]
        names = ", ".join(s.get("name", s.get("slug")) for s in top)
        return {
            "step_type": "project",
            "target_id": None,
            "title": "Apply your skills in a project",
            "reason": (
                f"You have {len(strong_skills)} skill(s) at {_PROJECT_READY_THRESHOLD}+ mastery ({names}); "
                "a project step consolidates them into applied, portfolio-worthy practice."
            ),
            "skill_focus": [s.get("slug") for s in top],
        }

    @staticmethod
    def _pad_to_minimum(steps: list[dict], unlocked_sorted: list[dict], curriculum_summary: list[dict]) -> list[dict]:
        if len(steps) >= _MIN_STEPS:
            return steps
        covered = {slug for step in steps for slug in step.get("skill_focus", [])}
        for s in unlocked_sorted:
            if len(steps) >= _MIN_STEPS:
                break
            slug = s.get("slug")
            if slug in covered:
                continue
            for item in curriculum_summary:
                if item.get("completed"):
                    continue
                if slug in (item.get("skills") or []):
                    steps.append(
                        {
                            "step_type": "lesson",
                            "target_id": item.get("lesson_id"),
                            "title": item.get("lesson_title") or "Next lesson",
                            "reason": (
                                f"Builds '{s.get('name', slug)}' (mastery {s.get('mastery', 0.0):.2f}), next in "
                                "ascending-mastery order among your unlocked skills."
                            ),
                            "skill_focus": [slug],
                        }
                    )
                    covered.add(slug)
                    break
        return steps

    @staticmethod
    def _build_summary(skills, unlocked_sorted, strong_skills, career_goal, target_role, steps) -> str:
        if not skills:
            return "No skill history was found for this student, so this plan starts from the beginning of the curriculum."

        weakest = unlocked_sorted[0] if unlocked_sorted else sorted(skills, key=lambda s: s.get("mastery", 0.0))[0]
        goal_bit = f" toward your goal of becoming a {target_role or career_goal}" if (target_role or career_goal) else ""
        step_types = sorted({step["step_type"] for step in steps})
        parts = [
            f"This plan focuses first on '{weakest.get('name', weakest.get('slug'))}' "
            f"(currently {weakest.get('mastery', 0.0):.0%} mastery){goal_bit}, with {len(steps)} step(s) "
            f"covering {', '.join(step_types)}."
        ]
        if strong_skills:
            names = ", ".join(s.get("name", s.get("slug")) for s in strong_skills[:3])
            parts.append(
                f"You're already strong in {len(strong_skills)} skill(s) ({names}), which is why applied/"
                "project practice is included."
            )
        return " ".join(parts)

    @staticmethod
    def _build_reasoning(skills: list[dict], unlocked_sorted: list[dict]) -> str:
        if not skills:
            return "No prior skill data was available for this student, so no prerequisite/mastery ranking could be computed."

        unlocked_slugs = {s.get("slug") for s in unlocked_sorted}
        locked = [s for s in skills if s.get("slug") not in unlocked_slugs]

        lines = [
            "Skills were ranked by ascending mastery among those whose prerequisites are sufficiently met "
            "(default required mastery 0.5 where not otherwise specified): "
            + ", ".join(f"{s.get('name', s.get('slug'))} ({s.get('mastery', 0.0):.2f})" for s in unlocked_sorted[:6])
            + "."
        ]
        if locked:
            lines.append(
                "These skills are not yet unlocked because their prerequisites aren't sufficiently met: "
                + ", ".join(s.get("name", s.get("slug")) for s in locked[:6])
                + "."
            )
        return " ".join(lines)
