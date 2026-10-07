export interface StudentSkillOut {
  skill_slug: string;
  skill_name: string;
  category: string;
  mastery: number;
  confidence: number;
  level: string;
  attempts: number;
}

export interface RecommendationOut {
  id: string;
  recommendation_type: string;
  target_id: string | null;
  target_type: string | null;
  title: string;
  reason: string;
  priority: number;
}

export interface LearningPlanStepOut {
  step_type: string;
  target_id: string | null;
  title: string;
  reason: string;
  skill_focus: string[];
}

export interface LearningPlanOut {
  id: string;
  summary: string;
  reasoning: string;
  recommended_path: LearningPlanStepOut[];
}

export interface DashboardCurrentCourse {
  id: string;
  title: string;
  slug: string;
  progress_percent: number;
}

export interface DashboardContinueLesson {
  id: string;
  title: string;
  course_title: string;
}

export interface DashboardPendingAssessment {
  assessment_id: string;
  module_id: string;
  module_title: string;
  level: string;
  status: string;
}

export interface DashboardRecentAssessment {
  attempt_id: string;
  assessment_id: string;
  title: string;
  assessment_type: string;
  score_percent: number;
  passed: boolean;
  submitted_at: string | null;
}

export interface DashboardUpcomingAssessment {
  assessment_id: string;
  title: string;
  assessment_type: string;
}

export interface DashboardProject {
  id: string;
  title: string;
  status: string;
  score: number | null;
}

export interface DashboardOut {
  full_name: string;
  curriculum_progress_percent: number;
  overall_skill_mastery_percent: number;
  current_course: DashboardCurrentCourse | null;
  continue_lesson: DashboardContinueLesson | null;
  pending_module_assessment?: DashboardPendingAssessment | null;
  skills: StudentSkillOut[];
  weak_skills: StudentSkillOut[];
  recent_assessment: DashboardRecentAssessment | null;
  upcoming_assessment: DashboardUpcomingAssessment | null;
  active_projects: DashboardProject[];
  learning_streak_days: number;
  recommendations: RecommendationOut[];
}

export interface ActivityItemOut {
  id: string;
  action: string;
  entity_type: string | null;
  entity_id: string | null;
  title: string | null;
  score_percent: number | null;
  created_at: string;
}

export interface OnboardingRequest {
  programming_experience: string;
  python_experience: string;
  ai_ml_experience: string;
  llm_experience: string;
  rag_experience: string;
  agent_experience: string;
  langchain_experience: string;
  langgraph_experience: string;
  career_goal: string;
  target_role: string;
  available_hours_per_week: number;
  preferred_pace: string;
}

export interface StudentProfileOut {
  id?: string;
  user_id?: string;
  onboarding_completed: boolean;
  diagnostic_completed: boolean;
  programming_experience?: string;
  python_experience?: string;
  ai_ml_experience?: string;
  llm_experience?: string;
  rag_experience?: string;
  agent_experience?: string;
  langchain_experience?: string;
  langgraph_experience?: string;
  career_goal?: string;
  target_role?: string;
  available_hours_per_week?: number;
  preferred_pace?: string;
  current_streak_days?: number;
  longest_streak_days?: number;
  streak_days?: number;
  bio?: string;
  certificates?: CertificateOut[];
}

export interface StudentProgressOut {
  curriculum_progress_percent: number;
  courses: { course_id: string; title: string; progress_percent: number }[];
}

export interface BookmarkItemOut {
  id: string;
  lesson_id: string;
  lesson_title: string;
  lesson_type: string;
  course_id: string;
  created_at: string | null;
}

export interface CertificateOut {
  id: string;
  certificate_number: string;
  course_id: string;
  course_title?: string;
  issued_at: string | null;
}

export interface ConversationSummaryOut {
  id: string;
  title: string;
  lesson_id: string | null;
  updated_at: string | null;
}

export interface SearchResult {
  type: "course" | "lesson" | "skill";
  id: string;
  slug: string;
  title: string;
  subtitle: string;
  badge: string;
  href: string;
}
