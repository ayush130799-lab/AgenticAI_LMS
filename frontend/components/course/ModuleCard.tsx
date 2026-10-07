"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { LessonCard } from "@/components/course/LessonCard";
import { ModuleAssessmentRow } from "@/components/module-assessment/ModuleAssessmentRow";
import { ModuleStatusBadge } from "@/components/module-assessment/ModuleStatusBadge";
import type { ModuleDetailOut } from "@/types";

interface ModuleCardProps {
  module: ModuleDetailOut;
  defaultOpen?: boolean;
}

export function ModuleCard({ module, defaultOpen = false }: ModuleCardProps) {
  const [open, setOpen] = useState(defaultOpen);
  const percent =
    module.lesson_count > 0 ? (module.completed_lesson_count / module.lesson_count) * 100 : 0;

  return (
    <div className={cn("rounded-2xl border bg-white", module.locked ? "border-ink-200 bg-ink-100/40" : "border-ink-200")}>
      <button
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
      >
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className={cn("text-sm font-bold", module.locked ? "text-ink-500" : "text-ink-900")}>{module.title}</p>
            <ModuleStatusBadge status={module.status} />
          </div>
          <p className="mt-0.5 truncate text-xs text-ink-500">{module.description}</p>
          <ProgressBar value={percent} className="mt-2 max-w-xs" />
        </div>
        <div className="flex shrink-0 items-center gap-3 text-xs text-ink-400">
          <span>
            {module.completed_lesson_count}/{module.lesson_count} lessons
          </span>
          <span
            className={cn(
              "inline-block transition-transform",
              open && "rotate-180"
            )}
          >
            ▾
          </span>
        </div>
      </button>
      {open && (
        <div className="space-y-2 border-t border-ink-100 px-5 py-4">
          {module.locked && module.locked_reason && (
            <p className="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">🔒 {module.locked_reason}</p>
          )}
          {module.lessons.length === 0 ? (
            <p className="text-sm text-ink-400">No lessons in this module yet.</p>
          ) : (
            module.lessons.map((lesson) => <LessonCard key={lesson.id} lesson={lesson} locked={module.locked} />)
          )}
          {module.has_assessment && <ModuleAssessmentRow module={module} />}
        </div>
      )}
    </div>
  );
}
