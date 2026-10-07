import { icons } from "@/components/layout/nav";

interface WelcomeSectionProps {
  name: string | null | undefined;
  streakDays?: number | null;
}

export function WelcomeSection({ name, streakDays }: WelcomeSectionProps) {
  const firstName = name?.trim().split(" ")[0];
  return (
    <section className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <p className="text-xs font-bold uppercase tracking-widest text-brand-blue">My Learning</p>
        <h2 className="mt-1 text-2xl font-extrabold tracking-tight text-ink-900 sm:text-3xl">
          Welcome back{firstName ? `, ${firstName}` : ""}
        </h2>
        <p className="mt-1 text-sm text-ink-500">Continue your AI learning journey and build your next project.</p>
      </div>
      {streakDays != null && streakDays > 0 && (
        <span className="inline-flex items-center gap-1.5 self-start rounded-full bg-amber-50 px-3 py-1.5 text-sm font-semibold text-amber-700 sm:self-auto">
          {icons.flame}
          {streakDays}-day learning streak
        </span>
      )}
    </section>
  );
}
