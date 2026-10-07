# API contract (backend ↔ frontend)

Base URL: `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000/api`).
Auth: `Authorization: Bearer <access_token>` header on every protected route.
All request/response bodies are JSON. Pydantic schemas live in
`backend/app/schemas/*.py` — read those for exact field names/types; this
file is the route map and a plain-English shape summary.

## Auth — `backend/app/schemas/auth.py`
- `POST /api/auth/register` — body `RegisterRequest{email,password,full_name}` → `TokenResponse{access_token,refresh_token,token_type}`. `email` must be a valid address, `password` 8–128 characters, `full_name` 1–255. Duplicate email → 409.
- `POST /api/auth/login` — body `LoginRequest{email,password}` → `TokenResponse`. Wrong credentials → 401. Register and login are limited to 20 requests/minute per IP (429).
- `POST /api/auth/refresh` — body `{refresh_token}` → new `TokenResponse`
- `POST /api/auth/logout` — no body → `{"ok": true}`
- `GET /api/auth/me` — → `UserOut{id,email,full_name,role,is_active}`

## Onboarding — `backend/app/schemas/learning.py`
- `POST /api/students/me/onboarding` — body `OnboardingRequest` (self-reported experience levels + goals) → `UserOut`-adjacent `{"ok": true}`
- `GET /api/students/me/profile` → student profile fields incl. `onboarding_completed`, `diagnostic_completed`

## Courses — `backend/app/schemas/curriculum.py`
- `GET /api/courses` → `CourseSummaryOut[]` (includes `progress_percent` when authenticated)
- `GET /api/courses/{course_id}` → `CourseDetailOut` (nested modules, lesson summaries)
- `GET /api/courses/{course_id}/modules` → `ModuleDetailOut[]`

## Lessons
- `GET /api/lessons/{lesson_id}` → `LessonDetailOut` (full markdown content, examples, practice, skills, `module_id`, `course_id`, `progress_status`)
- `POST /api/lessons/{lesson_id}/complete` → updated `LessonDetailOut.progress_status`
- `GET /api/lessons/{lesson_id}/notes` → `NoteOut[]` `{id, lesson_id, content, created_at}`
- `POST /api/lessons/{lesson_id}/notes` `{content}` (1–10,000 chars, not blank; trimmed) → `NoteOut`
- `POST /api/lessons/{lesson_id}/bookmark` (toggle, safe under concurrent requests) → `{"bookmarked": bool}`
- `POST /api/lessons/{lesson_id}/highlights` `{text, color?}` (`text` 1–2,000 chars, not blank; `color` ≤ 20 chars of `A-Za-z0-9#_-`, default `yellow`) → `HighlightOut` `{id, lesson_id, text, color, created_at}`
- The three write endpoints above return 404 for an unknown lesson and 403 when the lesson's module is locked (same rule as viewing it); invalid bodies → 422.
- `POST /api/lessons/{lesson_id}/practice/run` `{code}` → `{status: ok|error|timeout, stdout, stderr, error, duration_ms}` - runs open-ended practice code (no expected answer, not graded/persisted) in the sandbox; 403 if the module is locked, 503 if the sandbox is down.

## Skills — `backend/app/schemas/learning.py`
- `GET /api/skills` → `SkillOut[]` (full graph, incl. `parent_skill_id`)
- `GET /api/students/me/skills` → `StudentSkillOut[]` (mastery/confidence/level per skill)

## Progress
- `GET /api/students/me/progress` → `{curriculum_progress_percent, courses: [{course_id,title,progress_percent}]}`
- `GET /api/students/me/activity?limit=8` -> `[{id, action, entity_type, entity_id, title, score_percent, created_at}]`, newest first (actions: `lesson_completed`, `assessment_completed`, `project_submitted`)

