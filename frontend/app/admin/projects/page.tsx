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
import { useToast } from "@/components/ui/Toast";
import { api, ApiError } from "@/lib/api";
import type { ProjectSummaryOut } from "@/types";

interface ProjectFormState {
  slug: string;
  title: string;
  overview: string;
  objective: string;
  difficulty: string;
  estimated_hours: number;
}

const EMPTY_FORM: ProjectFormState = {
  slug: "",
  title: "",
  overview: "",
  objective: "",
  difficulty: "beginner",
  estimated_hours: 4,
};

const DIFFICULTY_OPTIONS = [
  { value: "beginner", label: "Beginner" },
  { value: "intermediate", label: "Intermediate" },
  { value: "advanced", label: "Advanced" },
  { value: "expert", label: "Expert" },
];

function AdminProjectsContent() {
  const { showToast } = useToast();
  const [projects, setProjects] = useState<ProjectSummaryOut[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<ProjectFormState>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.projects.list();
      setProjects(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load projects.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleDelete(p: ProjectSummaryOut) {
    if (!window.confirm(`Delete project "${p.title}"?`)) return;
    try {
      await api.admin.projects.remove(p.id);
      showToast("Project deleted.", "success");
      load();
    } catch (err) {
      showToast(err instanceof ApiError ? err.detail : "Unable to delete project.", "error");
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!form.slug.trim() || !form.title.trim()) {
      setFormError("Slug and title are required.");
      return;
    }
    setSaving(true);
    setFormError(null);
    try {
      await api.admin.projects.create({
        slug: form.slug.trim(),
        title: form.title.trim(),
        overview: form.overview.trim(),
        objective: form.objective.trim(),
        difficulty: form.difficulty,
        estimated_hours: form.estimated_hours,
        order_index: 0,
        prerequisites: [],
        learning_outcomes: [],
        requirements: [],
        architecture: "",
        milestones: [],
        tasks: [],
        expected_output: "",
        evaluation_criteria: [],
        resources: [],
      });
      showToast("Project created.", "success");
      setModalOpen(false);
      setForm(EMPTY_FORM);
      load();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.detail : "Unable to save project.");
    } finally {
      setSaving(false);
    }
  }

  const columns: Column<ProjectSummaryOut>[] = [
    { header: "Title", render: (p) => <span className="font-semibold text-ink-900">{p.title}</span> },
    { header: "Slug", render: (p) => <span className="text-ink-400">{p.slug}</span> },
    { header: "Difficulty", render: (p) => p.difficulty },
    { header: "Hours", render: (p) => p.estimated_hours },
    {
      header: "Actions",
      render: (p) => (
        <Button size="sm" variant="danger" onClick={() => handleDelete(p)}>
          Delete
        </Button>
      ),
    },
  ];

  return (
    <div>
      <AdminPageHeader
        title="Projects"
        description="Manage agent projects learners can build and submit."
        action={
          <Button
            onClick={() => {
              setForm(EMPTY_FORM);
              setFormError(null);
              setModalOpen(true);
            }}
          >
            + New project
          </Button>
        }
      />
      <AdminNav />

      <div className="mt-6">
        {loading && <LoadingState label="Loading projects..." />}
        {!loading && error && <ErrorState message={error} onRetry={load} />}
        {!loading && !error && projects && (
          <DataTable columns={columns} rows={projects} keyField={(p) => p.id} emptyTitle="No projects yet" />
        )}
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New project">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Input label="Title" value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} />
            <Input label="Slug" value={form.slug} onChange={(e) => setForm((f) => ({ ...f, slug: e.target.value }))} />
          </div>
          <Textarea
            label="Overview"
            rows={2}
            value={form.overview}
            onChange={(e) => setForm((f) => ({ ...f, overview: e.target.value }))}
          />
          <Textarea
            label="Objective"
            rows={2}
            value={form.objective}
            onChange={(e) => setForm((f) => ({ ...f, objective: e.target.value }))}
          />
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Select
              label="Difficulty"
              options={DIFFICULTY_OPTIONS}
              value={form.difficulty}
              onChange={(e) => setForm((f) => ({ ...f, difficulty: e.target.value }))}
            />
            <Input
              label="Estimated hours"
              type="number"
              min={1}
              value={form.estimated_hours}
              onChange={(e) => setForm((f) => ({ ...f, estimated_hours: Number(e.target.value) }))}
            />
          </div>
          {formError && <p className="text-sm text-red-600">{formError}</p>}
          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? "Saving..." : "Save project"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

export default function AdminProjectsPage() {
  return (
    <ProtectedRoute adminOnly>
      <AppLayout pageTitle="Admin · Projects">
        <AdminProjectsContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
