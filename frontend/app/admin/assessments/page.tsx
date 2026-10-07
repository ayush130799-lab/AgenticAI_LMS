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
import type { AssessmentListItemOut } from "@/types";

interface AssessmentFormState {
  title: string;
  description: string;
  assessment_type: string;
  passing_score: number; // held as a 0-100 percent in the form, converted on submit
  time_limit_minutes: number | "";
}

const EMPTY_FORM: AssessmentFormState = {
  title: "",
  description: "",
  assessment_type: "skill_check",
  passing_score: 70,
  time_limit_minutes: "",
};

// Must match the backend's CHECK constraint on assessments.assessment_type
// (see backend/app/models/assessment.py, ck_assessment_type).
const TYPE_OPTIONS = [
  { value: "diagnostic", label: "Diagnostic" },
  { value: "module_quiz", label: "Module quiz" },
  { value: "course_exam", label: "Course exam" },
  { value: "skill_check", label: "Skill check" },
];

function AdminAssessmentsContent() {
  const { showToast } = useToast();
  const [assessments, setAssessments] = useState<AssessmentListItemOut[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<AssessmentFormState>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.assessments.list();
      setAssessments(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load assessments.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleDelete(a: AssessmentListItemOut) {
    if (!window.confirm(`Delete assessment "${a.title}"?`)) return;
    try {
      await api.admin.assessments.remove(a.id);
      showToast("Assessment deleted.", "success");
      load();
    } catch (err) {
      showToast(err instanceof ApiError ? err.detail : "Unable to delete assessment.", "error");
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!form.title.trim()) {
      setFormError("Title is required.");
      return;
    }
    setSaving(true);
    setFormError(null);
    try {
      await api.admin.assessments.create({
        title: form.title.trim(),
        description: form.description.trim() || null,
        assessment_type: form.assessment_type,
        passing_score: form.passing_score / 100,
        time_limit_minutes: form.time_limit_minutes === "" ? null : Number(form.time_limit_minutes),
        questions: [],
      });
      showToast("Assessment created.", "success");
      setModalOpen(false);
      setForm(EMPTY_FORM);
      load();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.detail : "Unable to save assessment.");
    } finally {
      setSaving(false);
    }
  }

  const columns: Column<AssessmentListItemOut>[] = [
    { header: "Title", render: (a) => <span className="font-semibold text-ink-900">{a.title}</span> },
    { header: "Type", render: (a) => a.assessment_type },
    { header: "Passing score", render: (a) => `${Math.round(a.passing_score * 100)}%` },
    { header: "Questions", render: (a) => a.question_count },
    {
      header: "Actions",
      render: (a) => (
        <Button size="sm" variant="danger" onClick={() => handleDelete(a)}>
          Delete
        </Button>
      ),
    },
  ];

  return (
    <div>
      <AdminPageHeader
        title="Assessments"
        description="Manage diagnostic and skill assessments."
        action={
          <Button
            onClick={() => {
              setForm(EMPTY_FORM);
              setFormError(null);
              setModalOpen(true);
            }}
          >
            + New assessment
          </Button>
        }
      />
      <AdminNav />

      <div className="mt-6">
        {loading && <LoadingState label="Loading assessments..." />}
        {!loading && error && <ErrorState message={error} onRetry={load} />}
        {!loading && !error && assessments && (
          <DataTable columns={columns} rows={assessments} keyField={(a) => a.id} emptyTitle="No assessments yet" />
        )}
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New assessment">
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Title" value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} />
          <Textarea
            label="Description"
            rows={3}
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          />
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Select
              label="Type"
              options={TYPE_OPTIONS}
              value={form.assessment_type}
              onChange={(e) => setForm((f) => ({ ...f, assessment_type: e.target.value }))}
            />
            <Input
              label="Passing score (%)"
              type="number"
              min={0}
              max={100}
              value={form.passing_score}
              onChange={(e) => setForm((f) => ({ ...f, passing_score: Number(e.target.value) }))}
            />
            <Input
              label="Time limit (min)"
              type="number"
              min={0}
              value={form.time_limit_minutes}
              onChange={(e) =>
                setForm((f) => ({ ...f, time_limit_minutes: e.target.value === "" ? "" : Number(e.target.value) }))
              }
            />
          </div>
          {formError && <p className="text-sm text-red-600">{formError}</p>}
          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? "Saving..." : "Save assessment"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

export default function AdminAssessmentsPage() {
  return (
    <ProtectedRoute adminOnly>
      <AppLayout pageTitle="Admin · Assessments">
        <AdminAssessmentsContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
