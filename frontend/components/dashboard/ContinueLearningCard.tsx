import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { ProgressBar } from "@/components/ui/ProgressBar";

interface ContinueLearningCardProps {
  eyebrow: string;
  title: string;
  subtitle?: string;
  /** 0-100; hidden when unknown so we never show a made-up number. */
  percent?: number | null;
  href: string;
  cta?: string;
  primary?: boolean;
}

export function ContinueLearningCard({ eyebrow, title, subtitle, percent, href, cta = "Continue", primary }: ContinueLearningCardProps) {
  return (
    <div
      className={
        primary
          ? "flex flex-col gap-4 rounded-2xl border border-brand-blue/20 bg-surface-tint-blue p-5 sm:flex-row sm:items-center sm:justify-between"
          : "flex flex-col gap-4 rounded-2xl border border-ink-200 bg-white p-5 sm:flex-row sm:items-center sm:justify-between"
      }
    >
      <div className="min-w-0 flex-1">
        <Badge tone={primary ? "blue" : "gray"}>{eyebrow}</Badge>
        <h4 className="mt-2 truncate text-base font-bold text-ink-900">{title}</h4>
        {subtitle && <p className="mt-0.5 truncate text-sm text-ink-500">{subtitle}</p>}
        {percent != null && (
          <div className="mt-3 max-w-sm">
            <ProgressBar value={percent} showValue label="Course progress" />
          </div>
        )}
      </div>
      <Button href={href} variant={primary ? "primary" : "secondary"} className="shrink-0">
        {cta} →
      </Button>
    </div>
  );
}
