"""
Idempotent database seeder. Run with:

    python -m app.db.seed_runner

Loads the canonical skill graph, every course under content/seed/courses/,
the diagnostic assessment, and the capstone projects, then ingests lesson
content into the RAG vector store. Safe to re-run: existing rows are matched
by natural key (slug) and updated in place rather than duplicated.
"""
import asyncio
import importlib.util
import logging
import sys
from pathlib import Path
from types import ModuleType

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed_runner")

# backend/app/db/seed_runner.py -> repo root is 3 parents up (also true inside
# the Docker image, where backend/ is flattened onto /app and ai_engine/ +
# content/ are copied to / — see backend/Dockerfile).
REPO_ROOT = Path(__file__).resolve().parents[3]
CONTENT_SEED_DIR = REPO_ROOT / "content" / "seed"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.core.security import hash_password  # noqa: E402
from app.db.session import AsyncSessionLocal, engine  # noqa: E402
from app.models import Base  # noqa: E402
from app.models.assessment import Assessment, Question  # noqa: E402
from app.models.curriculum import Course, Lesson, LessonSkill, Module, Skill, SkillPrerequisite  # noqa: E402
from app.models.project import Project, ProjectSkill  # noqa: E402
from app.models.rag import DocumentChunk  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services import module_assessment_service  # noqa: E402

from ai_engine.rag.embedder import embed_text  # noqa: E402
from ai_engine.rag.ingest import build_lesson_chunks  # noqa: E402


def _load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


async def _seed_skills(db: AsyncSession) -> dict[str, Skill]:
    module = _load_module(CONTENT_SEED_DIR / "skills.py", "seed_skills")
    skills_data = module.SKILLS

    by_slug: dict[str, Skill] = {}
    for entry in skills_data:
        result = await db.execute(select(Skill).where(Skill.slug == entry["slug"]))
        skill = result.scalar_one_or_none()
        if skill is None:
            skill = Skill(slug=entry["slug"])
            db.add(skill)
        skill.name = entry["name"]
        skill.description = entry["description"]
        skill.category = entry["category"]
        by_slug[entry["slug"]] = skill
    await db.flush()

    for entry in skills_data:
        skill = by_slug[entry["slug"]]
        skill.parent_skill_id = by_slug[entry["parent"]].id if entry.get("parent") else None
    await db.flush()

    existing_prereqs = await db.execute(select(SkillPrerequisite))
    for p in existing_prereqs.scalars().all():
        await db.delete(p)
    await db.flush()

    for entry in skills_data:
        skill = by_slug[entry["slug"]]
        for prereq_slug, required_mastery in entry.get("prerequisites", []):
            db.add(SkillPrerequisite(skill_id=skill.id, prerequisite_skill_id=by_slug[prereq_slug].id, required_mastery=required_mastery))

    await db.commit()
    logger.info("Seeded %d skills", len(skills_data))
    return by_slug


async def _upsert_lesson_skills(db: AsyncSession, lesson: Lesson, skills_data: list[dict], skills_by_slug: dict[str, Skill]) -> None:
    existing = await db.execute(select(LessonSkill).where(LessonSkill.lesson_id == lesson.id))
    for ls in existing.scalars().all():
        await db.delete(ls)
    await db.flush()
    for s in skills_data:
        skill = skills_by_slug.get(s["slug"])
        if skill is None:
            logger.warning("Unknown skill slug %r referenced by lesson %r", s["slug"], lesson.slug)
            continue
        db.add(LessonSkill(lesson_id=lesson.id, skill_id=skill.id, weight=s.get("weight", 1.0)))


async def _upsert_course_exam(db: AsyncSession, course: Course, exam_data: dict, skills_by_slug: dict[str, Skill]) -> None:
    result = await db.execute(select(Assessment).where(Assessment.course_id == course.id, Assessment.assessment_type == "course_exam"))
    assessment = result.scalar_one_or_none()
    if assessment is None:
        assessment = Assessment(course_id=course.id, assessment_type="course_exam")
        db.add(assessment)
    assessment.title = exam_data["title"]
    assessment.description = exam_data.get("description")
    assessment.passing_score = exam_data.get("passing_score", 0.7)
    assessment.time_limit_minutes = exam_data.get("time_limit_minutes")
    await db.flush()

    existing_questions = await db.execute(select(Question).where(Question.assessment_id == assessment.id))
    for q in existing_questions.scalars().all():
        await db.delete(q)
    await db.flush()

    for idx, q in enumerate(exam_data["questions"]):
        skill = skills_by_slug.get(q.get("skill_slug")) if q.get("skill_slug") else None
        db.add(Question(
            assessment_id=assessment.id, skill_id=skill.id if skill else None,
            question_type=q["question_type"], prompt=q["prompt"], options=q.get("options", []),
            correct_answer=q.get("correct_answer", {}), explanation=q.get("explanation"),
            difficulty=q.get("difficulty", "medium"), points=q.get("points", 1.0), order_index=idx,
        ))


