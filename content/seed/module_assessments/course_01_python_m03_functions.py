"""Module assessments (beginner, intermediate, advanced) for python-for-ai / functions."""


def _opts(*texts):
    return [{"id": "abcde"[i], "text": t} for i, t in enumerate(texts)]


def _mcq(prompt, options, answer, explanation, difficulty):
    return {"type": "mcq", "prompt": prompt, "difficulty": difficulty, "points": 1, "skill_slug": "python",
            "options": _opts(*options), "correct_answer": {"choice": answer}, "explanation": explanation}


def _quiz(fmt, prompt, correct, explanation, difficulty, options=None):
    q = {"type": "quiz", "quiz_format": fmt, "prompt": prompt, "difficulty": difficulty, "points": 1,
         "skill_slug": "python", "correct_answer": correct, "explanation": explanation}
    if options:
        q["options"] = _opts(*options)
    return q


def _coding(prompt, difficulty, explanation, fn, starter, tests, expected_output, solution):
    return {"type": "coding", "prompt": prompt, "difficulty": difficulty, "points": 1, "skill_slug": "python",
            "explanation": explanation,
            "coding_config": {"language": "python", "function_name": fn, "starter_code": starter,
                              "test_cases": [{"args": a, "expected": e, "visible": v} for a, e, v in tests],
                              "expected_output": expected_output, "time_limit_seconds": 2,
                              "memory_limit_mb": 128, "solution": solution}}


# ---------------------------------------------------------------- beginner
_B = "easy"
_beginner = [
    _mcq("A function body finishes running without ever reaching a `return` statement. What does calling it give back?",
         ["0", "An empty string", "None", "It raises a ReturnError"], "c",
         "A function with no return statement (or a bare `return`) evaluates to None. Forgetting to return a value and then "
         "using the result is one of the most common beginner bugs.", _B),
    _mcq("Which function definition is valid Python?",
         ["def call_model(prompt, temperature=0.7):", "def call_model(temperature=0.7, prompt):",
          "def call_model(prompt = , temperature):", "def call_model(prompt, temperature=0.7)"], "a",
         "Parameters without defaults must come before parameters with defaults, and the def line must end with a colon. "
         "Option b puts a default before a non-default; option d has no colon.", _B),
    _mcq("Inside `def collect(*items):`, what is `items` when you call `collect('a', 'b', 'c')`?",
         ["A list ['a', 'b', 'c']", "A tuple ('a', 'b', 'c')", "A dict {'a': 'b'}", "A single string 'abc'"], "b",
         "*args packs the extra positional arguments into a tuple. **kwargs is the one that packs keyword arguments into a dict.", _B),
    _quiz("true_false",
          "True or false: when a function executes a `return` statement, the function stops immediately and any code after it in the body is not run.",
          {"choice": "true"},
          "`return` hands a value back to the caller and ends the call at once. Code below it in the same branch is unreachable.", _B),
    _quiz("short_answer",
          "In `def build_request(**params):`, what built-in type is `params` inside the function? (one word)",
          {"accepted": ["dict", "dictionary", "a dict"]},
          "**params collects all extra keyword arguments into a dictionary mapping names to values.", _B),
    _coding(
        "Write `build_message(role, content, name=None)` that returns a dict with keys 'role' and 'content'. "
        "Include a 'name' key (with the given value) ONLY if `name` was provided (not None).",
        _B,
        "The default None lets callers omit the argument. Testing `is not None` (rather than truthiness) adds the key whenever a name was actually given.",
        "build_message",
        "def build_message(role, content, name=None):\n    # TODO: return the message dict; add 'name' only when it is not None\n    pass\n",
        [(["user", "Hi"], {"role": "user", "content": "Hi"}, True),
         (["assistant", "Hello", "bot"], {"role": "assistant", "content": "Hello", "name": "bot"}, True),
         (["user", "", None], {"role": "user", "content": ""}, False),
         (["tool", "42", ""], {"role": "tool", "content": "42", "name": ""}, False)],
        "A dict with role and content, plus name only when name is not None.",
        "def build_message(role, content, name=None):\n    msg = {'role': role, 'content': content}\n    if name is not None:\n        msg['name'] = name\n    return msg\n"),
    _coding(
        "Write `sum_all(*numbers)` that returns the sum of any number of positional numeric arguments. "
        "With no arguments it returns 0.",
        _B,
        "*numbers collects every positional argument into a tuple, and the built-in sum() adds them (an empty tuple sums to 0).",
        "sum_all",
        "def sum_all(*numbers):\n    # TODO: return the sum of all the numbers\n    pass\n",
        [([1, 2, 3], 6, True),
         ([10], 10, True),
         ([], 0, False),
         ([-5, 5, 7, -2], 5, False)],
        "The integer sum of all arguments (0 if none).",
        "def sum_all(*numbers):\n    return sum(numbers)\n"),
]

