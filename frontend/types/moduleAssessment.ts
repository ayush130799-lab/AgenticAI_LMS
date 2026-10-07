export type ModuleStatus = "completed" | "in_progress" | "available" | "locked";
export type ModuleAssessmentStatus = "locked" | "available" | "in_progress" | "passed";

export interface AssessmentLevelOut {
  assessment_id: string;
  level: string;
  title: string;
  required: boolean;
  passed: boolean;
  attempts_count: number;
  best_percentage: number | null;
  in_progress_attempt_id: string | null;
}

export interface ModuleAssessmentStateOut {
  configured: boolean;
  status: ModuleAssessmentStatus;
  unavailable_reason: string | null;
  required_level: string;
  passed: boolean;
  attempts_count: number;
  best_percentage: number | null;
  levels: AssessmentLevelOut[];
}

export interface ModuleProgressOut {
  module_id: string;
  course_id: string;
  title: string;
  order_index: number;
  status: ModuleStatus;
  locked: boolean;
  locked_reason: string | null;
  lessons_total: number;
  lessons_completed: number;
  all_lessons_completed: boolean;
  has_assessment: boolean;
  assessment: ModuleAssessmentStateOut | null;
}

export interface AssessmentSummaryOut {
  id: string;
  module_id: string | null;
  title: string;
  description: string | null;
  level: string | null;
  is_published: boolean;
  total_questions: number;
  mcq_count: number;
  quiz_count: number;
  coding_count: number;
  passing_score_percent: number;
  required_coding_questions: number;
  time_limit_minutes: number | null;
}

export interface OptionOut {
  id: string;
  text: string;
}

export interface SampleTestOut {
  args: unknown[];
  expected: unknown;
}

export interface CodingViewOut {
  language: string;
  function_name: string;
  starter_code: string;
  expected_output: string;
  sample_tests: SampleTestOut[];
  hidden_test_count: number;
  time_limit_seconds: number;
  memory_limit_mb: number;
}

export type QuizFormat = "true_false" | "multi_select" | "scenario" | "short_answer";

export interface ModuleQuestionView {
  id: string;
  order: number;
  type: "mcq" | "quiz" | "coding";
  quiz_format: QuizFormat | null;
  prompt: string;
  difficulty: string;
  points: number;
  options: OptionOut[];
  coding: CodingViewOut | null;
}

export interface AssessmentViewOut extends AssessmentSummaryOut {
  questions: ModuleQuestionView[];
}

export interface AttemptOut {
  id: string;
  assessment_id: string;
  attempt_number: number | null;
  status: string;
  percentage: number | null;
  passed: boolean | null;
  started_at: string;
  submitted_at: string | null;
}

export interface StartAttemptOut {
  attempt: AttemptOut;
  assessment: AssessmentViewOut;
  saved_answers: Record<string, ModuleAnswer | null>;
}

/** What the client may send: answers only. Scores and correctness are always computed by the server. */
export type ModuleAnswer = { choice?: string; choices?: string[]; text?: string; code?: string };

export interface CodeTestResult {
  id: string;
  visible: boolean;
  status: string;
  passed: boolean;
  args?: unknown[];
  expected?: unknown;
  actual?: unknown;
  error?: string;
  stdout?: string;
}

export interface RunCodeOut {
  results: CodeTestResult[];
  passed_count: number;
  total_count: number;
}

export interface CategoryScore {
  correct: number;
  total: number;
}

export interface AttemptResultSummary {
  points_earned: number | null;
  points_total: number | null;
  percentage: number | null;
  passed: boolean;
  questions_correct: number | null;
  questions_total: number | null;
  mcq: CategoryScore;
  quiz: CategoryScore;
  coding: CategoryScore;
  passing_percent: number | null;
  required_coding: number | null;
  score_requirement_met: boolean | null;
  coding_requirement_met: boolean | null;
  weak_concepts: string[];
}

export interface QuestionResultOut {
  id: string;
  order: number;
  type: "mcq" | "quiz" | "coding";
  quiz_format: QuizFormat | null;
  prompt: string;
  points: number;
  points_awarded: number;
  is_correct: boolean;
  your_answer: ModuleAnswer | null;
  options: OptionOut[];
  coding: { passed_count: number; total_count: number; tests: CodeTestResult[] } | null;
  explanation?: string | null;
  correct_answer?: { choice?: string; choices?: string[]; accepted?: string[] } | null;
  reference_solution?: string | null;
}

export interface AttemptResultOut {
  attempt: AttemptOut;
  assessment: AssessmentSummaryOut;
  result: AttemptResultSummary | null;
  questions: QuestionResultOut[];
  module: ModuleProgressOut | null;
  next_module: { module_id: string; title: string; status: string } | null;
}
