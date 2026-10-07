from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.module_assessment import (
    AssessmentViewOut,
    AttemptOut,
    AttemptResultOut,
    ModuleAccessOut,
    ModuleProgressOut,
    AssessmentSummaryOut,
    RunCodeOut,
    RunCodeRequest,
    SaveAnswersRequest,
    StartAttemptOut,
    SubmitAttemptRequest,
)
from app.services import module_assessment_service as service
from app.services import planner_service, progression_service
from app.services.code_execution import CodeRunner, get_code_runner

modules_router = APIRouter(prefix="/modules", tags=["module-progress"])
router = APIRouter(prefix="/module-assessments", tags=["module-assessments"])


# ---- Module progress / access -----------------------------------------------------------------
@modules_router.get("/{module_id}/progress", response_model=ModuleProgressOut)
async def module_progress(module_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await progression_service.get_module_state(db, user, module_id)


@modules_router.get("/{module_id}/access", response_model=ModuleAccessOut)
async def module_access(module_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    state = await progression_service.get_module_state(db, user, module_id)
    return {"module_id": module_id, "accessible": not state["locked"], "reason": state["locked_reason"]}


@modules_router.get("/{module_id}/assessments", response_model=list[AssessmentSummaryOut])
async def module_assessments(module_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    await progression_service.assert_module_accessible(db, user, module_id)
    return [service.assessment_summary(a) for a in await service.list_module_assessments(db, module_id)]


# ---- Attempts -------------------------------------------------------------------------------------
# NOTE: literal "/attempts/..." routes are declared before "/{assessment_id}" so they are never shadowed.
@router.put("/attempts/{attempt_id}/answers")
async def save_answers(attempt_id: UUID, payload: SaveAnswersRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.save_draft(db, user, attempt_id, payload.answers)


@router.post("/attempts/{attempt_id}/questions/{question_id}/run", response_model=RunCodeOut)
async def run_code(
    attempt_id: UUID, question_id: UUID, payload: RunCodeRequest, db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user), runner: CodeRunner = Depends(get_code_runner),
):
    return await service.run_sample_tests(db, user, attempt_id, question_id, payload.code, runner)


@router.post("/attempts/{attempt_id}/submit", response_model=AttemptResultOut)
async def submit(
    attempt_id: UUID, payload: SubmitAttemptRequest, background: BackgroundTasks, db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user), runner: CodeRunner = Depends(get_code_runner),
):
    result = await service.submit_attempt(db, user, attempt_id, payload.answers, runner)
    background.add_task(planner_service.refresh_plan_in_background, user.id)  # only reached once grading succeeded
    return result


@router.get("/attempts/{attempt_id}", response_model=AttemptResultOut)
async def attempt_result(attempt_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.get_attempt_result(db, user, attempt_id)


@router.get("/{assessment_id}", response_model=AssessmentViewOut)
async def get_assessment(assessment_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.get_assessment_view(db, user, assessment_id)


@router.post("/{assessment_id}/attempts", response_model=StartAttemptOut)
async def start_attempt(assessment_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.start_attempt(db, user, assessment_id)


@router.get("/{assessment_id}/attempts", response_model=list[AttemptOut])
async def list_attempts(assessment_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await service.list_attempts(db, user, assessment_id)
