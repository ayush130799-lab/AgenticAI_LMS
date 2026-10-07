"""Module assessments (beginner, intermediate, advanced) for python-for-ai / python-fundamentals."""


def _o(*texts):
    return [{"id": "abcde"[i], "text": t} for i, t in enumerate(texts)]


def _mcq(prompt, options, answer, explanation, difficulty):
    return {"type": "mcq", "prompt": prompt, "difficulty": difficulty, "points": 1, "skill_slug": "python",
            "options": _o(*options), "correct_answer": {"choice": answer}, "explanation": explanation}


def _quiz(fmt, prompt, explanation, difficulty, correct, options=None):
    q = {"type": "quiz", "quiz_format": fmt, "prompt": prompt, "difficulty": difficulty, "points": 1,
         "skill_slug": "python", "correct_answer": correct, "explanation": explanation}
    if options:
        q["options"] = _o(*options)
    return q


def _coding(prompt, difficulty, explanation, fn, starter, tests, expected_output, solution):
    return {"type": "coding", "prompt": prompt, "difficulty": difficulty, "points": 1, "skill_slug": "python",
            "explanation": explanation,
            "coding_config": {
                "language": "python", "function_name": fn, "starter_code": starter,
                "test_cases": [{"args": a, "expected": e, "visible": v} for a, e, v in tests],
                "expected_output": expected_output, "time_limit_seconds": 2, "memory_limit_mb": 128,
                "solution": solution}}


def _assessment(level, title, description, questions):
    return {"course_slug": "python-for-ai", "module_slug": "python-fundamentals", "level": level,
            "title": title, "description": description, "passing_score": 80,
            "required_coding_questions": 1, "time_limit_minutes": 45, "questions": questions}


_B, _I, _A = "easy", "medium", "hard"

BEGINNER = _assessment(
    "beginner", "Python Fundamentals - Beginner Assessment",
    "Checks core built-in types, basic expressions, and the meaning of break, continue and loop else.",
    [
        _mcq("You write `temperature = 0.7`. Which built-in type does Python assign to `temperature`?",
             ["int", "float", "str", "bool"], "b",
             "A number with a decimal point is a float. Python infers the type from the value, which is why values like temperature or top_p are floats.", _B),
        _mcq("Which line raises a TypeError because Python will not silently mix types?",
             ["`max_tokens = 1024 + 1`", "`ok = 5 > 3`", "`msg = \"tokens: \" + 120`", "`msg = \"tokens: \" + str(120)`"], "c",
             "Adding a str and an int is an error; convert explicitly with str() or use an f-string. Options a, b and d are all valid.", _B),
        _mcq("Which statement skips the rest of the current loop iteration and moves straight to the next one?",
             ["pass", "break", "return", "continue"], "d",
             "continue jumps to the next iteration. break exits the loop entirely, and pass does nothing at all.", _B),
        _quiz("true_false",
              "True or false: a loop's `else` clause runs only when the loop finishes without hitting `break`.",
              "The else block on a for/while loop is skipped if break is executed. That makes it handy for 'searched everything and found nothing' logic.",
              _B, {"choice": "true"}),
        _quiz("short_answer",
              "Which built-in value does Python use to represent 'no value yet', often seen as a default argument (for example `system_prompt = ...`)? Answer with the value name.",
              "None is the single value of type NoneType and signals the absence of a value.",
              _B, {"accepted": ["none", "None".lower()]}),
        _coding(
            "Write `classify_status(code)` that takes an HTTP status code (int) and returns 'ok' for 200, 'retry' for 429 or any code >= 500, and 'skip' for everything else.",
            _B, "An if/elif/else chain checks the discrete cases in order; 429 and >= 500 share the 'retry' branch.",
            "classify_status",
            "def classify_status(code):\n    # TODO: return 'ok', 'retry' or 'skip'\n    pass\n",
            [([200], "ok", True), ([429], "retry", True), ([404], "skip", True),
             ([500], "retry", False), ([503], "retry", False), ([301], "skip", False), ([199], "skip", False)],
            "One of the strings 'ok', 'retry' or 'skip'.",
            "def classify_status(code):\n    if code == 200:\n        return 'ok'\n    elif code == 429 or code >= 500:\n        return 'retry'\n    else:\n        return 'skip'\n"),
        _coding(
            "Write `total_tokens(counts)` that receives a list whose items are ints or None (None means 'count unknown') and returns the sum of the ints, ignoring the None entries. An empty list gives 0.",
            _B, "Loop over the values, skipping None with a condition (or continue), and accumulate the rest.",
            "total_tokens",
            "def total_tokens(counts):\n    # TODO: sum the ints, ignore None\n    pass\n",
            [([[10, None, 5]], 15, True), ([[1, 2, 3]], 6, True), ([[]], 0, False),
             ([[None, None]], 0, False), ([[0, 3]], 3, False)],
            "The integer sum of all non-None values.",
            "def total_tokens(counts):\n    total = 0\n    for c in counts:\n        if c is None:\n            continue\n        total += c\n    return total\n"),
    ])

