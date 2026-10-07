from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.assessment import (
    AssessmentListItemOut,
    AssessmentOut,
    DiagnosticResultOut,
    StartAssessmentRequest,
    StartAssessmentResponse,
    SubmitAssessmentRequest,
    SubmitAssessmentResponse,
)
from app.services import assessment_service

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.get("", response_model=list[AssessmentListItemOut])
async def list_assessments(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await assessment_service.list_assessments(db, user.id)


@router.get("/diagnostic", response_model=AssessmentOut)
async def diagnostic(db: AsyncSession = Depends(get_db)):
    return await assessment_service.get_diagnostic_assessment(db)


@router.post("/start", response_model=StartAssessmentResponse)
async def start(payload: StartAssessmentRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    attempt = await assessment_service.start_attempt(db, user.id, payload.assessment_id)
    assessment = await assessment_service.get_assessment(db, payload.assessment_id)
    return {"attempt_id": attempt.id, "assessment": assessment}


@router.post("/submit", response_model=SubmitAssessmentResponse)
async def submit(payload: SubmitAssessmentRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await assessment_service.submit_attempt(db, user.id, payload.attempt_id, payload.answers)


@router.get("/{attempt_id}/results", response_model=SubmitAssessmentResponse)
async def results(attempt_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await assessment_service.get_attempt_results(db, user.id, attempt_id)


@router.get("/diagnostic/result", response_model=DiagnosticResultOut)
async def diagnostic_result(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await assessment_service.get_diagnostic_result(db, user.id)
