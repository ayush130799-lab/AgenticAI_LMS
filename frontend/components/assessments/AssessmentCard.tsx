import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { titleCase } from "@/lib/utils";
import type { AssessmentListItemOut } from "@/types";

interface AssessmentCardProps {
  assessment: AssessmentListItemOut;
}

export function AssessmentCard({ assessment }: AssessmentCardProps) {
  return (
    <Card className="flex h-full flex-col justify-between">
      <div>
        <div className="flex items-center justify-between gap-2">
          <Badge tone="blue">{titleCase(assessment.assessment_type)}</Badge>
          {assessment.time_limit_minutes && (
            <span className="text-xs font-medium text-ink-400">
              {assessment.time_limit_minutes} min
            </span>
          )}
        </div>
        <h3 className="mt-3 text-base font-bold text-ink-900">{assessment.title}</h3>
        {assessment.description && (
          <p className="mt-2 text-sm text-ink-500">{assessment.description}</p>
        )}
        <p className="mt-3 text-xs text-ink-400">
          {assessment.question_count} question{assessment.question_count === 1 ? "" : "s"} &middot; Passing
          score {Math.round(assessment.passing_score * 100)}%
          {assessment.last_score_percent != null && (
            <> &middot; Last score {Math.round(assessment.last_score_percent)}%</>
          )}
        </p>
      </div>
      <Button href={`/assessments/${assessment.id}`} className="mt-5" fullWidth>
        Start assessment
      </Button>
    </Card>
  );
}
