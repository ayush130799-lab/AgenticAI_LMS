import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_admin
from app.db.session import get_db
from app.models.curriculum import Course, Lesson, LessonSkill, Module, Skill, SkillPrerequisite
from app.models.assessment import Assessment, Question
from app.models.project import Project, ProjectSkill
from app.models.user import User
from app.services import audit_service, module_assessment_service
from app.schemas.admin import (
    AdminUserOut,
    AssessmentAdminIn,
    CourseAdminIn,
    LessonAdminIn,
    ModuleAssessmentAdminIn,
    ModuleAdminIn,
    ProjectAdminIn,
    SkillAdminIn,
)

logger = logging.getLogger("agentic_ai_lms")

_MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


async def admin_request_guard(request: Request, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    """Router-wide: admin-only access, an audit row per state-changing request, and DB integrity errors as 409.

    Without the 409 mapping, deleting a record that other rows still reference (or reusing a slug) surfaced as a
    generic 500 "Internal server error" with no hint about what to fix.
    """
    status_code = 200
    admin_id, admin_email = admin.id, admin.email  # read now: a rollback below expires the ORM object
    try:
        yield admin
    except IntegrityError as exc:
        await db.rollback()
        status_code = status.HTTP_409_CONFLICT
        logger.info("Admin %s %s hit an integrity conflict: %s", request.method, request.url.path, exc.orig)
        if request.method == "DELETE":
            detail = "This record is still referenced by other data (for example questions, lessons or student progress) and cannot be deleted."
        else:
            detail = "This change conflicts with existing data (for example a duplicate slug) or references a record that does not exist."
        raise HTTPException(status_code=status_code, detail=detail) from exc
    except HTTPException as exc:
        status_code = exc.status_code
        raise
    except Exception:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise
    finally:
        if request.method in _MUTATING_METHODS:
            await audit_service.record_admin_action(db, admin_id, admin_email, request, status_code)


router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(admin_request_guard)])


async def _get_or_404(db: AsyncSession, model, id_: UUID):
    result = await db.execute(select(model).where(model.id == id_))
    obj = result.scalar_one_or_none()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{model.__name__} not found")
    return obj


def _refuse_if_published_module_assessment(assessment: Assessment) -> None:
    if assessment.assessment_type == "module_quiz" and assessment.is_published:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This module assessment is published. Unpublish it first; edits go through /admin/module-assessments so the 3 MCQ + 2 quiz + 2 coding structure is re-validated.",
        )


# --- Courses ---

@router.post("/courses")
async def create_course(payload: CourseAdminIn, db: AsyncSession = Depends(get_db)):
    course = Course(**payload.model_dump())
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return {"id": course.id}


@router.put("/courses/{course_id}")
async def update_course(course_id: UUID, payload: CourseAdminIn, db: AsyncSession = Depends(get_db)):
    course = await _get_or_404(db, Course, course_id)
    for field, value in payload.model_dump().items():
        setattr(course, field, value)
    await db.commit()
    return {"id": course.id}


@router.delete("/courses/{course_id}")
async def delete_course(course_id: UUID, db: AsyncSession = Depends(get_db)):
    course = await _get_or_404(db, Course, course_id)
    await db.delete(course)
    await db.commit()
    return {"ok": True}


# --- Modules ---

@router.post("/modules")
async def create_module(payload: ModuleAdminIn, db: AsyncSession = Depends(get_db)):
    module = Module(**payload.model_dump())
    db.add(module)
    await db.commit()
    await db.refresh(module)
    return {"id": module.id}


@router.put("/modules/{module_id}")
async def update_module(module_id: UUID, payload: ModuleAdminIn, db: AsyncSession = Depends(get_db)):
    module = await _get_or_404(db, Module, module_id)
    for field, value in payload.model_dump().items():
        setattr(module, field, value)
    await db.commit()
    return {"id": module.id}


@router.delete("/modules/{module_id}")
async def delete_module(module_id: UUID, db: AsyncSession = Depends(get_db)):
    module = await _get_or_404(db, Module, module_id)
    await db.delete(module)
    await db.commit()
    return {"ok": True}


# --- Lessons ---

async def _resolve_skill_ids(db: AsyncSession, slugs: list[str]) -> list[UUID]:
    if not slugs:
        return []
    result = await db.execute(select(Skill).where(Skill.slug.in_(slugs)))
    return [s.id for s in result.scalars().all()]


