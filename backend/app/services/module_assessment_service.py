"""Module assessment lifecycle: content upsert/publish, attempts, grading, results.

All correctness decisions (which answers are right, the score, pass/fail) are made here on the
server from the stored answer key; nothing the client sends about correctness or score is read.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.activity import ActivityLog
from app.models.assessment import Assessment, AssessmentAnswer, AssessmentAttempt, Question
from app.models.curriculum import Course, Module, Skill
from app.models.user import User
from app.services import module_assessment_rules as rules
from app.services import progression_service, skill_service
from app.services.code_execution import CodeExecutionUnavailable, CodeRunner

logger = logging.getLogger(__name__)

STANDARD_QUESTION_TYPES = {"mcq": "mcq", "quiz": "quiz", "coding": "coding"}


# ---- Question <-> spec ------------------------------------------------------------
def question_to_spec(q: Question) -> dict:
    return {
        "id": q.id, "type": q.question_type, "quiz_format": q.quiz_format, "prompt": q.prompt, "options": q.options or [],
        "correct_answer": q.correct_answer or {}, "explanation": q.explanation, "difficulty": q.difficulty,
        "points": q.points, "order": q.order_index, "coding_config": q.coding_config, "skill_id": q.skill_id,
    }


def _tests_with_ids(cfg: dict) -> list[dict]:
    return [
        {"id": f"t{i}", "args": t["args"], "expected": t["expected"], "visible": bool(t.get("visible"))}
        for i, t in enumerate(cfg["test_cases"], 1)
    ]


def _public_options(spec: dict) -> list[dict]:
    if spec.get("quiz_format") == "true_false":
        return [{"id": "true", "text": "True"}, {"id": "false", "text": "False"}]
    return [{"id": o["id"], "text": o["text"]} for o in spec.get("options") or []]


def question_view(spec: dict) -> dict:
    """What a student may see BEFORE submitting: never the answer key, explanation or hidden tests."""
    view = {
        "id": spec["id"], "order": spec["order"], "type": spec["type"], "quiz_format": spec.get("quiz_format"),
        "prompt": spec["prompt"], "difficulty": spec["difficulty"], "points": spec["points"],
        "options": _public_options(spec) if spec["type"] != "coding" else [], "coding": None,
    }
    if spec["type"] == "coding":
        cfg = spec["coding_config"]
        view["coding"] = {
            "language": cfg["language"], "function_name": cfg["function_name"], "starter_code": cfg["starter_code"],
            "expected_output": cfg["expected_output"],
            "sample_tests": [{"args": t["args"], "expected": t["expected"]} for t in cfg["test_cases"] if t.get("visible")],
            "hidden_test_count": sum(1 for t in cfg["test_cases"] if not t.get("visible")),
            "time_limit_seconds": cfg.get("time_limit_seconds", 2), "memory_limit_mb": cfg.get("memory_limit_mb", 128),
        }
    return view


async def _load_assessment(db: AsyncSession, assessment_id: UUID) -> Assessment:
    result = await db.execute(select(Assessment).where(Assessment.id == assessment_id).options(selectinload(Assessment.questions)))
    assessment = result.scalar_one_or_none()
    if assessment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found")
    return assessment


def assessment_summary(assessment: Assessment) -> dict:
    specs = [question_to_spec(q) for q in assessment.questions]
    counts = {t: sum(1 for s in specs if s["type"] == t) for t in ("mcq", "quiz", "coding")}
    return {
        "id": assessment.id, "module_id": assessment.module_id, "title": assessment.title, "description": assessment.description,
        "level": assessment.level, "is_published": assessment.is_published, "total_questions": len(specs),
        "mcq_count": counts["mcq"], "quiz_count": counts["quiz"], "coding_count": counts["coding"],
        "passing_score_percent": round(assessment.passing_score * 100, 1),
        "required_coding_questions": assessment.required_coding_questions,
        "time_limit_minutes": assessment.time_limit_minutes,
    }


# ---- Content: validate / upsert / publish -----------------------------------------
def validate_assessment(assessment: Assessment) -> list[str]:
    errors = []
    if assessment.assessment_type != "module_quiz" or assessment.module_id is None:
        errors.append("only module assessments (assessment_type 'module_quiz' with a module) can be published")
    specs = [question_to_spec(q) for q in assessment.questions]
    errors += rules.validate_assessment_structure(
        specs, level=assessment.level, passing_percent=assessment.passing_score * 100, required_coding=assessment.required_coding_questions
    )
    if assessment.level is None:
        errors.append("a level (beginner, intermediate or advanced) is required")
    return errors


async def publish_assessment(db: AsyncSession, assessment_id: UUID) -> Assessment:
    assessment = await _load_assessment(db, assessment_id)
    errors = validate_assessment(assessment)
    if errors:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"message": "Assessment is invalid and cannot be published", "errors": errors})
    duplicate = (await db.execute(
        select(Assessment.id).where(
            Assessment.module_id == assessment.module_id, Assessment.assessment_type == "module_quiz",
            Assessment.level == assessment.level, Assessment.is_published.is_(True), Assessment.id != assessment.id,
        )
    )).first()
    if duplicate:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Another assessment is already published for this module and level")
    assessment.is_published = True
    await db.commit()
    return assessment


async def unpublish_assessment(db: AsyncSession, assessment_id: UUID) -> Assessment:
    assessment = await _load_assessment(db, assessment_id)
    assessment.is_published = False
    await db.commit()
    return assessment


def _apply_question(question: Question, item: dict, order: int, skill_id: UUID | None) -> None:
    kind = item["type"]
    question.question_type = kind
    question.quiz_format = item.get("quiz_format") if kind == "quiz" else None
    question.prompt = item["prompt"]
    question.options = item.get("options", []) if kind != "coding" else []
    question.correct_answer = item.get("correct_answer", {}) if kind != "coding" else {}
    question.explanation = item.get("explanation")
    question.difficulty = item["difficulty"]
    question.points = float(item.get("points", 1))
    question.order_index = order
    question.skill_id = skill_id
    question.coding_config = item.get("coding_config") if kind == "coding" else None


async def upsert_module_assessment(db: AsyncSession, data: dict, *, module_id: UUID, publish: bool = False) -> Assessment:
    """Create or update the assessment for (module, level) from a content dict, validating it first.

    Existing questions are updated IN PLACE (matched by order) when the shape is unchanged, so question
    ids - and therefore students' stored attempt answers - survive a content update.
    """
    passing = float(data.get("passing_score", rules.DEFAULT_PASSING_PERCENT))
    required = int(data.get("required_coding_questions", rules.DEFAULT_REQUIRED_CODING))
    items = data["questions"]
    specs = [{**item, "order": i} for i, item in enumerate(items, 1)]
    errors = rules.validate_assessment_structure(specs, level=data.get("level"), passing_percent=passing, required_coding=required)
    if errors:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"message": "Invalid module assessment", "errors": errors})

    assessment = (await db.execute(
        select(Assessment).where(
            Assessment.module_id == module_id, Assessment.assessment_type == "module_quiz", Assessment.level == data["level"]
        ).options(selectinload(Assessment.questions))
    )).scalar_one_or_none()
    is_new = assessment is None
    if is_new:
        assessment = Assessment(assessment_type="module_quiz", module_id=module_id, level=data["level"])
        db.add(assessment)
    assessment.title = data["title"]
    assessment.description = data.get("description")
    assessment.passing_score = passing / 100.0
    assessment.required_coding_questions = required
    assessment.time_limit_minutes = data.get("time_limit_minutes")
    await db.flush()

    slugs = {i.get("skill_slug") for i in items if i.get("skill_slug")}
    skills = {s.slug: s.id for s in (await db.execute(select(Skill).where(Skill.slug.in_(slugs)))).scalars().all()} if slugs else {}

    existing = [] if is_new else sorted(assessment.questions, key=lambda q: q.order_index)  # new: relationship not loaded
    same_shape = len(existing) == len(items) and all(q.question_type == it["type"] for q, it in zip(existing, items))
    if same_shape:
        for i, (question, item) in enumerate(zip(existing, items), 1):
            _apply_question(question, item, i, skills.get(item.get("skill_slug")))
    else:
        for question in existing:
            await db.delete(question)
        await db.flush()
        for i, item in enumerate(items, 1):
            question = Question(assessment_id=assessment.id)
            _apply_question(question, item, i, skills.get(item.get("skill_slug")))
            db.add(question)
    await db.flush()
    await db.commit()
    if publish:
        return await publish_assessment(db, assessment.id)
    return assessment


# ---- Student-facing views --------------------------------------------------------------
async def list_module_assessments(db: AsyncSession, module_id: UUID) -> list[Assessment]:
    result = await db.execute(
        select(Assessment).where(
            Assessment.module_id == module_id, Assessment.assessment_type == "module_quiz", Assessment.is_published.is_(True)
        ).options(selectinload(Assessment.questions))
    )
    return sorted(result.scalars().all(), key=lambda a: rules.LEVEL_RANK.get(a.level or "beginner", 0))


async def get_assessment_view(db: AsyncSession, user: User, assessment_id: UUID) -> dict:
    await progression_service.assert_assessment_available(db, user, assessment_id)
    assessment = await _load_assessment(db, assessment_id)
    return {**assessment_summary(assessment), "questions": [question_view(question_to_spec(q)) for q in assessment.questions]}


def _attempt_out(attempt: AssessmentAttempt) -> dict:
    return {
        "id": attempt.id, "assessment_id": attempt.assessment_id, "attempt_number": attempt.attempt_number, "status": attempt.status,
        "percentage": attempt.percentage, "passed": attempt.passed, "started_at": attempt.started_at, "submitted_at": attempt.submitted_at,
    }


async def start_attempt(db: AsyncSession, user: User, assessment_id: UUID) -> dict:
    """Start a new attempt, or resume the open one (so a refresh never loses or duplicates an attempt)."""
    assessment, state = await progression_service.assert_assessment_available(db, user, assessment_id)
    level_row = next((r for r in (state["assessment"] or {}).get("levels", []) if r["assessment_id"] == assessment_id), None)
    if level_row and level_row["passed"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You have already passed this assessment.")

    attempt = (await db.execute(
        select(AssessmentAttempt).where(
            AssessmentAttempt.user_id == user.id, AssessmentAttempt.assessment_id == assessment_id, AssessmentAttempt.status == "in_progress"
        ).order_by(AssessmentAttempt.started_at.desc())
    )).scalars().first()
    if attempt is None:
        # Serialise concurrent starts for this student+assessment so attempt numbers stay unique.
        await db.execute(select(Assessment.id).where(Assessment.id == assessment_id).with_for_update())
        last_number = (await db.execute(
            select(func.max(AssessmentAttempt.attempt_number)).where(
                AssessmentAttempt.user_id == user.id, AssessmentAttempt.assessment_id == assessment_id
            )
        )).scalar() or 0
        attempt = AssessmentAttempt(
            user_id=user.id, assessment_id=assessment_id, status="in_progress", answers={}, attempt_number=last_number + 1,
            started_at=datetime.now(timezone.utc),
        )
        db.add(attempt)
        await db.commit()
        await db.refresh(attempt)

    full = await get_assessment_view(db, user, assessment_id)
    return {"attempt": _attempt_out(attempt), "assessment": full, "saved_answers": attempt.answers or {}}


async def _get_owned_attempt(db: AsyncSession, user: User, attempt_id: UUID, *, lock: bool = False) -> AssessmentAttempt:
    query = select(AssessmentAttempt).where(AssessmentAttempt.id == attempt_id)
    if lock:
        query = query.with_for_update()
    attempt = (await db.execute(query)).scalar_one_or_none()
    if attempt is None or attempt.attempt_number is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    if attempt.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this attempt.")
    return attempt


def _check_answer_payload(answers: dict, valid_ids: set[str]) -> None:
    if not isinstance(answers, dict):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="answers must be an object keyed by question id")
    if len(json.dumps(answers, default=str)) > 200_000:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Answers are too large")
    unknown = [k for k in answers if k not in valid_ids]
    if unknown:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Unknown question ids: {unknown}")


async def save_draft(db: AsyncSession, user: User, attempt_id: UUID, answers: dict) -> dict:
    attempt = await _get_owned_attempt(db, user, attempt_id, lock=True)
    if attempt.status != "in_progress":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This attempt has already been submitted.")
    assessment = await _load_assessment(db, attempt.assessment_id)
    _check_answer_payload(answers, {str(q.id) for q in assessment.questions})
    attempt.answers = answers
    await db.commit()
    return {"saved": True}


async def run_sample_tests(db: AsyncSession, user: User, attempt_id: UUID, question_id: UUID, code: str, runner: CodeRunner) -> dict:
    """The "Run" button: execute the student's code against the visible sample tests only."""
    attempt = await _get_owned_attempt(db, user, attempt_id)
    if attempt.status != "in_progress":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This attempt has already been submitted.")
    assessment = await _load_assessment(db, attempt.assessment_id)
    question = next((q for q in assessment.questions if q.id == question_id and q.question_type == "coding"), None)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coding question not found")
    try:
        source = rules.validate_code_answer({"code": code})
    except rules.AnswerValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    if source is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Write some code before running it.")
    cfg = question.coding_config
    tests = [t for t in _tests_with_ids(cfg) if t["visible"]]
    try:
        results = await runner.run(
            language=cfg["language"], code=source, function_name=cfg["function_name"], tests=tests,
            time_limit=float(cfg.get("time_limit_seconds", 2)), memory_mb=int(cfg.get("memory_limit_mb", 128)),
        )
    except CodeExecutionUnavailable as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    return {"results": results, "passed_count": sum(1 for r in results if r.get("passed")), "total_count": len(results)}


