"use client";

import { useEffect, useState, type FormEvent } from "react";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { AdminNav } from "@/components/admin/AdminNav";
import { AdminPageHeader } from "@/components/admin/AdminPageHeader";
import { DataTable, type Column } from "@/components/admin/DataTable";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { Select } from "@/components/ui/Select";
import { useToast } from "@/components/ui/Toast";
import { api, ApiError } from "@/lib/api";
import type { CourseDetailOut, CourseSummaryOut, LessonSummaryOut } from "@/types";

interface LessonFormState {
  id?: string;
  slug: string;
  title: string;
  description: string;
  lesson_type: string;
  order_index: number;
  estimated_minutes: number;
  learning_objectives: string;
  content_markdown: string;
}

const EMPTY_FORM: LessonFormState = {
  slug: "",
  title: "",
  description: "",
  lesson_type: "reading",
  order_index: 0,
  estimated_minutes: 15,
  learning_objectives: "",
  content_markdown: "",
};

// Must match the backend's CHECK constraint on lessons.lesson_type
// (see backend/app/models/curriculum.py, ck_lesson_type).
const LESSON_TYPE_OPTIONS = [
  { value: "reading", label: "Reading" },
  { value: "coding", label: "Coding" },
  { value: "video", label: "Video" },
  { value: "project", label: "Project" },
  { value: "quiz", label: "Quiz" },
];