@router.post("/lessons")
async def create_lesson(payload: LessonAdminIn, db: AsyncSession = Depends(get_db)):
    data = payload.model_dump()
    skill_slugs = data.pop("skill_slugs")
    lesson = Lesson(**data)
    db.add(lesson)
    await db.flush()

    for skill_id in await _resolve_skill_ids(db, skill_slugs):
        db.add(LessonSkill(lesson_id=lesson.id, skill_id=skill_id, weight=1.0))

    await db.commit()
    await db.refresh(lesson)
    return {"id": lesson.id}


@router.put("/lessons/{lesson_id}")
async def update_lesson(lesson_id: UUID, payload: LessonAdminIn, db: AsyncSession = Depends(get_db)):
    lesson = await _get_or_404(db, Lesson, lesson_id)
    data = payload.model_dump()
    skill_slugs = data.pop("skill_slugs")
    for field, value in data.items():
        setattr(lesson, field, value)

    existing = await db.execute(select(LessonSkill).where(LessonSkill.lesson_id == lesson_id))
    for ls in existing.scalars().all():
        await db.delete(ls)
    for skill_id in await _resolve_skill_ids(db, skill_slugs):
        db.add(LessonSkill(lesson_id=lesson.id, skill_id=skill_id, weight=1.0))

    await db.commit()
    return {"id": lesson.id}


@router.delete("/lessons/{lesson_id}")
async def delete_lesson(lesson_id: UUID, db: AsyncSession = Depends(get_db)):
    lesson = await _get_or_404(db, Lesson, lesson_id)
    await db.delete(lesson)
    await db.commit()
    return {"ok": True}


# --- Skills ---

@router.post("/skills")
async def create_skill(payload: SkillAdminIn, db: AsyncSession = Depends(get_db)):
    data = payload.model_dump()
    parent_slug = data.pop("parent_slug")
    parent_id = None
    if parent_slug:
        result = await db.execute(select(Skill).where(Skill.slug == parent_slug))
        parent = result.scalar_one_or_none()
        parent_id = parent.id if parent else None
    skill = Skill(**data, parent_skill_id=parent_id)
    db.add(skill)
    await db.commit()
    await db.refresh(skill)
    return {"id": skill.id}


@router.put("/skills/{skill_id}")
async def update_skill(skill_id: UUID, payload: SkillAdminIn, db: AsyncSession = Depends(get_db)):
    skill = await _get_or_404(db, Skill, skill_id)
    data = payload.model_dump()
    parent_slug = data.pop("parent_slug")
    parent_id = None
    if parent_slug:
        result = await db.execute(select(Skill).where(Skill.slug == parent_slug))
        parent = result.scalar_one_or_none()
        parent_id = parent.id if parent else None
    for field, value in data.items():
        setattr(skill, field, value)
    skill.parent_skill_id = parent_id
    await db.commit()
    return {"id": skill.id}


@router.delete("/skills/{skill_id}")
async def delete_skill(skill_id: UUID, db: AsyncSession = Depends(get_db)):
    skill = await _get_or_404(db, Skill, skill_id)
    await db.delete(skill)
    await db.commit()
    return {"ok": True}


# --- Assessments ---

@router.post("/assessments")
async def create_assessment(payload: AssessmentAdminIn, db: AsyncSession = Depends(get_db)):
    data = payload.model_dump()
    questions_data = data.pop("questions")
    assessment = Assessment(**data)
    db.add(assessment)
    await db.flush()

    for order_index, q in enumerate(questions_data):
        skill_slug = q.pop("skill_slug", None)
        skill_id = None
        if skill_slug:
            result = await db.execute(select(Skill).where(Skill.slug == skill_slug))
            skill = result.scalar_one_or_none()
            skill_id = skill.id if skill else None
        db.add(Question(assessment_id=assessment.id, skill_id=skill_id, order_index=order_index, **q))

    await db.commit()
    await db.refresh(assessment)
    return {"id": assessment.id}


