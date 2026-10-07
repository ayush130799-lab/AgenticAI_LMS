"""Validate seeded module assessments. Run from anywhere:

    python content/seed/check_module_assessments.py

For every assessment in content/seed/module_assessments/*.py it:
  1. applies the SAME structure rules the backend enforces (3 MCQ + 2 quiz + 2 coding, ...),
  2. checks the module/skill references exist in the seeded curriculum,
  3. EXECUTES each coding question's reference solution against its test cases (must all pass),
  4. checks the starter code does NOT already pass every test.
Reference solutions are trusted repository content, so they run in-process here; student code never does.
Exit code 1 if anything is wrong.
"""
import glob
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.services import module_assessment_rules as rules  # noqa: E402


def load(path):
    spec = importlib.util.spec_from_file_location(Path(path).stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_function(source: str, name: str, args: list):
    namespace: dict = {}
    exec(compile(source, "<solution>", "exec"), namespace)  # noqa: S102 - trusted repo content
    result = namespace[name](*json.loads(json.dumps(args)))
    return json.loads(json.dumps(result))


def passes_all(source: str, cfg: dict) -> tuple[bool, list[str]]:
    failures = []
    for i, t in enumerate(cfg["test_cases"], 1):
        try:
            actual = run_function(source, cfg["function_name"], t["args"])
        except Exception as exc:  # noqa: BLE001
            failures.append(f"test {i}: raised {type(exc).__name__}: {exc}")
            continue
        if actual != json.loads(json.dumps(t["expected"])):
            failures.append(f"test {i}: args={t['args']} expected={t['expected']!r} got={actual!r}")
    return not failures, failures


def main() -> int:
    skills = {s["slug"] for s in load(ROOT / "content/seed/skills.py").SKILLS}
    curriculum = {}
    for path in glob.glob(str(ROOT / "content/seed/courses/course_*.py")):
        course = load(path).COURSE
        curriculum[course["slug"]] = {m["slug"] for m in course["modules"]}

    problems: list[str] = []
    seen: set = set()
    total = 0
    for path in sorted(glob.glob(str(ROOT / "content/seed/module_assessments/*.py"))):
        for a in load(path).MODULE_ASSESSMENTS:
            total += 1
            key = (a["course_slug"], a["module_slug"], a["level"])
            label = f"{Path(path).name}:{'/'.join(key)}"
            if key in seen:
                problems.append(f"{label}: duplicate (course, module, level)")
            seen.add(key)
            if a["module_slug"] not in curriculum.get(a["course_slug"], set()):
                problems.append(f"{label}: module does not exist in the seeded curriculum")

            specs = []
            for i, q in enumerate(a["questions"], 1):
                spec = dict(q)
                spec["order"] = i
                specs.append(spec)
                if q.get("skill_slug") and q["skill_slug"] not in skills:
                    problems.append(f"{label}: unknown skill_slug {q['skill_slug']!r}")
            passing = a.get("passing_score", rules.DEFAULT_PASSING_PERCENT)
            required = a.get("required_coding_questions", rules.DEFAULT_REQUIRED_CODING)
            problems += [f"{label}: {e}" for e in rules.validate_assessment_structure(
                specs, level=a["level"], passing_percent=passing, required_coding=required)]

            for i, q in enumerate(a["questions"], 1):
                if q.get("type") != "coding" or not isinstance(q.get("coding_config"), dict):
                    continue
                cfg = q["coding_config"]
                try:
                    ok, failures = passes_all(cfg["solution"], cfg)
                    problems += [f"{label} Q{i} reference solution fails: {f}" for f in failures]
                    starter_ok, _ = passes_all(cfg["starter_code"], cfg)
                    if starter_ok:
                        problems.append(f"{label} Q{i}: starter code already passes every test")
                except Exception as exc:  # noqa: BLE001
                    problems.append(f"{label} Q{i}: could not run solution/starter: {type(exc).__name__}: {exc}")

    print(f"Checked {total} module assessments.")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        return 1
    print("All module assessments are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
