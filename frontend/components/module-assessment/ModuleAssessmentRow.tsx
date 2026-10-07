import Link from "next/link";
import { cn } from "@/lib/utils";
import type { ModuleSummaryOut } from "@/types";

/** The "Module Assessment" line at the end of a module's lesson list, showing its gate state. */
export function ModuleAssessmentRow({ module }: { module: ModuleSummaryOut }) {
  const status = module.assessment_status;
  const href = `/modules/${module.id}/assessment`;

  const base = "flex items-center justify-between gap-3 rounded-xl border px-4 py-3";
  if (status === "passed") {
    return (
      <Link href={href} className={cn(base, "border-emerald-200 bg-emerald-50 transition-colors hover:bg-emerald-100/70")}>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-emerald-800">Module Assessment</p>
          <p className="text-xs text-emerald-700">
            ✓ Passed{module.assessment_best_percentage != null ? ` · best ${module.assessment_best_percentage}%` : ""}
          </p>
        </div>
        <span className="shrink-0 text-xs font-semibold text-emerald-700">View →</span>
      </Link>
    );
  }
  if (status === "available" || status === "in_progress") {
    return (
      <Link href={href} className={cn(base, "border-brand-blue/30 bg-surface-tint-blue transition-colors hover:border-brand-blue")}>
        <div className="min-w-0">
          <p className="text-sm font-semibold text-ink-900">Module Assessment</p>
          <p className="text-xs text-ink-500">Pass it to complete this module and unlock the next one.</p>
        </div>
        <span className="shrink-0 rounded-full bg-brand-blue px-3 py-1 text-xs font-semibold text-white">
          {status === "in_progress" ? "Resume" : "Take assessment"}
        </span>
      </Link>
    );
  }
  return (
    <div className={cn(base, "border-ink-200 bg-ink-100/50")} aria-disabled="true">
      <div className="min-w-0">
        <p className="text-sm font-semibold text-ink-500">🔒 Module Assessment</p>
        <p className="text-xs text-ink-500">{module.assessment_unavailable_reason ?? "Complete all lessons in this module to unlock the assessment."}</p>
      </div>
    </div>
  );
}
