"""Shared helpers for module-assessment tests."""
import copy
import importlib.util
import json
import uuid
from pathlib import Path

from app.services.code_execution import CodeRunner

REPO_ROOT = Path(__file__).resolve().parents[2]
SEED_DIR = REPO_ROOT / "content" / "seed" / "module_assessments"


def load_seed_assessments() -> list[dict]:
    """Every seeded module assessment (real content, so the tests also guard the seed files)."""
    out = []
    for path in sorted(SEED_DIR.glob("*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        out.extend(module.MODULE_ASSESSMENTS)
    return out


def seed_assessment(level: str = "beginner", module_slug: str = "python-fundamentals") -> dict:
    return copy.deepcopy(next(a for a in load_seed_assessments() if a["level"] == level and a["module_slug"] == module_slug))


class FakeCodeRunner(CodeRunner):
    """Runs TRUSTED test/reference code in-process. Only for tests - the real path is the sandbox service."""

    def __init__(self) -> None:
        self.calls = 0

    async def run(self, *, language, code, function_name, tests, time_limit, memory_mb):
        self.calls += 1
        namespace: dict = {}
        load_error = None
        try:
            exec(compile(code, "<student>", "exec"), namespace)  # noqa: S102
        except Exception as exc:  # noqa: BLE001
            load_error = f"{type(exc).__name__}: {exc}"
        results = []
        for t in tests:
            result = {"id": t["id"], "visible": t["visible"], "duration_ms": 1}
            try:
                if load_error:
                    raise RuntimeError(load_error)
                actual = json.loads(json.dumps(namespace[function_name](*json.loads(json.dumps(t["args"])))))
                passed = json.dumps(actual, sort_keys=True) == json.dumps(t["expected"], sort_keys=True)
                result.update(status="passed" if passed else "failed", passed=passed)
                if t["visible"]:
                    result.update(args=t["args"], expected=t["expected"], actual=actual)
            except Exception as exc:  # noqa: BLE001
                result.update(status="error", passed=False, error=str(exc)[:200])
            results.append(result)
        return results

    async def run_script(self, *, language, code, time_limit, memory_mb):
        self.calls += 1
        import io
        import contextlib

        out, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                exec(compile(code, "<practice>", "exec"), {})  # noqa: S102
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "stdout": out.getvalue(), "stderr": err.getvalue(), "error": f"{type(exc).__name__}: {exc}", "duration_ms": 1}
        return {"status": "ok", "stdout": out.getvalue(), "stderr": err.getvalue(), "error": None, "duration_ms": 1}


def answers_for(data: dict, view_questions: list[dict], *, wrong: set[int] = frozenset()) -> dict:
    """Correct answers for every question, except the 0-based indexes in `wrong`, which get a wrong answer."""
    answers = {}
    for i, (item, view) in enumerate(zip(data["questions"], sorted(view_questions, key=lambda q: q["order"]))):
        qid = str(view["id"])
        is_wrong = i in wrong
        if item["type"] == "coding":
            answers[qid] = {"code": item["coding_config"]["starter_code"] if is_wrong else item["coding_config"]["solution"]}
        elif item["type"] == "mcq" or item["quiz_format"] in ("true_false", "scenario"):
            correct = item["correct_answer"]["choice"]
            if is_wrong:
                options = [o["id"] for o in view["options"] if o["id"] != correct]
                answers[qid] = {"choice": options[0]}
            else:
                answers[qid] = {"choice": correct}
        elif item["quiz_format"] == "multi_select":
            correct = item["correct_answer"]["choices"]
            wrong_set = [o["id"] for o in view["options"] if o["id"] not in correct][:1]
            answers[qid] = {"choices": wrong_set if is_wrong else correct}
        else:  # short_answer
            answers[qid] = {"text": "definitely-not-the-answer" if is_wrong else item["correct_answer"]["accepted"][0]}
    return answers


def unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"