@router.put("/assessments/{assessment_id}")
async def update_assessment(assessment_id: UUID, payload: AssessmentAdminIn, db: AsyncSession = Depends(get_db)):
    assessment = await _get_or_404(db, Assessment, assessment_id)
    _refuse_if_published_module_assessment(assessment)
    data = payload.model_dump()
    questions_data = data.pop("questions")
    for field, value in data.items():
        setattr(assessment, field, value)
    await db.flush()

    existing = await db.execute(select(Question).where(Question.assessment_id == assessment.id))
    for q in existing.scalars().all():
        await db.delete(q)
    await db.flush()

    for order_index, q in enumerate(questions_data):
        skill_slug = q.pop("skill_slug", None)
        skill_id = None
        if skill_slug:
            result = await db.execute(select(Skill).where(Skill.slug == skill_slug))
            skill = result.scalar_one_or_none()
            skill_id = skill.id if skill else None
        db.add(Question(assessment_id=assessment.id, skill_id=skill_id, order_index=order_index, **q))

    await db.commit()
    return {"id": assessment.id}


@router.delete("/assessments/{assessment_id}")
async def delete_assessment(assessment_id: UUID, db: AsyncSession = Depends(get_db)):
    assessment = await _get_or_404(db, Assessment, assessment_id)
    _refuse_if_published_module_assessment(assessment)
    await db.delete(assessment)
    await db.commit()
    return {"ok": True}


# --- Projects ---

@router.post("/projects")
async def create_project(payload: ProjectAdminIn, db: AsyncSession = Depends(get_db)):
    data = payload.model_dump()
    skill_slugs = data.pop("skill_slugs")
    project = Project(**data)
    db.add(project)
    await db.flush()

    for skill_id in await _resolve_skill_ids(db, skill_slugs):
        db.add(ProjectSkill(project_id=project.id, skill_id=skill_id, weight=1.0))

    await db.commit()
    await db.refresh(project)
    return {"id": project.id}


@router.put("/projects/{project_id}")
async def update_project(project_id: UUID, payload: ProjectAdminIn, db: AsyncSession = Depends(get_db)):
    project = await _get_or_404(db, Project, project_id)
    data = payload.model_dump()
    skill_slugs = data.pop("skill_slugs")
    for field, value in data.items():
        setattr(project, field, value)
    await db.flush()

    existing = await db.execute(select(ProjectSkill).where(ProjectSkill.project_id == project_id))
    for ps in existing.scalars().all():
        await db.delete(ps)
    await db.flush()

    for skill_id in await _resolve_skill_ids(db, skill_slugs):
        db.add(ProjectSkill(project_id=project.id, skill_id=skill_id, weight=1.0))

    await db.commit()
    return {"id": project.id}


@router.delete("/projects/{project_id}")
async def delete_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    project = await _get_or_404(db, Project, project_id)
    await db.delete(project)
    await db.commit()
    return {"ok": True}


# --- Users ---

@router.get("/users", response_model=list[AdminUserOut])
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


# --- Module assessments (standard structure enforced) ---

@router.post("/module-assessments")
async def upsert_module_assessment(payload: ModuleAssessmentAdminIn, db: AsyncSession = Depends(get_db)):
    await _get_or_404(db, Module, payload.module_id)
    data = payload.model_dump(exclude={"module_id", "publish"})
    existing = (await db.execute(
        select(Assessment).where(
            Assessment.module_id == payload.module_id, Assessment.assessment_type == "module_quiz", Assessment.level == payload.level
        )
    )).scalar_one_or_none()
    if existing is not None:
        _refuse_if_published_module_assessment(existing)
    assessment = await module_assessment_service.upsert_module_assessment(db, data, module_id=payload.module_id, publish=payload.publish)
    return {"id": assessment.id, "is_published": assessment.is_published}


@router.get("/module-assessments/{assessment_id}/validate")
async def validate_module_assessment(assessment_id: UUID, db: AsyncSession = Depends(get_db)):
    assessment = await module_assessment_service._load_assessment(db, assessment_id)
    errors = module_assessment_service.validate_assessment(assessment)
    return {"valid": not errors, "errors": errors}


@router.post("/module-assessments/{assessment_id}/publish")
async def publish_module_assessment(assessment_id: UUID, db: AsyncSession = Depends(get_db)):
    assessment = await module_assessment_service.publish_assessment(db, assessment_id)
    return {"id": assessment.id, "is_published": True}


@router.post("/module-assessments/{assessment_id}/unpublish")
async def unpublish_module_assessment(assessment_id: UUID, db: AsyncSession = Depends(get_db)):
    assessment = await module_assessment_service.unpublish_assessment(db, assessment_id)
    return {"id": assessment.id, "is_published": False}
