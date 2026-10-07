"""Run one student function against test cases, each in its own resource-limited subprocess.

Isolation layers (defence in depth - this module is the innermost one):
  * a separate process per test case, started in its own session so the whole group can be killed
  * wall-clock timeout, CPU-time limit, address-space (memory) limit, output/file-size limit, no core dumps
  * a scrubbed environment and an empty working directory (deleted afterwards)
  * the expected values NEVER enter the child: it only receives the arguments and returns a value;
    the comparison happens here, so student code cannot read or tamper with the answer key
The container this runs in adds: no network, read-only root filesystem, non-root user, dropped
capabilities, pids/memory/cpu caps (see docker-compose.yml). Linux only (uses `resource`).
"""
from __future__ import annotations

import json
import os
import resource
import secrets
import shutil
import signal
import subprocess
import sys
import tempfile
import time

MAX_OUTPUT_BYTES = 256 * 1024
NPROC_LIMIT = 96
_MARKER = "__RESULT__"

# Runs inside the child. Deliberately tiny.
HARNESS = r'''
import importlib.util, json, sys
fn_name, nonce = sys.argv[1], sys.argv[2]
out = sys.__stdout__
def emit(payload):
    try:
        line = json.dumps(payload)
    except Exception:
        line = json.dumps({"ok": False, "error": "return value is not JSON serializable"})
    out.write("\n" + "__RESULT__" + nonce + ":" + line + "\n")
    out.flush()
try:
    args = json.loads(open("args.json").read())
    spec = importlib.util.spec_from_file_location("solution", "solution.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    func = getattr(module, fn_name, None)
    if not callable(func):
        emit({"ok": False, "error": "function '" + fn_name + "' is not defined"})
    else:
        emit({"ok": True, "value": func(*args)})
except SystemExit:
    emit({"ok": False, "error": "program exited before returning a value"})
except BaseException as exc:
    emit({"ok": False, "error": (type(exc).__name__ + ": " + str(exc))[:300]})
'''


def _kill_group(proc: subprocess.Popen) -> None:
    """SIGKILL the whole process group until nothing is left (a fork bomb can outrun a single kill).

    The direct child is reaped inside the loop: until it is, it lingers as a zombie that keeps the
    group "alive" and the loop would spin to its deadline.
    """
    deadline = time.monotonic() + 3.0
    while time.monotonic() < deadline:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            break
        proc.poll()
        time.sleep(0.01)
    proc.wait()


def _limits(time_limit: float, memory_mb: int):
    def apply() -> None:
        memory = max(memory_mb, 64) * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
        cpu = int(time_limit) + 1
        resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))
        resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT_BYTES, MAX_OUTPUT_BYTES))
        resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        # Fork-bomb guard: counts every process/thread of this uid (including the runner's own threads),
        # so the ceiling is well above the runner's baseline but far below the container pid cap.
        resource.setrlimit(resource.RLIMIT_NPROC, (NPROC_LIMIT, NPROC_LIMIT))

    return apply


