"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { AssessmentCard } from "@/components/assessments/AssessmentCard";
import { api, ApiError } from "@/lib/api";
import type { AssessmentListItemOut } from "@/types";

function AssessmentsList() {
  const [assessments, setAssessments] = useState<AssessmentListItemOut[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.assessments.list();
      setAssessments(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load assessments.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-bold uppercase tracking-wider text-blue-600 mb-1">
          EVALUATIONS & TESTS
        </p>
        <h1 className="text-2xl font-extrabold text-slate-900">Assessments</h1>
        <p className="mt-1 text-sm text-slate-500">
          Check your understanding and update your skill profile as you progress.
        </p>
      </div>

      <div className="mt-6">
        {loading && <LoadingState label="Loading assessments..." />}
        {!loading && error && <ErrorState message={error} onRetry={load} />}
        {!loading && !error && assessments && assessments.length === 0 && (
          <EmptyState
            title="No assessments available yet"
            description="Assessments will appear here as they're assigned to your learning path."
          />
        )}
        {!loading && !error && assessments && assessments.length > 0 && (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {assessments.map((a) => (
              <AssessmentCard key={a.id} assessment={a} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function AssessmentsPage() {
  return (
    <ProtectedRoute>
      <AppLayout pageTitle="Assessments">
        <AssessmentsList />
      </AppLayout>
    </ProtectedRoute>
  );
}