def _coding_outcome(results: list[dict]) -> dict:
    passed = bool(results) and all(r.get("passed") for r in results)
    return {
        "passed": passed, "passed_count": sum(1 for r in results if r.get("passed")), "total_count": len(results),
        "tests": [
            {k: r[k] for k in ("id", "visible", "status", "passed", "args", "expected", "actual", "error", "stdout", "duration_ms") if k in r}
            for r in results
        ],
    }


async def submit_attempt(db: AsyncSession, user: User, attempt_id: UUID, answers: dict | None, runner: CodeRunner) -> dict:
    attempt = await _get_owned_attempt(db, user, attempt_id, lock=True)
    if attempt.status != "in_progress":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This attempt has already been submitted.")
    assessment = await _load_assessment(db, attempt.assessment_id)
    await progression_service.assert_assessment_available(db, user, assessment.id)

    specs = [question_to_spec(q) for q in sorted(assessment.questions, key=lambda q: q.order_index)]
    by_id = {str(s["id"]): s for s in specs}
    submitted = answers if answers is not None else (attempt.answers or {})
    _check_answer_payload(submitted, set(by_id))

    # 1) validate every answer's shape before doing any work (malformed -> 422, attempt stays open)
    codes: dict[str, str | None] = {}
    objective: dict[str, bool] = {}
    try:
        for qid, spec in by_id.items():
            answer = submitted.get(qid)
            if spec["type"] == "coding":
                codes[qid] = rules.validate_code_answer(answer)
            else:
                objective[qid] = rules.grade_objective_question(spec, answer)
    except rules.AnswerValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))

    # 2) run coding answers in the sandbox (never in this process)
    coding: dict[str, dict] = {}
    for qid, code in codes.items():
        cfg = by_id[qid]["coding_config"]
        if code is None:
            coding[qid] = _coding_outcome([])
            continue
        try:
            results = await runner.run(
                language=cfg["language"], code=code, function_name=cfg["function_name"], tests=_tests_with_ids(cfg),
                time_limit=float(cfg.get("time_limit_seconds", 2)), memory_mb=int(cfg.get("memory_limit_mb", 128)),
            )
        except CodeExecutionUnavailable as exc:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Your submission could not be graded because code execution is unavailable ({exc}) Your answers are saved - please try again.",
            )
        coding[qid] = _coding_outcome(results)

    # 3) score (server-side, from the stored answer key only)
    outcomes = []
    for qid, spec in by_id.items():
        correct = coding[qid]["passed"] if spec["type"] == "coding" else objective[qid]
        outcomes.append({"qid": qid, "type": spec["type"], "points": float(spec["points"]), "correct": correct, "spec": spec})
    result = rules.compute_result(
        outcomes, passing_percent=assessment.passing_score * 100, required_coding=assessment.required_coding_questions
    )

    # 4) performance data for later AI use: weak concepts, incorrect questions by type
    skill_ids = {o["spec"]["skill_id"] for o in outcomes if o["spec"]["skill_id"]}
    skills = {s.id: s for s in (await db.execute(select(Skill).where(Skill.id.in_(skill_ids)))).scalars().all()} if skill_ids else {}
    per_skill: dict[UUID, list[bool]] = {}
    for o in outcomes:
        if o["spec"]["skill_id"]:
            per_skill.setdefault(o["spec"]["skill_id"], []).append(o["correct"])
    weak_concepts = sorted({skills[sid].name for sid, marks in per_skill.items() if sid in skills and sum(marks) / len(marks) < 0.5})
    incorrect = {t: [o["qid"] for o in outcomes if o["type"] == t and not o["correct"]] for t in ("mcq", "quiz", "coding")}
    attempts_so_far = attempt.attempt_number or 1

    # 5) persist the attempt (never overwriting earlier ones) and one answer row per question
    now = datetime.now(timezone.utc)
    by_type = result["by_type"]
    attempt.answers = submitted
    attempt.status = "graded"
    attempt.submitted_at = now
    attempt.score = result["percentage"] / 100.0
    attempt.percentage = result["percentage"]
    attempt.passed = result["passed"]
    attempt.mcq_score = by_type["mcq"]["points_earned"]
    attempt.quiz_score = by_type["quiz"]["points_earned"]
    attempt.coding_score = by_type["coding"]["points_earned"]
    attempt.coding_results = {qid: c for qid, c in coding.items()}
    attempt.skill_breakdown = {skills[sid].slug: sum(m) / len(m) for sid, m in per_skill.items() if sid in skills}
    attempt.weak_concepts = weak_concepts
    attempt.result_detail = {
        "summary": {k: v for k, v in result.items()}, "incorrect_question_ids": incorrect, "weak_concepts": weak_concepts,
        "difficulty": assessment.level, "attempt_count": attempts_so_far, "score_percentage": result["percentage"],
    }
    for o in outcomes:
        db.add(AssessmentAnswer(
            attempt_id=attempt.id, question_id=UUID(o["qid"]), answer=submitted.get(o["qid"]), is_correct=o["correct"],
            points_awarded=o["points"] if o["correct"] else 0.0, coding_result=coding.get(o["qid"]),
        ))
    module_title = (await db.execute(select(Module.title).where(Module.id == assessment.module_id))).scalar_one_or_none()
    db.add(ActivityLog(
        user_id=user.id, action="module_assessment_passed" if result["passed"] else "module_assessment_failed",
        entity_type="assessment", entity_id=assessment.id,
        metadata_json={"title": f"{module_title or assessment.title} assessment", "score_percent": result["percentage"], "attempt": attempts_so_far},
    ))
    await db.commit()

    # 6) feed the skill model (best-effort; grading is already saved). Recommendations refresh in the background.
    for sid, marks in per_skill.items():
        try:
            await skill_service.apply_evidence(db, user.id, sid, sum(marks) / len(marks), source="assessment")
        except Exception:
            await db.rollback()
            logger.exception("Could not update skill evidence for user %s", user.id)

    return await get_attempt_result(db, user, attempt.id)


