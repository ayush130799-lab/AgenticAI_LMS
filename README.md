# Agentic AI LMS

A learning management system that teaches Agentic AI — Python, ML foundations, LLMs,
prompt engineering, embeddings, RAG, AI agents, LangChain, LangGraph, multi-agent
systems, evaluation/safety, and production AI — through a fixed, standard curriculum
that an AI personalization layer adapts *per student*.

Two systems, working together:

- **Standard curriculum** (`content/seed/`): 13 courses (133 modules, 272
  lessons), a 24-skill graph, a diagnostic plus a per-course exam, and 7 capstone projects. Every
  student sees the same curriculum.
- **Personalization engine** (`ai_engine/`): a Learning Planner agent, an AI Tutor
  (RAG-grounded), an Assessment agent, a Skill Analysis agent, and a Project Mentor
  agent that together figure out *where a specific student should start, what to
  revise, and what to do next* — without changing the curriculum itself.

## Architecture

```
                    STUDENT
                       |
               NEXT.JS FRONTEND  (frontend/)
                       |
                    FastAPI API  (backend/app/api)
                       |
          +------------+------------+
          |                         |
     LMS BACKEND               AI ENGINE
   (backend/app/services)   (ai_engine/agents, orchestration, rag)
          |                         |
          |             +-----------+-----------+
          |             |           |           |
          |          PLANNER      TUTOR     ASSESSMENT
          |             |           |           |
          |             +-----------+-----------+
          |                         |
          |                  SKILL / PROJECT MENTOR
          |                         |
          +-------------+-----------+
                        |
                 STUDENT MODEL (student_skills, learning_plans)
                        |
                 PostgreSQL + pgvector
```

`backend/` and `ai_engine/` are two logically separate Python packages that share a
process. The backend owns every database write; `ai_engine` agents are plain
functions/classes that take dicts in and return dicts out (the RAG retriever is the
one exception — it takes an `AsyncSession` the backend passes in, since vector search
has to happen where pgvector lives). Every agent has both an LLM-backed mode and a
real, non-trivial rule-based fallback, so the whole product runs end-to-end without
any API key configured — useful for grading/local dev, and it degrades gracefully in
production if the LLM provider is briefly unavailable.

## Technology stack

| Layer | Choice |
|---|---|
| Frontend | Next.js 14 (App Router) + TypeScript + Tailwind CSS |
| Backend API | FastAPI + Python 3.11 |
| Database | PostgreSQL + pgvector (RAG embeddings live in the same DB — no separate vector store to run) |
| AI orchestration | LangGraph for stateful agent workflows (tutor RAG flow, planner reasoning) |
| AI framework | LangChain where it earns its keep (model/tool/prompt abstractions) |
| Auth | JWT access + refresh tokens, bcrypt password hashing |
| Deployment | Docker Compose (postgres + backend + frontend) |

## Project structure

```
agentic-ai-lms/
├── frontend/            Next.js app (pages, components, lib, hooks, types)
├── backend/              FastAPI app
│   ├── app/
│   │   ├── api/routes/   one router module per resource
│   │   ├── models/       SQLAlchemy ORM models (source of truth for the schema)
│   │   ├── schemas/      Pydantic request/response models (= the API contract)
│   │   ├── services/     business logic + queries (see note below)
│   │   ├── core/         config, security, auth dependencies
│   │   └── db/           session, base, seed_runner
│   ├── alembic/          migrations
│   └── tests/            pytest suite (needs a real Postgres+pgvector)
├── ai_engine/            agents, orchestration (LangGraph), RAG, prompts, tools
├── content/seed/         curriculum data: skills.py, courses/*.py, diagnostic.py, projects.py
├── docs/                 API_CONTRACT.md, DESIGN_SYSTEM.md (the specs the frontend/AI agents were built against)
├── docker-compose.yml
└── .env.example
```

**A deliberate simplification:** `app/repositories/` exists but is intentionally thin
— query logic lives directly in `app/services/*.py` rather than behind a separate
repository interface. At this project's size, a repository layer added indirection
without real benefit; see `backend/app/repositories/__init__.py`.

## Database

