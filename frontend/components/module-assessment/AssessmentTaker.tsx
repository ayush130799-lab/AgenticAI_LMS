"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { CodingQuestion } from "@/components/module-assessment/CodingQuestion";
import { ObjectiveQuestion, isAnswered } from "@/components/module-assessment/ObjectiveQuestion";
import { api, ApiError } from "@/lib/api";
import { cn, titleCase } from "@/lib/utils";
import type { AttemptResultOut, ModuleAnswer, StartAttemptOut } from "@/types";

type Answers = Record<string, ModuleAnswer | null>;
type SaveState = "idle" | "saving" | "saved" | "error";

const TYPE_LABEL = { mcq: "Multiple choice", quiz: "Quiz", coding: "Coding" } as const;

interface AssessmentTakerProps {
  session: StartAttemptOut;
  onFinished: (result: AttemptResultOut) => void;
}

export function AssessmentTaker({ session, onFinished }: AssessmentTakerProps) {
  const { attempt, assessment } = session;
  const questions = [...assessment.questions].sort((a, b) => a.order - b.order);
  const positionKey = `lms_ma_pos_${attempt.id}`;

  const [answers, setAnswers] = useState<Answers>(session.saved_answers ?? {});
  const [index, setIndex] = useState(0);
  const [saveState, setSaveState] = useState<SaveState>("idle");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [confirming, setConfirming] = useState(false);
  const dirty = useRef(false);

  useEffect(() => {
    try {
      const saved = Number(window.sessionStorage.getItem(positionKey));
      if (Number.isInteger(saved) && saved >= 0 && saved < questions.length) setIndex(saved);
    } catch {
      // storage unavailable: start at the first question
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attempt.id]);

  useEffect(() => {
    try {
      window.sessionStorage.setItem(positionKey, String(index));
    } catch {
      // ignore
    }
  }, [index, positionKey]);

  const save = useCallback(
    async (snapshot: Answers) => {
      setSaveState("saving");
      try {
        await api.moduleAssessments.saveAnswers(attempt.id, snapshot);
        setSaveState("saved");
      } catch {
        setSaveState("error");
      }
    },
    [attempt.id]
  );

  // Debounced autosave: a browser refresh resumes the same attempt with these answers.
  useEffect(() => {
    if (!dirty.current) return;
    const timer = setTimeout(() => {
      dirty.current = false;
      save(answers);
    }, 700);
    return () => clearTimeout(timer);
  }, [answers, save]);

  function setAnswer(questionId: string, answer: ModuleAnswer) {
    dirty.current = true;
    setSaveState("idle");
    setAnswers((prev) => ({ ...prev, [questionId]: answer }));
  }

  const question = questions[index];
  const answeredCount = questions.filter((q) => isAnswered(q, answers[q.id])).length;
  const unanswered = questions.length - answeredCount;
  const isLast = index === questions.length - 1;

  async function submit() {
    setSubmitting(true);
    setSubmitError(null);
    setConfirming(false);
    try {
      const result = await api.moduleAssessments.submit(attempt.id, answers);
      try {
        window.sessionStorage.removeItem(positionKey);
      } catch {
        // ignore
      }
      onFinished(result);
    } catch (err) {
      setSubmitError(
        err instanceof ApiError && err.status !== 0
          ? err.detail
          : "Your submission could not be completed. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  const code = (q: typeof question) => answers[q.id]?.code ?? q.coding?.starter_code ?? "";

  return (
    <div className="mx-auto max-w-3xl space-y-5">
      <Card>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-xs font-bold uppercase tracking-widest text-brand-blue">Module Assessment</p>
            <h1 className="mt-1 text-xl font-extrabold text-ink-900 sm:text-2xl">{assessment.title}</h1>
            <p className="mt-1 text-sm text-ink-500">
              {assessment.total_questions} Questions · {assessment.mcq_count} MCQ · {assessment.quiz_count} Quiz · {assessment.coding_count} Coding
            </p>
          </div>
          <div className="flex flex-col items-end gap-1 text-right text-xs text-ink-500">
            <Badge tone="blue">Attempt {attempt.attempt_number}</Badge>
            <span aria-live="polite">
              {saveState === "saving" && "Saving..."}
              {saveState === "saved" && "All changes saved"}
              {saveState === "error" && <span className="text-amber-700">Couldn&apos;t save yet - will retry</span>}
            </span>
          </div>
        </div>
        <div className="mt-4">
          <ProgressBar value={answeredCount} max={questions.length} label={`${answeredCount} of ${questions.length} answered`} />
        </div>
      </Card>

      <nav aria-label="Questions" className="flex flex-wrap gap-2">
        {questions.map((q, i) => (
          <button
            key={q.id}
            onClick={() => setIndex(i)}
            aria-label={`Question ${i + 1}, ${TYPE_LABEL[q.type]}${isAnswered(q, answers[q.id]) ? ", answered" : ""}`}
            aria-current={i === index ? "step" : undefined}
            className={cn(
              "h-9 w-9 rounded-full border text-sm font-semibold transition-colors",
              i === index
                ? "border-brand-blue bg-brand-blue text-white"
                : isAnswered(q, answers[q.id])
                  ? "border-brand-blue/40 bg-surface-tint-blue text-brand-blue-dark"
                  : "border-ink-200 bg-white text-ink-500 hover:border-brand-blue/60"
            )}
          >
            {i + 1}
          </button>
        ))}
      </nav>

      <Card>
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-semibold text-ink-500">
            Question {index + 1} of {questions.length}
          </span>
          <Badge tone={question.type === "coding" ? "purple" : question.type === "quiz" ? "cyan" : "blue"}>{TYPE_LABEL[question.type]}</Badge>
          {question.quiz_format && <Badge tone="gray">{titleCase(question.quiz_format)}</Badge>}
        </div>
        <h2 className="mt-3 whitespace-pre-wrap break-words text-base font-semibold text-ink-900 sm:text-lg">{question.prompt}</h2>

        <div className="mt-5">
          {question.type === "coding" ? (
            <CodingQuestion
              key={question.id}
              question={question}
              attemptId={attempt.id}
              code={code(question)}
              onCodeChange={(value) => setAnswer(question.id, { code: value })}
              disabled={submitting}
            />
          ) : (
            <ObjectiveQuestion question={question} value={answers[question.id]} onChange={(a) => setAnswer(question.id, a)} disabled={submitting} />
          )}
        </div>
      </Card>

      {submitError && (
        <p role="alert" className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600">
          {submitError}
        </p>
      )}

      {confirming && (
        <div role="alertdialog" aria-label="Confirm submission" className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <p className="font-semibold">
            You have {unanswered} unanswered question{unanswered === 1 ? "" : "s"}.
          </p>
          <p className="mt-1">Unanswered questions score zero. Submit anyway?</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Button size="sm" onClick={submit} disabled={submitting}>
              Submit anyway
            </Button>
            <Button size="sm" variant="secondary" onClick={() => setConfirming(false)}>
              Keep working
            </Button>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between gap-3">
        <Button variant="secondary" onClick={() => setIndex((i) => Math.max(0, i - 1))} disabled={index === 0 || submitting}>
          ← Previous
        </Button>
        {isLast ? (
          <Button onClick={() => (unanswered > 0 ? setConfirming(true) : submit())} disabled={submitting}>
            {submitting ? "Submitting..." : "Submit Assessment"}
          </Button>
        ) : (
          <Button onClick={() => setIndex((i) => Math.min(questions.length - 1, i + 1))} disabled={submitting}>
            Next →
          </Button>
        )}
      </div>
    </div>
  );
}
