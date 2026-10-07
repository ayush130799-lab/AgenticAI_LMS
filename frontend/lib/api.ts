import type {
  ActivityItemOut,
  AssessmentSummaryOut,
  AttemptOut,
  AttemptResultOut,
  AssessmentViewOut,
  BookmarkItemOut,
  CertificateOut,
  ConversationSummaryOut,
  ModuleAnswer,
  ModuleProgressOut,
  RunCodeOut,
  SearchResult,
  StartAttemptOut,
  AssessmentListItemOut,
  AssessmentOut,
  CourseDetailOut,
  CourseSummaryOut,
  DashboardOut,
  DiagnosticResultOut,
  LearningPlanOut,
  LessonDetailOut,
  LessonHighlight,
  LessonNote,
  LoginRequest,
  ModuleDetailOut,
  OnboardingRequest,
  PracticeRunOut,
  ProjectDetailOut,
  ProjectSubmissionOut,
  ProjectSubmitRequest,
  ProjectSummaryOut,
  RecommendationOut,
  RegisterRequest,
  SkillOut,
  StartAssessmentRequest,
  StartAssessmentResponse,
  StudentProfileOut,
  StudentProgressOut,
  StudentSkillOut,
  SubmitAssessmentRequest,
  SubmitAssessmentResponse,
  TokenResponse,
  TutorChatRequest,
  TutorChatResponse,
  UserOut,
} from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api";

/** Admin create/update endpoints answer with just the record id. */
export type AdminSaved = { id: string };

const ACCESS_TOKEN_KEY = "lms_access_token";
const REFRESH_TOKEN_KEY = "lms_refresh_token";

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setTokens(accessToken: string, refreshToken: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  window.localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function clearTokens(): void {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  skipAuth?: boolean;
}

export const SESSION_EXPIRED_EVENT = "lms:session-expired";

let refreshInFlight: Promise<boolean> | null = null;

/** Exchanges the stored refresh token for a new pair. Shared, so parallel 401s trigger one refresh. */
function refreshSession(): Promise<boolean> {
  if (refreshInFlight) return refreshInFlight;
  refreshInFlight = (async () => {
    const refreshToken = getRefreshToken();
    if (!refreshToken) return false;
    try {
      const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (!res.ok) return false;
      const tokens = (await res.json()) as TokenResponse;
      setTokens(tokens.access_token, tokens.refresh_token);
      return true;
    } catch {
      return false;
    }
  })().finally(() => {
    refreshInFlight = null;
  });
  return refreshInFlight;
}

function endSession(): void {
  clearTokens();
  if (typeof window !== "undefined") window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT));
}

const RETRYABLE_STATUS = new Set([502, 503, 504]);
const GET_RETRIES = 2;

/** Retries only when told to (idempotent GETs): on a network failure or a gateway error, e.g. while the API restarts. */
async function fetchWithRetry(url: string, init: RequestInit, retries: number): Promise<Response> {
  for (let attempt = 0; ; attempt++) {
    try {
      const res = await fetch(url, init);
      if (!RETRYABLE_STATUS.has(res.status) || attempt >= retries) return res;
    } catch (err) {
      if (attempt >= retries) throw err;
    }
    await new Promise((resolve) => setTimeout(resolve, 300 * 2 ** attempt));
  }
}

function formatFieldError(error: unknown): string {
  if (!error || typeof error !== "object") return "";
  const { loc, msg } = error as { loc?: unknown; msg?: unknown };
  if (typeof msg !== "string" || !msg) return "";
  const field = Array.isArray(loc)
    ? [...loc].reverse().find((part): part is string => typeof part === "string" && part !== "body")
    : undefined;
  const text = msg.replace(/^Value error, /, "");
  if (!field) return text;
  const label = field.replace(/_/g, " ");
  return `${label.charAt(0).toUpperCase()}${label.slice(1)}: ${text}`;
}

/** The API sends `detail` as a string, as {message, errors[]} (assessment publishing), or with a pydantic `errors[]` list (422). */
function describeError(status: number, payload: unknown): string {
  const fallback = `Request failed with status ${status}`;
  if (!payload || typeof payload !== "object") return fallback;
  const { detail, errors } = payload as { detail?: unknown; errors?: unknown };

  if (status === 422 && Array.isArray(errors)) {
    const messages = errors.slice(0, 3).map(formatFieldError).filter(Boolean);
    if (messages.length > 0) return messages.join(". ");
  }
  if (typeof detail === "string") return detail;
  if (detail && typeof detail === "object") {
    const { message, errors: nested } = detail as { message?: unknown; errors?: unknown };
    const parts = [
      typeof message === "string" ? message : "",
      Array.isArray(nested) ? nested.filter((e): e is string => typeof e === "string").slice(0, 3).join("; ") : "",
    ].filter(Boolean);
    if (parts.length > 0) return parts.join(": ");
  }
  return fallback;
}

