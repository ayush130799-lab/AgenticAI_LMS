"use client";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { cn, titleCase } from "@/lib/utils";
import type { AttemptResultOut, ModuleAnswer, QuestionResultOut } from "@/types";

interface AssessmentResultViewProps {
  data: AttemptResultOut;
  /** Where "Review Module" goes (first lesson of this module). */
  reviewHref: string;
  /** Where "Continue to Next Module" goes when passed. */
  nextHref: string | null;
  onRetry: () => void;
  retrying?: boolean;
}

function Check({ ok, children }: { ok: boolean; children: React.ReactNode }) {
  return (
    <li className={cn("flex items-start gap-2 text-sm", ok ? "text-emerald-700" : "text-red-700")}>
      <span aria-hidden="true">{ok ? "✓" : "✗"}</span>
      <span>{children}</span>
    </li>
  );
}

function describeAnswer(q: QuestionResultOut, answer: ModuleAnswer | null | undefined): string {
  if (!answer) return "No answer";
  const label = (id: string) => q.options.find((o) => o.id === id)?.text ?? id;
  if (answer.choices) return answer.choices.map(label).join(", ") || "No answer";
  if (answer.choice) return label(answer.choice);
  if (answer.text) return answer.text;
  return "No answer";
}

function describeKey(q: QuestionResultOut): string | null {
  const key = q.correct_answer;
  if (!key) return null;
  const label = (id: string) => (q.quiz_format === "true_false" ? titleCase(id) : q.options.find((o) => o.id === id)?.text ?? id);
  if (key.choices) return key.choices.map(label).join(", ");
  if (key.choice) return label(key.choice);
  if (key.accepted) return key.accepted.join(" / ");
  return null;
}

