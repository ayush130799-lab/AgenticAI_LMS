export type QuestionType =
  | "mcq"
  | "multi_select"
  | "short_answer"
  | "coding"
  | "scenario"
  | string;

export interface QuestionOut {
  id: string;
  question_type: QuestionType;
  prompt: string;
  options: Record<string, unknown>[];
  difficulty: string;
  points: number;
}

export interface AssessmentListItemOut {
  id: string;
  title: string;
  description: string | null;
  assessment_type: string;
  passing_score: number; // fraction 0-1, matches the backend model
  time_limit_minutes: number | null;
  question_count: number;
  last_score_percent: number | null;
}

export interface AssessmentOut {
  id: string;
  title: string;
  description: string | null;
  assessment_type: string;
  passing_score: number;
  time_limit_minutes: number | null;
  questions: QuestionOut[];
}

export interface StartAssessmentRequest {
  assessment_id: string;
}

export interface StartAssessmentResponse {
  attempt_id: string;
  assessment: AssessmentOut;
}

export interface AnswerValue {
  selected?: string | string[];
  text?: string;
  code?: string;
  [key: string]: unknown;
}

export interface SubmitAssessmentRequest {
  attempt_id: string;
  answers: Record<string, AnswerValue>;
}

export interface SkillResultOut {
  skill_slug: string;
  skill_name: string;
  score_percent: number;
  mastery_after: number;
}

export interface SubmitAssessmentResponse {
  attempt_id: string;
  score: number;
  passed: boolean;
  skill_breakdown: SkillResultOut[];
  weak_concepts: string[];
  strengths: string[];
  recommended_next_steps: string[];
}

export interface DiagnosticResultOut {
  attempt_id: string;
  skill_profile: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
  prerequisite_gaps: string[];
  recommended_starting_point: string;
  confidence: number;
}