function AdminLessonsContent() {
  const { showToast } = useToast();
  const [courses, setCourses] = useState<CourseSummaryOut[]>([]);
  const [courseId, setCourseId] = useState("");
  const [courseDetail, setCourseDetail] = useState<CourseDetailOut | null>(null);
  const [moduleId, setModuleId] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<LessonFormState>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      setLoading(true);
      setError(null);
      try {
        const list = await api.courses.list();
        setCourses(list);
        if (list.length > 0) setCourseId(list[0].id);
        else setLoading(false);
      } catch (err) {
        setError(err instanceof ApiError ? err.detail : "Unable to load courses.");
        setLoading(false);
      }
    })();
  }, []);

  async function loadCourseDetail(id: string) {
    setLoading(true);
    setError(null);
    try {
      const detail = await api.courses.get(id);
      setCourseDetail(detail);
      setModuleId(detail.modules[0]?.id ?? "");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load course modules.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (courseId) loadCourseDetail(courseId);
  }, [courseId]);

  const activeModule = courseDetail?.modules.find((m) => m.id === moduleId) ?? null;
  const lessons: LessonSummaryOut[] = activeModule?.lessons ?? [];

  function openCreate() {
    setForm(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  }

  function openEdit(lesson: LessonSummaryOut) {
    setForm({
      id: lesson.id,
      slug: lesson.slug,
      title: lesson.title,
      description: lesson.description,
      lesson_type: lesson.lesson_type,
      order_index: lesson.order_index,
      estimated_minutes: lesson.estimated_minutes,
      learning_objectives: "",
      content_markdown: "",
    });
    setFormError(null);
    setModalOpen(true);
    // fetch full detail to prefill markdown/objectives
    api.lessons
      .get(lesson.id)
      .then((detail) => {
        setForm((f) => ({
          ...f,
          learning_objectives: detail.learning_objectives.join("\n"),
          content_markdown: detail.content_markdown,
        }));
      })
      .catch(() => undefined);
  }

  async function handleDelete(lesson: LessonSummaryOut) {
    if (!window.confirm(`Delete lesson "${lesson.title}"?`)) return;
    try {
      await api.admin.lessons.remove(lesson.id);
      showToast("Lesson deleted.", "success");
      if (courseId) loadCourseDetail(courseId);
    } catch (err) {
      showToast(err instanceof ApiError ? err.detail : "Unable to delete lesson.", "error");
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!moduleId) {
      setFormError("Select a module first.");
      return;
    }
    if (!form.slug.trim() || !form.title.trim()) {
      setFormError("Slug and title are required.");
      return;
    }
    setSaving(true);
    setFormError(null);
    const body = {
      module_id: moduleId,
      slug: form.slug.trim(),
      title: form.title.trim(),
      description: form.description.trim(),
      lesson_type: form.lesson_type,
      order_index: form.order_index,
      estimated_minutes: form.estimated_minutes,
      learning_objectives: form.learning_objectives
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean),
      content_markdown: form.content_markdown,
      examples: [],
      practice_exercises: [],
      resources: [],
    };
    try {
      if (form.id) {
        await api.admin.lessons.update(form.id, body);
        showToast("Lesson updated.", "success");
      } else {
        await api.admin.lessons.create(body);
        showToast("Lesson created.", "success");
      }
      setModalOpen(false);
      if (courseId) loadCourseDetail(courseId);
    } catch (err) {
      setFormError(err instanceof ApiError ? err.detail : "Unable to save lesson.");
    } finally {
      setSaving(false);
    }
  }

  const columns: Column<LessonSummaryOut>[] = [
    { header: "Title", render: (l) => <span className="font-semibold text-ink-900">{l.title}</span> },
    { header: "Slug", render: (l) => <span className="text-ink-400">{l.slug}</span> },
    { header: "Type", render: (l) => l.lesson_type },
    { header: "Minutes", render: (l) => l.estimated_minutes },
    {
      header: "Actions",
      render: (l) => (
        <div className="flex gap-2">
          <Button size="sm" variant="secondary" onClick={() => openEdit(l)}>
            Edit
          </Button>
          <Button size="sm" variant="danger" onClick={() => handleDelete(l)}>
            Delete
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <AdminPageHeader
        title="Lessons"
        description="Manage lessons within a course's modules."
        action={
          <Button onClick={openCreate} disabled={!moduleId}>
            + New lesson
          </Button>
        }
      />
      <AdminNav />

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Select
          label="Course"
          options={courses.map((c) => ({ value: c.id, label: c.title }))}
          value={courseId}
          onChange={(e) => setCourseId(e.target.value)}
        />
        <Select
          label="Module"
          options={(courseDetail?.modules ?? []).map((m) => ({ value: m.id, label: m.title }))}
          value={moduleId}
          onChange={(e) => setModuleId(e.target.value)}
          placeholder={courseDetail && courseDetail.modules.length === 0 ? "No modules in this course" : undefined}
        />
      </div>

      <div className="mt-6">
        {loading && <LoadingState label="Loading lessons..." />}
        {!loading && error && <ErrorState message={error} onRetry={() => courseId && loadCourseDetail(courseId)} />}
        {!loading && !error && !moduleId && (
          <EmptyState title="Select a module" description="Choose a course and module to manage its lessons." />
        )}
        {!loading && !error && moduleId && (
          <DataTable
            columns={columns}
            rows={lessons}
            keyField={(l) => l.id}
            emptyTitle="No lessons in this module"
            emptyDescription="Create the first lesson for this module."
          />
        )}
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title={form.id ? "Edit lesson" : "New lesson"}>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Input
              label="Title"
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            />
            <Input
              label="Slug"
              value={form.slug}
              onChange={(e) => setForm((f) => ({ ...f, slug: e.target.value }))}
            />
          </div>
          <Textarea
            label="Description"
            rows={2}
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          />
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Select
              label="Lesson type"
              options={LESSON_TYPE_OPTIONS}
              value={form.lesson_type}
              onChange={(e) => setForm((f) => ({ ...f, lesson_type: e.target.value }))}
            />
            <Input
              label="Estimated minutes"
              type="number"
              min={1}
              value={form.estimated_minutes}
              onChange={(e) => setForm((f) => ({ ...f, estimated_minutes: Number(e.target.value) }))}
            />
            <Input
              label="Order index"
              type="number"
              min={0}
              value={form.order_index}
              onChange={(e) => setForm((f) => ({ ...f, order_index: Number(e.target.value) }))}
            />
          </div>
          <Textarea
            label="Learning objectives (one per line)"
            rows={3}
            value={form.learning_objectives}
            onChange={(e) => setForm((f) => ({ ...f, learning_objectives: e.target.value }))}
          />
          <Textarea
            label="Content (Markdown)"
            rows={8}
            className="font-mono text-xs"
            value={form.content_markdown}
            onChange={(e) => setForm((f) => ({ ...f, content_markdown: e.target.value }))}
          />

          {formError && <p className="text-sm text-red-600">{formError}</p>}

          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? "Saving..." : "Save lesson"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

export default function AdminLessonsPage() {
  return (
    <ProtectedRoute adminOnly>
      <AppLayout pageTitle="Admin · Lessons">
        <AdminLessonsContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
