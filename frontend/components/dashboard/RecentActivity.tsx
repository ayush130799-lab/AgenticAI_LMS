import Link from "next/link";
import { formatRelativeTime, titleCase } from "@/lib/utils";
import type { ActivityItemOut } from "@/types";

function describe(item: ActivityItemOut): { label: string; href: string | null } {
  const title = item.title ?? "";
  switch (item.action) {
    case "lesson_completed":
      return { label: `Completed lesson${title ? `: ${title}` : ""}`, href: item.entity_id ? `/lessons/${item.entity_id}` : null };
    case "assessment_completed":
      return {
        label: `Finished ${title || "an assessment"}${item.score_percent != null ? ` (${Math.round(item.score_percent)}%)` : ""}`,
        href: "/assessments",
      };
    case "module_assessment_passed":
    case "module_assessment_failed": {
      const passed = item.action === "module_assessment_passed";
      return {
        label: `${passed ? "Passed" : "Attempted"} ${title || "module assessment"}${item.score_percent != null ? ` (${Math.round(item.score_percent)}%)` : ""}`,
        href: null,
      };
    }
    case "project_submitted":
      return { label: `Submitted project${title ? `: ${title}` : ""}`, href: item.entity_id ? `/projects/${item.entity_id}` : null };
    default:
      return { label: titleCase(item.action), href: null };
  }
}

export function RecentActivity({ items }: { items: ActivityItemOut[] }) {
  return (
    <ul className="space-y-3">
      {items.map((item) => {
        const { label, href } = describe(item);
        const body = (
          <>
            <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-brand-cyan" aria-hidden="true" />
            <span className="min-w-0 flex-1">
              <span className="block truncate text-sm text-ink-700">{label}</span>
              <span className="text-xs text-ink-400">{formatRelativeTime(item.created_at)}</span>
            </span>
          </>
        );
        return (
          <li key={item.id}>
            {href ? (
              <Link href={href} className="flex items-start gap-3 rounded-lg hover:text-brand-blue">
                {body}
              </Link>
            ) : (
              <div className="flex items-start gap-3">{body}</div>
            )}
          </li>
        );
      })}
    </ul>
  );
}
