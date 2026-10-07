"""Module assessments (beginner, intermediate, advanced) for python-for-ai / data-structures."""


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


def _code(prompt, explanation, difficulty, fn, starter, tests, expected_output, solution):
    return {"type": "coding", "prompt": prompt, "difficulty": difficulty, "points": 1, "skill_slug": "python",
            "explanation": explanation,
            "coding_config": {
                "language": "python", "function_name": fn, "starter_code": starter,
                "test_cases": [{"args": a, "expected": e, "visible": v} for a, e, v in tests],
                "expected_output": expected_output, "time_limit_seconds": 2, "memory_limit_mb": 128,
                "solution": solution}}


_BEGINNER = [
    _mcq("Which line creates a tuple containing the two items \"user\" and \"hi\"?",
         ['msg = ["user", "hi"]', 'msg = {"user", "hi"}', 'msg = ("user", "hi")', 'msg = {"user": "hi"}'],
         "c", "Round brackets with comma-separated items make a tuple. Square brackets make a list, curly braces "
         "with bare items make a set, and curly braces with key: value pairs make a dict.", "easy"),
    _mcq("What does `len({1, 2, 2, 3, 3, 3})` return?",
         ["6", "3", "2", "It raises an error because of the duplicates"],
         "b", "A set stores each distinct value once, so the set is {1, 2, 3} and its length is 3.", "easy"),
    _mcq("Given `usage = {\"input_tokens\": 120}`, what happens when you run `usage[\"output_tokens\"]`?",
         ["It returns None", "It returns 0", "It returns an empty string", "It raises a KeyError"],
         "d", "Square-bracket access on a missing key raises KeyError. Use usage.get(\"output_tokens\", 0) to get "
         "a default instead.", "easy"),
    _quiz("true_false", "True or false: a Python list can be used as a key in a dictionary.",
          "Dictionary keys must be hashable. Lists are mutable and therefore unhashable; tuples of hashable items "
          "can be used as keys.", "easy", {"choice": "false"}),
    _quiz("short_answer", "Which list method adds one item to the END of a list? (give the method name)",
          "list.append(x) adds x at the end in place. insert() places it at a chosen index and extend() adds "
          "several items.", "easy", {"accepted": ["append", "append()", ".append", ".append()", "list.append"]}),
    _code("Conversation history is a list of messages. Implement `last_n(items, n)` that returns a new list with "
          "the most recent `n` items (the last n). If n is 0 return an empty list; if n is larger than the list "
          "return the whole list.",
          "A negative slice items[-n:] takes the tail, but n == 0 must be special-cased because items[-0:] is the "
          "whole list.", "easy", "last_n",
          "def last_n(items, n):\n    # TODO: return the last n items as a new list\n    pass\n",
          [([["a", "b", "c", "d"], 2], ["c", "d"], True),
           ([["a", "b"], 5], ["a", "b"], True),
           ([["a", "b", "c"], 0], [], False),
           ([[], 3], [], False)],
          "A list holding the last n items of items.",
          "def last_n(items, n):\n    if n <= 0:\n        return []\n    return list(items[-n:])\n"),
    _code("API responses may omit fields. Implement `total_tokens(usage)` where usage is a dict that may contain "
          "`input_tokens` and/or `output_tokens`. Return their sum, treating a missing key as 0.",
          "dict.get(key, 0) supplies a default instead of raising KeyError.", "easy", "total_tokens",
          "def total_tokens(usage):\n    # TODO: add input_tokens and output_tokens, missing keys count as 0\n    pass\n",
          [([{"input_tokens": 100, "output_tokens": 50}], 150, True),
           ([{"input_tokens": 120}], 120, True),
           ([{}], 0, False),
           ([{"output_tokens": 7, "model": "x"}], 7, False)],
          "The integer sum of input_tokens and output_tokens.",
          "def total_tokens(usage):\n    return usage.get('input_tokens', 0) + usage.get('output_tokens', 0)\n"),
]