# ---- Results -------------------------------------------------------------------------------
async def get_attempt_result(db: AsyncSession, user: User, attempt_id: UUID) -> dict:
    attempt = await _get_owned_attempt(db, user, attempt_id)
    assessment = await _load_assessment(db, attempt.assessment_id)
    if attempt.status != "graded":
        return {"attempt": _attempt_out(attempt), "assessment": assessment_summary(assessment), "result": None, "questions": [], "module": None}

    rows = {r.question_id: r for r in (await db.execute(select(AssessmentAnswer).where(AssessmentAnswer.attempt_id == attempt.id))).scalars().all()}
    summary = (attempt.result_detail or {}).get("summary") or {}
    passed = bool(attempt.passed)
    questions = []
    for q in sorted(assessment.questions, key=lambda x: x.order_index):
        spec = question_to_spec(q)
        row = rows.get(q.id)
        item = {
            "id": q.id, "order": q.order_index, "type": q.question_type, "quiz_format": q.quiz_format, "prompt": q.prompt,
            "points": q.points, "points_awarded": row.points_awarded if row else 0.0, "is_correct": bool(row and row.is_correct),
            "your_answer": row.answer if row else None, "options": _public_options(spec) if q.question_type != "coding" else [],
            "coding": None, "explanation": None, "correct_answer": None,
        }
        if q.question_type == "coding" and row and row.coding_result:
            cr = row.coding_result
            item["coding"] = {
                "passed_count": cr.get("passed_count", 0), "total_count": cr.get("total_count", 0),
                # hidden tests report pass/fail only; visible ones include args/expected/actual
                "tests": cr.get("tests", []),
            }
        if passed:  # answer key and teaching notes are revealed only after a pass, so retries can't be memorised
            item["explanation"] = q.explanation
            item["correct_answer"] = q.correct_answer if q.question_type != "coding" else None
            if q.question_type == "coding":
                item["reference_solution"] = (q.coding_config or {}).get("solution")
        questions.append(item)

    module_state = await progression_service.get_module_state(db, user, assessment.module_id) if assessment.module_id else None
    next_module = None
    if passed and module_state:
        states = await progression_service.get_course_states(db, user, module_state["course_id"])
        idx = next((i for i, s in enumerate(states) if s["module_id"] == module_state["module_id"]), None)
        if idx is not None and idx + 1 < len(states):
            nxt = states[idx + 1]
            next_module = {"module_id": nxt["module_id"], "title": nxt["title"], "status": nxt["status"]}

    return {
        "attempt": _attempt_out(attempt),
        "assessment": assessment_summary(assessment),
        "result": {
            "points_earned": summary.get("points_earned"), "points_total": summary.get("points_total"),
            "percentage": attempt.percentage, "passed": passed,
            "questions_correct": summary.get("questions_correct"), "questions_total": summary.get("questions_total"),
            "mcq": {"correct": attempt.result_detail["summary"]["by_type"]["mcq"]["correct"], "total": summary["by_type"]["mcq"]["total"]},
            "quiz": {"correct": summary["by_type"]["quiz"]["correct"], "total": summary["by_type"]["quiz"]["total"]},
            "coding": {"correct": summary["by_type"]["coding"]["correct"], "total": summary["by_type"]["coding"]["total"]},
            "passing_percent": summary.get("passing_percent"), "required_coding": summary.get("required_coding"),
            "score_requirement_met": summary.get("score_requirement_met"), "coding_requirement_met": summary.get("coding_requirement_met"),
            "weak_concepts": attempt.weak_concepts or [],
        },
        "questions": questions,
        "module": module_state,
        "next_module": next_module,
    }


async def list_attempts(db: AsyncSession, user: User, assessment_id: UUID) -> list[dict]:
    await progression_service.get_assessment_and_state(db, user, assessment_id)
    rows = (await db.execute(
        select(AssessmentAttempt).where(
            AssessmentAttempt.user_id == user.id, AssessmentAttempt.assessment_id == assessment_id, AssessmentAttempt.attempt_number.is_not(None)
        ).order_by(AssessmentAttempt.attempt_number)
    )).scalars().all()
    return [_attempt_out(a) for a in rows]
