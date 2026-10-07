"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { AssessmentResultView } from "@/components/module-assessment/AssessmentResultView";
import { AssessmentTaker } from "@/components/module-assessment/AssessmentTaker";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { ErrorState } from "@/components/ui/ErrorState";
import { LoadingState } from "@/components/ui/LoadingState";
import { api, ApiError } from "@/lib/api";
import { cn, titleCase } from "@/lib/utils";
import type {
  AssessmentLevelOut,
  AssessmentSummaryOut,
  AttemptResultOut,
  CourseDetailOut,
  ModuleProgressOut,
  StartAttemptOut,
} from "@/types";

type Screen = "intro" | "taking" | "result";

function ModulePanel({ children }: { children: React.ReactNode }) {
  return <div className="mx-auto max-w-2xl">{children}</div>;
}

function AssessmentPageContent() {
  const params = useParams<{ moduleId: string }>();
  const moduleId = params.moduleId;

  const [progress, setProgress] = useState<ModuleProgressOut | null>(null);
  const [course, setCourse] = useState<CourseDetailOut | null>(null);
  const [summaries, setSummaries] = useState<AssessmentSummaryOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [screen, setScreen] = useState<Screen>("intro");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [session, setSession] = useState<StartAttemptOut | null>(null);
  const [result, setResult] = useState<AttemptResultOut | null>(null);
  const [starting, setStarting] = useState(false);
  const [startError, setStartError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const state = await api.modules.progress(moduleId);
      setProgress(state);
      const [courseDetail, list] = await Promise.all([
        api.courses.get(state.course_id).catch(() => null),
        state.has_assessment && !state.locked ? api.modules.assessments(moduleId).catch(() => []) : Promise.resolve([]),
      ]);
      setCourse(courseDetail);
      setSummaries(list);
      const levels = state.assessment?.levels ?? [];
      setSelectedId((cur) => cur ?? (levels.find((l) => l.required) ?? levels[0])?.assessment_id ?? null);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load this module's assessment.");
    } finally {
      setLoading(false);
    }
  }, [moduleId]);

  useEffect(() => {
    load();
  }, [load]);

  const moduleInCourse = useMemo(() => course?.modules.find((m) => m.id === moduleId) ?? null, [course, moduleId]);
  const reviewHref = useMemo(() => {
    const lesson = moduleInCourse?.lessons[0];
    return lesson ? `/lessons/${lesson.id}` : progress ? `/courses/${progress.course_id}` : "/courses";
  }, [moduleInCourse, progress]);
  const firstIncompleteHref = useMemo(() => {
    const lesson = moduleInCourse?.lessons.find((l) => l.progress_status !== "completed") ?? moduleInCourse?.lessons[0];
    return lesson ? `/lessons/${lesson.id}` : reviewHref;
  }, [moduleInCourse, reviewHref]);
  const nextHref = useMemo(() => {
    if (!course || !progress) return null;
    const idx = course.modules.findIndex((m) => m.id === moduleId);
    const next = idx >= 0 ? course.modules[idx + 1] : undefined;
    if (!next) return `/courses/${progress.course_id}`;
    return next.lessons[0] ? `/lessons/${next.lessons[0].id}` : `/courses/${progress.course_id}`;
  }, [course, progress, moduleId]);

  async function startAttempt() {
    if (!selectedId) return;
    setStarting(true);
    setStartError(null);
    try {
      const started = await api.moduleAssessments.start(selectedId);
      setSession(started);
      setResult(null);
      setScreen("taking");
    } catch (err) {
      setStartError(err instanceof ApiError ? err.detail : "Could not start the assessment. Please try again.");
    } finally {
      setStarting(false);
    }
  }

  async function handleFinished(res: AttemptResultOut) {
    setResult(res);
    setScreen("result");
    window.scrollTo({ top: 0 });
    load(); // refresh module state (completion / unlocks) from the server
  }

  if (loading && !progress) return <LoadingState label="Loading assessment..." fullHeight />;
  if (error || !progress) {
    return (
      <ModulePanel>
        <ErrorState message={error ?? "Module not found."} onRetry={load} />
      </ModulePanel>
    );
  }

  const backToCourse = <Button variant="secondary" href={`/courses/${progress.course_id}`}>Back to course</Button>;

  if (screen === "taking" && session) {
    return <AssessmentTaker key={session.attempt.id} session={session} onFinished={handleFinished} />;
  }
  if (screen === "result" && result) {
    return (
      <AssessmentResultView
        data={result}
        reviewHref={reviewHref}
        nextHref={nextHref}
        retrying={starting}
        onRetry={startAttempt}
      />
    );
  }

  if (progress.locked) {
    return (
      <ModulePanel>
        <EmptyState
          icon="🔒"
          title="This module is locked"
          description={progress.locked_reason ?? "Complete the previous module's assessment to unlock this module."}
          action={backToCourse}
        />
      </ModulePanel>
    );
  }

  if (!progress.has_assessment || !progress.assessment) {
    return (
      <ModulePanel>
        <EmptyState
          title="No assessment has been configured for this module yet."
          description="You can continue with the next lesson - nothing is blocked."
          action={backToCourse}
        />
      </ModulePanel>
    );
  }

  const state = progress.assessment;
  const levels: AssessmentLevelOut[] = state.levels;
  const selected = levels.find((l) => l.assessment_id === selectedId) ?? levels[0];
  const summary = summaries.find((s) => s.id === selected?.assessment_id) ?? summaries[0];

  if (state.status === "locked") {
    return (
      <ModulePanel>
        <EmptyState
          icon="🔒"
          title="Module assessment locked"
          description={state.unavailable_reason ?? "Complete all lessons in this module to unlock the assessment."}
          action={
            <div className="space-y-3">
              <p className="text-sm text-ink-500">
                Lessons completed: <span className="font-semibold text-ink-900">{progress.lessons_completed} / {progress.lessons_total}</span>
              </p>
              <div className="flex flex-wrap justify-center gap-3">
                <Button href={firstIncompleteHref}>Continue lessons</Button>
                {backToCourse}
              </div>
            </div>
          }
        />
      </ModulePanel>
    );
  }

  const passedAlready = state.status === "passed";
  const canAttemptSelected = !!selected && !selected.passed;

  return (
    <div className="mx-auto max-w-2xl space-y-5">
      <Card>
        <p className="text-xs font-bold uppercase tracking-widest text-brand-blue">Module Assessment</p>
        <h1 className="mt-1 text-2xl font-extrabold text-ink-900">{progress.title}</h1>

        {passedAlready && (
          <div className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-900">
            <p className="font-semibold">You have already passed this module&apos;s assessment ✓</p>
            <p className="mt-1">
              Best score {state.best_percentage}% after {state.attempts_count} attempt{state.attempts_count === 1 ? "" : "s"}. This module is completed.
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              {nextHref && <Button size="sm" href={nextHref}>Continue to Next Module →</Button>}
              {backToCourse}
            </div>
          </div>
        )}

        {levels.length > 1 && (
          <div className="mt-5">
            <p className="text-xs font-semibold uppercase tracking-wide text-ink-400">Difficulty</p>
            <div className="mt-2 flex flex-wrap gap-2" role="radiogroup" aria-label="Assessment difficulty">
              {levels.map((l) => (
                <button
                  key={l.assessment_id}
                  role="radio"
                  aria-checked={l.assessment_id === selected?.assessment_id}
                  onClick={() => setSelectedId(l.assessment_id)}
                  className={cn(
                    "rounded-full border px-4 py-1.5 text-sm font-semibold transition-colors",
                    l.assessment_id === selected?.assessment_id
                      ? "border-brand-blue bg-brand-blue text-white"
                      : "border-ink-200 bg-white text-ink-700 hover:border-brand-blue/60"
                  )}
                >
                  {titleCase(l.level)}
                  {l.required ? " · required" : ""}
                  {l.passed ? " ✓" : ""}
                </button>
              ))}
            </div>
            <p className="mt-2 text-xs text-ink-500">
              Passing the {titleCase(state.required_level)} assessment (or a harder one) completes the module.
            </p>
          </div>
        )}

        <div className="mt-5 rounded-xl bg-ink-100/60 p-4 text-sm text-ink-700">
          <p className="font-semibold text-ink-900">
            {summary?.total_questions ?? 7} Questions
          </p>
          <p>
            {summary?.mcq_count ?? 3} MCQ · {summary?.quiz_count ?? 2} Quiz · {summary?.coding_count ?? 2} Coding
          </p>
          <ul className="mt-3 space-y-1">
            <li>Passing Score: {summary?.passing_score_percent ?? 80}%</li>
            <li>Coding Requirement: At least {summary?.required_coding_questions ?? 1} successful coding solution</li>
            <li className="text-xs text-ink-500">
              Every question counts equally. A coding question is passed only when all of its tests pass. Coding answers run in an isolated sandbox.
            </li>
          </ul>
        </div>

        {selected && selected.attempts_count > 0 && (
          <p className="mt-4 text-sm text-ink-600">
            Previous attempts: {selected.attempts_count} · best score {selected.best_percentage}%
          </p>
        )}

        {startError && (
          <p role="alert" className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
            {startError}
          </p>
        )}

        {canAttemptSelected && (
          <div className="mt-6 flex flex-wrap items-center gap-3">
            <Button onClick={startAttempt} disabled={starting}>
              {starting ? "Starting..." : selected?.in_progress_attempt_id ? "Resume Assessment" : selected && selected.attempts_count > 0 ? "Retry Assessment" : "Start Assessment"}
            </Button>
            {!passedAlready && <Button variant="secondary" href={reviewHref}>Review Module</Button>}
            {selected?.in_progress_attempt_id && <Badge tone="amber">Attempt in progress</Badge>}
          </div>
        )}
      </Card>
    </div>
  );
}

export default function ModuleAssessmentPage() {
  return (
    <ProtectedRoute>
      <AppLayout pageTitle="Module Assessment">
        <AssessmentPageContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
