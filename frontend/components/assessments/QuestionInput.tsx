"use client";

import { Textarea } from "@/components/ui/Textarea";
import { cn } from "@/lib/utils";
import type { AnswerValue, QuestionOut } from "@/types";

interface QuestionInputProps {
  question: QuestionOut;
  value: AnswerValue | undefined;
  onChange: (value: AnswerValue) => void;
  index: number;
}

function optionLabel(opt: Record<string, unknown>): string {
  if (typeof opt.label === "string") return opt.label;
  if (typeof opt.text === "string") return opt.text;
  return String(opt.value ?? "");
}

function optionValue(opt: Record<string, unknown>): string {
  if (typeof opt.value === "string") return opt.value;
  if (typeof opt.id === "string") return opt.id;
  return optionLabel(opt);
}

export function QuestionInput({ question, value, onChange, index }: QuestionInputProps) {
  const options = question.options as Record<string, unknown>[];

  return (
    <div className="rounded-2xl border border-ink-200 bg-white p-5">
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm font-semibold text-ink-900">
          {index + 1}. {question.prompt}
        </p>
        <span className="shrink-0 rounded-full bg-ink-100 px-2.5 py-1 text-[11px] font-semibold text-ink-500">
          {question.points} pt{question.points === 1 ? "" : "s"}
        </span>
      </div>

      <div className="mt-4">
        {question.question_type === "mcq" && (
          <div className="space-y-2">
            {options.map((opt) => {
              const val = optionValue(opt);
              const selected = value?.selected === val;
              return (
                <label
                  key={val}
                  className={cn(
                    "flex cursor-pointer items-center gap-3 rounded-xl border px-4 py-2.5 text-sm transition-colors",
                    selected
                      ? "border-brand-blue bg-surface-tint-blue text-ink-900"
                      : "border-ink-200 text-ink-700 hover:bg-ink-100/60"
                  )}
                >
                  <input
                    type="radio"
                    name={`q-${question.id}`}
                    className="accent-brand-blue"
                    checked={selected}
                    onChange={() => onChange({ selected: val })}
                  />
                  {optionLabel(opt)}
                </label>
              );
            })}
          </div>
        )}

        {question.question_type === "multi_select" && (
          <div className="space-y-2">
            {options.map((opt) => {
              const val = optionValue(opt);
              const currentList = Array.isArray(value?.selected) ? (value?.selected as string[]) : [];
              const selected = currentList.includes(val);
              return (
                <label
                  key={val}
                  className={cn(
                    "flex cursor-pointer items-center gap-3 rounded-xl border px-4 py-2.5 text-sm transition-colors",
                    selected
                      ? "border-brand-blue bg-surface-tint-blue text-ink-900"
                      : "border-ink-200 text-ink-700 hover:bg-ink-100/60"
                  )}
                >
                  <input
                    type="checkbox"
                    className="accent-brand-blue"
                    checked={selected}
                    onChange={() => {
                      const next = selected
                        ? currentList.filter((v) => v !== val)
                        : [...currentList, val];
                      onChange({ selected: next });
                    }}
                  />
                  {optionLabel(opt)}
                </label>
              );
            })}
          </div>
        )}

        {question.question_type === "short_answer" && (
          <Textarea
            rows={3}
            placeholder="Type your answer..."
            value={value?.text ?? ""}
            onChange={(e) => onChange({ text: e.target.value })}
          />
        )}

        {question.question_type === "coding" && (
          <Textarea
            rows={8}
            className="font-mono text-xs"
            placeholder="// Write your code here"
            value={value?.code ?? ""}
            onChange={(e) => onChange({ code: e.target.value })}
          />
        )}

        {question.question_type === "scenario" && (
          <Textarea
            rows={5}
            placeholder="Describe your approach..."
            value={value?.text ?? ""}
            onChange={(e) => onChange({ text: e.target.value })}
          />
        )}
      </div>
    </div>
  );
}
