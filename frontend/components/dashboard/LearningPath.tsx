import Link from "next/link";
import { icons } from "@/components/layout/nav";
import { cn } from "@/lib/utils";
import type { CourseSummaryOut } from "@/types";

type StepStatus = "completed" | "current" | "upcoming";

interface Step {
  course: CourseSummaryOut;
  status: StepStatus;
  progress: number;
}

/** Curriculum order is fixed; status is derived from the student's real per-course progress. */
export function buildPathSteps(courses: CourseSummaryOut[]): Step[] {
  const sorted = [...courses].sort((a, b) => a.order_index - b.order_index);
  const currentIndex = sorted.findIndex((c) => (c.progress_percent ?? 0) < 100);
  return sorted.map((course, i) => {
    const progress = course.progress_percent ?? 0;
    const status: StepStatus = progress >= 100 ? "completed" : i === currentIndex ? "current" : "upcoming";
    return { course, status, progress };
  });
}

export function LearningPath({ courses }: { courses: CourseSummaryOut[] }) {
  const steps = buildPathSteps(courses);
  const done = steps.filter((s) => s.status === "completed").length;

  return (
    <div>
      <p className="mb-3 text-xs text-ink-500">
        {done} of {steps.length} courses completed
      </p>
      <ol className="max-h-[26rem] space-y-0 overflow-y-auto pr-1">
        {steps.map((step, i) => (
          <li key={step.course.id} className="relative pl-9">
            {i < steps.length - 1 && (
              <span
                className={cn("absolute left-[11px] top-6 h-full w-0.5", step.status === "completed" ? "bg-brand-blue" : "bg-ink-200")}
                aria-hidden="true"
              />
            )}
            <span
              className={cn(
                "absolute left-0 top-1 flex h-6 w-6 items-center justify-center rounded-full border-2 text-[11px] font-bold",
                step.status === "completed" && "border-brand-blue bg-brand-blue text-white",
                step.status === "current" && "border-brand-cyan bg-white text-brand-cyan-dark",
                step.status === "upcoming" && "border-ink-200 bg-white text-ink-400"
              )}
            >
              {step.status === "completed" ? <span className="scale-75">{icons.check}</span> : i + 1}
            </span>
            <Link
              href={`/courses/${step.course.id}`}
              className={cn(
                "mb-2 block rounded-xl px-3 py-2 transition-colors hover:bg-ink-100",
                step.status === "current" && "bg-surface-tint"
              )}
            >
              <span className="flex items-center justify-between gap-2">
                <span className={cn("truncate text-sm font-semibold", step.status === "upcoming" ? "text-ink-500" : "text-ink-900")}>
                  {step.course.title}
                </span>
                <span className="shrink-0 text-[11px] font-semibold text-ink-400">
                  {step.status === "completed" ? "Done" : step.status === "current" ? (step.progress > 0 ? `${Math.round(step.progress)}%` : "Up next") : ""}
                </span>
              </span>
              {step.status === "current" && step.progress > 0 && (
                <span className="mt-1.5 block h-1.5 overflow-hidden rounded-full bg-ink-100">
                  <span className="block h-full rounded-full bg-brand-cyan" style={{ width: `${Math.min(100, step.progress)}%` }} />
                </span>
              )}
            </Link>
          </li>
        ))}
      </ol>
    </div>
  );
}