async function request<T>(path: string, options: RequestOptions = {}, isRetry = false): Promise<T> {
  const { body, skipAuth, headers, ...rest } = options;

  const finalHeaders: Record<string, string> = {
    "Content-Type": "application/json",
    ...(headers as Record<string, string> | undefined),
  };

  if (!skipAuth) {
    const token = getAccessToken();
    if (token) {
      finalHeaders["Authorization"] = `Bearer ${token}`;
    }
  }

  const isGet = (rest.method ?? "GET").toUpperCase() === "GET";
  let response: Response;
  try {
    response = await fetchWithRetry(
      `${API_BASE_URL}${path}`,
      {
        ...rest,
        headers: finalHeaders,
        body: body !== undefined ? JSON.stringify(body) : undefined,
      },
      isGet ? GET_RETRIES : 0
    );
  } catch {
    throw new ApiError(0, "Unable to reach the server. Please check your connection.");
  }

  // An expired/invalid access token: refresh once and replay the request, otherwise end the session.
  if (response.status === 401 && !skipAuth && !isRetry && getRefreshToken()) {
    if (await refreshSession()) {
      return request<T>(path, options, true);
    }
    endSession();
    throw new ApiError(401, "Your session has expired. Please log in again.");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  let payload: unknown = null;
  const text = await response.text();
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = null;
    }
  }

  if (!response.ok) {
    throw new ApiError(response.status, describeError(response.status, payload));
  }

  return payload as T;
}