def canonical(value) -> str:
    """Strict, order-insensitive-for-dicts comparison form (so True != 1 and 1 != 1.0)."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _read(path: str, limit: int = 2000) -> str:
    try:
        with open(path, "rb") as f:
            return f.read(limit).decode("utf-8", "replace")
    except OSError:
        return ""


def _run_one(workdir: str, function_name: str, args: list, time_limit: float, memory_mb: int) -> dict:
    nonce = secrets.token_hex(12)
    with open(os.path.join(workdir, "args.json"), "w") as f:
        json.dump(args, f)
    out_path, err_path = os.path.join(workdir, "stdout.txt"), os.path.join(workdir, "stderr.txt")
    started = time.monotonic()
    with open(out_path, "wb") as out, open(err_path, "wb") as err:
        proc = subprocess.Popen(
            [sys.executable, "-I", "-B", "harness.py", function_name, nonce],
            cwd=workdir, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
            env={"PATH": "/usr/local/bin:/usr/bin", "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
            preexec_fn=_limits(time_limit, memory_mb), start_new_session=True,
        )
        timed_out = False
        try:
            proc.wait(timeout=time_limit)
        except subprocess.TimeoutExpired:
            timed_out = True
        finally:
            _kill_group(proc)  # always: the student's code may have left children behind
    duration_ms = int((time.monotonic() - started) * 1000)
    stdout = _read(out_path, MAX_OUTPUT_BYTES)
    stderr = _read(err_path)

    if timed_out or proc.returncode == -signal.SIGXCPU:
        return {"status": "timeout", "error": f"Time limit exceeded ({time_limit:g}s)", "duration_ms": duration_ms, "stdout": stdout[:500]}

    marker = f"{_MARKER}{nonce}:"
    payload = None
    visible_stdout = []
    for line in stdout.splitlines():
        if line.startswith(marker):
            try:
                payload = json.loads(line[len(marker):])
            except ValueError:
                payload = None
        else:
            visible_stdout.append(line)
    text = "\n".join(visible_stdout)[:500]

    if payload is None:
        if proc.returncode in (-signal.SIGKILL, -signal.SIGSEGV, -signal.SIGXFSZ, -signal.SIGABRT):
            return {"status": "error", "error": "Process was killed (memory or output limit exceeded)", "duration_ms": duration_ms, "stdout": text}
        detail = stderr.strip().splitlines()[-1] if stderr.strip() else "no result was returned"
        return {"status": "error", "error": detail[:300], "duration_ms": duration_ms, "stdout": text}
    if not payload.get("ok"):
        return {"status": "error", "error": str(payload.get("error", "error"))[:300], "duration_ms": duration_ms, "stdout": text}
    return {"status": "ok", "value": payload["value"], "duration_ms": duration_ms, "stdout": text}


def run_script(code: str, time_limit: float = 5.0, memory_mb: int = 128) -> dict:
    """Run `code` as a plain script (no function call, no expected value) and capture stdout/stderr.

    For open-ended practice exercises that have no fixed answer to grade against - a "does this run"
    scratchpad, not a grader. Same process isolation as `run_submission` (own subprocess/session,
    rlimits, killed and reaped as a group), just without the harness/comparison layer.
    """
    workdir = tempfile.mkdtemp(prefix="run-")
    os.chmod(workdir, 0o700)
    try:
        with open(os.path.join(workdir, "solution.py"), "w") as f:
            f.write(code)
        out_path, err_path = os.path.join(workdir, "stdout.txt"), os.path.join(workdir, "stderr.txt")
        started = time.monotonic()
        with open(out_path, "wb") as out, open(err_path, "wb") as err:
            proc = subprocess.Popen(
                [sys.executable, "-I", "-B", "solution.py"],
                cwd=workdir, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                env={"PATH": "/usr/local/bin:/usr/bin", "PYTHONHASHSEED": "0", "PYTHONDONTWRITEBYTECODE": "1"},
                preexec_fn=_limits(time_limit, memory_mb), start_new_session=True,
            )
            timed_out = False
            try:
                proc.wait(timeout=time_limit)
            except subprocess.TimeoutExpired:
                timed_out = True
            finally:
                _kill_group(proc)  # always: the student's code may have left children behind
        duration_ms = int((time.monotonic() - started) * 1000)
        stdout = _read(out_path, MAX_OUTPUT_BYTES)[:4000]
        stderr = _read(err_path, MAX_OUTPUT_BYTES)[:2000]

        if timed_out or proc.returncode == -signal.SIGXCPU:
            return {"status": "timeout", "stdout": stdout, "stderr": "", "error": f"Time limit exceeded ({time_limit:g}s)", "duration_ms": duration_ms}
        if proc.returncode == 0:
            return {"status": "ok", "stdout": stdout, "stderr": stderr, "error": None, "duration_ms": duration_ms}
        if proc.returncode in (-signal.SIGKILL, -signal.SIGSEGV, -signal.SIGXFSZ, -signal.SIGABRT):
            return {"status": "error", "stdout": stdout, "stderr": "", "error": "Process was killed (memory or output limit exceeded)", "duration_ms": duration_ms}
        last_line = stderr.strip().splitlines()[-1] if stderr.strip() else f"Process exited with status {proc.returncode}"
        return {"status": "error", "stdout": stdout, "stderr": stderr, "error": last_line[:300], "duration_ms": duration_ms}
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def run_submission(code: str, function_name: str, tests: list[dict], time_limit: float = 2.0, memory_mb: int = 128) -> list[dict]:
    """Run `code` against every test; returns one result dict per test (never raises for student errors)."""
    workdir = tempfile.mkdtemp(prefix="run-")
    os.chmod(workdir, 0o700)
    results: list[dict] = []
    try:
        with open(os.path.join(workdir, "solution.py"), "w") as f:
            f.write(code)
        with open(os.path.join(workdir, "harness.py"), "w") as f:
            f.write(HARNESS)
        timed_out_once = False
        for test in tests:
            visible = bool(test.get("visible"))
            if timed_out_once:
                results.append({"id": test["id"], "visible": visible, "duration_ms": 0, "status": "skipped", "passed": False,
                                "error": "Skipped: an earlier test exceeded the time limit"})
                continue
            run = _run_one(workdir, function_name, test["args"], time_limit, memory_mb)
            timed_out_once = run["status"] == "timeout"
            result = {"id": test["id"], "visible": visible, "duration_ms": run["duration_ms"]}
            if run["status"] == "ok":
                passed = canonical(run["value"]) == canonical(test["expected"])
                result.update(status="passed" if passed else "failed", passed=passed)
                if visible:
                    result.update(args=test["args"], expected=test["expected"], actual=run["value"], stdout=run["stdout"])
            else:
                result.update(status=run["status"], passed=False)
                if visible:
                    result.update(args=test["args"], expected=test["expected"], stdout=run.get("stdout", ""))
                result["error"] = run["error"] if visible else ("Time limit exceeded" if run["status"] == "timeout" else "Runtime error")
            results.append(result)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    return results
