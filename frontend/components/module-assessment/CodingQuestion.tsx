"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { CodeEditor } from "@/components/module-assessment/CodeEditor";
import { api, ApiError } from "@/lib/api";
import { cn } from "@/lib/utils";
import type { CodeTestResult, ModuleQuestionView } from "@/types";

interface CodingQuestionProps {
  question: ModuleQuestionView;
  attemptId: string;
  code: string;
  onCodeChange: (code: string) => void;
  disabled?: boolean;
}

const show = (value: unknown) => JSON.stringify(value);

export function CodingQuestion({ question, attemptId, code, onCodeChange, disabled }: CodingQuestionProps) {
  const coding = question.coding!;
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState<CodeTestResult[] | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  async function run() {
    if (running || disabled) return;
    if (!code.trim()) {
      setRunError("Write some code before running it.");
      return;
    }
    setRunning(true);
    setRunError(null);
    try {
      const res = await api.moduleAssessments.runCode(attemptId, question.id, code);
      setResults(res.results);
    } catch (err) {
      setResults(null);
      setRunError(err instanceof ApiError ? err.detail : "Could not run your code. Please try again.");
    } finally {
      setRunning(false);
    }
  }

  const passed = results?.filter((r) => r.passed).length ?? 0;

  return (
    <div className="space-y-4">
      <div className="rounded-xl bg-ink-100/60 p-4 text-sm text-ink-700">
        <p className="text-xs font-semibold uppercase tracking-wide text-ink-400">Implement</p>
        <code className="mt-1 block break-all font-mono text-[13px] text-ink-900">{coding.function_name}()</code>
        <p className="mt-2">{coding.expected_output}</p>
      </div>

      {coding.sample_tests.length > 0 && (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-ink-400">Examples</p>
          <ul className="mt-2 space-y-1.5">
            {coding.sample_tests.map((t, i) => (
              <li key={i} className="overflow-x-auto rounded-lg border border-ink-200 bg-white px-3 py-2 font-mono text-xs text-ink-700">
                <span className="whitespace-pre">
                  {coding.function_name}({t.args.map(show).join(", ")}) → <span className="font-semibold text-ink-900">{show(t.expected)}</span>
                </span>
              </li>
            ))}
          </ul>
          {coding.hidden_test_count > 0 && (
            <p className="mt-2 text-xs text-ink-400">
              Your solution is also checked against {coding.hidden_test_count} hidden test{coding.hidden_test_count === 1 ? "" : "s"}. It passes only if every test passes.
            </p>
          )}
        </div>
      )}

      <CodeEditor value={code} onChange={onCodeChange} onRun={run} disabled={disabled} />

      <div className="flex flex-wrap items-center gap-2">
        <Button size="sm" onClick={run} disabled={running || disabled}>
          {running ? "Running..." : "Run sample tests"}
        </Button>
        <Button size="sm" variant="secondary" onClick={() => onCodeChange(coding.starter_code)} disabled={disabled || code === coding.starter_code}>
          Reset to starter code
        </Button>
        {results && (
          <span className={cn("text-xs font-semibold", passed === results.length ? "text-emerald-600" : "text-amber-700")}>
            {passed}/{results.length} sample tests passed
          </span>
        )}
      </div>

      {runError && (
        <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
          {runError}
        </p>
      )}

      {results && (
        <ul className="space-y-2" aria-label="Sample test results">
          {results.map((r, i) => (
            <li key={r.id} className={cn("rounded-lg border px-3 py-2 text-xs", r.passed ? "border-emerald-200 bg-emerald-50" : "border-red-200 bg-red-50")}>
              <p className={cn("font-semibold", r.passed ? "text-emerald-700" : "text-red-700")}>
                {r.passed ? "✓" : "✗"} Test {i + 1}: {r.passed ? "passed" : r.status === "timeout" ? "time limit exceeded" : r.status === "error" ? "error" : "wrong answer"}
              </p>
              {!r.passed && (
                <div className="mt-1 space-y-0.5 overflow-x-auto font-mono text-[11px] text-ink-700">
                  {r.args && <p className="whitespace-pre">input: {r.args.map(show).join(", ")}</p>}
                  {"expected" in r && <p className="whitespace-pre">expected: {show(r.expected)}</p>}
                  {"actual" in r && <p className="whitespace-pre">got: {show(r.actual)}</p>}
                  {r.error && <p className="whitespace-pre-wrap break-words text-red-700">{r.error}</p>}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
