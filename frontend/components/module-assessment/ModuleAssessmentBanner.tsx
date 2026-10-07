import { Button } from "@/components/ui/Button";
import type { ModuleSummaryOut } from "@/types";

/** Shown under the final lesson of a module once every lesson is done. */
export function ModuleAssessmentBanner({ module }: { module: ModuleSummaryOut }) {
  const href = `/modules/${module.id}/assessment`;
  if (module.assessment_status === "passed") {
    return (
      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900 sm:px-8">
        <span>
          <strong>Module completed ✓</strong> - you passed the module assessment.
        </span>
        <Button size="sm" variant="secondary" href={href}>
          View result
        </Button>
      </div>
    );
  }
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-t border-brand-blue/20 bg-surface-tint-blue px-4 py-3 text-sm text-ink-900 sm:px-8">
      <span>
        <strong>All lessons completed.</strong> The Module Assessment is available - pass it to complete this module and unlock the next one.
      </span>
      <Button size="sm" href={href}>
        {module.assessment_status === "in_progress" ? "Resume assessment" : "Start assessment"}
      </Button>
    </div>
  );
}
