interface LessonObjectivesProps {
  objectives: string[];
}

export function LessonObjectives({ objectives }: LessonObjectivesProps) {
  if (objectives.length === 0) return null;

  return (
    <div className="mt-5 rounded-xl bg-surface-tint-blue p-4">
      <p className="text-sm font-semibold text-ink-900">Learning objectives</p>
      <ul className="mt-2 space-y-1">
        {objectives.map((o) => (
          <li key={o} className="text-sm text-ink-700">
            • {o}
          </li>
        ))}
      </ul>
    </div>
  );
}