INTERMEDIATE = _assessment(
    "intermediate", "Python Fundamentals - Intermediate Assessment",
    "Checks reading and debugging loops, float and comparison behaviour, and validating loosely typed parameters.",
    [
        _mcq("What does this code print?\n\n```python\ntotal = 0\nfor n in [1, 2, 3, 4]:\n    if n % 2 == 0:\n        continue\n    total += n\nprint(total)\n```",
             ["4", "6", "10", "2"], "a",
             "Even numbers hit continue and are skipped, so only 1 and 3 are added: 4.", _I),
        _mcq("A retry loop is meant to stop after 3 attempts but the program hangs. Why?\n\n```python\nattempt = 0\nwhile attempt < 3:\n    if attempt == 1:\n        continue\n    attempt += 1\n```",
             ["`continue` ends the whole while loop early, so attempt never reaches 3", "`attempt < 3` is never true at the start", "The loop is fine; it just takes long to finish", "When attempt is 1, `continue` skips `attempt += 1`, so attempt stays 1 forever"], "d",
             "continue jumps back to the condition check without running the increment. attempt is stuck at 1 and the loop never ends. Increment before the continue, or restructure the loop.", _I),
        _mcq("What does `0.1 + 0.2 == 0.3` evaluate to in Python, and what is the practical lesson?",
             ["True, because Python rounds to 15 digits", "False, because binary floats cannot represent 0.1 and 0.2 exactly; compare with a tolerance", "A TypeError, because floats cannot be compared with ==", "False, because 0.1 + 0.2 is converted to an int first"], "b",
             "The sum is 0.30000000000000004. When thresholding computed floats such as similarity scores, use a tolerance (for example math.isclose) or comparison operators rather than ==.", _I),
        _quiz("scenario",
              "Your agent calls a flaky API up to 3 times and must log 'all retries failed' only when no attempt succeeded:\n\n```python\nfor attempt in range(3):\n    if call_api():\n        break\n```\n\nWhat is the cleanest way to run the logging code only when every attempt failed?",
              "A for loop's else clause runs only if the loop was never ended by break. Success breaks out, so the else block (all attempts failed) is skipped. A flag would work too, but the loop else needs no extra state; option d logs on success as well.",
              _I, {"choice": "c"},
              ["Put the log call after the loop with no condition", "Put the log call inside the `if`, before break", "Add an `else:` clause to the for loop and log inside it", "Wrap the loop in `while True:` and log after it"]),
        _quiz("multi_select",
              "Select ALL expressions that evaluate to True.",
              "1 < 2 < 3 is a valid chained comparison (True); 1 == 1.0 is True because numeric values compare equal across int/float; 2 ** 3 == 6 + 2 is 8 == 8. A str never equals an int, and not (5 >= 5) is False.",
              _I, {"choices": ["a", "c", "d"]},
              ["`1 < 2 < 3`", "`\"1\" == 1`", "`1 == 1.0`", "`2 ** 3 == 6 + 2`", "`not (5 >= 5)`"]),
        _coding(
            "Write `validate_params(temperature, max_tokens)` returning a list of error strings (empty if all is valid), in this order: temperature first, then max_tokens.\n"
            "- temperature must be an int or float (bool does NOT count), else 'temperature must be a number'; if it is a number but outside 0 <= t <= 1, 'temperature out of range'.\n"
            "- max_tokens must be an int (bool does NOT count), else 'max_tokens must be an int'; if an int but outside 1 <= n <= 8192, 'max_tokens out of range'.\n"
            "Each parameter contributes at most one message.",
            _I, "bool is a subclass of int, so isinstance(True, int) is True; it must be excluded explicitly. Check the type first, then the range.",
            "validate_params",
            "def validate_params(temperature, max_tokens):\n    # TODO: return a list of error messages\n    pass\n",
            [([0.7, 100], [], True), ([1.5, 100], ["temperature out of range"], True),
             ([0.5, 0], ["max_tokens out of range"], True),
             (["hot", 10], ["temperature must be a number"], False),
             ([True, 100], ["temperature must be a number"], False),
             ([0.5, 3.5], ["max_tokens must be an int"], False),
             ([2, False], ["temperature out of range", "max_tokens must be an int"], False),
             ([0, 8192], [], False), ([1, 1], [], False)],
            "A list of error message strings, empty when both parameters are valid.",
            "def validate_params(temperature, max_tokens):\n    errors = []\n    if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):\n        errors.append('temperature must be a number')\n    elif not 0 <= temperature <= 1:\n        errors.append('temperature out of range')\n    if isinstance(max_tokens, bool) or not isinstance(max_tokens, int):\n        errors.append('max_tokens must be an int')\n    elif not 1 <= max_tokens <= 8192:\n        errors.append('max_tokens out of range')\n    return errors\n"),
        _coding(
            "Write `total_backoff(failures, base, cap)`: an API call failed `failures` times in a row, and before each retry you wait an exponentially growing delay: base, base*2, base*4, ... but never more than `cap` seconds. Return the total seconds waited across all `failures` waits (all ints). 0 failures means 0 seconds.",
            _I, "Loop `failures` times, computing min(base * 2**i, cap) for each wait (or double a delay variable and cap it), and add it to a running total.",
            "total_backoff",
            "def total_backoff(failures, base, cap):\n    # TODO: sum the capped exponential delays\n    pass\n",
            [([3, 1, 10], 7, True), ([5, 1, 10], 25, True), ([0, 1, 10], 0, False),
             ([4, 3, 5], 18, False), ([1, 20, 10], 10, False)],
            "The integer total of all waits.",
            "def total_backoff(failures, base, cap):\n    total = 0\n    delay = base\n    for _ in range(failures):\n        total += min(delay, cap)\n        delay *= 2\n    return total\n"),
    ])