_INTERMEDIATE = [
    _mcq("What is printed?\n\nhistory = [\"a\", \"b\"]\nbackup = history\nbackup.append(\"c\")\nprint(history)",
         ["['a', 'b']", "['a', 'b', 'c']", "['c', 'a', 'b']", "Nothing; it raises an error"],
         "b", "`backup = history` copies the reference, not the list. Both names point to the same list, so the "
         "append shows through both. Use history.copy() or history[:] for an independent shallow copy.", "medium"),
    _mcq("A developer writes `chunks = chunks.sort()` to order retrieved chunks and later gets "
         "`TypeError: 'NoneType' object is not iterable`. Why?",
         ["sort() only works on lists of numbers", "sort() returns a new list, which is then mutated",
          "sort() sorts in place and returns None, so chunks is now None",
          "sort() converts the list into a tuple"],
         "c", "list.sort() mutates the list in place and returns None. Use chunks.sort() alone, or "
         "chunks = sorted(chunks) to get a new sorted list.", "medium"),
    _mcq("You need to remove duplicate document IDs from a list while keeping the order in which they first "
         "appeared. Which approach does that?",
         ["list(set(ids))", "sorted(set(ids))", "list(dict.fromkeys(ids))", "tuple(ids)"],
         "c", "Dicts keep insertion order and keys are unique, so dict.fromkeys(ids) dedupes while preserving first "
         "appearance. set() has no guaranteed order and sorted() reorders the values.", "medium"),
    _quiz("scenario", "Your agent keeps a registry of tools as a list of 500 tool-name strings and checks "
          "`if name in registry` on every incoming request, which is now slow. What is the most appropriate fix?",
          "Membership on a list scans it linearly (O(n)); on a set or dict it is O(1) on average. Sorting does not "
          "speed up `in`, and a tuple is also scanned linearly.", "medium", {"choice": "b"},
          ["Convert the list to a tuple so it is immutable", "Keep a set of the names for the lookups",
           "Sort the list before every lookup", "Wrap the lookup in try/except"]),
    _quiz("multi_select", "Which of these expressions are valid dictionary keys? (select all that apply)",
          "Keys must be hashable. Strings, ints and tuples of hashable values work. Lists and sets are mutable and "
          "unhashable, and a tuple that contains a list is unhashable too.", "medium", {"choices": ["a", "c", "e"]},
          ['("user", 1)', '["user", 1]', '"user"', '{"user", 1}', "42"]),
    _code("Find and fix the behaviour: implement `dedupe_chunks(chunks)` that removes duplicate strings from a "
          "list while keeping the FIRST occurrence of each and the original order. Return a new list and do not "
          "modify the input. (Hint: list(set(chunks)) loses the order.)",
          "Track seen items in a set (O(1) lookups) and append unseen items to the output as we go.",
          "medium", "dedupe_chunks",
          "def dedupe_chunks(chunks):\n    # TODO: keep first occurrences, preserve order\n    return list(set(chunks))\n",
          [([["a", "b", "a", "c", "b"]], ["a", "b", "c"], True),
           ([["z", "y", "x"]], ["z", "y", "x"], True),
           ([[]], [], False),
           ([["q", "q", "q"]], ["q"], False),
           ([["b", "a", "b", "c", "a", "d"]], ["b", "a", "c", "d"], False)],
          "A list of unique strings in first-seen order.",
          "def dedupe_chunks(chunks):\n    seen = set()\n    out = []\n    for c in chunks:\n"
          "        if c not in seen:\n            seen.add(c)\n            out.append(c)\n    return out\n"),
    _code("Implement `group_by_role(messages)`. `messages` is a list of dicts like {\"role\": \"user\", "
          "\"content\": \"hi\"}. Return a dict mapping each role to the list of its contents, in the original "
          "order. Messages missing the `role` key are grouped under \"unknown\". Empty input gives {}.",
          "Use setdefault (or a check) to create the list the first time a role appears, and .get for the "
          "optional role.", "medium", "group_by_role",
          "def group_by_role(messages):\n    # TODO: return {role: [contents...]}\n    return {}\n",
          [([[{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"},
              {"role": "user", "content": "bye"}]], {"user": ["hi", "bye"], "assistant": ["hello"]}, True),
           ([[]], {}, True),
           ([[{"content": "orphan"}, {"role": "user", "content": "x"}]],
            {"unknown": ["orphan"], "user": ["x"]}, False),
           ([[{"role": "system", "content": "s"}]], {"system": ["s"]}, False)],
          "A dict mapping role names to lists of message contents.",
          "def group_by_role(messages):\n    out = {}\n    for m in messages:\n"
          "        out.setdefault(m.get('role', 'unknown'), []).append(m['content'])\n    return out\n"),
]

_ADVANCED = [
    _mcq("What does this print?\n\ngrid = [[0] * 2] * 2\ngrid[0][0] = 1\nprint(grid)",
         ["[[1, 0], [0, 0]]", "[[1, 0], [1, 0]]", "[[1, 1], [0, 0]]", "[[0, 0], [0, 0]]"],
         "b", "`[row] * 2` repeats a reference to the SAME inner list, so both rows are one object. Mutating "
         "grid[0][0] is visible through grid[1][0]. Build independent rows with [[0] * 2 for _ in range(2)].", "hard"),
    _mcq("Which explains why `def add(msg, log=[]): log.append(msg); return log` behaves badly when called "
         "repeatedly without the `log` argument?",
         ["Default values are evaluated once at function definition, so every call shares the same list",
          "Lists passed as defaults are converted to tuples, so append fails silently",
          "Python copies the default list on each call but only keeps the last copy",
          "Default arguments are re-evaluated on each call, which makes the list grow inside the loop"],
         "a", "Defaults are evaluated once when `def` runs, so a mutable default persists across calls and "
         "accumulates state (a classic source of cross-request leaks). Use log=None and create a new list inside.",
         "hard"),
    _mcq("You cache LLM responses keyed by the request parameters {\"model\": ..., \"temperature\": ...}. "
         "Which key design is correct and robust?",
         ["Use the dict itself as the key", "Use a list of the values, e.g. [model, temperature]",
          "Use a set of the items, e.g. {model, temperature}",
          "Use a tuple such as (model, temperature), or a tuple of sorted items"],
         "d", "Dicts, lists and sets are unhashable so they raise TypeError as keys. A tuple of hashable values is "
         "hashable, and a set would also lose which value belongs to which parameter.", "hard"),
    _quiz("scenario", "A RAG pipeline must return only chunks that appear in BOTH the keyword-search results "
          "(2,000 chunk IDs) and the vector-search results (2,000 chunk IDs), preserving the vector-search "
          "ranking. Which implementation has the best complexity and keeps the ranking?",
          "Build a set of one side once (O(n)), then filter the ranked list with O(1) membership tests, for O(n) "
          "total. set & set is fast but loses the ranking, and nested list scans are O(n*m).", "hard",
          {"choice": "c"},
          ["Return list(set(vector) & set(keyword))", "For each vector ID, test `id in keyword_list` (both lists)",
           "keyword_set = set(keyword); [i for i in vector if i in keyword_set]",
           "Sort both lists and compare them element by element"]),
    _quiz("short_answer", "What built-in exception does Python raise for `{[1, 2]: \"x\"}` or "
          "`{}[[1, 2]]`? (give the exception name)",
          "Lists are unhashable, and using one where a hash is required raises TypeError: unhashable type: 'list'.",
          "hard", {"accepted": ["typeerror", "type error", "typeerror: unhashable type"]}),
    _code("Implement `deep_merge(base, override)` for nested config dicts. Return a NEW dict where keys from "
          "`override` win, except that when both values are dicts they are merged recursively. Lists and other "
          "values are replaced, not merged. Neither input may be modified (including nested dicts of the result "
          "that came from the inputs: mutating the result must not affect the inputs).",
          "Recurse only when both sides are dicts; deep-copy non-shared values so the result never aliases the "
          "inputs' nested structures.", "hard", "deep_merge",
          "def deep_merge(base, override):\n    # TODO: recursive merge into a new dict\n    return dict(base)\n",
          [([{"a": 1, "b": {"x": 1, "y": 2}}, {"b": {"y": 3, "z": 4}, "c": 5}],
            {"a": 1, "b": {"x": 1, "y": 3, "z": 4}, "c": 5}, True),
           ([{"a": {"k": 1}}, {"a": 5}], {"a": 5}, True),
           ([{"a": 1}, {"a": {"k": 1}}], {"a": {"k": 1}}, False),
           ([{}, {}], {}, False),
           ([{"l": [1, 2], "d": {"e": {"f": 1}}}, {"l": [3], "d": {"e": {"g": 2}}}],
            {"l": [3], "d": {"e": {"f": 1, "g": 2}}}, False)],
          "A new dict with override merged over base recursively.",
          "import copy\n\n\ndef deep_merge(base, override):\n    out = {k: copy.deepcopy(v) for k, v in base.items()}\n"
          "    for k, v in override.items():\n        if isinstance(v, dict) and isinstance(out.get(k), dict):\n"
          "            out[k] = deep_merge(out[k], v)\n        else:\n            out[k] = copy.deepcopy(v)\n"
          "    return out\n"),
    _code("Implement `flatten(data, sep=\".\")` for JSON-style data. Convert nested dicts and lists into a flat "
          "dict whose keys are paths joined with `sep`; list items use their index as the path part. Example: "
          "{\"a\": {\"b\": 1}, \"c\": [10, {\"d\": 2}]} -> {\"a.b\": 1, \"c.0\": 10, \"c.1.d\": 2}. Scalars "
          "(including None) are leaves. Empty dicts/lists are kept as leaf values at their path (e.g. {} stays "
          "{}). A top-level scalar or empty container returns {} .",
          "Recurse with a path prefix, treating dicts and lists as containers, and stop at scalars or empty "
          "containers so information is not silently dropped.", "hard", "flatten",
          "def flatten(data, sep='.'):\n    # TODO: flatten nested dicts/lists into path -> leaf\n    return {}\n",
          [([{"a": {"b": 1}, "c": [10, {"d": 2}]}], {"a.b": 1, "c.0": 10, "c.1.d": 2}, True),
           ([{"x": 1, "y": None}], {"x": 1, "y": None}, True),
           ([{"a": {"b": {"c": 1}}}, "/"], {"a/b/c": 1}, False),
           ([{"e": {}, "l": [], "n": [[1, 2]]}], {"e": {}, "l": [], "n.0.0": 1, "n.0.1": 2}, False),
           ([{}], {}, False)],
          "A flat dict mapping joined key paths to leaf values.",
          "def flatten(data, sep='.'):\n    out = {}\n\n    def walk(node, path):\n"
          "        if isinstance(node, dict) and node:\n            for k, v in node.items():\n"
          "                walk(v, f'{path}{sep}{k}' if path else str(k))\n"
          "        elif isinstance(node, list) and node:\n            for i, v in enumerate(node):\n"
          "                walk(v, f'{path}{sep}{i}' if path else str(i))\n"
          "        elif path:\n            out[path] = node\n\n    walk(data, '')\n    return out\n"),
]

_COMMON = {"course_slug": "python-for-ai", "module_slug": "data-structures", "passing_score": 80,
           "required_coding_questions": 1, "time_limit_minutes": 45}

MODULE_ASSESSMENTS = [
    {**_COMMON, "level": "beginner", "title": "Data Structures - Beginner Assessment",
     "description": "Checks core knowledge of lists, tuples, sets and dictionaries and safe key access.",
     "questions": _BEGINNER},
    {**_COMMON, "level": "intermediate", "title": "Data Structures - Intermediate Assessment",
     "description": "Checks practical use of collections: aliasing, ordering, hashing and grouping message data.",
     "questions": _INTERMEDIATE},
    {**_COMMON, "level": "advanced", "title": "Data Structures - Advanced Assessment",
     "description": "Checks deep understanding of mutability, hashing, complexity and robust nested JSON-style data handling.",
     "questions": _ADVANCED},
]
