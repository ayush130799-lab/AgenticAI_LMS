"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { Navbar } from "@/components/layout/Navbar";
import { Sidebar } from "@/components/layout/Sidebar";
import { TutorChat } from "@/components/tutor/TutorChat";
import { PracticeExercises } from "@/components/lesson/PracticeExercises";
import { LessonObjectives } from "@/components/lesson/LessonObjectives";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Textarea";
import { useToast } from "@/components/ui/Toast";
import { cn } from "@/lib/utils";
import { api, ApiError } from "@/lib/api";
import { ModuleAssessmentBanner } from "@/components/module-assessment/ModuleAssessmentBanner";
import type { CourseDetailOut, LessonDetailOut, LessonNote } from "@/types";

type RightTab = "tutor" | "notes" | "bookmark";

function useCourseForLesson(lesson: LessonDetailOut | null) {
  const [course, setCourse] = useState<CourseDetailOut | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!lesson) return;
    let cancelled = false;
    setLoading(true);
    // One request: the lesson payload carries its course_id (this used to fetch every course to find the match).
    api.courses
      .get(lesson.course_id)
      .then((c) => {
        if (!cancelled) setCourse(c);
      })
      .catch(() => {
        if (!cancelled) setCourse(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [lesson]);

  return { course, loading };
}

function LessonPageContent() {
  const params = useParams<{ lessonId: string }>();
  const router = useRouter();
  const { showToast } = useToast();

  const [lesson, setLesson] = useState<LessonDetailOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lockedReason, setLockedReason] = useState<string | null>(null);
  const [completing, setCompleting] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);
  const [rightTab, setRightTab] = useState<RightTab>("tutor");
  const [mobilePanel, setMobilePanel] = useState<"content" | "side">("content");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notes, setNotes] = useState<LessonNote[]>([]);
  const [noteDraft, setNoteDraft] = useState("");
  const [savingNote, setSavingNote] = useState(false);

  async function loadLesson() {
    setLoading(true);
    setError(null);
    setLockedReason(null);
    try {
      const data = await api.lessons.get(params.lessonId);
      setLesson(data);
      setBookmarked(Boolean(data.is_bookmarked));
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        setLockedReason(err.detail); // module locked by the server: pass the previous module's assessment
      } else {
        setError(err instanceof ApiError ? err.detail : "Unable to load this lesson.");
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadLesson();
    setRightTab("tutor");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.lessonId]);

  useEffect(() => {
    if (rightTab === "notes" && lesson) {
      api.lessons
        .getNotes(lesson.id)
        .then(setNotes)
        .catch(() => setNotes([]));
    }
  }, [rightTab, lesson]);

  const { course } = useCourseForLesson(lesson);

  const { prevLesson, nextLesson } = useMemo(() => {
    if (!course || !lesson) return { prevLesson: null, nextLesson: null };
    const flat = course.modules.flatMap((m) => m.lessons);
    const idx = flat.findIndex((l) => l.id === lesson.id);
    return {
      prevLesson: idx > 0 ? flat[idx - 1] : null,
      nextLesson: idx >= 0 && idx < flat.length - 1 ? flat[idx + 1] : null,
    };
  }, [course, lesson]);

  const currentModule = course?.modules.find((m) => m.id === lesson?.module_id) ?? null;
  const isLastInModule = !!currentModule && currentModule.lessons[currentModule.lessons.length - 1]?.id === lesson?.id;
  const assessmentPending = !!currentModule?.has_assessment && currentModule.assessment_status !== "passed";
  // After the last lesson of a gated module, "Next" leads to the assessment - never straight into the next module.
  const goToAssessment = isLastInModule && assessmentPending;
  const nextIsLocked = !!nextLesson && !!course?.modules.find((m) => m.lessons.some((l) => l.id === nextLesson.id))?.locked;

  async function handleComplete() {
    if (!lesson) return;
    setCompleting(true);
    try {
      const updated = await api.lessons.complete(lesson.id);
      setLesson(updated);
      showToast("Lesson marked complete.", "success");
    } catch (err) {
      showToast(err instanceof ApiError ? err.detail : "Unable to mark lesson complete.", "error");
    } finally {
      setCompleting(false);
    }
  }

  async function handleBookmark() {
    if (!lesson) return;
    try {
      const res = await api.lessons.toggleBookmark(lesson.id);
      setBookmarked(res.bookmarked);
      showToast(res.bookmarked ? "Bookmarked." : "Bookmark removed.", "info");
    } catch (err) {
      showToast(err instanceof ApiError ? err.detail : "Unable to update bookmark.", "error");
    }
  }

  async function handleAddNote() {
    if (!lesson || !noteDraft.trim()) return;
    setSavingNote(true);
    try {
      const note = await api.lessons.addNote(lesson.id, noteDraft.trim());
      setNotes((prev) => [note, ...prev]);
      setNoteDraft("");
    } catch (err) {
      showToast(err instanceof ApiError ? err.detail : "Unable to save note.", "error");
    } finally {
      setSavingNote(false);
    }
  }

  if (loading) return <LoadingState label="Loading lesson..." fullHeight />;
  if (lockedReason) {
    return (
      <div className="container-lms py-10">
        <EmptyState
          icon="🔒"
          title="This module is locked"
          description={lockedReason}
          action={<Button href="/courses">Back to courses</Button>}
        />
      </div>
    );
  }
  if (error || !lesson) {
    return (
      <div className="container-lms py-10">
        <ErrorState message={error ?? "Lesson not found."} onRetry={loadLesson} />
      </div>
    );
  }

  return (
    <div className="flex min-h-[calc(100vh-64px)]">
      {course && (
        <Sidebar
          courseTitle={course.title}
          courseId={course.id}
          modules={course.modules}
          activeLessonId={lesson.id}
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />
      )}

      <div className="flex min-w-0 flex-1 flex-col">
        <div className="flex items-center justify-between gap-3 border-b border-ink-100 px-4 py-3 lg:hidden">
          <button
            className="rounded-lg border border-ink-200 px-3 py-1.5 text-xs font-semibold text-ink-700"
            onClick={() => setSidebarOpen(true)}
          >
            ☰ Course menu
          </button>
          <div className="flex gap-1 rounded-full bg-ink-100 p-1 text-xs font-semibold">
            <button
              className={cn(
                "rounded-full px-3 py-1",
                mobilePanel === "content" ? "bg-white shadow-sm" : "text-ink-500"
              )}
              onClick={() => setMobilePanel("content")}
            >
              Lesson
            </button>
            <button
              className={cn(
                "rounded-full px-3 py-1",
                mobilePanel === "side" ? "bg-white shadow-sm" : "text-ink-500"
              )}
              onClick={() => setMobilePanel("side")}
            >
              Tutor / Notes
            </button>
          </div>
        </div>

        <div className="flex flex-1 flex-col lg:flex-row">
          <main className={cn("flex-1 overflow-y-auto px-4 py-6 sm:px-8", mobilePanel !== "content" && "hidden lg:block")}>
            <Badge tone="blue">{lesson.lesson_type}</Badge>
            <h1 className="mt-3 text-2xl font-extrabold text-ink-900 sm:text-3xl">{lesson.title}</h1>
            <p className="mt-2 text-sm text-ink-500">{lesson.description}</p>

            <LessonObjectives objectives={lesson.learning_objectives} />

            <article className="prose-lesson mt-6">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{lesson.content_markdown}</ReactMarkdown>
            </article>

            <PracticeExercises exercises={lesson.practice_exercises} lessonId={lesson.id} />

            {lesson.skills.length > 0 && (
              <div className="mt-8 flex flex-wrap gap-2">
                {lesson.skills.map((s) => (
                  <Badge key={s.id} tone="cyan">
                    {s.name}
                  </Badge>
                ))}
              </div>
            )}
          </main>

          <aside
            className={cn(
              "flex w-full flex-col border-t border-ink-100 bg-white lg:h-[calc(100vh-64px)] lg:w-96 lg:border-l lg:border-t-0",
              mobilePanel !== "side" && "hidden lg:flex"
            )}
          >
            <div className="flex border-b border-ink-100 px-2 pt-2">
              {(["tutor", "notes", "bookmark"] as RightTab[]).map((tab) => (
                <button
                  key={tab}
                  onClick={() => (tab === "bookmark" ? handleBookmark() : setRightTab(tab))}
                  className={cn(
                    "rounded-t-lg px-3 py-2 text-xs font-semibold capitalize",
                    rightTab === tab && tab !== "bookmark"
                      ? "border-b-2 border-brand-blue text-brand-blue"
                      : "text-ink-500 hover:text-ink-800"
                  )}
                >
                  {tab === "bookmark" ? (bookmarked ? "★ Bookmarked" : "☆ Bookmark") : tab}
                </button>
              ))}
            </div>

            {rightTab === "tutor" && (
              <TutorChat lessonId={lesson.id} className="flex-1" />
            )}

            {rightTab === "notes" && (
              <div className="flex flex-1 flex-col overflow-y-auto p-4">
                <Textarea
                  rows={4}
                  placeholder="Write a note about this lesson..."
                  value={noteDraft}
                  onChange={(e) => setNoteDraft(e.target.value)}
                />
                <Button size="sm" className="mt-2 self-end" onClick={handleAddNote} disabled={savingNote}>
                  {savingNote ? "Saving..." : "Add note"}
                </Button>
                <div className="mt-4 space-y-3">
                  {notes.length === 0 ? (
                    <p className="text-sm text-ink-400">No notes yet for this lesson.</p>
                  ) : (
                    notes.map((n) => (
                      <div key={n.id} className="rounded-xl bg-ink-100/60 p-3 text-sm text-ink-700">
                        {n.content}
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </aside>
        </div>

        {isLastInModule && currentModule?.has_assessment && currentModule.all_lessons_completed && (
          <ModuleAssessmentBanner module={currentModule} />
        )}

        <div className="sticky bottom-0 flex items-center justify-between gap-3 border-t border-ink-100 bg-white px-4 py-3 sm:px-8">
          <Button
            variant="secondary"
            size="sm"
            disabled={!prevLesson}
            onClick={() => prevLesson && router.push(`/lessons/${prevLesson.id}`)}
          >
            ← Previous
          </Button>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" href="#practice">
              Practice
            </Button>
            <Button size="sm" onClick={handleComplete} disabled={completing || lesson.progress_status === "completed"}>
              {lesson.progress_status === "completed"
                ? "Completed ✓"
                : completing
                ? "Saving..."
                : "Mark Complete"}
            </Button>
          </div>
          {goToAssessment && currentModule ? (
            <Button
              size="sm"
              disabled={!currentModule.all_lessons_completed}
              title={currentModule.all_lessons_completed ? undefined : "Complete all lessons in this module to unlock the assessment."}
              onClick={() => router.push(`/modules/${currentModule.id}/assessment`)}
            >
              Module Assessment →
            </Button>
          ) : (
            <Button
              variant="secondary"
              size="sm"
              disabled={!nextLesson || nextIsLocked}
              onClick={() => nextLesson && router.push(`/lessons/${nextLesson.id}`)}
            >
              Next →
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

export default function LessonPage() {
  return (
    <ProtectedRoute>
      <Navbar />
      <LessonPageContent />
    </ProtectedRoute>
  );
}
