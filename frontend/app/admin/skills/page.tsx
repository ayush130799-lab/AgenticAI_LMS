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
import { useToast } from "@/components/ui/Toast";
import { api, ApiError } from "@/lib/api";
import type { SkillOut } from "@/types";

interface SkillFormState {
  slug: string;
  name: string;
  description: string;
  category: string;
}

const EMPTY_FORM: SkillFormState = { slug: "", name: "", description: "", category: "" };

function AdminSkillsContent() {
  const { showToast } = useToast();
  const [skills, setSkills] = useState<SkillOut[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<SkillFormState>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.skills.list();
      setSkills(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load skills.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleDelete(skill: SkillOut) {
    if (!window.confirm(`Delete skill "${skill.name}"?`)) return;
    try {
      await api.admin.skills.remove(skill.id);
      showToast("Skill deleted.", "success");
      load();
    } catch (err) {
      showToast(err instanceof ApiError ? err.detail : "Unable to delete skill.", "error");
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!form.slug.trim() || !form.name.trim() || !form.category.trim()) {
      setFormError("Slug, name, and category are required.");
      return;
    }
    setSaving(true);
    setFormError(null);
    try {
      await api.admin.skills.create({
        slug: form.slug.trim(),
        name: form.name.trim(),
        description: form.description.trim() || null,
        category: form.category.trim(),
      });
      showToast("Skill created.", "success");
      setModalOpen(false);
      setForm(EMPTY_FORM);
      load();
    } catch (err) {
      setFormError(err instanceof ApiError ? err.detail : "Unable to save skill.");
    } finally {
      setSaving(false);
    }
  }

  const columns: Column<SkillOut>[] = [
    { header: "Name", render: (s) => <span className="font-semibold text-ink-900">{s.name}</span> },
    { header: "Slug", render: (s) => <span className="text-ink-400">{s.slug}</span> },
    { header: "Category", render: (s) => s.category },
    {
      header: "Actions",
      render: (s) => (
        <Button size="sm" variant="danger" onClick={() => handleDelete(s)}>
          Delete
        </Button>
      ),
    },
  ];

  return (
    <div>
      <AdminPageHeader
        title="Skills"
        description="Manage the skill graph used for mastery tracking."
        action={
          <Button
            onClick={() => {
              setForm(EMPTY_FORM);
              setFormError(null);
              setModalOpen(true);
            }}
          >
            + New skill
          </Button>
        }
      />
      <AdminNav />

      <div className="mt-6">
        {loading && <LoadingState label="Loading skills..." />}
        {!loading && error && <ErrorState message={error} onRetry={load} />}
        {!loading && !error && skills && (
          <DataTable columns={columns} rows={skills} keyField={(s) => s.id} emptyTitle="No skills yet" />
        )}
      </div>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New skill">
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Name" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} />
          <Input label="Slug" value={form.slug} onChange={(e) => setForm((f) => ({ ...f, slug: e.target.value }))} />
          <Input
            label="Category"
            value={form.category}
            onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))}
          />
          <Textarea
            label="Description"
            rows={3}
            value={form.description}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          />
          {formError && <p className="text-sm text-red-600">{formError}</p>}
          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? "Saving..." : "Save skill"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

export default function AdminSkillsPage() {
  return (
    <ProtectedRoute adminOnly>
      <AppLayout pageTitle="Admin · Skills">
        <AdminSkillsContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
