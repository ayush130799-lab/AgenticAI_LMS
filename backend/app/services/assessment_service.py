from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import ActivityLog
from app.models.assessment import Assessment, AssessmentAttempt, Question
from app.models.curriculum import Skill
from app.models.user import StudentProfile
from app.services import planner_service, skill_service

from ai_engine.agents.assessment import AssessmentAgent

_assessment_agent = AssessmentAgent()

DIAGNOSTIC_SLUG_TITLE = "Agentic AI LMS Diagnostic Assessment"


def normalize_answer(question_type: str, raw):
    """Translate the client's answer payload into the grader's canonical shape.

    The frontend submits {selected}, {text} or {code}; the grader expects
    {choice} / {choices} for choice questions and plain text for open ones.
    Canonical shapes pass through unchanged.
    """
    if raw is None:
        return None
    if question_type == "mcq":
        if isinstance(raw, dict):
            value = raw.get("choice", raw.get("selected"))
            if isinstance(value, list):
                value = value[0] if value else None
            return {"choice": value}
        return {"choice": raw}
    if question_type == "multi_select":
        if isinstance(raw, dict):
            value = raw.get("choices", raw.get("selected"))
        else:
            value = raw
        if value is None:
            value = []
        return {"choices": list(value) if isinstance(value, (list, tuple, set)) else [value]}
    if isinstance(raw, dict):
        return raw.get("text") or raw.get("code") or raw.get("answer") or ""
    return str(raw)


async def list_assessments(db: AsyncSession, user_id: UUID) -> list[dict]:
    result = await db.execute(select(Assessment).where(Assessment.assessment_type != "module_quiz").options(selectinload(Assessment.questions)).order_by(Assessment.created_at))
    assessments = result.scalars().all()

    attempts_result = await db.execute(
        select(AssessmentAttempt).where(AssessmentAttempt.user_id == user_id, AssessmentAttempt.status == "graded")
    )
    latest_score: dict[UUID, float] = {}
    for attempt in attempts_result.scalars().all():
        latest_score[attempt.assessment_id] = attempt.score or 0.0

    out = []
    for a in assessments:
        out.append({
            "id": a.id, "title": a.title, "description": a.description, "assessment_type": a.assessment_type,
            "passing_score": a.passing_score, "time_limit_minutes": a.time_limit_minutes,
            "question_count": len(a.questions), "last_score_percent": round(latest_score[a.id] * 100, 1) if a.id in latest_score else None,
        })
    return out


async def get_diagnostic_assessment(db: AsyncSession) -> Assessment:
    result = await db.execute(
        select(Assessment)
        .where(Assessment.assessment_type == "diagnostic")
        .options(selectinload(Assessment.questions))
        .order_by(Assessment.created_at)
    )
    assessment = result.scalars().first()
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnostic assessment not seeded yet")
    return assessment


async def get_assessment(db: AsyncSession, assessment_id: UUID) -> Assessment:
    result = await db.execute(
        select(Assessment).where(Assessment.id == assessment_id).options(selectinload(Assessment.questions))
    )
    assessment = result.scalar_one_or_none()
    if assessment is None or assessment.assessment_type == "module_quiz":
        # Module assessments are only reachable through /module-assessments (they are gated and graded there).
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return assessment


async def start_attempt(db: AsyncSession, user_id: UUID, assessment_id: UUID) -> AssessmentAttempt:
    await get_assessment(db, assessment_id)  # 404s if missing
    attempt = AssessmentAttempt(
        user_id=user_id, assessment_id=assessment_id, status="in_progress", started_at=datetime.now(timezone.utc)
    )
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)
    return attempt


