"""Sandbox tests. Linux only (run inside the runner image):

    docker build -t agenticai-code-runner code_runner
    docker run --rm --user root -v "$PWD/code_runner/tests:/srv/tests" --entrypoint sh agenticai-code-runner \
        -c "pip install -q pytest && cd /srv && python -m pytest -q tests"
"""
import time

import pytest

from sandbox import run_script, run_submission

ADD = "def add(a, b):\n    return a + b\n"


def run(code, tests, fn="add", limit=1.5, memory=128):
    return run_submission(code, fn, tests, limit, memory)


def t(args, expected, visible=True, id="t"):
    return {"id": id, "args": args, "expected": expected, "visible": visible}


def test_correct_solution_passes_every_test():
    results = run(ADD, [t([1, 2], 3, id="a"), t([-1, 1], 0, visible=False, id="b")])
    assert [r["passed"] for r in results] == [True, True]
    assert results[0]["actual"] == 3


def test_wrong_answer_fails_and_reports_actual_for_visible_only():
    visible, hidden = run("def add(a, b):\n    return a - b\n", [t([2, 1], 3, id="v"), t([2, 1], 3, visible=False, id="h")])
    assert visible["status"] == "failed" and visible["actual"] == 1 and visible["expected"] == 3
    assert hidden["status"] == "failed"
    assert "actual" not in hidden and "expected" not in hidden and "args" not in hidden


def test_runtime_error_is_reported_not_raised():
    (r,) = run("def add(a, b):\n    return a / 0\n", [t([1, 2], 3)])
    assert r["status"] == "error" and "ZeroDivisionError" in r["error"]


def test_hidden_test_errors_are_generic():
    (r,) = run("def add(a, b):\n    return a / 0\n", [t([1, 2], 3, visible=False)])
    assert r["error"] == "Runtime error" and "ZeroDivisionError" not in str(r)


def test_syntax_error_fails_every_test():
    results = run("def add(a, b)\n    return a + b\n", [t([1, 2], 3), t([2, 2], 4)])
    assert all(r["status"] == "error" and not r["passed"] for r in results)


def test_missing_function():
    (r,) = run("def other():\n    return 1\n", [t([1, 2], 3)])
    assert r["status"] == "error" and "not defined" in r["error"]


def test_infinite_loop_is_killed_at_the_time_limit():
    started = time.monotonic()
    (r,) = run("def add(a, b):\n    while True:\n        pass\n", [t([1, 2], 3)], limit=1.0)
    assert r["status"] == "timeout" and not r["passed"]
    assert time.monotonic() - started < 5


def test_memory_bomb_is_contained():
    (r,) = run("def add(a, b):\n    x = bytearray(1024 * 1024 * 1024)\n    return 3\n", [t([1, 2], 3)], memory=64)
    assert not r["passed"] and r["status"] in ("error", "timeout")


def test_output_flood_is_contained():
    code = "import sys\ndef add(a, b):\n    while True:\n        sys.stdout.write('x' * 100000)\n"
    (r,) = run(code, [t([1, 2], 3)], limit=2.0)
    assert not r["passed"]


def test_exit_before_returning_is_an_error():
    (r,) = run("import sys\ndef add(a, b):\n    sys.exit(0)\n", [t([1, 2], 3)])
    assert r["status"] == "error" and not r["passed"]


def test_forged_result_line_is_ignored():
    code = "def add(a, b):\n    print('__RESULT__deadbeef:{\"ok\": true, \"value\": 3}')\n    return 0\n"
    (r,) = run(code, [t([1, 2], 3)])
    assert r["status"] == "failed" and r["actual"] == 0


def test_comparison_is_strict_about_types():
    (bool_vs_int,) = run("def add(a, b):\n    return True\n", [t([0, 1], 1)])
    (float_vs_int,) = run("def add(a, b):\n    return float(a + b)\n", [t([1, 2], 3)])
    assert not bool_vs_int["passed"] and not float_vs_int["passed"]


def test_dict_key_order_does_not_matter():
    (r,) = run("def f(x):\n    return {'b': 2, 'a': 1}\n", [t([0], {"a": 1, "b": 2})], fn="f")
    assert r["passed"]


def test_non_json_return_value_fails_cleanly():
    (r,) = run("def add(a, b):\n    return {1, 2}\n", [t([1, 2], 3)])
    assert not r["passed"] and r["status"] == "error"


