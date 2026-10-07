export interface SkillOut {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  category: string;
  parent_skill_id: string | null;
}

export interface LessonSummaryOut {
  id: string;
  slug: string;
  title: string;
  description: string;
  lesson_type: string;
  order_index: number;
  estimated_minutes: number;
  progress_status?: string | null;
}

// Shapes of the JSON stored on a lesson (see content/seed/courses). `type` aliases, not interfaces, so they stay
// assignable to Record<string, unknown> for generic renderers.
export type LessonExample = { title: string; code?: string; explanation?: string };
export type LessonResource = { title: string; url: string; resource_type?: string };
export type PracticeExercise = { prompt: string; hint?: string; difficulty?: string };

export interface LessonDetailOut extends LessonSummaryOut {
  learning_objectives: string[];
  content_markdown: string;
  examples: LessonExample[];
  practice_exercises: PracticeExercise[];
  resources: LessonResource[];
  skills: SkillOut[];
  module_id: string;
  course_id: string;
  progress_status: string | null;
  is_bookmarked?: boolean;
}

export interface ModuleSummaryOut {
  id: string;
  slug: string;
  title: string;
  description: string;
  order_index: number;
  estimated_hours: number;
  lesson_count: number;
  completed_lesson_count: number;
  // Progression, derived by the server (absent on older payloads).
  status?: "completed" | "in_progress" | "available" | "locked" | null;
  locked?: boolean;
  locked_reason?: string | null;
  all_lessons_completed?: boolean;
  has_assessment?: boolean;
  assessment_status?: "locked" | "available" | "in_progress" | "passed" | null;
  assessment_unavailable_reason?: string | null;
  assessment_best_percentage?: number | null;
}

export interface ModuleDetailOut extends ModuleSummaryOut {
  lessons: LessonSummaryOut[];
}

export type CourseLevel = "beginner" | "intermediate" | "advanced" | string;

export interface CourseSummaryOut {
  id: string;
  slug: string;
  title: string;
  subtitle: string | null;
  description: string;
  order_index: number;
  estimated_hours: number;
  level: CourseLevel;
  icon: string | null;
  module_count: number;
  lesson_count: number;
  progress_percent: number | null;
}

export interface CourseDetailOut extends CourseSummaryOut {
  modules_completed?: number;
  learning_outcomes: string[];
  modules: ModuleDetailOut[];
}

export interface LessonNote {
  id: string;
  lesson_id: string;
  content: string;
  created_at: string;
}

export interface PracticeRunOut {
  status: "ok" | "error" | "timeout";
  stdout: string;
  stderr: string;
  error: string | null;
  duration_ms: number;
}

export interface LessonHighlight {
  id: string;
  lesson_id: string;
  text: string;
  color: string;
  created_at: string;
}