async def submit_attempt(db: AsyncSession, user_id: UUID, attempt_id: UUID, answers: dict) -> dict:
    result = await db.execute(select(AssessmentAttempt).where(AssessmentAttempt.id == attempt_id))
    attempt = result.scalar_one_or_none()
    if attempt is None or attempt.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    if attempt.status == "graded":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attempt already graded")

    assessment = await get_assessment(db, attempt.assessment_id)
    questions = [
        {
            "id": str(q.id), "question_type": q.question_type, "correct_answer": q.correct_answer,
            "points": q.points, "skill_slug": None,
        }
        for q in assessment.questions
    ]
    # attach skill slugs
    skill_ids = {q.skill_id for q in assessment.questions if q.skill_id}
    skill_map: dict[UUID, Skill] = {}
    if skill_ids:
        skills_result = await db.execute(select(Skill).where(Skill.id.in_(skill_ids)))
        skill_map = {s.id: s for s in skills_result.scalars().all()}
    for q, qd in zip(assessment.questions, questions):
        qd["skill_slug"] = skill_map[q.skill_id].slug if q.skill_id else None
        qd["skill_name"] = skill_map[q.skill_id].name if q.skill_id else None

    type_by_id = {q["id"]: q["question_type"] for q in questions}
    normalized = {qid: normalize_answer(type_by_id[qid], raw) for qid, raw in answers.items() if qid in type_by_id}
    grading = _assessment_agent.grade(questions=questions, answers=normalized)

    attempt.answers = answers
    attempt.score = grading["total_score"]
    attempt.skill_breakdown = grading["skill_scores"]
    attempt.weak_concepts = grading["weak_concepts"]
    attempt.status = "graded"
    attempt.submitted_at = datetime.now(timezone.utc)

    if assessment.assessment_type == "diagnostic":
        profile_result = await db.execute(select(StudentProfile).where(StudentProfile.user_id == user_id))
        profile = profile_result.scalar_one_or_none()
        if profile:
            profile.diagnostic_completed = True

    db.add(ActivityLog(
        user_id=user_id, action="assessment_completed", entity_type="assessment", entity_id=assessment.id,
        metadata_json={"title": assessment.title, "score_percent": round(grading["total_score"] * 100, 1)},
    ))
    await db.commit()

    # update the student's persistent skill profile from this evidence
    source = "assessment" if assessment.assessment_type in ("diagnostic", "course_exam") else "quiz"
    skill_results = []
    for skill_slug, score_percent in grading["skill_scores"].items():
        skill_result = await db.execute(select(Skill).where(Skill.slug == skill_slug))
        skill = skill_result.scalar_one_or_none()
        if skill is None:
            continue
        updated = await skill_service.apply_evidence(db, user_id, skill.id, score_percent, source=source)
        skill_results.append({
            "skill_slug": skill.slug, "skill_name": skill.name,
            "score_percent": round(score_percent * 100, 1), "mastery_after": round(updated.mastery * 100, 1),
        })

    await planner_service.refresh_plan_after_evidence(db, user_id)

    return {
        "attempt_id": attempt.id,
        "score": round(grading["total_score"] * 100, 1),
        "passed": grading["total_score"] >= assessment.passing_score,
        "skill_breakdown": skill_results,
        "weak_concepts": grading["weak_concepts"],
        "strengths": grading["strengths"],
        "recommended_next_steps": [
            f"Revisit lessons covering {concept}" for concept in grading["weak_concepts"][:3]
        ] or ["Great work — move on to the next module."],
    }


async def get_attempt_results(db: AsyncSession, user_id: UUID, attempt_id: UUID) -> dict:
    result = await db.execute(select(AssessmentAttempt).where(AssessmentAttempt.id == attempt_id))
    attempt = result.scalar_one_or_none()
    if attempt is None or attempt.user_id != user_id or attempt.status != "graded":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Graded attempt not found")

    assessment = await get_assessment(db, attempt.assessment_id)
    skill_breakdown = []
    for slug, pct in attempt.skill_breakdown.items():
        skills_result = await db.execute(select(Skill).where(Skill.slug == slug))
        skill = skills_result.scalar_one_or_none()
        if skill:
            skill_breakdown.append({"skill_slug": slug, "skill_name": skill.name, "score_percent": round(pct * 100, 1), "mastery_after": round(pct * 100, 1)})

    return {
        "attempt_id": attempt.id, "score": round((attempt.score or 0) * 100, 1),
        "passed": (attempt.score or 0) >= assessment.passing_score,
        "skill_breakdown": skill_breakdown, "weak_concepts": attempt.weak_concepts,
        "strengths": [], "recommended_next_steps": [],
    }


async def get_diagnostic_result(db: AsyncSession, user_id: UUID) -> dict:
    diagnostic = await get_diagnostic_assessment(db)
    result = await db.execute(
        select(AssessmentAttempt)
        .where(AssessmentAttempt.user_id == user_id, AssessmentAttempt.assessment_id == diagnostic.id, AssessmentAttempt.status == "graded")
        .order_by(AssessmentAttempt.submitted_at.desc())
    )
    attempt = result.scalars().first()
    if attempt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnostic not yet completed")

    profile = {slug: round(pct * 100, 1) for slug, pct in attempt.skill_breakdown.items()}
    weaknesses = attempt.weak_concepts
    strengths = [slug for slug, pct in attempt.skill_breakdown.items() if pct >= 0.75]

    sorted_scores = sorted(attempt.skill_breakdown.items(), key=lambda kv: kv[1])
    recommended_start = sorted_scores[0][0] if sorted_scores else "python"

    return {
        "attempt_id": attempt.id, "skill_profile": profile, "strengths": strengths,
        "weaknesses": weaknesses, "prerequisite_gaps": weaknesses,
        "recommended_starting_point": recommended_start,
        "confidence": round(min(1.0, len(attempt.answers) / 20), 2) if attempt.answers else 0.5,
    }
