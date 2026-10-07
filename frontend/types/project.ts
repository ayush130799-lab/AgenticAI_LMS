export interface ProjectSummaryOut {
  id: string;
  slug: string;
  title: string;
  overview: string;
  difficulty: string;
  estimated_hours: number;
  order_index: number;
  submission_status: string | null;
}

export type ProjectStep = { title: string; description?: string };
export type ProjectCriterion = { criterion: string; weight: number };
export type ProjectResource = { title: string; url: string; resource_type?: string };

export interface ProjectDetailOut extends ProjectSummaryOut {
  objective: string;
  prerequisites: string[];
  learning_outcomes: string[];
  requirements: string[];
  architecture: string;
  milestones: ProjectStep[];
  tasks: ProjectStep[];
  expected_output: string;
  evaluation_criteria: ProjectCriterion[];
  resources: ProjectResource[];
}

/** AI mentor review stored on a submission (see project_service.submit_project). */
export interface ProjectAiFeedback {
  feedback?: string;
  strengths?: string[];
  improvements?: string[];
}

export interface ProjectSubmitRequest {
  repo_url?: string | null;
  submission_notes?: string | null;
}

export interface ProjectSubmissionOut {
  id: string;
  status: string;
  ai_feedback: ProjectAiFeedback;
  score: number | null;
  submitted_at: string;
}

export interface TutorChatRequest {
  message: string;
  conversation_id?: string | null;
  lesson_id?: string | null;
}

export interface TutorChatResponse {
  conversation_id: string;
  reply: string;
  citations: TutorCitation[];
}

export interface TutorCitation {
  lesson_id?: string | null;
  title: string;
}

export interface TutorMessage {
  id?: string;
  role: "user" | "assistant";
  content: string;
  citations?: TutorCitation[];
  created_at?: string;
}
