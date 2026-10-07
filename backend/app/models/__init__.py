from app.db.base import Base
from app.models.activity import ActivityLog, AIInteraction, Conversation, Message
from app.models.assessment import Assessment, AssessmentAnswer, AssessmentAttempt, Question, StudentSkill
from app.models.audit import AdminAuditLog
from app.models.content import Bookmark, Certificate, Highlight, Note, Resource
from app.models.curriculum import Course, Lesson, LessonSkill, Module, Skill, SkillPrerequisite
from app.models.enrollment import Enrollment, LessonProgress
from app.models.learning import LearningPlan, Recommendation
from app.models.project import Project, ProjectSkill, ProjectSubmission
from app.models.rag import DocumentChunk
from app.models.user import StudentProfile, User

__all__ = [
    "Base",
    "User",
    "StudentProfile",
    "Course",
    "Module",
    "Lesson",
    "Skill",
    "SkillPrerequisite",
    "LessonSkill",
    "Enrollment",
    "LessonProgress",
    "Assessment",
    "Question",
    "AssessmentAttempt",
    "AssessmentAnswer",
    "StudentSkill",
    "Project",
    "ProjectSkill",
    "ProjectSubmission",
    "LearningPlan",
    "Recommendation",
    "Note",
    "Bookmark",
    "Highlight",
    "Resource",
    "Certificate",
    "ActivityLog",
    "Conversation",
    "Message",
    "AIInteraction",
    "DocumentChunk",
    "AdminAuditLog",
]