# ------------------------------------------------------------ intermediate
_M = "medium"
_intermediate = [
    _mcq("What happens when this code runs?\n\ncount = 10\n\ndef bump():\n    count += 1\n    return count\n\nprint(bump())",
         ["It prints 11 and leaves the global count as 11", "It prints 11 but the global count stays 10",
          "It prints 1", "It raises UnboundLocalError"], "d",
         "Assigning to `count` anywhere in the function makes it a local variable for the whole function, so `count += 1` reads a "
         "local that has no value yet. Use `global count` or, better, pass the value in and return the new one.", _M),
    _mcq("Given `def f(*args, **kwargs): return len(args), len(kwargs)`, what does `f(1, 2, a=3)` return?",
         ["(2, 1)", "(3, 0)", "(1, 2)", "(3, 3)"], "a",
         "Positional arguments 1 and 2 land in the args tuple (length 2); the keyword argument a=3 lands in the kwargs dict (length 1).", _M),
    _mcq("What does `lo` hold after this code?\n\ndef stats(nums):\n    return min(nums), max(nums)\n\nlo = stats([3, 1, 2])",
         ["1", "The list [1, 3]", "The tuple (1, 3)", "A SyntaxError is raised because you cannot return two values"], "c",
         "`return a, b` returns a single tuple. Unpacking (`lo, hi = stats(...)`) is what splits it; without unpacking you get the whole tuple.", _M),
    _quiz("scenario",
          "Your wrapper is `def call_llm(prompt, **options): return client.create(prompt=prompt, **options)`. A teammate calls "
          "`call_llm('hi', temprature=0.2)` (typo). What is the most likely outcome?",
          {"choice": "b"},
          "**options accepts any keyword name, so the wrapper itself never complains. The typo is forwarded, and the failure "
          "(or silent ignoring) happens later inside the SDK. This is the price of flexible signatures: explicit parameters give earlier, clearer errors.",
          _M,
          options=["Python raises a SyntaxError at the call site",
                   "The wrapper accepts it and forwards it; any error appears inside client.create, not in the wrapper's signature",
                   "Python auto-corrects it to temperature",
                   "The typo is silently dropped by **options"]),
    _quiz("multi_select",
          "Given `def f(a, b=1, *args, **kwargs):`, which calls are valid? Select ALL that apply.",
          {"choices": ["a", "b", "c"]},
          "f(1), f(1, 2, 3, 4) and f(a=1, b=2, c=3) all bind correctly. f(b=2) leaves the required `a` missing, and f(1, a=2) gives `a` two values (TypeError).",
          _M,
          options=["f(1)", "f(1, 2, 3, 4)", "f(a=1, b=2, c=3)", "f(b=2)", "f(1, a=2)"]),
    _coding(
        "Write `format_call(name, args, kwargs)` that returns the text of a function call. `args` is a list of positional "
        "values and `kwargs` is a dict of keyword values (keep dict order). Render each value with repr(). Positional "
        "arguments come first, then keywords as `key=value`, joined by ', '. Example: "
        "format_call('search', ['python'], {'max_results': 5}) -> \"search('python', max_results=5)\".",
        _M,
        "Build one list of string pieces (repr of positionals, then key=repr(value) for keywords) and join with ', '. "
        "This mirrors what a logging wrapper does with *args and **kwargs.",
        "format_call",
        "def format_call(name, args, kwargs):\n    # TODO: return e.g. \"search('python', max_results=5)\"\n    pass\n",
        [(["search", ["python"], {"max_results": 5}], "search('python', max_results=5)", True),
         (["add", [1, 2], {}], "add(1, 2)", True),
         (["ping", [], {}], "ping()", False),
         (["call", [], {"model": "m", "stream": True, "stop": None}], "call(model='m', stream=True, stop=None)", False),
         (["f", ["a", 2.5], {"k": "v"}], "f('a', 2.5, k='v')", False)],
        "A string such as \"name(arg1, arg2, key=value)\" using repr() for values.",
        "def format_call(name, args, kwargs):\n    parts = [repr(a) for a in args]\n    parts += [f'{k}={v!r}' for k, v in kwargs.items()]\n    return f\"{name}({', '.join(parts)})\"\n"),
    _coding(
        "Write `top_n(records, key, n=3, reverse=True)` where `records` is a list of dicts. Return the first `n` records "
        "after sorting them by `record[key]`, largest first when reverse is True and smallest first when False. Records "
        "with equal values must keep their original relative order. If n is larger than the list, return everything; n=0 returns [].",
        _M,
        "sorted() with key=lambda r: r[key] and reverse=reverse is stable (even with reverse=True), then slicing [:n] takes the first n. "
        "Default parameters let callers just write top_n(records, 'score').",
        "top_n",
        "def top_n(records, key, n=3, reverse=True):\n    # TODO: sort by record[key] and return the first n records\n    pass\n",
        [([[{"id": 1, "score": 5}, {"id": 2, "score": 9}, {"id": 3, "score": 7}, {"id": 4, "score": 1}], "score"],
          [{"id": 2, "score": 9}, {"id": 3, "score": 7}, {"id": 1, "score": 5}], True),
         ([[{"id": 1, "score": 5}, {"id": 2, "score": 9}, {"id": 3, "score": 7}], "score", 2, False],
          [{"id": 1, "score": 5}, {"id": 3, "score": 7}], True),
         ([[{"id": "a", "s": 1}, {"id": "b", "s": 1}, {"id": "c", "s": 2}], "s", 3],
          [{"id": "c", "s": 2}, {"id": "a", "s": 1}, {"id": "b", "s": 1}], False),
         ([[{"id": 1, "v": 3}], "v", 5], [{"id": 1, "v": 3}], False),
         ([[{"id": 1, "v": 3}, {"id": 2, "v": 4}], "v", 0], [], False),
         ([[], "v"], [], False)],
        "A list of at most n records sorted by the given key (stable for ties).",
        "def top_n(records, key, n=3, reverse=True):\n    return sorted(records, key=lambda r: r[key], reverse=reverse)[:n]\n"),
]

