"use client";

import { useRef, type KeyboardEvent } from "react";

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  onRun?: () => void;
  disabled?: boolean;
  label?: string;
}

/**
 * A dependency-free code editor: monospace textarea that scrolls horizontally inside its own box (so the
 * page never overflows on mobile), inserts 4 spaces on Tab, and runs on Ctrl/Cmd+Enter.
 * Keyboard users: press Escape, then Tab, to move focus out of the editor.
 */
export function CodeEditor({ value, onChange, onRun, disabled, label = "Python code editor" }: CodeEditorProps) {
  const releaseTab = useRef(false);

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Escape") {
      releaseTab.current = true;
      return;
    }
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      onRun?.();
      return;
    }
    if (e.key === "Tab" && !e.shiftKey) {
      if (releaseTab.current) {
        releaseTab.current = false;
        return;
      }
      e.preventDefault();
      const el = e.currentTarget;
      const { selectionStart, selectionEnd } = el;
      const next = value.slice(0, selectionStart) + "    " + value.slice(selectionEnd);
      onChange(next);
      requestAnimationFrame(() => {
        el.selectionStart = el.selectionEnd = selectionStart + 4;
      });
      return;
    }
    releaseTab.current = false;
  }

  return (
    <div className="overflow-hidden rounded-xl border border-ink-200 bg-slate-950 shadow-inner">
      <div className="flex items-center justify-between border-b border-slate-800 px-3 py-1.5 text-[11px] font-medium text-slate-400">
        <span>python</span>
        <span className="hidden sm:inline">Tab = indent · Ctrl+Enter = run</span>
      </div>
      <textarea
        aria-label={label}
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        spellCheck={false}
        autoCapitalize="off"
        autoCorrect="off"
        wrap="off"
        rows={Math.min(22, Math.max(10, value.split("\n").length + 2))}
        className="block min-h-[14rem] w-full resize-y overflow-x-auto whitespace-pre bg-transparent p-4 font-mono text-[13px] leading-6 text-slate-100 outline-none placeholder:text-slate-500 disabled:opacity-60"
      />
    </div>
  );
}
