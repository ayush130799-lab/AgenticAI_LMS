from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.learning import LearningPlanOut, RecommendationOut
from app.services import planner_service

router = APIRouter(tags=["learning-path"])


@router.get("/learning-path", response_model=LearningPlanOut)
async def get_learning_path(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    plan = await planner_service.get_active_plan(db, user.id)
    if plan is None:
        plan = await planner_service.generate_learning_plan(db, user.id)
    return plan


@router.post("/learning-path/generate", response_model=LearningPlanOut)
async def regenerate_learning_path(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await planner_service.generate_learning_plan(db, user.id)


@router.get("/recommendations", response_model=list[RecommendationOut])
async def get_recommendations(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    return await planner_service.list_recommendations(db, user.id)
