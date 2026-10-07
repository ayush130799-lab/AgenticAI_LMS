"""Pure rules for module assessments: structure validation, grading, scoring.

No database or HTTP here. The service layer feeds these functions "question
specs" (plain dicts), so the exact same validation runs for seed content,
admin-created assessments, and rows loaded from the database.

Question spec keys:
    type            "mcq" | "quiz" | "coding"
    quiz_format     (quiz only) "true_false" | "multi_select" | "scenario" | "short_answer"
    prompt, options, correct_answer, explanation, difficulty, points, order
    coding_config   (coding only) language, starter_code, function_name, test_cases,
                    expected_output, time_limit_seconds, memory_limit_mb, solution

Scoring (deterministic, communicated to students): every question is worth its
`points` (default 1). MCQ and quiz questions are all-or-nothing. A coding
question is passed - and earns its points - only when ALL of its test cases pass.
"""
from __future__ import annotations

import keyword
import re

# ---- The fixed standard structure -------------------------------------------------
TOTAL_QUESTIONS = 7
MCQ_COUNT = 3
QUIZ_COUNT = 2
CODING_COUNT = 2
DEFAULT_PASSING_PERCENT = 80.0
DEFAULT_REQUIRED_CODING = 1

LEVELS = ("beginner", "intermediate", "advanced")
LEVEL_RANK = {level: i for i, level in enumerate(LEVELS)}
LEVEL_DIFFICULTY = {"beginner": "easy", "intermediate": "medium", "advanced": "hard"}
QUIZ_FORMATS = ("true_false", "multi_select", "scenario", "short_answer")
CODING_LANGUAGES = ("python",)


class AnswerValidationError(ValueError):
    """A submitted answer is malformed for its question (maps to HTTP 422)."""


# ---- Validation ---------------------------------------------------------------------
def _json_safe(value) -> bool:
    if value is None or isinstance(value, (bool, int, float, str)):
        return True
    if isinstance(value, (list, tuple)):
        return all(_json_safe(v) for v in value)
    if isinstance(value, dict):
        return all(isinstance(k, str) and _json_safe(v) for k, v in value.items())
    return False


def _option_ids(options) -> list[str]:
    return [o.get("id") for o in (options or []) if isinstance(o, dict)]