def test_student_cannot_see_the_answer_key():
    # The expected value is never sent to the child process, so it cannot be discovered from inside.
    code = "import os\ndef add(a, b):\n    return sorted(os.listdir('.'))\n"
    (r,) = run(code, [t([1, 2], 3)])
    assert r["actual"] == ["args.json", "harness.py", "solution.py", "stderr.txt", "stdout.txt"]


def test_environment_is_scrubbed():
    (r,) = run("import os\ndef add(a, b):\n    return sorted(os.environ)\n", [t([1, 2], 3)])
    assert "RUNNER_TOKEN" not in r["actual"]


def test_no_state_leaks_between_test_cases():
    code = "counter = []\ndef add(a, b):\n    counter.append(1)\n    return len(counter)\n"
    results = run(code, [t([0, 0], 1), t([0, 0], 1)])
    assert [r["passed"] for r in results] == [True, True]  # fresh process per test


def _leftover_processes():
    import os

    count = 0
    for pid in filter(str.isdigit, os.listdir("/proc")):
        try:
            with open(f"/proc/{pid}/cmdline", "rb") as f:
                if b"harness.py" in f.read():
                    count += 1
        except OSError:
            pass
    return count


def test_fork_bomb_is_contained_and_leaves_nothing_behind():
    bomb = "import os\ndef add(a, b):\n    while True:\n        os.fork()\n"
    started = time.monotonic()
    results = run(bomb, [t([1, 2], 3, id=str(i)) for i in range(6)], limit=1.5)
    assert not any(r["passed"] for r in results)
    assert time.monotonic() - started < 12
    time.sleep(0.3)
    assert _leftover_processes() == 0
    # the sandbox still works afterwards
    (ok,) = run(ADD, [t([1, 2], 3)])
    assert ok["passed"]


def test_remaining_tests_are_skipped_after_a_timeout():
    started = time.monotonic()
    loop = "def add(a, b):\n    while True:\n        pass\n"
    results = run(loop, [t([1, 2], 3, id=str(i)) for i in range(6)], limit=1.0)
    assert results[0]["status"] == "timeout" and all(r["status"] == "skipped" for r in results[1:])
    assert time.monotonic() - started < 6


# ---- run_script: open-ended practice code, no function call, no expected answer -----------------


def test_script_prints_are_captured():
    r = run_script("print('hello')\nprint(1 + 2)\n")
    assert r["status"] == "ok" and r["stdout"] == "hello\n3\n" and r["error"] is None


def test_script_traceback_is_reported_as_an_error():
    r = run_script("x = 1\nraise ValueError('bad input')\n")
    assert r["status"] == "error" and "ValueError: bad input" in r["error"]


def test_script_syntax_error_is_reported():
    r = run_script("def broken(\n")
    assert r["status"] == "error" and r["error"]


def test_script_infinite_loop_is_killed_at_the_time_limit():
    started = time.monotonic()
    r = run_script("while True:\n    pass\n", time_limit=1.0)
    assert r["status"] == "timeout"
    assert time.monotonic() - started < 5


def test_script_memory_bomb_is_contained():
    r = run_script("x = bytearray(1024 * 1024 * 1024)\n", memory_mb=64)
    assert r["status"] in ("error", "timeout")


def test_script_fork_bomb_is_contained_and_leaves_nothing_behind():
    bomb = "import os\nwhile True:\n    os.fork()\n"
    started = time.monotonic()
    r = run_script(bomb, time_limit=1.5)
    assert r["status"] in ("error", "timeout")
    assert time.monotonic() - started < 12
    time.sleep(0.3)
    assert _leftover_processes() == 0
    # the sandbox still works afterwards
    assert run_script("print('ok')\n")["status"] == "ok"


def test_script_environment_is_scrubbed():
    r = run_script("import os\nprint(sorted(os.environ))\n")
    assert "RUNNER_TOKEN" not in r["stdout"]


def test_script_output_is_truncated():
    r = run_script("print('x' * 20000)\n")
    assert r["status"] == "ok" and len(r["stdout"]) <= 4000


def test_script_stderr_without_a_raised_exception_is_still_reported():
    r = run_script("import sys\nsys.exit(1)\n")
    assert r["status"] == "error"
