"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useParams } from "next/navigation";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";
import { api, ApiError } from "@/lib/api";
import { titleCase, formatDate } from "@/lib/utils";
import type { ProjectCriterion, ProjectDetailOut, ProjectStep, ProjectSubmissionOut } from "@/types";

function renderItem(item: ProjectStep, key: string) {
  const title = typeof item.title === "string" ? item.title : null;
  const desc = typeof item.description === "string" ? item.description : null;
  return (
    <div key={key} className="rounded-xl border border-ink-200 p-3">
      {title && <p className="text-sm font-semibold text-ink-900">{title}</p>}
      {desc && <p className="mt-1 text-sm text-ink-500">{desc}</p>}
      {!title && !desc && <p className="text-sm text-ink-500">{JSON.stringify(item)}</p>}
    </div>
  );
}

function renderCriterion(c: ProjectCriterion, key: string) {
  return (
    <div key={key} className="flex items-start justify-between gap-3 rounded-xl border border-ink-200 p-3">
      <p className="text-sm text-ink-700">{c.criterion}</p>
      {typeof c.weight === "number" && (
        <span className="shrink-0 rounded-full bg-ink-100 px-2 py-0.5 text-xs font-semibold text-ink-500">
          {Math.round(c.weight * 100)}%
        </span>
      )}
    </div>
  );
}

function ProjectContent() {
  const params = useParams<{ projectId: string }>();
  const [project, setProject] = useState<ProjectDetailOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [repoUrl, setRepoUrl] = useState("");
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submission, setSubmission] = useState<ProjectSubmissionOut | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.projects.get(params.projectId);
      setProject(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load this project.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.projectId]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!project) return;
    if (!repoUrl.trim() && !notes.trim()) {
      setSubmitError("Add a repo URL or submission notes before submitting.");
      return;
    }
    setSubmitting(true);
    setSubmitError(null);
    try {
      const res = await api.projects.submit(project.id, {
        repo_url: repoUrl.trim() || undefined,
        submission_notes: notes.trim() || undefined,
      });
      setSubmission(res);
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err.detail : "Unable to submit your project.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return <LoadingState label="Loading project..." fullHeight />;
  if (error || !project) {
    return (
      <div>
        <ErrorState message={error ?? "Project not found."} onRetry={load} />
      </div>
    );
  }

  return (
    <div>
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Badge tone="purple">{titleCase(project.difficulty)}</Badge>
          <h1 className="mt-3 text-3xl font-extrabold text-ink-900">{project.title}</h1>
          <p className="mt-3 text-sm leading-relaxed text-ink-600">{project.overview}</p>

          <Card className="mt-6">
            <h2 className="text-base font-bold text-ink-900">Objective</h2>
            <p className="mt-2 text-sm text-ink-600">{project.objective}</p>
          </Card>

          <Card className="mt-4">
            <h2 className="text-base font-bold text-ink-900">Architecture</h2>
            <p className="mt-2 whitespace-pre-line text-sm text-ink-600">{project.architecture}</p>
          </Card>

          {project.milestones.length > 0 && (
            <Card className="mt-4">
              <h2 className="text-base font-bold text-ink-900">Milestones</h2>
              <div className="mt-3 space-y-2">
                {project.milestones.map((m, i) => renderItem(m, `m-${i}`))}
              </div>
            </Card>
          )}

          {project.tasks.length > 0 && (
            <Card className="mt-4">
              <h2 className="text-base font-bold text-ink-900">Tasks</h2>
              <div className="mt-3 space-y-2">
                {project.tasks.map((t, i) => renderItem(t, `t-${i}`))}
              </div>
            </Card>
          )}

          {project.evaluation_criteria.length > 0 && (
            <Card className="mt-4">
              <h2 className="text-base font-bold text-ink-900">Evaluation criteria</h2>
              <div className="mt-3 space-y-2">
                {project.evaluation_criteria.map((c, i) => renderCriterion(c, `c-${i}`))}
              </div>
            </Card>
          )}

          {project.prerequisites.length > 0 && (
            <div className="mt-6">
              <h2 className="text-base font-bold text-ink-900">Prerequisites</h2>
              <div className="mt-2 flex flex-wrap gap-2">
                {project.prerequisites.map((p) => (
                  <Badge key={p} tone="gray">
                    {p}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>

        <div>
          <Card className="sticky top-24">
            <h2 className="text-base font-bold text-ink-900">Submit your work</h2>
            <p className="mt-1 text-xs text-ink-400">Estimated {project.estimated_hours}h</p>

            {submission ? (
              <div className="mt-4 space-y-3">
                <Badge tone={submission.status === "evaluated" ? "green" : "blue"}>
                  {titleCase(submission.status)}
                </Badge>
                {typeof submission.score === "number" && (
                  <p className="text-2xl font-extrabold text-ink-900">{Math.round(submission.score)}%</p>
                )}
                {Boolean(
                  submission.ai_feedback?.feedback ||
                    submission.ai_feedback?.strengths?.length ||
                    submission.ai_feedback?.improvements?.length
                ) && (
                    <div className="space-y-3 rounded-xl bg-ink-100/60 p-3 text-sm text-ink-700">
                      {submission.ai_feedback.feedback && <p>{submission.ai_feedback.feedback}</p>}
                      {!!submission.ai_feedback.strengths?.length && (
                        <div>
                          <p className="font-semibold text-ink-900">Strengths</p>
                          <ul className="mt-1 list-disc space-y-1 pl-5">
                            {submission.ai_feedback.strengths.map((s, i) => (
                              <li key={i}>{s}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {!!submission.ai_feedback.improvements?.length && (
                        <div>
                          <p className="font-semibold text-ink-900">Improvements</p>
                          <ul className="mt-1 list-disc space-y-1 pl-5">
                            {submission.ai_feedback.improvements.map((s, i) => (
                              <li key={i}>{s}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                <p className="text-xs text-ink-400">Submitted {formatDate(submission.submitted_at)}</p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="mt-4 space-y-3">
                <Input
                  label="Repository URL"
                  placeholder="https://github.com/you/project"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                />
                <Textarea
                  label="Submission notes"
                  rows={4}
                  placeholder="What did you build, and any known limitations?"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
                {submitError && <p className="text-xs text-red-600">{submitError}</p>}
                <Button type="submit" fullWidth disabled={submitting}>
                  {submitting ? "Submitting..." : "Submit project"}
                </Button>
              </form>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}

export default function ProjectDetailPage() {
  return (
    <ProtectedRoute>
      <AppLayout pageTitle="Projects">
        <ProjectContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
