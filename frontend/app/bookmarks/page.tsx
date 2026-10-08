"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { useToast } from "@/components/ui/Toast";
import { api, ApiError } from "@/lib/api";
import type { BookmarkItemOut } from "@/types";

function BookmarksContent() {
  const { showToast } = useToast();
  const [bookmarks, setBookmarks] = useState<BookmarkItemOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.students.bookmarks();
      setBookmarks(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load saved bookmarks.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleRemove(lessonId: string) {
    try {
      await api.lessons.toggleBookmark(lessonId);
      setBookmarks((prev) => prev.filter((b) => b.lesson_id !== lessonId));
      showToast("Bookmark removed.", "info");
    } catch (err) {
      showToast(err instanceof ApiError ? err.detail : "Could not remove bookmark.", "error");
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-blue-600 mb-1">
            SAVED LESSONS
          </p>
          <h1 className="text-2xl font-extrabold text-slate-900">Bookmarks Library</h1>
          <p className="mt-1 text-sm text-slate-500">
            Quickly return to lessons, concepts, and code exercises you have flagged for revision.
          </p>
        </div>
        <Badge tone="blue">{bookmarks.length} Saved</Badge>
      </div>

      {loading && <LoadingState label="Loading your bookmarks..." />}
      {!loading && error && <ErrorState message={error} onRetry={load} />}

      {!loading && !error && bookmarks.length === 0 && (
        <Card className="rounded-2xl border-slate-200 py-12 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-blue-50 text-2xl">
            🔖
          </div>
          <h3 className="mt-4 text-base font-bold text-slate-900">No bookmarks saved yet</h3>
          <p className="mx-auto mt-2 max-w-sm text-sm text-slate-500">
            Click the &quot;☆ Bookmark&quot; button in the upper right header while reading any lesson to save it here.
          </p>
          <div className="mt-6">
            <Button href="/courses" size="sm">
              Explore Courses
            </Button>
          </div>
        </Card>
      )}

      {!loading && !error && bookmarks.length > 0 && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {bookmarks.map((bm) => (
            <Card
              key={bm.id}
              className="group flex flex-col justify-between rounded-2xl border-slate-200 p-5 transition hover:border-blue-300 hover:shadow-sm"
            >
              <div>
                <div className="flex items-center justify-between">
                  <Badge tone="blue" className="capitalize">
                    {bm.lesson_type || "Lesson"}
                  </Badge>
                  <button
                    onClick={() => handleRemove(bm.lesson_id)}
                    className="text-slate-400 hover:text-red-500 transition text-xs font-semibold"
                    title="Remove bookmark"
                  >
                    Remove
                  </button>
                </div>
                <h3 className="mt-3 text-base font-bold text-slate-900 group-hover:text-blue-600 transition">
                  {bm.lesson_title}
                </h3>
                {bm.created_at && (
                  <p className="mt-2 text-xs text-slate-400">
                    Saved on {new Date(bm.created_at).toLocaleDateString()}
                  </p>
                )}
              </div>
              <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between">
                <Link
                  href={`/lessons/${bm.lesson_id}`}
                  className="text-xs font-bold text-blue-600 hover:text-blue-800 transition flex items-center gap-1"
                >
                  Open Lesson →
                </Link>
                <Link
                  href={`/courses/${bm.course_id}`}
                  className="text-[11px] font-medium text-slate-400 hover:text-slate-600"
                >
                  Course overview
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

export default function BookmarksPage() {
  return (
    <ProtectedRoute>
      <AppLayout pageTitle="Bookmarks Library">
        <BookmarksContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
