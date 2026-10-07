"use client";

import { useMemo, useState } from "react";
import type { StudentSkillOut } from "@/types";

interface SkillNode {
  id: string;
  slug: string;
  name: string;
  category: string;
  description: string;
}

interface SkillEdge {
  source: string;
  target: string;
  required_mastery: number;
}

interface SkillsDAGProps {
  nodes: SkillNode[];
  edges: SkillEdge[];
  studentSkills: StudentSkillOut[];
}

export function SkillsDAG({ nodes, edges, studentSkills }: SkillsDAGProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [activeNode, setActiveNode] = useState<SkillNode | null>(null);

  const skillMasteryMap = useMemo(() => {
    const map = new Map<string, StudentSkillOut>();
    for (const s of studentSkills) {
      map.set(s.skill_slug, s);
    }
    return map;
  }, [studentSkills]);

  const categories = useMemo(() => {
    const set = new Set<string>();
    nodes.forEach((n) => set.add(n.category));
    return Array.from(set);
  }, [nodes]);

  const filteredNodes = useMemo(() => {
    if (selectedCategory === "all") return nodes;
    return nodes.filter((n) => n.category === selectedCategory);
  }, [nodes, selectedCategory]);

  const nodeMap = useMemo(() => {
    const map = new Map<string, SkillNode>();
    nodes.forEach((n) => map.set(n.id, n));
    return map;
  }, [nodes]);

  // Group nodes by category to lay them out in sequential progression tiers
  const groupedByCategory = useMemo(() => {
    const map: Record<string, SkillNode[]> = {};
    for (const n of filteredNodes) {
      map[n.category] = map[n.category] || [];
      map[n.category].push(n);
    }
    return map;
  }, [filteredNodes]);

  return (
    <div className="rounded-2xl border border-slate-200/90 bg-white p-6 shadow-xs">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <span>🕸️ Skills Prerequisite Graph (DAG)</span>
            <span className="rounded bg-blue-100 px-2 py-0.5 text-[10px] font-bold text-blue-700">
              Interactive
            </span>
          </h2>
          <p className="mt-1 text-xs text-slate-500">
            Explore how fundamental AI skills build up into advanced multi-agent and production architectures.
          </p>
        </div>

        {/* Filter categories */}
        <div className="flex flex-wrap gap-1.5">
          <button
            onClick={() => setSelectedCategory("all")}
            className={`rounded-full px-3 py-1 text-xs font-semibold transition ${
              selectedCategory === "all"
                ? "bg-blue-600 text-white"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            All Categories
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`rounded-full px-3 py-1 text-xs font-semibold capitalize transition ${
                selectedCategory === cat
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {cat.replace(/_/g, " ")}
            </button>
          ))}
        </div>
      </div>

      {/* DAG Visualization Canvas */}
      <div className="mt-6 space-y-6">
        {Object.entries(groupedByCategory).map(([cat, catNodes]) => (
          <div key={cat} className="rounded-xl border border-slate-100 bg-slate-50/60 p-4">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                {cat.replace(/_/g, " ")}
              </span>
              <span className="text-[11px] font-medium text-slate-400">
                {catNodes.length} skill{catNodes.length > 1 ? "s" : ""}
              </span>
            </div>

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
              {catNodes.map((node) => {
                const studentSkill = skillMasteryMap.get(node.slug);
                const mastery = studentSkill ? Math.round(studentSkill.mastery * 100) : 0;
                const isSelected = activeNode?.id === node.id;

                // Find prerequisites (incoming edges)
                const prereqEdges = edges.filter((e) => e.target === node.id);
                const prereqNames = prereqEdges
                  .map((e) => nodeMap.get(e.source)?.name)
                  .filter(Boolean);

                return (
                  <div
                    key={node.id}
                    onClick={() => setActiveNode(isSelected ? null : node)}
                    className={`cursor-pointer rounded-xl border p-3.5 transition ${
                      isSelected
                        ? "border-blue-500 bg-blue-50/90 shadow-xs ring-2 ring-blue-500/20"
                        : "border-slate-200 bg-white hover:border-blue-300 hover:shadow-xs"
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <span className="text-xs font-bold text-slate-900 line-clamp-1">
                        {node.name}
                      </span>
                      <span
                        className={`ml-1 text-[11px] font-bold ${
                          mastery >= 70
                            ? "text-emerald-600"
                            : mastery >= 40
                            ? "text-blue-600"
                            : "text-slate-400"
                        }`}
                      >
                        {mastery}%
                      </span>
                    </div>

                    {/* Mastery Bar */}
                    <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
                      <div
                        className={`h-full transition-all duration-300 ${
                          mastery >= 70
                            ? "bg-emerald-500"
                            : mastery >= 40
                            ? "bg-blue-500"
                            : "bg-slate-300"
                        }`}
                        style={{ width: `${mastery}%` }}
                      />
                    </div>

                    {/* Prerequisite Tags */}
                    {prereqNames.length > 0 && (
                      <div className="mt-3 border-t border-slate-100 pt-2">
                        <p className="text-[10px] uppercase font-bold text-slate-400">Requires:</p>
                        <div className="mt-1 flex flex-wrap gap-1">
                          {prereqNames.map((pName, idx) => (
                            <span
                              key={idx}
                              className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-slate-600"
                            >
                              ↳ {pName}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Selected Node Details Drawer */}
      {activeNode && (
        <div className="mt-6 rounded-xl border border-blue-200 bg-gradient-to-r from-blue-50/80 to-indigo-50/40 p-4">
          <div className="flex items-start justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600">
                SKILL INSPECTION
              </span>
              <h3 className="text-base font-bold text-slate-900">{activeNode.name}</h3>
              {activeNode.description && (
                <p className="mt-1 text-xs text-slate-600 max-w-2xl">{activeNode.description}</p>
              )}
            </div>
            <button
              onClick={() => setActiveNode(null)}
              className="text-slate-400 hover:text-slate-600 text-xs font-semibold"
            >
              ✕ Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
