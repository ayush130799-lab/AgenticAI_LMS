import type { ReactNode } from "react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-xl bg-ink-100", className)} aria-hidden="true" />;
}

interface SectionStateProps {
  loading: boolean;
  error: string | null;
  onRetry: () => void;
  skeleton?: ReactNode;
  children: ReactNode;
}

/** Renders a per-section loading skeleton, an inline error with retry, or the section content. */
export function SectionState({ loading, error, onRetry, skeleton, children }: SectionStateProps) {
  if (loading) {
    return <>{skeleton ?? <Skeleton className="h-24 w-full" />}</>;
  }
  if (error) {
    return (
      <div className="flex flex-col items-start gap-2 rounded-xl border border-red-100 bg-red-50/60 p-4 text-sm text-red-600">
        <p>{error}</p>
        <Button size="sm" variant="secondary" onClick={onRetry}>
          Try again
        </Button>
      </div>
    );
  }
  return <>{children}</>;
}