# ----------------------------------------------------------------- advanced
_A = "hard"
_advanced = [
    _mcq("What does this code return?\n\ndef make_callbacks():\n    fs = []\n    for i in range(3):\n        fs.append(lambda: i)\n    return [f() for f in fs]",
         ["[0, 1, 2]", "[1, 2, 3]", "[2, 2, 2]", "[None, None, None]"], "c",
         "Closures capture the variable `i`, not its value at creation time (late binding). By the time the lambdas run, the loop has "
         "finished and i is 2. Fix with a default argument (`lambda i=i: i`) or a factory function that binds each value.", _A),
    _mcq("A decorator returns an inner `wrapper(*args, **kwargs)` but does not use `functools.wraps`. A framework then builds an LLM tool "
         "schema from the decorated function. What goes wrong?",
         ["The schema is built from the wrapper's name and docstring (`wrapper`, usually None), so the model sees wrong or missing tool metadata",
          "Nothing: decorators automatically copy __name__ and __doc__ onto the wrapper",
          "The decorated function can no longer be called with keyword arguments",
          "Python raises TypeError at decoration time because wrapper has no docstring"], "a",
         "Without functools.wraps the decorated name points to `wrapper`, so __name__ and __doc__ (and inspect-based signatures) describe the wrapper, "
         "not your function. Tool-schema builders that read them produce misleading descriptions. functools.wraps(fn) copies the metadata and sets __wrapped__.", _A),
    _mcq("Both decorators below wrap the function. What does `greet()` return?\n\ndef swap(fn):\n    def w(*a, **k):\n        return fn(*a, **k).replace('!', '?')\n    return w\n\n"
         "def exclaim(fn):\n    def w(*a, **k):\n        return fn(*a, **k) + '!'\n    return w\n\n@swap\n@exclaim\ndef greet():\n    return 'hi'",
         ["'hi!'", "'hi'", "'hi!?'", "'hi?'"], "d",
         "Stacked decorators apply bottom-up: greet = swap(exclaim(greet)). At call time the outer wrapper (swap) calls the inner one (exclaim), which yields 'hi!', "
         "and swap then replaces '!' with '?', giving 'hi?'. Reversing the order would give 'hi!'.", _A),
    _quiz("multi_select",
          "You write a `retry(times)` decorator factory that wraps LLM calls in `try/except Exception`. Which statements are TRUE? Select ALL that apply.",
          {"choices": ["a", "b", "d"]},
          "retry(times=3) runs once at decoration time and returns the real decorator (a). *args/**kwargs forwarding lets one decorator wrap any signature (b). "
          "Catching bare Exception also retries bugs such as TypeError, so catch specific transient errors (d). Retrying is NOT automatically safe for calls with side effects (c), "
          "and without functools.wraps the signature/metadata is not preserved (e).",
          _A,
          options=["`retry(times=3)` is evaluated once, at decoration time, and returns the actual decorator",
                   "Forwarding *args and **kwargs in the wrapper lets the same decorator wrap functions with any signature",
                   "Retrying is always safe, even for calls that charge a payment or send an email",
                   "Catching bare Exception also retries programming errors like TypeError, so narrowing to transient errors is better",
                   "The decorated function automatically keeps its original signature and docstring"]),
    _quiz("scenario",
          "Your team wraps `call_llm(prompt, temperature)` with `functools.lru_cache` to save cost. Later, users complain that with temperature=1.0 "
          "'regenerate' always returns the identical answer. What is the best diagnosis and fix?",
          {"choice": "c"},
          "lru_cache returns the stored result for identical arguments, so a sampling call at temperature>0 is frozen to its first output. Caching is only semantically safe "
          "when the call is (near) deterministic, e.g. temperature 0, or when a varying argument such as a seed/attempt number is part of the key.",
          _A,
          options=["lru_cache has a bug with float arguments; convert temperature to a string",
                   "The model provider is caching responses; nothing can be done in Python",
                   "The cache returns the first result for identical arguments; only cache deterministic calls (temperature 0) or include a seed/attempt in the key",
                   "Increase lru_cache's maxsize so it evicts old answers"]),
    _coding(
        "Write `run_pipeline(value, steps)` that applies steps to `value` in order. Each step is a list whose first item is the operation name and the rest are its "
        "parameters: ['add', n] -> value + n; ['mul', n] -> value * n; ['clip', lo, hi] -> min(max(value, lo), hi); ['neg'] -> -value. "
        "Return {'result': value, 'error': None} on success. If a step has an unknown name, stop and return {'result': <value so far>, 'error': 'unknown step: <name>'}. "
        "If a known step is given the wrong number of parameters, stop and return {'result': <value so far>, 'error': 'bad arguments for <name>'}.",
        _A,
        "Keep a registry dict mapping names to functions taking (value, *params), then forward params with *. A wrong parameter count raises TypeError at the call, "
        "which is caught and reported without losing the value computed so far. This dispatch-and-forward shape is how agent tool dispatchers work.",
        "run_pipeline",
        "def run_pipeline(value, steps):\n    # TODO: dispatch each step by name, forwarding its parameters with *\n    pass\n",
        [([3, [["add", 2], ["mul", 4]]], {"result": 20, "error": None}, True),
         ([50, [["clip", 0, 10], ["neg"]]], {"result": -10, "error": None}, True),
         ([5, []], {"result": 5, "error": None}, False),
         ([1, [["add", 1], ["sqrt"], ["mul", 9]]], {"result": 2, "error": "unknown step: sqrt"}, False),
         ([7, [["mul", 2], ["add"], ["neg"]]], {"result": 14, "error": "bad arguments for add"}, False),
         ([7, [["neg", 1]]], {"result": 7, "error": "bad arguments for neg"}, False)],
        "A dict with the final (or last successful) 'result' and an 'error' message or None.",
        "def run_pipeline(value, steps):\n"
        "    ops = {\n"
        "        'add': lambda v, n: v + n,\n"
        "        'mul': lambda v, n: v * n,\n"
        "        'clip': lambda v, lo, hi: min(max(v, lo), hi),\n"
        "        'neg': lambda v: -v,\n"
        "    }\n"
        "    for step in steps:\n"
        "        name, params = step[0], step[1:]\n"
        "        if name not in ops:\n"
        "            return {'result': value, 'error': 'unknown step: ' + name}\n"
        "        try:\n"
        "            value = ops[name](value, *params)\n"
        "        except TypeError:\n"
        "            return {'result': value, 'error': 'bad arguments for ' + name}\n"
        "    return {'result': value, 'error': None}\n"),
    _coding(
        "An LLM produced tool-call arguments and you must validate them like Python's own argument binding. Write `bind_args(params, provided)`. "
        "`params` is a list of dicts like {'name': 'query'} (required) or {'name': 'limit', 'default': 5} (optional; the key 'default' is present, its value may be None). "
        "`provided` is a dict of arguments from the model. If `provided` has names not in params, return {'ok': False, 'error': 'unexpected: a, b'} listing them "
        "alphabetically. Otherwise, if required params are missing, return {'ok': False, 'error': 'missing: x, y'} listing them in params order. "
        "Otherwise return {'ok': True, 'args': {...}} with EVERY param (in params order), using defaults for those not provided. Unexpected-name errors take precedence over missing ones.",
        _A,
        "Check unexpected names first (set difference, sorted), then missing required names (in declaration order), then build the bound dict by looking up each "
        "parameter in `provided` and falling back to its default. Testing `'default' in p` (not truthiness) matters because a default may be None or 0.",
        "bind_args",
        "def bind_args(params, provided):\n    # TODO: validate provided against params and apply defaults\n    pass\n",
        [([[{"name": "query"}, {"name": "limit", "default": 5}], {"query": "cats"}],
          {"ok": True, "args": {"query": "cats", "limit": 5}}, True),
         ([[{"name": "query"}, {"name": "limit", "default": 5}], {"limit": 2}],
          {"ok": False, "error": "missing: query"}, True),
         ([[{"name": "a"}, {"name": "b"}, {"name": "c", "default": None}], {"c": 0}],
          {"ok": False, "error": "missing: a, b"}, False),
         ([[{"name": "q"}], {"q": "x", "z": 1, "b": 2}],
          {"ok": False, "error": "unexpected: b, z"}, False),
         ([[{"name": "q"}, {"name": "n"}], {"zzz": 1}],
          {"ok": False, "error": "unexpected: zzz"}, False),
         ([[{"name": "flag", "default": False}, {"name": "note", "default": None}], {}],
          {"ok": True, "args": {"flag": False, "note": None}}, False),
         ([[], {}], {"ok": True, "args": {}}, False)],
        "A dict with ok True and the fully bound args, or ok False and an error message.",
        "def bind_args(params, provided):\n"
        "    names = [p['name'] for p in params]\n"
        "    unexpected = sorted(k for k in provided if k not in names)\n"
        "    if unexpected:\n"
        "        return {'ok': False, 'error': 'unexpected: ' + ', '.join(unexpected)}\n"
        "    missing = [p['name'] for p in params if 'default' not in p and p['name'] not in provided]\n"
        "    if missing:\n"
        "        return {'ok': False, 'error': 'missing: ' + ', '.join(missing)}\n"
        "    args = {}\n"
        "    for p in params:\n"
        "        args[p['name']] = provided[p['name']] if p['name'] in provided else p['default']\n"
        "    return {'ok': True, 'args': args}\n"),
]


def _assessment(level, title_level, description, questions):
    return {"course_slug": "python-for-ai", "module_slug": "functions", "level": level,
            "title": f"Functions - {title_level} Assessment", "description": description,
            "passing_score": 80, "required_coding_questions": 1, "time_limit_minutes": 45,
            "questions": questions}


MODULE_ASSESSMENTS = [
    _assessment("beginner", "Beginner",
                "Checks the fundamentals of defining functions: parameters, defaults, return values, *args and **kwargs.", _beginner),
    _assessment("intermediate", "Intermediate",
                "Checks practical reasoning about scope, argument binding, *args/**kwargs forwarding and default parameters.", _intermediate),
    _assessment("advanced", "Advanced",
                "Checks deeper understanding of closures, decorators, argument forwarding and robust dispatch logic.", _advanced),
]
