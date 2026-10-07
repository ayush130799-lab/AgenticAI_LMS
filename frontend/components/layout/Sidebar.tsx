"use client";

import Link from "next/link";
import { cn } from "@/lib/utils";
import type { ModuleDetailOut } from "@/types";

interface SidebarProps {
  courseTitle: string;
  courseId: string;
  modules: ModuleDetailOut[];
  activeLessonId: string;
  open?: boolean;
  onClose?: () => void;
}

function StatusDot({ status }: { status: string | null | undefined }) {
  if (status === "completed") {
    return <span className="flex h-4 w-4 items-center justify-center rounded-full bg-emerald-500 text-[9px] text-white">✓</span>;
  }
  if (status === "in_progress") {
    return <span className="h-3 w-3 rounded-full border-2 border-brand-blue bg-white" />;
  }
  return <span className="h-3 w-3 rounded-full border-2 border-ink-200 bg-white" />;
}

export function Sidebar({ courseTitle, courseId, modules, activeLessonId, open, onClose }: SidebarProps) {
  const content = (
    <div className="flex h-full flex-col">
      <div className="border-b border-ink-100 px-4 py-4">
        <Link href={`/courses/${courseId}`} className="text-xs font-semibold text-brand-blue hover:underline">
          ← Back to course
        </Link>
        <p className="mt-2 text-sm font-bold text-ink-900">{courseTitle}</p>
      </div>
      <div className="flex-1 overflow-y-auto px-2 py-3">
        {modules.map((mod) => (
          <div key={mod.id} className="mb-3">
            <p className="px-2 py-1.5 text-[11px] font-semibold uppercase tracking-wide text-ink-400">
              {mod.locked && <span aria-label="Locked">🔒 </span>}
              {mod.title}
            </p>
            <div className="space-y-0.5">
              {mod.lessons.map((lesson) => mod.locked ? (
                <span
                  key={lesson.id}
                  aria-disabled="true"
                  title={mod.locked_reason ?? "Locked"}
                  className="flex cursor-not-allowed items-center gap-2.5 rounded-lg px-2 py-2 text-sm text-ink-400"
                >
                  <span className="h-3 w-3 rounded-full border-2 border-ink-200 bg-white" />
                  <span className="truncate">{lesson.title}</span>
                </span>
              ) : (
                <Link
                  key={lesson.id}
                  href={`/lessons/${lesson.id}`}
                  className={cn(
                    "flex items-center gap-2.5 rounded-lg px-2 py-2 text-sm transition-colors",
                    lesson.id === activeLessonId
                      ? "bg-surface-tint-blue font-semibold text-brand-blue-dark"
                      : "text-ink-600 hover:bg-ink-100"
                  )}
                >
                  <StatusDot status={lesson.progress_status} />
                  <span className="truncate">{lesson.title}</span>
                </Link>
              ))}
              {mod.has_assessment && !mod.locked && (
                <Link
                  href={`/modules/${mod.id}/assessment`}
                  className="flex items-center gap-2.5 rounded-lg px-2 py-2 text-sm font-medium text-brand-blue hover:bg-ink-100"
                >
                  <span aria-hidden="true">{mod.assessment_status === "passed" ? "✓" : "★"}</span>
                  <span className="truncate">Module Assessment{mod.assessment_status === "locked" ? " (locked)" : ""}</span>
                </Link>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <>
      <aside className="hidden w-72 shrink-0 border-r border-ink-100 bg-white lg:block">
        {content}
      </aside>

      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-ink-900/50" onClick={onClose} />
          <div className="absolute inset-y-0 left-0 w-72 max-w-[85vw] bg-white shadow-soft">
            <div className="flex justify-end p-2">
              <button onClick={onClose} className="rounded-full p-2 text-ink-500 hover:bg-ink-100" aria-label="Close menu">
                ✕
              </button>
            </div>
            {content}
          </div>
        </div>
      )}
    </>
  );
}
