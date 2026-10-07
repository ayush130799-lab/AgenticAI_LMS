"use client";

import { useEffect, useMemo, useState } from "react";
import { AppLayout } from "@/components/layout/AppLayout";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { CourseCard } from "@/components/course/CourseCard";
import { cn } from "@/lib/utils";
import { api, ApiError } from "@/lib/api";
import type { CourseSummaryOut } from "@/types";

const LEVEL_FILTERS = ["all", "beginner", "intermediate", "advanced"];

export default function CoursesPage() {
  const [courses, setCourses] = useState<CourseSummaryOut[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [level, setLevel] = useState("all");

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.courses.list();
      setCourses(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load courses.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const filtered = useMemo(() => {
    if (!courses) return [];
    if (level === "all") return courses;
    return courses.filter((c) => c.level === level);
  }, [courses, level]);

  return (
    <AppLayout pageTitle="Courses">
      <div className="space-y-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-blue-600 mb-1">
              CURRICULUM & MODULES
            </p>
            <h1 className="text-2xl font-extrabold text-slate-900">Course Catalog</h1>
            <p className="mt-1 text-sm text-slate-500">
              Browse the full Agentic AI curriculum, from Python foundations to production agents.
            </p>
          </div>
          <div className="flex gap-2 overflow-x-auto">
            {LEVEL_FILTERS.map((l) => (
              <button
                key={l}
                onClick={() => setLevel(l)}
                className={cn(
                  "shrink-0 rounded-full border px-4 py-1.5 text-xs font-semibold capitalize transition-colors",
                  level === l
                    ? "border-blue-600 bg-blue-600 text-white shadow-xs"
                    : "border-slate-200 bg-white text-slate-600 hover:bg-slate-50"
                )}
              >
                {l}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-6">
          {loading && <LoadingState label="Loading courses..." />}
          {!loading && error && <ErrorState message={error} onRetry={load} />}
          {!loading && !error && filtered.length === 0 && (
            <EmptyState title="No courses found" description="Try a different level filter." />
          )}
          {!loading && !error && filtered.length > 0 && (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {filtered.map((course) => (
                <CourseCard key={course.id} course={course} />
              ))}
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
