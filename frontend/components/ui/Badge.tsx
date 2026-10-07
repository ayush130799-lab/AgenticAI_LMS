import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

type Tone = "blue" | "cyan" | "purple" | "magenta" | "amber" | "gray" | "green" | "red";

const toneClasses: Record<Tone, string> = {
  blue: "bg-surface-tint-blue text-brand-blue-dark",
  cyan: "bg-surface-tint text-brand-cyan-dark",
  purple: "bg-purple-50 text-brand-purple",
  magenta: "bg-fuchsia-50 text-brand-magenta",
  amber: "bg-amber-50 text-amber-700",
  gray: "bg-ink-100 text-ink-500",
  green: "bg-emerald-50 text-emerald-700",
  red: "bg-red-50 text-red-600",
};

interface BadgeProps {
  children: ReactNode;
  tone?: Tone;
  icon?: ReactNode;
  className?: string;
}

export function Badge({ children, tone = "blue", icon, className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-semibold",
        toneClasses[tone],
        className
      )}
    >
      {icon}
      {children}
    </span>
  );
}
