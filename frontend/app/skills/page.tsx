"use client";

import { useEffect, useMemo, useState } from "react";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { EmptyState } from "@/components/ui/EmptyState";
import { SkillCard } from "@/components/skills/SkillCard";
import { SkillsDAG } from "@/components/skills/SkillsDAG";
import { api, ApiError } from "@/lib/api";
import { titleCase } from "@/lib/utils";
import type { StudentSkillOut } from "@/types";

function SkillsContent() {
  const [skills, setSkills] = useState<StudentSkillOut[] | null>(null);
  const [graphData, setGraphData] = useState<{
    nodes: { id: string; slug: string; name: string; category: string; description: string }[];
    edges: { source: string; target: string; required_mastery: number }[];
  } | null>(null);
  const [viewMode, setViewMode] = useState<"matrix" | "graph">("matrix");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [skillsData, graph] = await Promise.all([
        api.students.skills(),
        api.skills.graph(),
      ]);
      setSkills(skillsData);
      setGraphData(graph);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load your skills.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const grouped = useMemo(() => {
    if (!skills) return {};
    return skills.reduce<Record<string, StudentSkillOut[]>>((acc, skill) => {
      acc[skill.category] = acc[skill.category] || [];
      acc[skill.category].push(skill);
      return acc;
    }, {});
  }, [skills]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-blue-600 mb-1">
            COMPETENCY MATRIX & HEATMAP
          </p>
          <h1 className="text-2xl font-extrabold text-slate-900">Your Skills</h1>
          <p className="mt-1 text-sm text-slate-500">
            Mastery and confidence across every skill in the Agentic AI curriculum.
          </p>
        </div>

        {/* View Toggle */}
        <div className="flex items-center gap-1 rounded-xl border border-slate-200 bg-white p-1">
          <button
            onClick={() => setViewMode("matrix")}
            className={`rounded-lg px-3 py-1.5 text-xs font-bold transition ${
              viewMode === "matrix"
                ? "bg-blue-600 text-white shadow-xs"
                : "text-slate-600 hover:bg-slate-50"
            }`}
          >
            📊 Matrix View
          </button>
          <button
            onClick={() => setViewMode("graph")}
            className={`rounded-lg px-3 py-1.5 text-xs font-bold transition ${
              viewMode === "graph"
                ? "bg-blue-600 text-white shadow-xs"
                : "text-slate-600 hover:bg-slate-50"
            }`}
          >
            🕸️ Prerequisite DAG
          </button>
        </div>
      </div>

      <div className="mt-6">
        {loading && <LoadingState label="Loading competency matrix..." />}
        {!loading && error && <ErrorState message={error} onRetry={load} />}
        {!loading && !error && skills && skills.length === 0 && (
          <EmptyState
            title="No skill data yet"
            description="Complete the diagnostic assessment or your first lessons to start building your skill profile."
          />
        )}

        {!loading && !error && viewMode === "graph" && graphData && skills && (
          <SkillsDAG
            nodes={graphData.nodes}
            edges={graphData.edges}
            studentSkills={skills}
          />
        )}

        {!loading &&
          !error &&
          viewMode === "matrix" &&
          Object.entries(grouped).map(([category, items]) => (
            <div key={category} className="mb-10">
              <h2 className="mb-4 text-base font-bold text-slate-800 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-600" />
                <span>{titleCase(category)}</span>
              </h2>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {items.map((skill) => (
                  <SkillCard key={skill.skill_slug} skill={skill} />
                ))}
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}

export default function SkillsPage() {
  return (
    <ProtectedRoute>
      <AppLayout pageTitle="Skills">
        <SkillsContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
