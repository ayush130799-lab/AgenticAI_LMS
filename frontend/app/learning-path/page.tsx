"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { useToast } from "@/components/ui/Toast";
import { api, ApiError } from "@/lib/api";
import type { LearningPlanOut } from "@/types";

const STEP_ICON: Record<string, string> = {
  lesson: "📖",
  course: "📘",
  assessment: "🩺",
  project: "🚀",
  skill: "🧩",
  review: "🔁",
};

function targetHref(stepType: string, targetId: string | null): string {
  if (!targetId) return "/courses";
  switch (stepType) {
    case "lesson":
      return `/lessons/${targetId}`;
    case "course":
      return `/courses/${targetId}`;
    case "project":
      return `/projects/${targetId}`;
    case "assessment":
      return `/assessments/${targetId}`;
    default:
      return "/skills";
  }
}

function LearningPathContent() {
  const { showToast } = useToast();
  const [plan, setPlan] = useState<LearningPlanOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.learningPath.get();
      setPlan(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load your AI learning path.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleRegenerate() {
    setRegenerating(true);
    try {
      const data = await api.learningPath.generate();
      setPlan(data);
      showToast("Learning path regenerated.", "success");
    } catch (err) {
      showToast(err instanceof ApiError ? err.detail : "Unable to regenerate your learning path.", "error");
    } finally {
      setRegenerating(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-blue-600 mb-1">
            PERSONALIZED SEQUENCE
          </p>
          <h1 className="text-2xl font-extrabold text-slate-900">Your AI Learning Path</h1>
          <p className="mt-1 text-sm text-slate-500">
            Generated from your diagnostic assessment and ongoing curriculum progress.
          </p>
        </div>
        <Button onClick={handleRegenerate} disabled={regenerating || loading} variant="secondary">
          {regenerating ? "Regenerating..." : "Regenerate Path"}
        </Button>
      </div>

      <div className="mt-6">
        {loading && <LoadingState label="Building your personalized learning path..." />}
        {!loading && error && <ErrorState message={error} onRetry={load} />}
        {!loading && !error && plan && (
          <div className="space-y-6">
            <Card>
              <h2 className="text-base font-bold text-slate-900">Summary</h2>
              <p className="mt-2 text-sm text-slate-600 leading-relaxed">{plan.summary}</p>
              <h3 className="mt-4 text-sm font-semibold text-slate-800">Why this path</h3>
              <p className="mt-1 text-sm text-slate-600 leading-relaxed">{plan.reasoning}</p>
            </Card>

            <div className="relative space-y-4 border-l-2 border-dashed border-slate-200 pl-6">
              {plan.recommended_path.map((step, idx) => (
                <div key={idx} className="relative">
                  <span className="absolute -left-[31px] flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white shadow-xs">
                    {idx + 1}
                  </span>
                  <Link
                    href={targetHref(step.step_type, step.target_id)}
                    className="block rounded-2xl border border-slate-200 bg-white p-5 transition-all hover:border-blue-500 hover:shadow-xs"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xl">{STEP_ICON[step.step_type] || "•"}</span>
                      <Badge tone="blue">{step.step_type}</Badge>
                    </div>
                    <p className="mt-2 text-sm font-bold text-slate-900">{step.title}</p>
                    <p className="mt-1 text-sm text-slate-500">{step.reason}</p>
                    {step.skill_focus.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {step.skill_focus.map((s) => (
                          <Badge key={s} tone="gray">
                            {s}
                          </Badge>
                        ))}
                      </div>
                    )}
                  </Link>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function LearningPathPage() {
  return (
    <ProtectedRoute>
      <AppLayout pageTitle="AI Learning Path">
        <LearningPathContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