async def _seed_courses(db: AsyncSession, skills_by_slug: dict[str, Skill]) -> list[dict]:
    courses_dir = CONTENT_SEED_DIR / "courses"
    lessons_for_rag: list[dict] = []

    for i, path in enumerate(sorted(courses_dir.glob("course_*.py"))):
        module = _load_module(path, f"seed_course_{i}")
        course_data = module.COURSE

        result = await db.execute(select(Course).where(Course.slug == course_data["slug"]))
        course = result.scalar_one_or_none()
        if course is None:
            course = Course(slug=course_data["slug"])
            db.add(course)
        course.title = course_data["title"]
        course.subtitle = course_data.get("subtitle")
        course.description = course_data["description"]
        course.learning_outcomes = course_data.get("learning_outcomes", [])
        course.order_index = course_data.get("order_index", 0)
        course.estimated_hours = course_data.get("estimated_hours", 0)
        course.level = course_data.get("level", "beginner")
        course.icon = course_data.get("icon")
        course.is_published = True
        await db.flush()

        for module_data in course_data["modules"]:
            mod_result = await db.execute(select(Module).where(Module.course_id == course.id, Module.slug == module_data["slug"]))
            db_module = mod_result.scalar_one_or_none()
            if db_module is None:
                db_module = Module(course_id=course.id, slug=module_data["slug"])
                db.add(db_module)
            db_module.title = module_data["title"]
            db_module.description = module_data["description"]
            db_module.order_index = module_data.get("order_index", 0)
            db_module.estimated_hours = module_data.get("estimated_hours", 0)
            await db.flush()

            for lesson_data in module_data["lessons"]:
                lesson_result = await db.execute(select(Lesson).where(Lesson.module_id == db_module.id, Lesson.slug == lesson_data["slug"]))
                lesson = lesson_result.scalar_one_or_none()
                if lesson is None:
                    lesson = Lesson(module_id=db_module.id, slug=lesson_data["slug"])
                    db.add(lesson)
                lesson.title = lesson_data["title"]
                lesson.description = lesson_data["description"]
                lesson.lesson_type = lesson_data.get("lesson_type", "reading")
                lesson.order_index = lesson_data.get("order_index", 0)
                lesson.estimated_minutes = lesson_data.get("estimated_minutes", 20)
                lesson.learning_objectives = lesson_data.get("learning_objectives", [])
                lesson.content_markdown = lesson_data["content_markdown"]
                lesson.examples = lesson_data.get("examples", [])
                lesson.practice_exercises = lesson_data.get("practice_exercises", [])
                lesson.resources = lesson_data.get("resources", [])
                await db.flush()

                await _upsert_lesson_skills(db, lesson, lesson_data.get("skills", []), skills_by_slug)
                lessons_for_rag.append({
                    "id": str(lesson.id), "title": lesson.title,
                    "content_markdown": lesson.content_markdown, "examples": lesson.examples,
                })

        if hasattr(module, "COURSE_EXAM"):
            await _upsert_course_exam(db, course, module.COURSE_EXAM, skills_by_slug)

        await db.commit()
        logger.info("Seeded course %s", course.slug)

    return lessons_for_rag


async def _seed_module_assessments(db: AsyncSession) -> None:
    """Upsert + publish the standard module assessments (3 MCQ + 2 quiz + 2 coding). Invalid content is skipped loudly."""
    directory = CONTENT_SEED_DIR / "module_assessments"
    if not directory.exists():
        return
    seeded = 0
    for i, path in enumerate(sorted(directory.glob("*.py"))):
        for data in _load_module(path, f"seed_module_assessments_{i}").MODULE_ASSESSMENTS:
            module_id = (await db.execute(
                select(Module.id).join(Course, Course.id == Module.course_id).where(
                    Course.slug == data["course_slug"], Module.slug == data["module_slug"]
                )
            )).scalar_one_or_none()
            if module_id is None:
                logger.error("Module assessment %s/%s/%s: module not found - skipped", data["course_slug"], data["module_slug"], data["level"])
                continue
            try:
                await module_assessment_service.upsert_module_assessment(db, data, module_id=module_id, publish=True)
                seeded += 1
            except Exception as exc:  # noqa: BLE001 - one bad file must not abort the whole seed
                await db.rollback()
                logger.error("Module assessment %s/%s/%s not seeded: %s", data["course_slug"], data["module_slug"], data["level"], getattr(exc, "detail", exc))
    logger.info("Seeded %d module assessments", seeded)


