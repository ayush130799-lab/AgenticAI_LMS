import { cn } from "@/lib/utils";

interface ProgressBarProps {
  value: number;
  max?: number;
  className?: string;
  trackClassName?: string;
  barClassName?: string;
  gradient?: boolean;
  label?: string;
  showValue?: boolean;
}

export function ProgressBar({
  value,
  max = 100,
  className,
  trackClassName,
  barClassName,
  gradient = false,
  label,
  showValue = false,
}: ProgressBarProps) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100));

  return (
    <div className={cn("w-full", className)}>
      {(label || showValue) && (
        <div className="mb-1.5 flex items-center justify-between text-xs font-medium text-ink-500">
          {label && <span>{label}</span>}
          {showValue && <span className="text-ink-700">{Math.round(pct)}%</span>}
        </div>
      )}
      <div
        className={cn("h-2 w-full overflow-hidden rounded-full bg-ink-100", trackClassName)}
        role="progressbar"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className={cn(
            "h-full rounded-full transition-all duration-500",
            gradient ? "bg-mastery-gradient" : "bg-brand-blue",
            barClassName
          )}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
