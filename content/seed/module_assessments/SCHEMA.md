# Module assessment seed content

One Python file per module (e.g. `course_01_python_m01_python_fundamentals.py`) exporting
`MODULE_ASSESSMENTS: list[dict]` - one entry per difficulty level (beginner, intermediate, advanced).

**Every assessment has EXACTLY 7 questions: 3 `mcq` + 2 `quiz` + 2 `coding`. The structure never changes
between levels - only the depth of the questions does.** Run
`python content/seed/check_module_assessments.py` before finishing; it must print "All module assessments are valid."

```python
MODULE_ASSESSMENTS = [
    {
        "course_slug": "python-for-ai",
        "module_slug": "python-fundamentals",       # must exist in content/seed/courses/
        "level": "beginner",                        # beginner | intermediate | advanced
        "title": "Python Fundamentals - Beginner Assessment",
        "description": "One sentence on what this checks.",
        "passing_score": 80,                        # percent (always 80)
        "required_coding_questions": 1,             # always 1
        "time_limit_minutes": 45,
        "questions": [ ...exactly 7... ],           # order in the list = display order: 3 mcq, 2 quiz, 2 coding
    },
]
```

## The three question types

Every question: `prompt` (str), `explanation` (str, teaches WHY - shown to the student after a pass),
`difficulty` (`easy` for beginner, `medium` for intermediate, `hard` for advanced - EVERY question in an
assessment uses the level's difficulty), `points` (always 1), `skill_slug` (from content/seed/skills.py).

### mcq (exactly 3) - exactly 4 options, exactly one correct
```python
{"type": "mcq", "prompt": "...", "difficulty": "easy", "points": 1, "skill_slug": "python",
 "options": [{"id": "a", "text": "..."}, {"id": "b", "text": "..."}, {"id": "c", "text": "..."}, {"id": "d", "text": "..."}],
 "correct_answer": {"choice": "c"}, "explanation": "..."}
```

### quiz (exactly 2) - must NOT be a plain MCQ. Pick a different `quiz_format` for each of the two.
* `true_false`  -> `correct_answer: {"choice": "true"}` (or `"false"`); no options needed.
* `multi_select` -> 4-5 options, `correct_answer: {"choices": ["a", "c"]}` (unique ids, at least one; student must pick exactly the right set).
* `scenario`    -> a short realistic scenario in `prompt`, 3-4 options, `correct_answer: {"choice": "b"}`.
* `short_answer`-> one-word/short objective answer, `correct_answer: {"accepted": ["len", "len()"]}` (lower-case; list every
  reasonable spelling - matching ignores case and extra whitespace).
```python
{"type": "quiz", "quiz_format": "multi_select", "prompt": "...", "difficulty": "easy", "points": 1, "skill_slug": "python",
 "options": [{"id": "a", "text": "..."}, ...], "correct_answer": {"choices": ["a", "c"]}, "explanation": "..."}
```

### coding (exactly 2) - a single Python function checked by test cases
```python
{"type": "coding", "prompt": "Problem statement: what to implement, inputs, outputs, edge cases.",
 "difficulty": "easy", "points": 1, "skill_slug": "python", "explanation": "Why the reference solution works.",
 "coding_config": {
     "language": "python",
     "function_name": "count_vowels",
     "starter_code": "def count_vowels(text):\n    # TODO: return how many vowels (a, e, i, o, u) are in text\n    pass\n",
     "test_cases": [
         {"args": ["hello"], "expected": 2, "visible": True},        # >= 1 visible (shown to the student)
         {"args": ["sky"], "expected": 0, "visible": True},
         {"args": [""], "expected": 0, "visible": False},            # >= 1 hidden; at least 3 tests in total
         {"args": ["AEIOU"], "expected": 5, "visible": False},
     ],
     "expected_output": "One sentence describing what the function returns.",
     "time_limit_seconds": 2, "memory_limit_mb": 128,
     "solution": "def count_vowels(text):\n    return sum(1 for c in text.lower() if c in 'aeiou')\n",
 }}
```
Rules for coding questions:
* `args` is the JSON list of positional arguments; `expected` is the JSON return value. Tuples are compared as lists,
  so write expected tuples as lists. No floats that need tolerance (avoid rounding traps), no randomness, no I/O, no printing.
* Standard library only; the function must be pure and deterministic and run in well under a second.
* The starter code must define the function with the right signature and must NOT already pass the tests.
* Hidden tests must cover edge cases a partial solution would miss (empty input, duplicates, boundaries).

## Difficulty - the level changes the depth, never the structure
* **beginner**: MCQ = definitions/fundamentals; quiz = basic concepts + common misconceptions; coding = simple logic, basic syntax/API use.
* **intermediate**: MCQ = practical application, "what does this code do / why does it fail"; quiz = reasoning about realistic
  scenarios; coding = multi-step logic, moderate debugging (e.g. fix behaviour, handle edge cases).
* **advanced**: MCQ = deep conceptual understanding, trade-offs, subtle language behaviour; quiz = architecture/scenario analysis,
  trade-offs; coding = complex multi-step logic, optimisation, real-world AI-flavoured data handling, robust edge cases.
  Advanced questions must need deeper understanding, NOT just be longer.

Base every question on what the module's lessons actually teach (read the module in the course file) and connect to
building AI applications where natural. Wrong options must be plausible, not silly. Do not reuse questions between levels.