25 tables covering users/auth, curriculum (courses → modules → lessons), the skill
graph (skills, prerequisites, lesson↔skill mappings), enrollment/progress, assessments
(assessments, questions, attempts), the persistent per-student skill model
(`student_skills`), projects/submissions, the AI layer's outputs (`learning_plans`,
`recommendations`), content extras (notes/bookmarks/highlights/resources/certificates),
activity/AI logging, and RAG (`document_chunks`, pgvector). See
`backend/app/models/*.py` for the full schema — every table has real foreign keys,
indexes on natural keys, and check constraints on enum-like string columns.

**Curriculum progress vs. skill mastery are tracked separately, on purpose.**
Completing a lesson updates `lesson_progress`/enrollment progress. It does **not**
touch `student_skills`. Mastery only moves in response to real evidence — a graded
assessment attempt, a quiz, or a project submission — via
`ai_engine.agents.skill.SkillAnalysisAgent.update_mastery`. A student can be "80%
through the RAG course" and still show 40% RAG mastery if they haven't proven it on
an assessment yet; that's intentional, not a bug.

## Setup

### 1. Environment

```bash
cp .env.example .env
# fill in LLM_API_KEY / EMBEDDING_API_KEY if you have them — the app runs
# without them (agents use their rule-based fallback path), but real answers
# from the AI Tutor / Planner need a configured LLM_API_KEY.
```

### 2. Run everything with Docker (recommended)

```bash
docker compose up --build
```

This starts Postgres (with pgvector), runs `alembic upgrade head`, seeds the full
curriculum + diagnostic assessment + projects + RAG embeddings, and starts both
the API (`:8000`) and the frontend (`:3000`). A default admin account is created
on first seed — check the backend container logs for its generated credentials
(or set `ADMIN_EMAIL`/`ADMIN_PASSWORD` in `.env` to pin them).

### 3. Or run locally without Docker

```bash
# Postgres WITH the pgvector extension must be reachable at DATABASE_URL
# (the ankane/pgvector image works: docker run -e POSTGRES_PASSWORD=... -p 5432:5432 ankane/pgvector)
cd backend
python -m venv .venv && . .venv/Scripts/activate   # or source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.db.seed_runner
python serve.py --port 8000            # add --reload for development
```

```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api npm run dev
```

Use `python serve.py` rather than bare `uvicorn app.main:app`: on **Windows**, uvicorn's
default event loop is incompatible with psycopg's async driver (the seed script and
`serve.py` both use `app/core/runtime.py` to pick a compatible loop). On Linux/macOS/Docker
plain `uvicorn` works too. `ai_engine/` is put on `sys.path` automatically by
`backend/app/__init__.py`, so no `PYTHONPATH` setup is needed.

### 4. Try it

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/api/docs
- Sign up as a student → onboarding → diagnostic assessment → dashboard with a
  real AI-generated learning path.
- Log in as the seeded admin → `/admin` → curriculum CMS.

## Testing

```bash
cd backend
createdb -h localhost -U lms_user agentic_ai_lms_test   # once
TEST_DATABASE_URL=postgresql+psycopg://lms_user:lms_password@localhost:5432/agentic_ai_lms_test pytest
```

Tests need a real Postgres+pgvector instance — the schema uses UUID/JSONB/ARRAY/
vector columns that SQLite can't represent. Coverage: auth (register/login/duplicate/
protected routes), courses & lessons (listing, detail, completion, progress, notes/
highlights/bookmarks incl. concurrency), assessments (grading, skill mastery updates,
weak-concept detection, re-submission guard), the AI Tutor (RAG-grounded chat,
conversation continuity, auth requirement), the learning path/recommendation engine,
the dashboard, project submission with AI Mentor feedback, admin permission
enforcement, admin conflict handling and the audit trail, and rate limiting.

**The suite drops and recreates every table**, so `conftest.py` refuses to run unless
`DATABASE_URL`'s database name ends in `_test`. Inside the docker-compose backend
container `DATABASE_URL` points at the *development* database, so override it explicitly:

```bash
T=postgresql+psycopg://lms_user:lms_password@postgres:5432/agentic_ai_lms_test
docker exec agentic_lms_postgres psql -U lms_user -d postgres -c "CREATE DATABASE agentic_ai_lms_test"   # once
docker exec -e DATABASE_URL=$T -e DATABASE_URL_SYNC=$T -e VECTOR_DATABASE_URL=$T agentic_lms_backend \
  sh -c "cd /app && python -m pytest -q"
```

## Rate limiting & admin audit trail

- **Rate limits** are per client IP (slowapi): `RATE_LIMIT_DEFAULT` (120/minute) for every route except
  `/api/health`, and a stricter `RATE_LIMIT_AUTH` (20/minute) on login and register to slow credential
  stuffing. Exceeded limits return `429 {"detail": ...}` with a `Retry-After` header. The suite runs with
  `RATE_LIMIT_ENABLED=false`; the rate-limit tests switch it on themselves. Behind a reverse proxy, start
  uvicorn with `--proxy-headers` so the real client IP is used.
- **Admin audit trail**: every state-changing `/api/admin/*` request (POST/PUT/DELETE, including failed
  ones) writes a row to `admin_audit_log` — who (id + email), method, path, entity and record id, HTTP
  status, client IP, time. Read-only requests are not recorded, and request bodies are deliberately not
  stored (they can contain assessment answer keys). Creates record the entity type but not the new id.
  Query it with e.g. `SELECT created_at, actor_email, method, path, status_code FROM admin_audit_log ORDER BY created_at DESC;`.
- **Conflicts**: deleting a record other rows still reference, or reusing a slug, returns `409` with a
  readable message instead of a generic 500.

## Module assessments & progression gating

A module with a published assessment is a **gate**: 7 questions (3 MCQ, 2 quiz, 2 coding) at
beginner/intermediate/advanced difficulty. Pass = **>= 80% overall AND >= 1 coding question passed**.
It unlocks only after every lesson in the module is complete; passing completes the module and
unlocks the next. Failed attempts can be retried and every attempt is stored. Modules without an
assessment behave exactly as before. Module state is derived (lessons + passed attempts), not a second
progress table; a module you had already started before gating existed stays open.

- **Coding runs in a separate sandbox** (`code_runner/`): its own container on an internal network,
  a fresh `python -I` subprocess per test with CPU/memory/process/file limits, read-only rootfs, all
  capabilities dropped. Expected values never enter the student's process. The backend talks to it
  through a `CodeRunner` interface (`app/services/code_execution.py`); set `CODE_RUNNER_TOKEN`
  (shared secret) in `.env`. If the sandbox is down, submit returns 503 and the attempt stays open.
- **Content**: `content/seed/module_assessments/*.py` (format in `SCHEMA.md`, validate with
  `python content/seed/check_module_assessments.py`); the seed runner upserts and publishes valid ones.
  Currently seeded: Python for AI modules 1-3 (all three levels).
- **Sandbox tests**: `docker build -t agenticai-code-runner code_runner`, then
  `docker run --rm --user root -v "$PWD/code_runner/tests:/srv/tests" --entrypoint sh agenticai-code-runner -c "pip install -q pytest && cd /srv && python -m pytest -q tests"`.

### Practice code editor (lesson practice exercises)

Every practice exercise gets an inline "Try it in the editor" button
(`frontend/components/lesson/PracticeCodeRunner.tsx`), backed by
`POST /api/lessons/{lesson_id}/practice/run`. Unlike module-assessment coding questions, a
practice exercise has no fixed function signature or expected value - there's nothing to grade -
so this runs the student's code as a plain script in the same sandbox (`sandbox.run_script` /
`POST /run-script` on the `code_runner` service) and returns whatever it printed or raised.
Nothing is scored, persisted, or fed into progression; the only gate is the same module-locked
check used for viewing/completing the lesson (403 if the module isn't unlocked yet, 503 if the
sandbox is down). It's offered on every exercise regardless of `lesson_type` - even a "reading"
lesson can ask the student to write and run code (e.g. an intro-to-variables lesson) - and it's
opt-in (a collapsed button, not forced open), so a purely conceptual/written exercise can simply
be left alone.

## The signed-in experience