export const api = {
  auth: {
    register: (body: RegisterRequest) =>
      request<TokenResponse>("/auth/register", { method: "POST", body, skipAuth: true }),
    login: (body: LoginRequest) =>
      request<TokenResponse>("/auth/login", { method: "POST", body, skipAuth: true }),
    logout: () => request<{ ok: boolean }>("/auth/logout", { method: "POST" }),
    me: () => request<UserOut>("/auth/me"),
  },
  students: {
    onboarding: (body: OnboardingRequest) =>
      request<{ ok: boolean }>("/students/me/onboarding", { method: "POST", body }),
    profile: () => request<StudentProfileOut>("/students/me/profile"),
    skills: () => request<StudentSkillOut[]>("/students/me/skills"),
    progress: () => request<StudentProgressOut>("/students/me/progress"),
    activity: (limit = 8) => request<ActivityItemOut[]>(`/students/me/activity?limit=${limit}`),
    bookmarks: () => request<BookmarkItemOut[]>("/students/me/bookmarks"),
    certificates: () => request<CertificateOut[]>("/students/me/certificates"),
  },
  courses: {
    list: () => request<CourseSummaryOut[]>("/courses"),
    get: (courseId: string) => request<CourseDetailOut>(`/courses/${courseId}`),
    modules: (courseId: string) =>
      request<ModuleDetailOut[]>(`/courses/${courseId}/modules`),
  },
  lessons: {
    get: (lessonId: string) => request<LessonDetailOut>(`/lessons/${lessonId}`),
    complete: (lessonId: string) =>
      request<LessonDetailOut>(`/lessons/${lessonId}/complete`, { method: "POST" }),
    getNotes: (lessonId: string) =>
      request<LessonNote[]>(`/lessons/${lessonId}/notes`),
    addNote: (lessonId: string, content: string) =>
      request<LessonNote>(`/lessons/${lessonId}/notes`, {
        method: "POST",
        body: { content },
      }),
    toggleBookmark: (lessonId: string) =>
      request<{ bookmarked: boolean }>(`/lessons/${lessonId}/bookmark`, {
        method: "POST",
      }),
    runPractice: (lessonId: string, code: string) =>
      request<PracticeRunOut>(`/lessons/${lessonId}/practice/run`, {
        method: "POST",
        body: { code },
      }),
    addHighlight: (lessonId: string, text: string, color: string) =>
      request<LessonHighlight>(`/lessons/${lessonId}/highlights`, {
        method: "POST",
        body: { text, color },
      }),
  },
  skills: {
    list: () => request<SkillOut[]>("/skills"),
    graph: () =>
      request<{
        nodes: { id: string; slug: string; name: string; category: string; description: string }[];
        edges: { source: string; target: string; required_mastery: number }[];
      }>("/skills/graph"),
  },
  assessments: {
    diagnostic: () => request<AssessmentOut>("/assessments/diagnostic"),
    diagnosticResult: () =>
      request<DiagnosticResultOut>("/assessments/diagnostic/result"),
    list: () => request<AssessmentListItemOut[]>("/assessments"),
    start: (body: StartAssessmentRequest) =>
      request<StartAssessmentResponse>("/assessments/start", { method: "POST", body }),
    submit: (body: SubmitAssessmentRequest) =>
      request<SubmitAssessmentResponse>("/assessments/submit", {
        method: "POST",
        body,
      }),
    results: (attemptId: string) =>
      request<SubmitAssessmentResponse>(`/assessments/${attemptId}/results`),
  },
  modules: {
    progress: (moduleId: string) => request<ModuleProgressOut>(`/modules/${moduleId}/progress`),
    assessments: (moduleId: string) => request<AssessmentSummaryOut[]>(`/modules/${moduleId}/assessments`),
  },
  moduleAssessments: {
    get: (assessmentId: string) => request<AssessmentViewOut>(`/module-assessments/${assessmentId}`),
    start: (assessmentId: string) =>
      request<StartAttemptOut>(`/module-assessments/${assessmentId}/attempts`, { method: "POST" }),
    attempts: (assessmentId: string) => request<AttemptOut[]>(`/module-assessments/${assessmentId}/attempts`),
    saveAnswers: (attemptId: string, answers: Record<string, ModuleAnswer | null>) =>
      request<{ saved: boolean }>(`/module-assessments/attempts/${attemptId}/answers`, {
        method: "PUT",
        body: { answers },
      }),
    runCode: (attemptId: string, questionId: string, code: string) =>
      request<RunCodeOut>(`/module-assessments/attempts/${attemptId}/questions/${questionId}/run`, {
        method: "POST",
        body: { code },
      }),
    submit: (attemptId: string, answers: Record<string, ModuleAnswer | null>) =>
      request<AttemptResultOut>(`/module-assessments/attempts/${attemptId}/submit`, {
        method: "POST",
        body: { answers },
      }),
    result: (attemptId: string) => request<AttemptResultOut>(`/module-assessments/attempts/${attemptId}`),
  },
  learningPath: {
    get: () => request<LearningPlanOut>("/learning-path"),
    generate: () => request<LearningPlanOut>("/learning-path/generate", { method: "POST" }),
  },
  recommendations: {
    list: () => request<RecommendationOut[]>("/recommendations"),
  },
  tutor: {
    chat: (body: TutorChatRequest) =>
      request<TutorChatResponse>("/tutor/chat", { method: "POST", body }),
    conversations: () => request<ConversationSummaryOut[]>("/tutor/conversations"),
    conversation: (id: string) =>
      request<Record<string, unknown>>(`/tutor/conversations/${id}`),
  },
  search: {
    query: (q: string) => request<{ results: SearchResult[]; query: string }>(`/search?q=${encodeURIComponent(q)}`),
  },
  projects: {
    list: () => request<ProjectSummaryOut[]>("/projects"),
    get: (projectId: string) => request<ProjectDetailOut>(`/projects/${projectId}`),
    submit: (projectId: string, body: ProjectSubmitRequest) =>
      request<ProjectSubmissionOut>(`/projects/${projectId}/submit`, {
        method: "POST",
        body,
      }),
  },
  dashboard: {
    get: () => request<DashboardOut>("/dashboard"),
  },
  admin: {
    courses: {
      create: (body: Record<string, unknown>) =>
        request<AdminSaved>("/admin/courses", { method: "POST", body }),
      update: (id: string, body: Record<string, unknown>) =>
        request<AdminSaved>(`/admin/courses/${id}`, { method: "PUT", body }),
      remove: (id: string) =>
        request<{ ok: boolean }>(`/admin/courses/${id}`, { method: "DELETE" }),
    },
    modules: {
      create: (body: Record<string, unknown>) =>
        request<AdminSaved>("/admin/modules", { method: "POST", body }),
      update: (id: string, body: Record<string, unknown>) =>
        request<AdminSaved>(`/admin/modules/${id}`, { method: "PUT", body }),
      remove: (id: string) =>
        request<{ ok: boolean }>(`/admin/modules/${id}`, { method: "DELETE" }),
    },
    lessons: {
      create: (body: Record<string, unknown>) =>
        request<AdminSaved>("/admin/lessons", { method: "POST", body }),
      update: (id: string, body: Record<string, unknown>) =>
        request<AdminSaved>(`/admin/lessons/${id}`, { method: "PUT", body }),
      remove: (id: string) =>
        request<{ ok: boolean }>(`/admin/lessons/${id}`, { method: "DELETE" }),
    },
    skills: {
      create: (body: Record<string, unknown>) =>
        request<AdminSaved>("/admin/skills", { method: "POST", body }),
      update: (id: string, body: Record<string, unknown>) =>
        request<AdminSaved>(`/admin/skills/${id}`, { method: "PUT", body }),
      remove: (id: string) =>
        request<{ ok: boolean }>(`/admin/skills/${id}`, { method: "DELETE" }),
    },
    assessments: {
      create: (body: Record<string, unknown>) =>
        request<AdminSaved>("/admin/assessments", { method: "POST", body }),
      update: (id: string, body: Record<string, unknown>) =>
        request<AdminSaved>(`/admin/assessments/${id}`, { method: "PUT", body }),
      remove: (id: string) =>
        request<{ ok: boolean }>(`/admin/assessments/${id}`, { method: "DELETE" }),
    },
    projects: {
      create: (body: Record<string, unknown>) =>
        request<AdminSaved>("/admin/projects", { method: "POST", body }),
      update: (id: string, body: Record<string, unknown>) =>
        request<AdminSaved>(`/admin/projects/${id}`, { method: "PUT", body }),
      remove: (id: string) =>
        request<{ ok: boolean }>(`/admin/projects/${id}`, { method: "DELETE" }),
    },
    users: {
      list: () => request<UserOut[]>("/admin/users"),
    },
  },
};

export { request };
