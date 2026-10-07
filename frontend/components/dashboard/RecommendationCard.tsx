import Link from "next/link";
import { Badge } from "@/components/ui/Badge";
import type { RecommendationOut } from "@/types";
import { titleCase } from "@/lib/utils";

interface RecommendationCardProps {
  recommendation: RecommendationOut;
}

export function recommendationHref(rec: RecommendationOut): string {
  if (!rec.target_id || !rec.target_type) return "/learning-path";
  switch (rec.target_type) {
    case "lesson":
      return `/lessons/${rec.target_id}`;
    case "course":
      return `/courses/${rec.target_id}`;
    case "project":
      return `/projects/${rec.target_id}`;
    case "assessment":
      return `/assessments/${rec.target_id}`;
    case "skill":
      return "/skills";
    default:
      return "/learning-path";
  }
}

export function RecommendationCard({ recommendation }: RecommendationCardProps) {
  return (
    <Link
      href={recommendationHref(recommendation)}
      className="flex flex-col gap-2 rounded-xl border border-ink-200 p-4 transition-colors hover:border-brand-blue hover:bg-surface-tint-blue"
    >
      <div className="flex items-center justify-between gap-2">
        <Badge tone="cyan">AI Recommended</Badge>
        <span className="text-[11px] font-semibold uppercase tracking-wide text-ink-400">
          {titleCase(recommendation.recommendation_type)}
        </span>
      </div>
      <p className="text-sm font-semibold text-ink-900">{recommendation.title}</p>
      <p className="text-xs text-ink-500">{recommendation.reason}</p>
    </Link>
  );
}
