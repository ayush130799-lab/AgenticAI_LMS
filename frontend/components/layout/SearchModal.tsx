"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { SearchResult } from "@/types";

interface SearchModalProps {
  open: boolean;
  onClose: () => void;
}

const TYPE_ICONS: Record<string, string> = {
  course: "📘",
  lesson: "📖",
  skill: "🧩",
};

export function SearchModal({ open, onClose }: SearchModalProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 50);
    } else {
      setQuery("");
      setResults([]);
    }
  }, [open]);

  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length < 2) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await api.search.query(trimmed);
        setResults(data.results);
      } catch {
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [query]);

  if (!open) return null;

  function handleSelect(href: string) {
    onClose();
    router.push(href);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-slate-900/40 p-4 pt-20 backdrop-blur-xs">
      <div
        className="w-full max-w-xl overflow-hidden rounded-2xl bg-white shadow-2xl ring-1 ring-slate-900/10"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input */}
        <div className="relative border-b border-slate-100 px-4 py-3">
          <span className="absolute left-4 top-3.5 text-slate-400 text-lg">🔍</span>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search courses, lessons, skills..."
            className="w-full pl-8 pr-12 text-sm text-slate-900 placeholder-slate-400 focus:outline-none"
            onKeyDown={(e) => {
              if (e.key === "Escape") onClose();
            }}
          />
          <button
            onClick={onClose}
            className="absolute right-4 top-3 rounded px-1.5 py-0.5 text-xs font-semibold text-slate-400 hover:text-slate-600"
          >
            ESC
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-[60vh] overflow-y-auto p-2">
          {loading && (
            <p className="p-4 text-center text-xs text-slate-400">Searching curriculum...</p>
          )}

          {!loading && query.trim().length >= 2 && results.length === 0 && (
            <p className="p-6 text-center text-xs text-slate-400">
              No courses, lessons, or skills found matching &quot;{query}&quot;.
            </p>
          )}

          {!loading && query.trim().length < 2 && (
            <p className="p-4 text-center text-xs text-slate-400">
              Type at least 2 characters to search...
            </p>
          )}

          {!loading && results.length > 0 && (
            <div className="space-y-1">
              {results.map((item) => (
                <button
                  key={`${item.type}-${item.id}`}
                  onClick={() => handleSelect(item.href)}
                  className="w-full flex items-center justify-between rounded-xl p-3 text-left transition hover:bg-blue-50/80 group"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{TYPE_ICONS[item.type] || "📄"}</span>
                    <div>
                      <p className="text-sm font-bold text-slate-900 group-hover:text-blue-600 transition">
                        {item.title}
                      </p>
                      {item.subtitle && (
                        <p className="text-xs text-slate-500 line-clamp-1">{item.subtitle}</p>
                      )}
                    </div>
                  </div>
                  <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-slate-500 group-hover:bg-blue-100 group-hover:text-blue-700">
                    {item.badge}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