def _validate_options(options, minimum: int, exact: int | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(options, list):
        return ["options must be a list"]
    ids = _option_ids(options)
    if exact is not None and len(options) != exact:
        errors.append(f"must have exactly {exact} options (has {len(options)})")
    elif len(options) < minimum:
        errors.append(f"must have at least {minimum} options")
    if any(not isinstance(i, str) or not i.strip() for i in ids) or len(ids) != len(options):
        errors.append("every option needs a non-empty string id")
    elif len(set(ids)) != len(ids):
        errors.append("option ids must be unique")
    if any(not isinstance(o, dict) or not str(o.get("text", "")).strip() for o in options):
        errors.append("every option needs non-empty text")
    return errors


def _validate_mcq(q: dict) -> list[str]:
    errors = _validate_options(q.get("options"), 4, exact=4)
    choice = (q.get("correct_answer") or {}).get("choice")
    if choice is None or choice not in _option_ids(q.get("options")):
        errors.append("correct_answer.choice must be the id of exactly one option")
    return errors


def _validate_quiz(q: dict) -> list[str]:
    fmt = q.get("quiz_format")
    answer = q.get("correct_answer") or {}
    if fmt not in QUIZ_FORMATS:
        return [f"quiz_format must be one of {', '.join(QUIZ_FORMATS)}"]
    if fmt == "true_false":
        return [] if answer.get("choice") in ("true", "false") else ["true_false needs correct_answer.choice of 'true' or 'false'"]
    if fmt == "short_answer":
        accepted = answer.get("accepted")
        if not isinstance(accepted, list) or not accepted or any(not isinstance(a, str) or not a.strip() for a in accepted):
            return ["short_answer needs correct_answer.accepted: a non-empty list of accepted answers"]
        return []
    errors = _validate_options(q.get("options"), 3)
    ids = _option_ids(q.get("options"))
    if fmt == "scenario":
        if answer.get("choice") not in ids:
            errors.append("scenario needs correct_answer.choice matching one option id")
    else:  # multi_select
        choices = answer.get("choices")
        if not isinstance(choices, list) or not choices or len(set(choices)) != len(choices) or any(c not in ids for c in choices):
            errors.append("multi_select needs correct_answer.choices: unique ids of the correct options")
    return errors


def _validate_coding(q: dict) -> list[str]:
    cfg = q.get("coding_config")
    if not isinstance(cfg, dict):
        return ["coding questions need coding_config"]
    errors: list[str] = []
    if cfg.get("language") not in CODING_LANGUAGES:
        errors.append(f"language must be one of {', '.join(CODING_LANGUAGES)}")
    name = cfg.get("function_name")
    if not isinstance(name, str) or not name.isidentifier() or keyword.iskeyword(name):
        errors.append("function_name must be a valid identifier")
    starter = cfg.get("starter_code")
    if not isinstance(starter, str) or not starter.strip():
        errors.append("starter_code is required")
    elif isinstance(name, str) and not re.search(rf"def\s+{re.escape(name)}\s*\(", starter):
        errors.append("starter_code must define the function named by function_name")
    if not isinstance(cfg.get("solution"), str) or not cfg["solution"].strip():
        errors.append("a reference solution is required")
    if not isinstance(cfg.get("expected_output"), str) or not cfg["expected_output"].strip():
        errors.append("expected_output (a description of the expected result) is required")
    tests = cfg.get("test_cases")
    if not isinstance(tests, list) or len(tests) < 3:
        errors.append("at least 3 test_cases are required")
    else:
        for i, t in enumerate(tests, 1):
            if not isinstance(t, dict) or not isinstance(t.get("args"), list) or "expected" not in t or not _json_safe(t):
                errors.append(f"test case {i} needs a JSON 'args' list and an 'expected' value")
        visible = sum(1 for t in tests if isinstance(t, dict) and t.get("visible"))
        if visible < 1 or visible == len(tests):
            errors.append("test_cases need at least one visible and at least one hidden case")
    limit = cfg.get("time_limit_seconds", 2)
    if not isinstance(limit, (int, float)) or not 0 < limit <= 10:
        errors.append("time_limit_seconds must be between 0 and 10")
    memory = cfg.get("memory_limit_mb", 128)
    if not isinstance(memory, (int, float)) or not 32 <= memory <= 512:
        errors.append("memory_limit_mb must be between 32 and 512")
    return errors


def validate_assessment_structure(
    questions: list[dict], *, level: str | None = None, passing_percent: float | None = None, required_coding: int | None = None
) -> list[str]:
    """Return every reason this set of questions can't be a standard module assessment (empty list = valid)."""
    errors: list[str] = []
    if len(questions) != TOTAL_QUESTIONS:
        errors.append(f"must have exactly {TOTAL_QUESTIONS} questions (has {len(questions)})")
    counts = {t: sum(1 for q in questions if q.get("type") == t) for t in ("mcq", "quiz", "coding")}
    expected = {"mcq": MCQ_COUNT, "quiz": QUIZ_COUNT, "coding": CODING_COUNT}
    for t, want in expected.items():
        if counts[t] != want:
            errors.append(f"must have exactly {want} {t} questions (has {counts[t]})")
    unknown = [q.get("type") for q in questions if q.get("type") not in expected]
    if unknown:
        errors.append(f"unknown question types: {sorted(set(map(str, unknown)))}")

    if level is not None and level not in LEVELS:
        errors.append(f"level must be one of {', '.join(LEVELS)}")
    if passing_percent is not None and not 0 < passing_percent <= 100:
        errors.append("passing score must be a percentage between 0 and 100")
    if required_coding is not None and not 0 <= required_coding <= CODING_COUNT:
        errors.append(f"required coding questions must be between 0 and {CODING_COUNT}")

    orders = [q.get("order") for q in questions]
    if any(not isinstance(o, int) or isinstance(o, bool) for o in orders) or len(set(orders)) != len(orders):
        errors.append("every question needs a unique integer order")

    for i, q in enumerate(questions, 1):
        label = f"question {i} ({q.get('type')})"
        if not str(q.get("prompt") or "").strip():
            errors.append(f"{label}: prompt is required")
        points = q.get("points")
        if not isinstance(points, (int, float)) or isinstance(points, bool) or points <= 0:
            errors.append(f"{label}: points must be a positive number")
        difficulty = q.get("difficulty")
        if difficulty not in LEVEL_DIFFICULTY.values():
            errors.append(f"{label}: difficulty must be easy, medium or hard")
        elif level in LEVEL_DIFFICULTY and difficulty != LEVEL_DIFFICULTY[level]:
            errors.append(f"{label}: difficulty '{difficulty}' does not match the {level} level ('{LEVEL_DIFFICULTY[level]}')")
        checker = {"mcq": _validate_mcq, "quiz": _validate_quiz, "coding": _validate_coding}.get(q.get("type"))
        if checker:
            errors.extend(f"{label}: {e}" for e in checker(q))
    return errors


# ---- Grading ------------------------------------------------------------------------
def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _require_key(answer, key: str, kind: str):
    """None or an empty object = unanswered. A non-empty answer must carry the key its question type expects."""
    if answer is None:
        return None
    if not isinstance(answer, dict):
        raise AnswerValidationError(f"{kind} answer must be an object with a '{key}' field")
    if not answer:
        return None
    if key not in answer:
        raise AnswerValidationError(f"{kind} answer must include '{key}'")
    return answer[key]


def _choice(answer, question_type: str) -> str | None:
    value = _require_key(answer, "choice", question_type)
    if value is None:
        return None
    if not isinstance(value, str):
        raise AnswerValidationError(f"{question_type} answer 'choice' must be a string")
    return value


def grade_choice_question(spec: dict, answer) -> bool:
    """MCQ, true/false and scenario questions. None/blank = unanswered (incorrect); malformed = error."""
    valid_ids = {"true", "false"} if spec.get("quiz_format") == "true_false" else set(_option_ids(spec.get("options")))
    choice = _choice(answer, spec.get("quiz_format") or spec["type"])
    if choice is None:
        return False
    if choice not in valid_ids:
        raise AnswerValidationError(f"'{choice}' is not one of the options for this question")
    return choice == spec["correct_answer"]["choice"]


def grade_multi_select(spec: dict, answer) -> bool:
    choices = _require_key(answer, "choices", "multi_select")
    if choices is None:
        return False
    if not isinstance(choices, list) or any(not isinstance(c, str) for c in choices):
        raise AnswerValidationError("multi_select answer 'choices' must be a list of option ids")
    valid = set(_option_ids(spec.get("options")))
    unknown = [c for c in choices if c not in valid]
    if unknown:
        raise AnswerValidationError(f"unknown option ids: {unknown}")
    return set(choices) == set(spec["correct_answer"]["choices"])


def grade_short_answer(spec: dict, answer) -> bool:
    text = _require_key(answer, "text", "short_answer")
    if text is None:
        return False
    if not isinstance(text, str):
        raise AnswerValidationError("short_answer answer 'text' must be a string")
    if len(text) > 500:
        raise AnswerValidationError("short_answer answer is too long")
    return _norm(text) in {_norm(a) for a in spec["correct_answer"]["accepted"]}


def grade_objective_question(spec: dict, answer) -> bool:
    """Grade an MCQ or quiz question. Raises AnswerValidationError for malformed answers."""
    if spec["type"] == "mcq":
        return grade_choice_question(spec, answer)
    fmt = spec.get("quiz_format")
    if fmt in ("true_false", "scenario"):
        return grade_choice_question(spec, answer)
    if fmt == "multi_select":
        return grade_multi_select(spec, answer)
    if fmt == "short_answer":
        return grade_short_answer(spec, answer)
    raise AnswerValidationError(f"unsupported quiz format: {fmt}")


def validate_code_answer(answer) -> str | None:
    """Return the submitted source code (None when unanswered); reject malformed payloads."""
    code = _require_key(answer, "code", "coding")
    if code is None:
        return None
    if not isinstance(code, str):
        raise AnswerValidationError("coding answer 'code' must be a string")
    if len(code) > 20_000:
        raise AnswerValidationError("code is too long (limit 20,000 characters)")
    return code if code.strip() else None


# ---- Scoring ------------------------------------------------------------------------
def compute_result(outcomes: list[dict], *, passing_percent: float, required_coding: int) -> dict:
    """Aggregate per-question outcomes into the attempt result. The single source of pass/fail.

    Each outcome: {"type", "points", "correct": bool}
    """
    total = sum(o["points"] for o in outcomes)
    earned = sum(o["points"] for o in outcomes if o["correct"])
    by_type: dict[str, dict] = {}
    for t in ("mcq", "quiz", "coding"):
        group = [o for o in outcomes if o["type"] == t]
        by_type[t] = {
            "correct": sum(1 for o in group if o["correct"]),
            "total": len(group),
            "points_earned": sum(o["points"] for o in group if o["correct"]),
            "points_total": sum(o["points"] for o in group),
        }
    percentage = (earned / total * 100.0) if total else 0.0
    coding_passed = by_type["coding"]["correct"]
    score_ok = total > 0 and earned * 100.0 >= passing_percent * total - 1e-9
    coding_ok = coding_passed >= required_coding
    return {
        "points_earned": earned,
        "points_total": total,
        "percentage": round(percentage, 1),
        "by_type": by_type,
        "questions_correct": sum(1 for o in outcomes if o["correct"]),
        "questions_total": len(outcomes),
        "passing_percent": passing_percent,
        "required_coding": required_coding,
        "coding_passed": coding_passed,
        "score_requirement_met": score_ok,
        "coding_requirement_met": coding_ok,
        "passed": bool(score_ok and coding_ok),
    }
