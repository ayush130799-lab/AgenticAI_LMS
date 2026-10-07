"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { recommendationHref } from "@/components/dashboard/RecommendationCard";
import { icons } from "@/components/layout/nav";
import { api } from "@/lib/api";
import { titleCase } from "@/lib/utils";

export interface NotificationItem {
  id: string;
  title: string;
  body: string;
  href: string;
  tag: string;
}

/**
 * There is no notifications backend, so this derives "things that need your
 * attention" from real state: unfinished onboarding/diagnostic and the AI
 * planner's current recommendations. Nothing here is fabricated.
 */
export function useNotifications() {
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const hasLoaded = useRef(false);

  const load = useCallback(async () => {
    // Refresh silently after the first load so the panel never flashes back to "Loading...".
    if (!hasLoaded.current) setLoading(true);
    setFailed(false);
    const [profile, recs] = await Promise.allSettled([api.students.profile(), api.recommendations.list()]);
    if (profile.status === "rejected" && recs.status === "rejected") {
      setFailed(true);
      setLoading(false);
      return;
    }
    hasLoaded.current = true;

    const next: NotificationItem[] = [];
    if (profile.status === "fulfilled") {
      if (!profile.value.onboarding_completed) {
        next.push({
          id: "onboarding",
          title: "Finish setting up your profile",
          body: "Tell us your experience and goals so the planner can personalize your path.",
          href: "/onboarding",
          tag: "Setup",
        });
      }
      if (!profile.value.diagnostic_completed) {
        next.push({
          id: "diagnostic",
          title: "Take the diagnostic assessment",
          body: "It builds your starting skill profile across Python, LLMs, RAG, and agents.",
          href: "/assessments",
          tag: "Assessment",
        });
      }
    }
    if (recs.status === "fulfilled") {
      for (const rec of recs.value.slice(0, 3)) {
        next.push({
          id: rec.id,
          title: rec.title,
          body: rec.reason,
          href: recommendationHref(rec),
          tag: titleCase(rec.recommendation_type),
        });
      }
    }
    setItems(next);
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return { items, loading, failed, reload: load };
}

interface NotificationsPanelProps {
  open: boolean;
  onClose: () => void;
  items: NotificationItem[];
  loading: boolean;
  failed: boolean;
  onRetry: () => void;
}

export function NotificationsPanel({ open, onClose, items, loading, failed, onRetry }: NotificationsPanelProps) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[60] flex justify-end bg-ink-900/30" onClick={onClose}>
      <aside
        role="dialog"
        aria-label="Notifications"
        onClick={(e) => e.stopPropagation()}
        className="flex h-full w-full max-w-sm flex-col border-l border-ink-200 bg-white shadow-soft"
      >
        <div className="flex items-center justify-between border-b border-ink-100 px-5 py-4">
          <h2 className="text-base font-bold text-ink-900">Notifications</h2>
          <button onClick={onClose} className="rounded-lg p-1.5 text-ink-500 hover:bg-ink-100" aria-label="Close notifications">
            {icons.close}
          </button>
        </div>
        <div className="flex-1 space-y-3 overflow-y-auto p-4">
          {loading && <p className="py-8 text-center text-sm text-ink-400">Loading...</p>}
          {!loading && failed && (
            <div className="rounded-xl border border-red-100 bg-red-50/60 p-4 text-center text-sm text-red-600">
              Could not load notifications.
              <button onClick={onRetry} className="mt-2 block w-full font-semibold underline">
                Try again
              </button>
            </div>
          )}
          {!loading && !failed && items.length === 0 && (
            <p className="py-8 text-center text-sm text-ink-500">You are all caught up. Nothing needs your attention right now.</p>
          )}
          {!loading &&
            items.map((item) => (
              <Link
                key={item.id}
                href={item.href}
                onClick={onClose}
                className="block rounded-xl border border-ink-200 p-4 transition-colors hover:border-brand-blue hover:bg-surface-tint-blue"
              >
                <span className="text-[11px] font-semibold uppercase tracking-wide text-brand-cyan-dark">{item.tag}</span>
                <p className="mt-1 text-sm font-semibold text-ink-900">{item.title}</p>
                <p className="mt-1 text-xs text-ink-500">{item.body}</p>
              </Link>
            ))}
        </div>
      </aside>
    </div>
  );
}
