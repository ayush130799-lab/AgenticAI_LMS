"use client";

import { cn } from "@/lib/utils";
import type { ModuleAnswer, ModuleQuestionView } from "@/types";

interface ObjectiveQuestionProps {
  question: ModuleQuestionView;
  value: ModuleAnswer | null | undefined;
  onChange: (answer: ModuleAnswer) => void;
  disabled?: boolean;
}

const LETTERS = ["A", "B", "C", "D", "E", "F"];

/** Renders MCQ and every quiz format (true/false, scenario, multi-select, short answer). */
export function ObjectiveQuestion({ question, value, onChange, disabled }: ObjectiveQuestionProps) {
  const isMulti = question.type === "quiz" && question.quiz_format === "multi_select";
  const isShort = question.type === "quiz" && question.quiz_format === "short_answer";

  if (isShort) {
    return (
      <div>
        <label htmlFor={`q-${question.id}`} className="text-xs font-semibold uppercase tracking-wide text-ink-400">
          Your answer
        </label>
        <input
          id={`q-${question.id}`}
          type="text"
          value={value?.text ?? ""}
          maxLength={200}
          disabled={disabled}
          autoComplete="off"
          onChange={(e) => onChange({ text: e.target.value })}
          placeholder="Type a short answer"
          className="mt-1 w-full rounded-xl border border-ink-200 px-4 py-3 text-sm focus:border-brand-blue focus:outline-none focus:ring-2 focus:ring-brand-blue/20 disabled:bg-ink-100"
        />
      </div>
    );
  }

  const selected = new Set(isMulti ? value?.choices ?? [] : value?.choice ? [value.choice] : []);

  function toggle(id: string) {
    if (isMulti) {
      const next = new Set(selected);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      onChange({ choices: Array.from(next) });
    } else {
      onChange({ choice: id });
    }
  }

  return (
    <fieldset disabled={disabled}>
      <legend className="sr-only">{question.prompt}</legend>
      {isMulti && <p className="mb-2 text-xs font-medium text-ink-500">Select all that apply.</p>}
      <div className="space-y-2.5" role={isMulti ? "group" : "radiogroup"}>
        {question.options.map((opt, i) => {
          const checked = selected.has(opt.id);
          return (
            <label
              key={opt.id}
              className={cn(
                "flex cursor-pointer items-start gap-3 rounded-xl border px-4 py-3 text-sm transition-colors",
                checked ? "border-brand-blue bg-surface-tint-blue text-ink-900" : "border-ink-200 bg-white text-ink-700 hover:border-brand-blue/60",
                disabled && "cursor-not-allowed opacity-70"
              )}
            >
              <input
                type={isMulti ? "checkbox" : "radio"}
                name={`q-${question.id}`}
                checked={checked}
                onChange={() => toggle(opt.id)}
                className="mt-1 h-4 w-4 shrink-0 accent-[#2563eb]"
              />
              <span className="min-w-0 break-words">
                {question.quiz_format !== "true_false" && (
                  <span className="mr-2 font-semibold text-ink-400">{LETTERS[i] ?? i + 1}.</span>
                )}
                {opt.text}
              </span>
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}

export function isAnswered(question: ModuleQuestionView, value: ModuleAnswer | null | undefined): boolean {
  if (!value) return false;
  if (question.type === "coding") return !!value.code && value.code.trim() !== "" && value.code !== question.coding?.starter_code;
  if (question.quiz_format === "multi_select") return (value.choices?.length ?? 0) > 0;
  if (question.quiz_format === "short_answer") return !!value.text && value.text.trim() !== "";
  return !!value.choice;
}