async def _seed_diagnostic(db: AsyncSession, skills_by_slug: dict[str, Skill]) -> None:
    module = _load_module(CONTENT_SEED_DIR / "diagnostic.py", "seed_diagnostic")
    data = module.DIAGNOSTIC_ASSESSMENT

    result = await db.execute(select(Assessment).where(Assessment.assessment_type == "diagnostic"))
    assessment = result.scalars().first()
    if assessment is None:
        assessment = Assessment(assessment_type="diagnostic")
        db.add(assessment)
    assessment.title = data["title"]
    assessment.description = data.get("description")
    assessment.passing_score = data.get("passing_score", 0.0)
    assessment.time_limit_minutes = data.get("time_limit_minutes")
    await db.flush()

    existing_questions = await db.execute(select(Question).where(Question.assessment_id == assessment.id))
    for q in existing_questions.scalars().all():
        await db.delete(q)
    await db.flush()

    for idx, q in enumerate(data["questions"]):
        skill = skills_by_slug.get(q.get("skill_slug")) if q.get("skill_slug") else None
        db.add(Question(
            assessment_id=assessment.id, skill_id=skill.id if skill else None,
            question_type=q["question_type"], prompt=q["prompt"], options=q.get("options", []),
            correct_answer=q.get("correct_answer", {}), explanation=q.get("explanation"),
            difficulty=q.get("difficulty", "medium"), points=q.get("points", 1.0), order_index=idx,
        ))
    await db.commit()
    logger.info("Seeded diagnostic assessment with %d questions", len(data["questions"]))


async def _seed_projects(db: AsyncSession, skills_by_slug: dict[str, Skill]) -> None:
    path = CONTENT_SEED_DIR / "projects.py"
    if not path.exists():
        logger.warning("content/seed/projects.py not found yet — skipping projects")
        return
    module = _load_module(path, "seed_projects")

    for project_data in module.PROJECTS:
        result = await db.execute(select(Project).where(Project.slug == project_data["slug"]))
        project = result.scalar_one_or_none()
        if project is None:
            project = Project(slug=project_data["slug"])
            db.add(project)
        for field in [
            "title", "overview", "objective", "prerequisites", "learning_outcomes", "requirements",
            "architecture", "milestones", "tasks", "expected_output", "evaluation_criteria", "resources",
            "order_index", "estimated_hours", "difficulty",
        ]:
            setattr(project, field, project_data.get(field, getattr(project, field, None)))
        await db.flush()

        existing = await db.execute(select(ProjectSkill).where(ProjectSkill.project_id == project.id))
        for ps in existing.scalars().all():
            await db.delete(ps)
        await db.flush()

        for s in project_data.get("skills", []):
            skill = skills_by_slug.get(s["slug"])
            if skill:
                db.add(ProjectSkill(project_id=project.id, skill_id=skill.id, weight=s.get("weight", 1.0)))

    await db.commit()
    logger.info("Seeded %d projects", len(module.PROJECTS))


async def _seed_rag_chunks(db: AsyncSession, lessons: list[dict]) -> None:
    for lesson in lessons:
        lesson_id = lesson["id"]
        existing = await db.execute(select(DocumentChunk).where(DocumentChunk.lesson_id == lesson_id))
        existing_chunks = existing.scalars().all()
        if existing_chunks:
            continue  # already ingested; content is stable once seeded

        chunks = build_lesson_chunks(lesson)
        for chunk in chunks:
            db.add(DocumentChunk(
                lesson_id=lesson_id, source_type="lesson", title=chunk.get("title", lesson["title"]),
                chunk_index=chunk["chunk_index"], content=chunk["content"],
                embedding=embed_text(chunk["content"]),
            ))
    await db.commit()
    logger.info("RAG-ingested %d lessons", len(lessons))


async def _seed_admin_user(db: AsyncSession) -> None:
    import os

    # `or`, not a get() default: .env.example ships "ADMIN_EMAIL=" / "ADMIN_PASSWORD=" (set but blank), which docker
    # passes through as empty strings - that used to seed an admin account with a blank email and password.
    default_email, default_password = "admin@agenticailms.dev", "AdminPass123!"
    admin_email = (os.environ.get("ADMIN_EMAIL") or "").strip() or default_email
    admin_password = os.environ.get("ADMIN_PASSWORD") or default_password

    result = await db.execute(select(User).where(User.email == admin_email))
    if result.scalar_one_or_none() is not None:
        return

    db.add(User(email=admin_email, hashed_password=hash_password(admin_password), full_name="LMS Admin", role="admin"))
    await db.commit()
    if admin_password == default_password:
        logger.warning("Seeded admin %s with the DEFAULT password - set ADMIN_PASSWORD before any shared deployment", admin_email)
    else:
        logger.info("Seeded admin account %s", admin_email)


async def run_seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        skills_by_slug = await _seed_skills(db)
        lessons = await _seed_courses(db, skills_by_slug)
        await _seed_module_assessments(db)
        await _seed_diagnostic(db, skills_by_slug)
        await _seed_projects(db, skills_by_slug)
        await _seed_rag_chunks(db, lessons)
        await _seed_admin_user(db)

    logger.info("Seed complete.")


if __name__ == "__main__":
    from app.core.runtime import run_async

    run_async(run_seed())
