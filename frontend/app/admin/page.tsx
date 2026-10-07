"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { AdminNav } from "@/components/admin/AdminNav";
import { Card } from "@/components/ui/Card";
import { LoadingState } from "@/components/ui/LoadingState";
import { api } from "@/lib/api";

interface Counts {
  courses: number | null;
  skills: number | null;
  assessments: number | null;
  projects: number | null;
  users: number | null;
}

function AdminOverview() {
  const [counts, setCounts] = useState<Counts>({
    courses: null,
    skills: null,
    assessments: null,
    projects: null,
    users: null,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const [courses, skills, assessments, projects, users] = await Promise.all([
        api.courses.list().catch(() => []),
        api.skills.list().catch(() => []),
        api.assessments.list().catch(() => []),
        api.projects.list().catch(() => []),
        api.admin.users.list().catch(() => []),
      ]);
      setCounts({
        courses: courses.length,
        skills: skills.length,
        assessments: assessments.length,
        projects: projects.length,
        users: users.length,
      });
      setLoading(false);
    })();
  }, []);

  const cards = [
    { label: "Courses", value: counts.courses, href: "/admin/courses" },
    { label: "Skills", value: counts.skills, href: "/admin/skills" },
    { label: "Assessments", value: counts.assessments, href: "/admin/assessments" },
    { label: "Projects", value: counts.projects, href: "/admin/projects" },
    { label: "Users", value: counts.users, href: "/admin/users" },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-ink-900">Admin</h1>
      <p className="mt-1 text-sm text-ink-500">Manage the curriculum content that powers Agentic AI LMS.</p>

      <div className="mt-6">
        <AdminNav />
      </div>

      <div className="mt-8">
        {loading ? (
          <LoadingState label="Loading overview..." />
        ) : (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            {cards.map((c) => (
              <Link key={c.label} href={c.href}>
                <Card className="text-center transition-shadow hover:shadow-soft">
                  <p className="text-3xl font-extrabold text-ink-900">{c.value ?? "—"}</p>
                  <p className="mt-1 text-sm text-ink-500">{c.label}</p>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function AdminPage() {
  return (
    <ProtectedRoute adminOnly>
      <AppLayout pageTitle="Admin Console">
        <AdminOverview />
      </AppLayout>
    </ProtectedRoute>
  );
}
