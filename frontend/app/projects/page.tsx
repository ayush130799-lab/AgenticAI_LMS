"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { ProjectCard } from "@/components/projects/ProjectCard";
import { api, ApiError } from "@/lib/api";
import type { ProjectSummaryOut } from "@/types";

function ProjectsContent() {
  const [projects, setProjects] = useState<ProjectSummaryOut[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-bold uppercase tracking-wider text-blue-600 mb-1">
          HANDS-ON LABS & PROJECTS
        </p>
        <h1 className="text-2xl font-extrabold text-slate-900">Agent Projects</h1>
        <p className="mt-1 text-sm text-slate-500">
          Apply what you&apos;ve learned by building real, end-to-end AI agent projects.
        </p>
      </div>

      <div className="mt-6">
        {loading && <LoadingState label="Loading projects..." />}
        {!loading && error && <ErrorState message={error} onRetry={load} />}
        {!loading && !error && projects && projects.length === 0 && (
          <EmptyState title="No projects available yet" description="Projects will appear here as they're published." />
        )}
        {!loading && !error && projects && projects.length > 0 && (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((p) => (
              <ProjectCard key={p.id} project={p} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function ProjectsPage() {
  return (
    <ProtectedRoute>
      <AppLayout pageTitle="Projects">
        <ProjectsContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