function QuestionReview({ q, passed }: { q: QuestionResultOut; passed: boolean }) {
  const key = describeKey(q);
  return (
    <li className={cn("rounded-xl border p-4", q.is_correct ? "border-emerald-200 bg-emerald-50/50" : "border-red-200 bg-red-50/50")}>
      <div className="flex flex-wrap items-center gap-2 text-xs font-semibold">
        <span className={q.is_correct ? "text-emerald-700" : "text-red-700"}>
          {q.is_correct ? "✓ Correct" : "✗ Incorrect"} · {q.points_awarded}/{q.points} pt
        </span>
        <Badge tone="gray">{q.type === "mcq" ? "MCQ" : q.type === "quiz" ? "Quiz" : "Coding"}</Badge>
      </div>
      <p className="mt-2 whitespace-pre-wrap break-words text-sm font-semibold text-ink-900">
        {q.order}. {q.prompt}
      </p>

      {q.type !== "coding" && (
        <p className="mt-2 break-words text-sm text-ink-600">
          <span className="text-ink-400">Your answer: </span>
          {describeAnswer(q, q.your_answer)}
        </p>
      )}
      {passed && key && !q.is_correct && (
        <p className="mt-1 break-words text-sm text-emerald-800">
          <span className="text-ink-400">Correct answer: </span>
          {key}
        </p>
      )}

      {q.coding && (
        <div className="mt-2 text-sm">
          <p className="text-ink-600">
            Tests passed: <span className="font-semibold">{q.coding.passed_count}/{q.coding.total_count}</span>
            {q.coding.total_count === 0 && " (no code submitted)"}
          </p>
          <ul className="mt-1.5 space-y-1">
            {q.coding.tests.map((t, i) => (
              <li key={t.id} className={cn("overflow-x-auto rounded-md px-2 py-1 font-mono text-[11px]", t.passed ? "bg-emerald-100/60 text-emerald-800" : "bg-red-100/60 text-red-800")}>
                <span className="whitespace-pre">
                  {t.passed ? "✓" : "✗"} {t.visible ? `Test ${i + 1}` : `Hidden test ${i + 1}`}
                  {t.visible && !t.passed && t.args ? ` - input ${JSON.stringify(t.args)}, expected ${JSON.stringify(t.expected)}, got ${JSON.stringify(t.actual)}` : ""}
                  {!t.passed && t.error ? ` - ${t.error}` : ""}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {passed && q.explanation && <p className="mt-3 border-t border-ink-200 pt-2 text-sm text-ink-600">{q.explanation}</p>}
      {passed && q.reference_solution && !q.is_correct && (
        <pre className="mt-2 overflow-x-auto rounded-lg bg-slate-950 p-3 font-mono text-xs text-slate-100">{q.reference_solution}</pre>
      )}
    </li>
  );
}

export function AssessmentResultView({ data, reviewHref, nextHref, onRetry, retrying }: AssessmentResultViewProps) {
  const r = data.result;
  if (!r) return null;
  const passed = r.passed;

  return (
    <div className="mx-auto max-w-3xl space-y-5">
      <Card className={cn("text-center", passed ? "border-emerald-200 bg-emerald-50/40" : "border-red-200 bg-red-50/30")}>
        <p className={cn("text-xs font-bold uppercase tracking-widest", passed ? "text-emerald-700" : "text-red-700")}>
          Attempt {data.attempt.attempt_number}
        </p>
        <h1 className="mt-1 text-2xl font-extrabold text-ink-900 sm:text-3xl">{passed ? "Assessment Passed" : "Assessment Not Passed"}</h1>
        <p className="mt-4 text-4xl font-black text-ink-900">
          {r.questions_correct} / {r.questions_total}
        </p>
        <p className="mt-1 text-lg font-semibold text-ink-600">{r.percentage}%</p>
        {!passed && <p className="mt-1 text-sm text-ink-500">Required: {r.passing_percent}%</p>}

        <dl className="mx-auto mt-5 grid max-w-md grid-cols-3 gap-3 text-sm">
          {(
            [
              ["MCQ", r.mcq],
              ["Quiz", r.quiz],
              ["Coding", r.coding],
            ] as const
          ).map(([label, score]) => (
            <div key={label} className="rounded-xl bg-white p-3 shadow-card">
              <dt className="text-xs font-semibold uppercase tracking-wide text-ink-400">{label}</dt>
              <dd className="mt-1 text-lg font-bold text-ink-900">
                {score.correct} / {score.total}
              </dd>
            </div>
          ))}
        </dl>

        <ul className="mx-auto mt-5 max-w-md space-y-1.5 text-left">
          <Check ok={!!r.score_requirement_met}>
            {r.score_requirement_met ? "Passing score achieved" : `Passing score not reached (need ${r.passing_percent}%)`}
          </Check>
          <Check ok={!!r.coding_requirement_met}>
            {r.coding_requirement_met
              ? "Coding requirement achieved"
              : `Coding requirement not met (at least ${r.required_coding} coding solution must pass)`}
          </Check>
        </ul>

        {passed ? (
          <div className="mt-6">
            <p className="text-sm font-semibold text-emerald-800">Module Completed</p>
            <p className="mt-1 text-sm text-ink-600">
              {data.next_module ? "The next module is now unlocked." : "You have completed the last module of this course."}
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-3">
              {nextHref && <Button href={nextHref}>Continue to Next Module →</Button>}
              <Button variant="secondary" href={data.module ? `/courses/${data.module.course_id}` : "/courses"}>
                Back to course
              </Button>
            </div>
          </div>
        ) : (
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <Button variant="secondary" href={reviewHref}>
              Review Module
            </Button>
            <Button onClick={onRetry} disabled={retrying}>
              {retrying ? "Starting..." : "Retry Assessment"}
            </Button>
          </div>
        )}
      </Card>

      {!passed && r.weak_concepts.length > 0 && (
        <Card>
          <h2 className="text-base font-bold text-ink-900">Concepts to revisit</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            {r.weak_concepts.map((c) => (
              <Badge key={c} tone="amber">
                {c}
              </Badge>
            ))}
          </div>
          <p className="mt-3 text-xs text-ink-500">
            Correct answers and explanations are shown once you pass, so a retry tests what you have learned.
          </p>
        </Card>
      )}

      <Card>
        <h2 className="text-base font-bold text-ink-900">Question review</h2>
        <p className="mt-1 text-xs text-ink-500">
          Scoring: every question is worth {data.questions[0]?.points ?? 1} point. A coding question is passed only when all of its test cases pass.
        </p>
        <ul className="mt-4 space-y-3">
          {data.questions.map((q) => (
            <QuestionReview key={q.id} q={q} passed={passed} />
          ))}
        </ul>
      </Card>
    </div>
  );
}
