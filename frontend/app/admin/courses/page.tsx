"use client";

import { useEffect, useState, type FormEvent } from "react";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { AdminNav } from "@/components/admin/AdminNav";
import { AdminPageHeader } from "@/components/admin/AdminPageHeader";
import { DataTable, type Column } from "@/components/admin/DataTable";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Button } from "@/components/ui/Button";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { Select } from "@/components/ui/Select";
import { Badge } from "@/components/ui/Badge";
import { useToast } from "@/components/ui/Toast";
import { api, ApiError } from "@/lib/api";
import type { CourseSummaryOut } from "@/types";

interface CourseFormState {
  id?: string;
  slug: string;
  title: string;
  subtitle: string;
  description: string;
  order_index: number;
  estimated_hours: number;
  level: string;
  icon: string;
  learning_outcomes: string;
}

const EMPTY_FORM: CourseFormState = {
  slug: "",
  title: "",
  subtitle: "",
  description: "",
  order_index: 0,
  estimated_hours: 1,
  level: "beginner",
  icon: "",
  learning_outcomes: "",
};

const LEVEL_OPTIONS = [
  { value: "beginner", label: "Beginner" },
  { value: "intermediate", label: "Intermediate" },
  { value: "advanced", label: "Advanced" },
];

function AdminCoursesContent() {
  const { showToast } = useToast();
  const [courses, setCourses] = useState<CourseSummaryOut[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<CourseFormState>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.courses.list();
      setCourses(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load courses.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function openCreate() {
    setForm(EMPTY_FORM);
    setFormError(null);
    setModalOpen(true);
  }

  async function openEdit(course: CourseSummaryOut) {
    try {
      const detail = await api.courses.get(course.id);
      setForm({
        id: detail.id,
        slug: detail.slug,
        title: detail.title,
        subtitle: detail.subtitle ?? "",
        description: detail.description,
        order_index: detail.order_index,
        estimated_hours: detail.estimated_hours,
        level: detail.level,
        icon: detail.icon ?? "",
        learning_outcomes: detail.learning_outcomes.join("\n"),
      });
      setFormError(null);
      setModalOpen(true);
    } catch (err) {
      showToast(err instanceof ApiError ? err.detail : "Unable to load course details.", "error");
    }
  }

  async function handleDelete(course: CourseSummaryOut) {
    if (!window.confirm(`Delete course "${course.title}"? This cannot be undone.`)) return;
    try {
      await api.admin.courses.remove(course.id);
      showToast("Course deleted.", "success");
      load();
    } catch (err) {
      showToast(err instanceof ApiError ? err.detail : "Unable to delete course.", "error");
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!form.slug.trim() || !form.title.trim() || !form.description.trim()) {
      setFormError("Slug, title, and description are required.");
      return;
    }
    setSaving(true);
    setFormError(null);
    const body = {
      slug: form.slug.trim(),
      title: form.title.trim(),
      subtitle: form.subtitle.trim() || null,
      description: form.description.trim(),
      order_index: form.order_index,
      estimated_hours: form.estimated_hours,
      level: form.level,
      icon: form.icon.trim() || null,
      learning_outcomes: form.learning_outcomes
        .split("\n")
        .map((s) => s.trim())
        .filter(Boolean),
    };
    try {
      if (form.id) {
        await api.admin.courses.update(form.id, body);
        showToast("Course updated.", "success");
      } else {
        await api.admin.courses.create(body);
        showToast("Course created.", "success");
      }
      setModalOpen(false);
      load();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.detail : "Unable to save course.");
    } finally {
      setSaving(false);
    }
  }

  const columns: Column<CourseSummaryOut>[] = [
    { header: "Title", render: (c) => <span className="font-semibold text-ink-900">{c.title}</span> },
    { header: "Slug", render: (c) => <span className="text-ink-400">{c.slug}</span> },
    { header: "Level", render: (c) => <Badge tone="blue">{c.level}</Badge> },
    { header: "Modules", render: (c) => c.module_count },
    { header: "Lessons", render: (c) => c.lesson_count },
    {
      header: "Actions",
      render: (c) => (
        <div className="flex gap-2">
          <Button size="sm" variant="secondary" onClick={() => openEdit(c)}>
            Edit
          </Button>
          <Button size="sm" variant="danger" onClick={() => handleDelete(c)}>
            Delete
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <AdminPageHeader
        title="Courses"
        description="Create and manage courses in the curriculum."
        action={<Button onClick={openCreate}>+ New course</Button>}
      />
      <AdminNav />

      <div className="mt-6">
        {loading && <LoadingState label="Loading courses..." />}
        {!loading && error && <ErrorState message={error} onRetry={load} />}
        {!loading && !error && courses && (
          <DataTable
            columns={columns}
            rows={courses}
            keyField={(c) => c.id}
            emptyTitle="No courses yet"
            emptyDescription="Create your first course to start building the curriculum."
          />
        )}
      </div>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={form.id ? "Edit course" : "New course"}
      >
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
          <Input
            label="Subtitle"
            value={form.subtitle}
            onChange={(e) => setForm((f) => ({ ...f, subtitle: e.target.value }))}
          />
          <Textarea
            label="Description"
            rows={3}
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          />
          <Textarea
            label="Learning outcomes (one per line)"
            rows={3}
            value={form.learning_outcomes}
            onChange={(e) => setForm((f) => ({ ...f, learning_outcomes: e.target.value }))}
          />
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Select
              label="Level"
              options={LEVEL_OPTIONS}
              value={form.level}
              onChange={(e) => setForm((f) => ({ ...f, level: e.target.value }))}
            />
            <Input
              label="Estimated hours"
              type="number"
              min={0}
              value={form.estimated_hours}
              onChange={(e) => setForm((f) => ({ ...f, estimated_hours: Number(e.target.value) }))}
            />
            <Input
              label="Order index"
              type="number"
              min={0}
              value={form.order_index}
              onChange={(e) => setForm((f) => ({ ...f, order_index: Number(e.target.value) }))}
            />
          </div>
          <Input
            label="Icon (emoji or name)"
            hint="An emoji, or one of: python, brain, message-circle, terminal, vector, search, bot, cpu, link, workflow, network, shield, server."
            value={form.icon}
            onChange={(e) => setForm((f) => ({ ...f, icon: e.target.value }))}
          />

          {formError && <p className="text-sm text-red-600">{formError}</p>}

          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? "Saving..." : "Save course"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

export default function AdminCoursesPage() {
  return (
    <ProtectedRoute adminOnly>
      <AppLayout pageTitle="Admin · Courses">
        <AdminCoursesContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
