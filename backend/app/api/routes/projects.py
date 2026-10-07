from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.project import ProjectDetailOut, ProjectSubmissionOut, ProjectSubmitRequest, ProjectSummaryOut
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectSummaryOut])
async def list_projects(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await project_service.list_projects(db, user.id)


@router.get("/{project_id}", response_model=ProjectDetailOut)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await project_service.get_project_detail(db, project_id, user.id)


@router.post("/{project_id}/submit", response_model=ProjectSubmissionOut)
async def submit_project(
    project_id: UUID, payload: ProjectSubmitRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    return await project_service.submit_project(db, user.id, project_id, payload.repo_url, payload.submission_notes)
