import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { Button } from "@/components/ui/Button";
import type { DiagnosticResultOut, SubmitAssessmentResponse } from "@/types";
import { titleCase } from "@/lib/utils";

interface AssessmentResultsProps {
  result: SubmitAssessmentResponse;
  diagnosticResult?: DiagnosticResultOut | null;
}

export function AssessmentResults({ result, diagnosticResult }: AssessmentResultsProps) {
  return (
    <div className="space-y-6">
      <Card className="text-center">
        <Badge tone={diagnosticResult ? "blue" : result.passed ? "green" : "amber"}>
          {diagnosticResult ? "Diagnostic complete" : result.passed ? "Passed" : "Needs improvement"}
        </Badge>
        <p className="mt-4 text-5xl font-extrabold text-ink-900">{Math.round(result.score)}%</p>
        <p className="mt-1 text-sm text-ink-500">Overall score</p>
      </Card>

      {result.skill_breakdown.length > 0 && (
        <Card>
          <h3 className="text-base font-bold text-ink-900">Skill breakdown</h3>
          <div className="mt-4 space-y-4">
            {result.skill_breakdown.map((s) => (
              <ProgressBar
                key={s.skill_slug}
                value={s.score_percent}
                gradient
                showValue
                label={s.skill_name}
              />
            ))}
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
        <Card>
          <h3 className="text-base font-bold text-ink-900">Strengths</h3>
          {result.strengths.length === 0 ? (
            <p className="mt-2 text-sm text-ink-400">No standout strengths identified yet.</p>
          ) : (
            <ul className="mt-3 space-y-2">
              {result.strengths.map((s) => (
                <li key={s} className="flex items-center gap-2 text-sm text-ink-700">
                  <span className="text-emerald-500">●</span> {s}
                </li>
              ))}
            </ul>
          )}
        </Card>
        <Card>
          <h3 className="text-base font-bold text-ink-900">Weak concepts</h3>
          {result.weak_concepts.length === 0 ? (
            <p className="mt-2 text-sm text-ink-400">No weak concepts identified.</p>
          ) : (
            <ul className="mt-3 space-y-2">
              {result.weak_concepts.map((s) => (
                <li key={s} className="flex items-center gap-2 text-sm text-ink-700">
                  <span className="text-amber-500">●</span> {s}
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <Card>
        <h3 className="text-base font-bold text-ink-900">Recommended next steps</h3>
        <ul className="mt-3 space-y-2">
          {result.recommended_next_steps.map((s, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-ink-700">
              <span className="mt-0.5 text-brand-cyan">→</span> {s}
            </li>
          ))}
        </ul>
      </Card>

      {diagnosticResult && (
        <Card>
          <h3 className="text-base font-bold text-ink-900">Your diagnostic profile</h3>
          <p className="mt-2 text-sm text-ink-500">
            Recommended starting point:{" "}
            <span className="font-semibold text-ink-900">
              {titleCase(diagnosticResult.recommended_starting_point)}
            </span>{" "}
            &middot; Confidence {Math.round(diagnosticResult.confidence * 100)}%
          </p>
          {diagnosticResult.prerequisite_gaps.length > 0 && (
            <div className="mt-4">
              <p className="text-sm font-semibold text-ink-700">Prerequisite gaps</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {diagnosticResult.prerequisite_gaps.map((g) => (
                  <Badge key={g} tone="amber">
                    {g}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </Card>
      )}

      <div className="flex flex-col gap-3 sm:flex-row">
        <Button href="/learning-path" fullWidth>
          View my learning path
        </Button>
        <Button href="/dashboard" variant="secondary" fullWidth>
          Go to dashboard
        </Button>
      </div>
    </div>
  );
}