## Assessments — `backend/app/schemas/assessment.py`
- `GET /api/assessments` → `AssessmentListItemOut[]` (all assessments with question_count + the student's last score if any)
- `GET /api/assessments/diagnostic` → `AssessmentOut` (the onboarding diagnostic)
- `POST /api/assessments/start` — body `StartAssessmentRequest{assessment_id}` → `StartAssessmentResponse{attempt_id, assessment}`
- `POST /api/assessments/submit` — body `SubmitAssessmentRequest{attempt_id, answers}` → `SubmitAssessmentResponse{score, passed, skill_breakdown, weak_concepts, strengths, recommended_next_steps}`
- `GET /api/assessments/{attempt_id}/results` → same shape as submit response, re-fetchable
- `GET /api/assessments/diagnostic/result` (after first diagnostic submit) → `DiagnosticResultOut{skill_profile, strengths, weaknesses, prerequisite_gaps, recommended_starting_point, confidence}`

## Learning path / recommendations — `backend/app/schemas/learning.py`
- `GET /api/learning-path` → `LearningPlanOut`
- `POST /api/learning-path/generate` → regenerates and returns `LearningPlanOut`
- `GET /api/recommendations` → `RecommendationOut[]`

## Tutor — `backend/app/schemas/project.py`
- `POST /api/tutor/chat` — body `TutorChatRequest{message, conversation_id?, lesson_id?}` → `TutorChatResponse{conversation_id, reply, citations}`
- `GET /api/tutor/conversations/{id}` → messages list

## Projects — `backend/app/schemas/project.py`
- `GET /api/projects` → `ProjectSummaryOut[]`
- `GET /api/projects/{id}` → `ProjectDetailOut`
- `POST /api/projects/{id}/submit` — body `ProjectSubmitRequest{repo_url?, submission_notes?}` → `ProjectSubmissionOut{status, ai_feedback, score}`

## Dashboard — `backend/app/schemas/learning.py`
- `GET /api/dashboard` → `DashboardOut` — **every field is computed from real DB state, nothing hardcoded**:
  `recent_assessment{attempt_id,assessment_id,title,assessment_type,score_percent,passed,submitted_at}` and `upcoming_assessment{assessment_id,title,assessment_type}` (the diagnostic until taken, then the current course's exam until passed) are computed server-side. Fields: `full_name, curriculum_progress_percent, overall_skill_mastery_percent, current_course, continue_lesson, skills[], weak_skills[], recent_assessment, upcoming_assessment, active_projects[], learning_streak_days, recommendations[]`

## Module assessments & progression gating — `backend/app/schemas/module_assessment.py`
The backend is the source of truth for score, correctness, completion and unlocking. Client-sent scores/`is_correct`/pass flags do not exist in any request model.
- `GET /api/modules/{id}/progress` → `ModuleProgressOut` (`status: completed|in_progress|available|locked`, `locked_reason`, `lessons_completed/total`, `assessment{status: locked|available|in_progress|passed, required_level, levels[], attempts_count, best_percentage}`)
- `GET /api/modules/{id}/access` → `{accessible, reason}`; `GET /api/modules/{id}/assessments` (403 if the module is locked)
- `GET /api/module-assessments/{assessment_id}` → questions **without** answer keys/hidden tests (403 until all lessons are done)
- `POST /api/module-assessments/{assessment_id}/attempts` → start, or resume the open attempt (409 if already passed)
- `GET  /api/module-assessments/{assessment_id}/attempts` → attempt history (each attempt stored separately)
- `PUT  /api/module-assessments/attempts/{id}/answers` → autosave draft
- `POST /api/module-assessments/attempts/{id}/questions/{qid}/run` → run **visible** sample tests in the sandbox
- `POST /api/module-assessments/attempts/{id}/submit` → grade (422 malformed answers, 503 sandbox down – attempt stays open)
- `GET  /api/module-assessments/attempts/{id}` → result; answer key/explanations are revealed only after a pass
- Lessons of a locked module: `GET /api/lessons/{id}` and `POST .../complete` return 403 with the reason.
- Admin: `POST /api/admin/module-assessments` (upsert), `GET .../{id}/validate`, `POST .../{id}/publish|unpublish`. Publishing enforces exactly 3 MCQ + 2 quiz + 2 coding, a valid level, 80% passing score and >=1 required coding question.

## Admin (role=admin only, same base path + `/admin`)
Create/update endpoints answer `{"id": "<uuid>"}`; deletes answer `{"ok": true}`. Every POST/PUT/DELETE (successful or not) is recorded in the `admin_audit_log` table.
- `POST/PUT/DELETE /api/admin/courses[/​{id}]`
- `POST/PUT/DELETE /api/admin/modules[/​{id}]`
- `POST/PUT/DELETE /api/admin/lessons[/​{id}]`
- `POST/PUT/DELETE /api/admin/skills[/​{id}]`
- `POST/PUT/DELETE /api/admin/assessments[/​{id}]`
- `POST/PUT/DELETE /api/admin/projects[/​{id}]`
- `GET /api/admin/users`

## Conventions
- All list endpoints return plain JSON arrays (no envelope).
- Errors: `{"detail": "message"}` with standard HTTP status codes (401/403/404/409/422/429/500). Never render raw stack traces.
  Variations the client must handle (`frontend/lib/api.ts` `describeError` does):
  - 422 validation: `{"detail": "Invalid request data", "errors": [{"loc": [...], "msg": "...", "type": "..."}]}` — only `loc/msg/type` are sent; the submitted values are never echoed back.
  - Publishing an invalid module assessment: `detail` is an object `{"message": "...", "errors": ["..."]}`.
  - 429 (rate limited): `{"detail": "Too many requests..."}` plus a `Retry-After` header. Limits are per client IP: 120/minute overall (`/api/health` exempt), 20/minute on login/register.
  - 409 (admin): deleting a record that is still referenced, or reusing a slug.
- Authentication on routes that also allow anonymous visitors (`GET /courses`, `/courses/{id}`, `/lessons/{id}`): **no** `Authorization` header = anonymous; a header that is present but expired/invalid = **401** (never silently downgraded to anonymous), so the client's refresh-token flow runs.
- Dates are ISO-8601 strings.
- IDs are UUID strings everywhere.
