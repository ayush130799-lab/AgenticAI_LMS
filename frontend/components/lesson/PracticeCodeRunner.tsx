"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { CodeEditor } from "@/components/module-assessment/CodeEditor";
import { api, ApiError } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { PracticeRunOut } from "@/types";

/**
 * Inline "run my code" scratchpad for a lesson's practice exercises. There is no expected
 * output to grade against here (unlike the module-assessment coding editor) - this just
 * executes the student's code in the sandbox and shows whatever it printed or raised.
 */
export function PracticeCodeRunner({ lessonId }: { lessonId: string }) {
  const [open, setOpen] = useState(false);
  const [code, setCode] = useState("");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<PracticeRunOut | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  async function run() {
    if (running) return;
    if (!code.trim()) {
      setRunError("Write some code before running it.");
      return;
    }
    setRunning(true);
    setRunError(null);
    try {
      const res = await api.lessons.runPractice(lessonId, code);
      setResult(res);
    } catch (err) {
      setResult(null);
      setRunError(err instanceof ApiError ? err.detail : "Could not run your code. Please try again.");
    } finally {
      setRunning(false);
    }
  }

  if (!open) {
    return (
      <Button size="sm" variant="secondary" onClick={() => setOpen(true)}>
        Try it in the editor
      </Button>
    );
  }

  return (
    <div className="mt-3 space-y-3">
      <CodeEditor value={code} onChange={setCode} onRun={run} label="Practice code editor" />

      <div className="flex flex-wrap items-center gap-2">
        <Button size="sm" onClick={run} disabled={running}>
          {running ? "Running..." : "Run code"}
        </Button>
        <Button size="sm" variant="secondary" onClick={() => { setCode(""); setResult(null); setRunError(null); }} disabled={running || !code}>
          Clear
        </Button>
      </div>

      {runError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
          {runError}
        </p>
      )}

      {result && (
        <div
          className={cn(
            "space-y-2 rounded-lg border px-3 py-2 text-xs",
            result.status === "ok" ? "border-emerald-200 bg-emerald-50" : "border-amber-200 bg-amber-50",
          )}
        >
          <p className={cn("font-semibold", result.status === "ok" ? "text-emerald-700" : "text-amber-800")}>
            {result.status === "ok" ? "✓ Ran successfully" : result.status === "timeout" ? "⏱ Time limit exceeded" : "✗ Error"}
            <span className="ml-2 font-normal text-ink-400">{result.duration_ms}ms</span>
          </p>
          {result.stdout && (
            <pre className="max-h-48 overflow-auto whitespace-pre-wrap break-words rounded-md bg-white/70 p-2 font-mono text-[11px] text-ink-900">
              {result.stdout}
            </pre>
          )}
          {result.error && <p className="whitespace-pre-wrap break-words font-mono text-[11px] text-red-700">{result.error}</p>}
          {result.status === "ok" && result.stderr && (
            <pre className="max-h-32 overflow-auto whitespace-pre-wrap break-words rounded-md bg-white/70 p-2 font-mono text-[11px] text-amber-700">
              {result.stderr}
            </pre>
          )}
          {!result.stdout && !result.error && !result.stderr && <p className="text-ink-400">No output.</p>}
        </div>
      )}
    </div>
  );
}
