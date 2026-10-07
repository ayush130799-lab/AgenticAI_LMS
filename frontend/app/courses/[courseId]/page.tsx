"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppLayout } from "@/components/layout/AppLayout";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { ModuleCard } from "@/components/course/ModuleCard";
import { CourseIcon } from "@/components/course/CourseIcon";
import { api, ApiError } from "@/lib/api";
import { titleCase } from "@/lib/utils";
import type { CourseDetailOut, LessonSummaryOut } from "@/types";

type NextStep =
  | { kind: "lesson"; lesson: LessonSummaryOut }
  | { kind: "assessment"; moduleId: string; moduleTitle: string }
  | null;

/** The next thing to do: an unfinished lesson in an unlocked module, or that module's pending assessment. */
function findNextStep(course: CourseDetailOut): NextStep {
  for (const mod of course.modules) {
    if (mod.locked) break; // everything after a locked module is locked too
    for (const lesson of mod.lessons) {
      if (lesson.progress_status !== "completed") return { kind: "lesson", lesson };
    }
    if (mod.assessment_status === "available" || mod.assessment_status === "in_progress") {
      return { kind: "assessment", moduleId: mod.id, moduleTitle: mod.title };
    }
  }
  return null;
}

export default function CourseDetailPage() {
  const params = useParams<{ courseId: string }>();
  const [course, setCourse] = useState<CourseDetailOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.courses.get(params.courseId);
      setCourse(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load this course.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.courseId]);

  if (loading) {
    return (
      <AppLayout pageTitle="Courses">
        <LoadingState label="Loading course..." fullHeight />
      </AppLayout>
    );
  }

  if (error || !course) {
    return (
      <AppLayout pageTitle="Courses">
        <div className="py-10">
          <ErrorState message={error ?? "Course not found."} onRetry={load} />
        </div>
      </AppLayout>
    );
  }

  const nextStep = findNextStep(course);
  const currentModuleId = course.modules.find((m) => !m.locked && m.status !== "completed")?.id;
  const hasProgress = typeof course.progress_percent === "number";

  return (
    <AppLayout pageTitle={`Courses · ${course.title}`}>
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <div className="flex items-center gap-3">
              <CourseIcon
                icon={course.icon}
                className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-2xl text-brand-blue"
              />
              <Badge tone="blue">{titleCase(course.level)}</Badge>
            </div>
            <h1 className="mt-4 text-3xl font-extrabold text-slate-900">{course.title}</h1>
            {course.subtitle && <p className="mt-1 text-base text-slate-500">{course.subtitle}</p>}
            <p className="mt-4 text-sm leading-relaxed text-slate-600">{course.description}</p>

            {course.learning_outcomes.length > 0 && (
              <div className="mt-6">
                <h2 className="text-base font-bold text-slate-900">What you&apos;ll learn</h2>
                <ul className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
                  {course.learning_outcomes.map((o) => (
                    <li key={o} className="flex items-start gap-2 text-sm text-slate-600">
                      <span className="mt-0.5 text-blue-600">✓</span> {o}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="mt-8">
              <h2 className="text-base font-bold text-slate-900">Modules</h2>
              <div className="mt-4 space-y-3">
                {course.modules.length === 0 ? (
                  <p className="text-sm text-slate-400">No modules published yet.</p>
                ) : (
                  course.modules.map((mod, idx) => (
                    <ModuleCard key={mod.id} module={mod} defaultOpen={currentModuleId ? mod.id === currentModuleId : idx === 0} />
                  ))
                )}
              </div>
            </div>
          </div>

          <div>
            <div className="sticky top-24 rounded-2xl border border-slate-200 bg-white p-6 shadow-xs">
              {hasProgress && (
                <ProgressBar
                  value={course.progress_percent ?? 0}
                  gradient
                  showValue
                  label="Your progress"
                  className="mb-5"
                />
              )}
              <dl className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <dt className="text-slate-500">Modules</dt>
                  <dd className="font-semibold text-slate-900">{course.module_count}</dd>
                </div>
                {typeof course.modules_completed === "number" && (
                  <div className="flex justify-between">
                    <dt className="text-slate-500">Modules completed</dt>
                    <dd className="font-semibold text-slate-900">{course.modules_completed} / {course.module_count}</dd>
                  </div>
                )}
                <div className="flex justify-between">
                  <dt className="text-slate-500">Lessons</dt>
                  <dd className="font-semibold text-slate-900">{course.lesson_count}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-slate-500">Estimated time</dt>
                  <dd className="font-semibold text-slate-900">{course.estimated_hours}h</dd>
                </div>
              </dl>

              {nextStep?.kind === "lesson" ? (
                <Button href={`/lessons/${nextStep.lesson.id}`} fullWidth className="mt-6">
                  {nextStep.lesson.progress_status ? "Continue" : "Start"} course
                </Button>
              ) : nextStep?.kind === "assessment" ? (
                <Button href={`/modules/${nextStep.moduleId}/assessment`} fullWidth className="mt-6">
                  Take module assessment
                </Button>
              ) : (
                <Button variant="secondary" fullWidth className="mt-6" disabled>
                  Course complete
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
