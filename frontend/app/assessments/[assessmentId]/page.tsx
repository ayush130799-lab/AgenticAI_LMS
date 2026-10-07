"use client";

import { useEffect, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { QuestionInput } from "@/components/assessments/QuestionInput";
import { AssessmentResults } from "@/components/assessments/AssessmentResults";
import { api, ApiError } from "@/lib/api";
import type {
  AnswerValue,
  AssessmentOut,
  DiagnosticResultOut,
  SubmitAssessmentResponse,
} from "@/types";

function TakeAssessment() {
  const params = useParams<{ assessmentId: string }>();
  const searchParams = useSearchParams();
  const isDiagnostic = searchParams.get("diagnostic") === "1";

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [assessment, setAssessment] = useState<AssessmentOut | null>(null);
  const [answers, setAnswers] = useState<Record<string, AnswerValue>>({});
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<SubmitAssessmentResponse | null>(null);
  const [diagnosticResult, setDiagnosticResult] = useState<DiagnosticResultOut | null>(null);

  async function start() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.assessments.start({ assessment_id: params.assessmentId });
      setAttemptId(res.attempt_id);
      setAssessment(res.assessment);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to start this assessment.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    start();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.assessmentId]);

  function setAnswer(questionId: string, value: AnswerValue) {
    setAnswers((prev) => ({ ...prev, [questionId]: value }));
  }

  const unanswered = assessment
    ? assessment.questions.filter((q) => !answers[q.id]).length
    : 0;

  async function handleSubmit() {
    if (!attemptId) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await api.assessments.submit({ attempt_id: attemptId, answers });
      setResult(res);
      if (isDiagnostic) {
        try {
          const diag = await api.assessments.diagnosticResult();
          setDiagnosticResult(diag);
        } catch {
          // diagnostic result is a bonus view, non-fatal if unavailable
        }
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to submit your answers.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <LoadingState label="Preparing your assessment..." fullHeight />;
  if (error && !assessment) return <ErrorState message={error} onRetry={start} className="my-10" />;
  if (!assessment) return null;

  if (result) {
    return (
      <div className="mx-auto max-w-3xl">
        <AssessmentResults result={result} diagnosticResult={diagnosticResult} />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl">
      <Card className="mb-6">
        <h1 className="text-2xl font-bold text-ink-900">{assessment.title}</h1>
        {assessment.description && <p className="mt-2 text-sm text-ink-500">{assessment.description}</p>}
        <p className="mt-3 text-xs font-medium text-ink-400">
          {assessment.questions.length} questions &middot; Passing score{" "}
          {Math.round(assessment.passing_score * 100)}%
          {assessment.time_limit_minutes ? ` · Time limit ${assessment.time_limit_minutes} min` : ""}
        </p>
      </Card>

      <div className="space-y-4">
        {assessment.questions.map((q, idx) => (
          <QuestionInput
            key={q.id}
            question={q}
            value={answers[q.id]}
            onChange={(v) => setAnswer(q.id, v)}
            index={idx}
          />
        ))}
      </div>

      {error && <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}

      <div className="mt-6 flex items-center justify-between rounded-2xl border border-ink-200 bg-white p-4">
        <p className="text-sm text-ink-500">
          {unanswered === 0 ? "All questions answered." : `${unanswered} question(s) remaining.`}
        </p>
        <Button onClick={handleSubmit} disabled={submitting}>
          {submitting ? "Submitting..." : "Submit assessment"}
        </Button>
      </div>
    </div>
  );
}

export default function AssessmentTakePage() {
  return (
    <ProtectedRoute>
      <AppLayout pageTitle="Assessments">
        <TakeAssessment />
      </AppLayout>
    </ProtectedRoute>
  );
}
