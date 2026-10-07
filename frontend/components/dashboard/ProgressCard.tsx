import { ProgressBar } from "@/components/ui/ProgressBar";

interface ProgressCardProps {
  title: string;
  percent: number;
  subtitle?: string;
  gradient?: boolean;
}

export function ProgressCard({ title, percent, subtitle, gradient }: ProgressCardProps) {
  return (
    <div className="rounded-2xl border border-ink-200 bg-white p-5">
      <p className="text-sm font-medium text-ink-500">{title}</p>
      <p className="mt-1 text-3xl font-extrabold text-ink-900">{Math.round(percent)}%</p>
      <ProgressBar value={percent} gradient={gradient} className="mt-3" />
      {subtitle && <p className="mt-2 text-xs text-ink-400">{subtitle}</p>}
    </div>
  );
}
