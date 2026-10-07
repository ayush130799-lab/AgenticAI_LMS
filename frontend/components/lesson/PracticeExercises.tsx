import { PracticeCodeRunner } from "@/components/lesson/PracticeCodeRunner";
import type { PracticeExercise } from "@/types";

interface PracticeExercisesProps {
  exercises: PracticeExercise[];
  lessonId: string;
}

// Every course's practice exercises are Python-runnable in practice (even lessons tagged
// "reading" - e.g. an intro-to-variables lesson still asks the student to write and run code),
// and the editor is opt-in (a button, not forced open), so it's offered on every exercise rather
// than gated by lesson_type. A student on a purely conceptual/written exercise can simply ignore it.
export function PracticeExercises({ exercises, lessonId }: PracticeExercisesProps) {
  if (exercises.length === 0) return null;

  return (
    <div id="practice" className="mt-8">
      <h2 className="text-lg font-bold text-ink-900">Practice</h2>
      <div className="mt-3 space-y-3">
        {exercises.map((ex, i) => (
          <div key={i} className="rounded-xl border border-ink-200 p-4 text-sm text-ink-700">
            <p>{typeof ex.prompt === "string" ? ex.prompt : JSON.stringify(ex)}</p>
            {typeof ex.hint === "string" && ex.hint && <p className="mt-2 text-xs text-ink-400">Hint: {ex.hint}</p>}
            <PracticeCodeRunner lessonId={lessonId} />
          </div>
        ))}
      </div>
    </div>
  );
}
