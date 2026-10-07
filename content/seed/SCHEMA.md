# Seed content schema

All files below are plain Python modules (not JSON) so they can contain
multi-line markdown strings comfortably. They are imported by
`backend/app/db/seed_runner.py`, which upserts them into Postgres. Nothing in
here talks to the database directly — these are pure data files.

## Skills

Already authored at `content/seed/skills.py` as `SKILLS: list[dict]`. Course
content must reference these slugs only — do not invent new ones.

## Courses

One file per course at `content/seed/courses/course_NN_<slug>.py`, each
exporting a module-level `COURSE: dict`:

```python
COURSE = {
    "slug": "python-for-ai",
    "title": "Python for AI",
    "subtitle": "Short one-line hook",
    "description": "2-4 sentence real description of the course.",
    "learning_outcomes": ["Outcome 1", "Outcome 2", "..."],
    "order_index": 1,             # 1-14, matches course number in the brief
    "estimated_hours": 18,
    "level": "beginner",          # beginner | intermediate | advanced
    "icon": "python",             # short icon keyword, frontend maps it
    "modules": [
        {
            "slug": "python-fundamentals",
            "title": "Python Fundamentals",
            "description": "What this module covers and why it matters.",
            "order_index": 1,
            "estimated_hours": 2.5,
            "lessons": [
                {
                    "slug": "variables-and-types",
                    "title": "Variables, Types, and Expressions",
                    "description": "One or two sentence summary shown in lesson lists.",
                    "lesson_type": "reading",   # reading | coding | video | project | quiz
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain X",
                        "Apply Y",
                        "Distinguish Z from W",
                    ],
                    "content_markdown": """
## Why this matters
...full real lesson content, 400-800 words, with ## subheadings,
prose paragraphs, and fenced ```python code blocks where relevant...
                    """,
                    "examples": [
                        {"title": "Example: ...", "code": "x = 1\n...", "explanation": "Walks through what happens and why."}
                    ],
                    "practice_exercises": [
                        {"prompt": "Write a function that ...", "difficulty": "easy", "hint": "Think about ..."}
                    ],
                    "resources": [
                        {"title": "Official docs: ...", "url": "https://docs.python.org/3/...", "resource_type": "docs"}
                    ],
                    "skills": [
                        {"slug": "python", "weight": 1.0}
                    ],
                },
                # 2-4 lessons per module, each this fully fleshed out
            ],
        },
        # one entry per module listed for this course in the master brief
    ],
}
```

Rules:
- No lesson titled "Lesson 1" / module titled "Module 1". Every title is a
  real, specific topic name.
- `content_markdown` must be genuine teaching content: explain the concept,
  show at least one code or worked example inline, and connect to why it
  matters for building agentic AI systems. 400-800 words is the target size;
  it's fine to run longer for meaty topics (e.g. transformers, LangGraph
  state).
- Every lesson needs 1-3 `examples`, 2-3 `practice_exercises`, and at least
  one `resources` entry.
- `skills` maps the lesson to 1-3 slugs from `content/seed/skills.py` with a
  weight from 0.1 (minor touch) to 1.0 (core skill of the lesson).

## Course-level assessment

Each course file also exports `COURSE_EXAM: dict`:

```python
COURSE_EXAM = {
    "title": "Python for AI: Course Assessment",
    "description": "Checks readiness to move into AI/ML Foundations.",
    "assessment_type": "course_exam",
    "passing_score": 0.7,
    "time_limit_minutes": 30,
    "questions": [
        {
            "question_type": "mcq",              # mcq | multi_select | short_answer | coding | scenario
            "prompt": "Full question text.",
            "options": [{"id": "a", "text": "..."}, {"id": "b", "text": "..."}],  # [] for short_answer/coding
            "correct_answer": {"choice": "a"},   # shape depends on question_type, see below
            "explanation": "Why this is correct, shown after grading.",
            "difficulty": "easy",                 # easy | medium | hard
            "points": 1.0,
            "skill_slug": "python",
        },
        # 10-15 questions total, spread across the course's modules/skills
    ],
}
```

`correct_answer` shapes:
- `mcq`: `{"choice": "<option id>"}`
- `multi_select`: `{"choices": ["<id>", "<id>"]}`
- `short_answer`: `{"expected": "short reference answer", "keywords": ["kw1", "kw2"]}` (graded by keyword/LLM match)
- `coding`: `{"expected_behavior": "description of correct output/behavior", "sample_solution": "code"}`
- `scenario`: `{"expected": "reference answer describing the right judgment call"}`

## Projects (Course 14)

One file: `content/seed/projects.py`, exporting `PROJECTS: list[dict]`:

```python
PROJECTS = [
    {
        "slug": "rag-knowledge-assistant",
        "title": "RAG Knowledge Assistant",
        "overview": "...",
        "objective": "...",
        "prerequisites": ["Completed RAG course", "..."],
        "learning_outcomes": ["...", "..."],
        "requirements": ["...", "..."],
        "architecture": "Prose + simple ascii diagram of the intended architecture.",
        "milestones": [{"title": "...", "description": "..."}],
        "tasks": [{"title": "...", "description": "..."}],
        "expected_output": "...",
        "evaluation_criteria": [{"criterion": "...", "weight": 0.2}],
        "resources": [{"title": "...", "url": "...", "resource_type": "docs"}],
        "order_index": 1,
        "estimated_hours": 10,
        "difficulty": "intermediate",
        "skills": [{"slug": "rag", "weight": 1.0}, {"slug": "vector-db", "weight": 0.6}],
    },
    # all 7 projects from the brief
]
```

## Diagnostic assessment

Authored separately by the lead engineer at `content/seed/diagnostic.py` —
content agents do not need to touch this file.
