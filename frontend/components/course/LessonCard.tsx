import Link from "next/link";
import { cn } from "@/lib/utils";
import type { LessonSummaryOut } from "@/types";

interface LessonCardProps {
  lesson: LessonSummaryOut;
  /** Lessons of a locked module are shown but cannot be opened (the server also refuses access). */
  locked?: boolean;
}

function statusMeta(status: string | null | undefined) {
  switch (status) {
    case "completed":
      return { label: "Completed", icon: "✓", cls: "text-emerald-600 bg-emerald-50" };
    case "in_progress":
      return { label: "In progress", icon: "●", cls: "text-brand-blue bg-surface-tint-blue" };
    default:
      return { label: "Not started", icon: "○", cls: "text-ink-400 bg-ink-100" };
  }
}

export function LessonCard({ lesson, locked }: LessonCardProps) {
  const meta = statusMeta(lesson.progress_status);
  if (locked) {
    return (
      <div aria-disabled="true" className="flex items-center justify-between gap-3 rounded-xl border border-ink-200 bg-ink-100/50 px-4 py-3 opacity-70">
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-ink-500">{lesson.title}</p>
          <p className="truncate text-xs text-ink-400">{lesson.description}</p>
        </div>
        <span className="shrink-0 text-xs font-semibold text-ink-400">🔒 Locked</span>
      </div>
    );
  }
  return (
    <Link
      href={`/lessons/${lesson.id}`}
      className="flex items-center justify-between gap-3 rounded-xl border border-ink-200 bg-white px-4 py-3 transition-colors hover:border-brand-blue hover:bg-surface-tint-blue"
    >
      <div className="min-w-0">
        <p className="truncate text-sm font-semibold text-ink-900">{lesson.title}</p>
        <p className="truncate text-xs text-ink-400">{lesson.description}</p>
      </div>
      <div className="flex shrink-0 items-center gap-3">
        <span className="text-xs text-ink-400">{lesson.estimated_minutes} min</span>
        <span
          className={cn(
            "flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-semibold",
            meta.cls
          )}
        >
          {meta.icon} {meta.label}
        </span>
      </div>
    </Link>
  );
}