Every authenticated page renders inside one shell (`frontend/components/layout/`):
`DashboardLayout` (`AppLayout.tsx`) composes `AppSidebar` (grouped nav, collapsible, mobile
drawer, role-aware "Admin Console" item), `TopHeader`, `NotificationsPanel`, and `UserProfile`.
The sidebar lists **only routes that exist** (`nav.tsx`); add an item there when a page ships.

The dashboard (`app/dashboard/page.tsx`) loads four independent sources so one failing
endpoint only degrades its own section (each has loading, empty, and retry states):

| Section | Source | Backend |
|---|---|---|
| Stat cards, resume lesson, weak skills, recommendations | `GET /api/dashboard` | `dashboard_service` (real progress, mastery, plan) |
| Course progress, learning-path stepper | `GET /api/courses` | per-course progress from `lesson_progress` |
| Projects | `GET /api/projects` | `projects` + `project_submissions` |
| Recent activity | `GET /api/students/me/activity` | `activity_logs` (lesson/assessment/project events) |

Recommendations refresh automatically after every assessment or project submission
(`planner_service.refresh_plan_after_evidence`), so the loop assess -> update skills ->
recommend closes without the student pressing anything. The notifications bell has no
backend of its own: it derives items from real state (unfinished onboarding/diagnostic and
the planner's current recommendations).

## Troubleshooting

- **AI answers look like pasted lesson excerpts.** That is the no-LLM fallback. Check
  `docker logs agentic_lms_backend | grep ai_engine` for the real reason (bad key, model not
  available, rate limit). With Groq, `LLM_MODEL` may not exist on your account; the client then
  picks the best available model and logs which one. Free-tier Groq limits tokens per minute, so
  several rapid questions can briefly fall back.
- **`.env` edits are ignored by running containers.** Compose reads `.env` when a container is
  *created*: `docker compose up -d --force-recreate backend`. Put the API key alone on its line
  (`LLM_API_KEY=gsk_...`) with no trailing comment.
- **"Session expired".** Access tokens last 60 minutes; the frontend refreshes them silently via
  `POST /api/auth/refresh` (refresh tokens last 14 days) and only sends you to the login page
  when that fails. Set a real `JWT_SECRET` (`python -c "import secrets;print(secrets.token_urlsafe(48))"`)
  outside local development; changing it signs everyone out.
- **Frontend edits don't show up in Docker on Windows/macOS.** The compose file sets
  `WATCHPACK_POLLING=true` for this; without it Next serves stale copies of edited files.
- **Retrieval** is hybrid (Postgres full-text + vector, rank-fused). Without an embedding API key
  the vector half is a weak offline hash, so answer quality leans on the full-text half; set
  `EMBEDDING_API_KEY` (Voyage) for semantic search.

## AI safety notes

- Agent tools are explicit, narrow, and take no filesystem/network/DB/code-exec
  access beyond what's passed to them (`ai_engine/tools/curriculum_tools.py`).
- Every LLM-facing prompt (`ai_engine/prompts/*.py`) frames retrieved lesson content
  and student input as **data, never instructions** — a baseline prompt-injection
  defense, since RAG content and free-text answers are both attacker-influenceable
  surfaces.
- The Project Mentor agent never executes submitted code; it reasons over submission
  notes/URLs as text only.
- Errors never leak stack traces to the client (`app/main.py` exception handlers);
  unhandled exceptions are logged server-side and returned as a generic 500.

## What's intentionally scoped down

Given the size of this brief, a few things were scoped for a working, coherent v1
rather than exhaustively built out — each is a natural next increment:
- Admin CMS has full CRUD for courses and lessons; skills/assessments/projects/users
  have functional list + create/delete (edit forms are a follow-up).
- Course-level assessments (`course_exam`) exist for every course; a dedicated quiz
  per individual module was scoped out in favor of one solid exam per course plus
  the cross-cutting diagnostic — see `content/seed/SCHEMA.md`.
- Refresh-token rotation/revocation endpoints aren't wired up yet — access tokens
  are short-lived (60 min) and refresh tokens are issued but not yet exchanged by a
  dedicated `/api/auth/refresh` route.
