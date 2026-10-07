from fastapi import APIRouter

from app.api.routes import admin, assessments, auth, courses, dashboard, learning_path, lessons, projects, search, skills, module_assessments, students, tutor

api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(students.router)
api_router.include_router(courses.router)
api_router.include_router(lessons.router)
api_router.include_router(skills.router)
api_router.include_router(assessments.router)
api_router.include_router(module_assessments.modules_router)
api_router.include_router(module_assessments.router)
api_router.include_router(learning_path.router)
api_router.include_router(tutor.router)
api_router.include_router(projects.router)
api_router.include_router(dashboard.router)
api_router.include_router(search.router)
api_router.include_router(admin.router)
