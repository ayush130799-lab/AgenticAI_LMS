import { cn } from "@/lib/utils";

interface LoadingStateProps {
  label?: string;
  className?: string;
  fullHeight?: boolean;
}

export function LoadingState({ label = "Loading...", className, fullHeight }: LoadingStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 py-12 text-ink-400",
        fullHeight && "min-h-[50vh]",
        className
      )}
    >
      <span className="h-8 w-8 animate-spin rounded-full border-2 border-ink-200 border-t-brand-blue" />
      <p className="text-sm font-medium">{label}</p>
    </div>
  );
}
