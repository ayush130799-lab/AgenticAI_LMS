import Link from "next/link";
import { Skeleton } from "@/components/dashboard/SectionState";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { cn } from "@/lib/utils";

interface StatCardProps {
  label: string;
  value: string;
  caption?: string;
  /** 0-100; renders a progress bar when provided. */
  percent?: number | null;
  gradient?: boolean;
  loading?: boolean;
  error?: boolean;
  action?: { label: string; href: string };
  accent?: "blue" | "cyan" | "purple" | "amber";
}

const ACCENT: Record<NonNullable<StatCardProps["accent"]>, string> = {
  blue: "bg-brand-blue",
  cyan: "bg-brand-cyan",
  purple: "bg-brand-purple",
  amber: "bg-brand-amber",
};

export function StatCard({ label, value, caption, percent, gradient, loading, error, action, accent = "blue" }: StatCardProps) {
  return (
    <div className="flex flex-col overflow-hidden rounded-2xl border border-ink-200 bg-white shadow-card">
      <div className={cn("h-1", ACCENT[accent])} />
      <div className="flex flex-1 flex-col p-5">
        <p className="text-[11px] font-semibold uppercase tracking-wider text-ink-400">{label}</p>
        {loading ? (
          <div className="mt-3 space-y-2">
            <Skeleton className="h-8 w-20" />
            <Skeleton className="h-3 w-32" />
          </div>
        ) : error ? (
          <p className="mt-3 text-sm text-ink-400">Unavailable right now</p>
        ) : (
          <>
            <p className="mt-2 text-3xl font-extrabold text-ink-900">{value}</p>
            {percent != null && <ProgressBar value={percent} gradient={gradient} className="mt-3" />}
            {caption && <p className="mt-2 text-xs text-ink-500">{caption}</p>}
            {action && (
              <Link href={action.href} className="mt-auto pt-3 text-xs font-semibold text-brand-blue hover:underline">
                {action.label} →
              </Link>
            )}
          </>
        )}
      </div>
    </div>
  );
}