ADVANCED = _assessment(
    "advanced", "Python Fundamentals - Advanced Assessment",
    "Checks subtle expression and loop semantics, robust handling of loosely typed LLM inputs, and safe loop design for agents.",
    [
        _mcq("An API wrapper does `temperature = temperature or 0.7` to apply a default. A caller passes `temperature=0` intending deterministic output. What happens, and what is the correct fix?",
             ["It keeps 0, because `or` only replaces None", "It raises a TypeError, because 0 is an int and 0.7 is a float", "It silently becomes 0.7 because 0 is falsy; use `if temperature is None: temperature = 0.7`", "It becomes 0.7 only if the module is running in debug mode"], "c",
             "`or` returns the first truthy operand, and 0, 0.0, '' and empty containers are falsy. Valid values get overwritten. Use an explicit `is None` check when None is the only 'missing' sentinel.", _A),
        _mcq("A tool-call validator must reject `max_tokens=True` coming from untrusted JSON. Which check correctly accepts real ints but rejects booleans?",
             ["`type(x) is int`", "`isinstance(x, int)`", "`x == int(x)`", "`x in (0, 1) or x > 1`"], "a",
             "bool is a subclass of int, so isinstance(True, int) is True and `True == int(True)` too. `type(x) is int` compares the exact type (as would `isinstance(x, int) and not isinstance(x, bool)`). The trade-off is that it also rejects int subclasses.", _A),
        _mcq("What does this code print?\n\n```python\nresult = []\nfor i in range(4):\n    if i == 1:\n        continue\n    if i == 3:\n        break\n    result.append(i)\nelse:\n    result.append('end')\nprint(result)\n```",
             ["[0, 2, 'end']", "[0, 1, 2]", "[0, 2, 3]", "[0, 2]"], "d",
             "i=1 is skipped by continue, i=0 and 2 are appended, and i=3 hits break, so the else clause (which needs a loop that ended without break) never runs.", _A),
        _quiz("scenario",
              "You are writing the outer loop of an LLM agent that keeps calling tools until the model returns a final answer. A colleague proposes `while True:` with a `break` when the answer arrives. In production the model occasionally loops on the same tool call forever. Which design best handles this?",
              "An unbounded loop ties cost and latency to model behaviour. A bounded for loop with else (or a step counter) guarantees termination and gives one explicit place to handle exhaustion. Retrying identical calls or ignoring the cap does not remove the failure mode.",
              _A, {"choice": "b"},
              ["Keep `while True:` but sleep between iterations so the loop uses fewer resources", "Use `for step in range(MAX_STEPS)` with `break` on a final answer, and an `else` branch that raises or returns a clear 'step limit reached' error", "Keep `while True:` and rely on the API's token limit to eventually stop it", "Catch every exception inside the loop and `continue` so the agent never crashes"]),
        _quiz("true_false",
              "True or false: in the chained comparison `a < f(x) < b`, the middle expression `f(x)` is evaluated twice, once for each comparison.",
              "False. Chained comparisons evaluate the middle operand once (and short-circuit: if `a < f(x)` is false, `b` is not evaluated). That is a real difference from writing `a < f(x) and f(x) < b`, which calls f twice.",
              _A, {"choice": "false"}),
        _coding(
            "Tool-call arguments from an LLM arrive as loosely typed JSON. Write `parse_llm_args(raw)` taking a dict and returning a NEW dict with only valid, normalized entries. Ignore unknown keys and omit invalid ones (never raise):\n"
            "- 'max_tokens': an int (bool is NOT valid) or a str that `int(s.strip())` can parse; must be >= 1. Result is an int.\n"
            "- 'temperature': an int/float (bool NOT valid) or a str that `float(s.strip())` can parse; must satisfy 0 <= t <= 1 (so NaN is rejected). Result is a float.\n"
            "- 'stream': a bool, or a str that equals 'true' or 'false' ignoring case and surrounding spaces. Result is a bool.",
            _A, "Each field needs an exact-type check (bool is an int!), a safe conversion for strings using try/except, then a range check. NaN fails `0 <= t <= 1` because every comparison with NaN is False.",
            "parse_llm_args",
            "def parse_llm_args(raw):\n    # TODO: return a dict of cleaned, valid arguments\n    pass\n",
            [([{"max_tokens": "512", "temperature": "0.5", "stream": "True"}], {"max_tokens": 512, "temperature": 0.5, "stream": True}, True),
             ([{"max_tokens": 100, "temperature": 1, "stream": False, "extra": 1}], {"max_tokens": 100, "temperature": 1.0, "stream": False}, True),
             ([{"max_tokens": True, "temperature": True, "stream": "yes"}], {}, False),
             ([{"max_tokens": "0", "temperature": "1.5"}], {}, False),
             ([{"max_tokens": " 42 ", "temperature": " 0 ", "stream": " FALSE "}], {"max_tokens": 42, "temperature": 0.0, "stream": False}, False),
             ([{"max_tokens": 3.0, "temperature": "nan"}], {}, False),
             ([{"max_tokens": "abc", "temperature": None, "stream": 1}], {}, False),
             ([{}], {}, False)],
            "A new dict containing only the valid, normalized max_tokens, temperature and stream values.",
            "def parse_llm_args(raw):\n    out = {}\n    mt = raw.get('max_tokens')\n    if isinstance(mt, str):\n        try:\n            mt = int(mt.strip())\n        except ValueError:\n            mt = None\n    if isinstance(mt, int) and not isinstance(mt, bool) and mt >= 1:\n        out['max_tokens'] = mt\n    t = raw.get('temperature')\n    if isinstance(t, str):\n        try:\n            t = float(t.strip())\n        except ValueError:\n            t = None\n    if isinstance(t, (int, float)) and not isinstance(t, bool) and 0 <= t <= 1:\n        out['temperature'] = float(t)\n    s = raw.get('stream')\n    if isinstance(s, str) and s.strip().lower() in ('true', 'false'):\n        s = s.strip().lower() == 'true'\n    if isinstance(s, bool):\n        out['stream'] = s\n    return out\n"),
        _coding(
            "Write `trim_history(messages, budget)` to fit a conversation into a token budget. `messages` is a list of [role, tokens] pairs in chronological order. Rules:\n"
            "- If the first message has role 'system', it is always kept and its tokens count against the budget; if it alone exceeds the budget, return [].\n"
            "- From the remaining messages keep the most recent CONTIGUOUS run that fits: walk backwards from the newest message and stop at the first one that does not fit (do not skip it to include older, smaller ones).\n"
            "- Return the kept messages in their original order.",
            _A, "Reserve the system message first, then scan from the end and break at the first message that overflows. Skipping over a large message to include older ones would create a conversation with a hole in it.",
            "trim_history",
            "def trim_history(messages, budget):\n    # TODO: keep the system message plus the newest messages that fit\n    pass\n",
            [([[["system", 10], ["user", 20], ["assistant", 30], ["user", 15]], 60], [["system", 10], ["assistant", 30], ["user", 15]], True),
             ([[["user", 5], ["assistant", 5]], 100], [["user", 5], ["assistant", 5]], True),
             ([[["system", 10], ["user", 5]], 8], [], False),
             ([[["user", 1], ["assistant", 50], ["user", 2]], 10], [["user", 2]], False),
             ([[], 10], [], False),
             ([[["system", 10], ["user", 5]], 10], [["system", 10]], False),
             ([[["user", 3], ["assistant", 4], ["user", 3]], 7], [["assistant", 4], ["user", 3]], False)],
            "The list of kept [role, tokens] messages in original order.",
            "def trim_history(messages, budget):\n    head = []\n    rest = messages\n    if messages and messages[0][0] == 'system':\n        head = [messages[0]]\n        rest = messages[1:]\n        budget -= messages[0][1]\n        if budget < 0:\n            return []\n    kept = []\n    for m in reversed(rest):\n        if m[1] > budget:\n            break\n        budget -= m[1]\n        kept.append(m)\n    return head + kept[::-1]\n"),
    ])

MODULE_ASSESSMENTS = [BEGINNER, INTERMEDIATE, ADVANCED]
