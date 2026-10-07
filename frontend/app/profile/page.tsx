"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";
import { api, ApiError } from "@/lib/api";
import { initials, titleCase } from "@/lib/utils";
import type { StudentProfileOut } from "@/types";

function ProfileContent() {
  const { user, logout } = useAuth();
  const [profile, setProfile] = useState<StudentProfileOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.students.profile();
      setProfile(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load your profile.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (!user) return null;

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-bold uppercase tracking-wider text-blue-600 mb-1">
          ACCOUNT & PREFERENCES
        </p>
        <h1 className="text-2xl font-extrabold text-slate-900">Profile & Settings</h1>
        <p className="mt-1 text-sm text-slate-500">
          Manage your account details, career goals, study preferences, and certificates.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* User Card */}
        <Card className="lg:col-span-1 rounded-2xl border-slate-200">
          <div className="flex flex-col items-center text-center p-2">
            <div className="flex h-20 w-20 items-center justify-center rounded-full bg-blue-900 text-2xl font-bold text-white shadow-xs">
              {initials(user.full_name)}
            </div>
            <h2 className="mt-4 text-xl font-bold text-slate-900">{user.full_name}</h2>
            <p className="text-sm text-slate-500">{user.email}</p>
            <span className="mt-3 inline-block px-3 py-1 rounded-full bg-blue-50 text-blue-600 font-semibold text-xs capitalize">
              {user.role === "student" ? "Learner" : user.role}
            </span>
            <div className="mt-4 flex items-center justify-center gap-4 border-t border-slate-100 pt-4 w-full">
              <div className="text-center">
                <p className="text-xl font-bold text-slate-900">🔥 {profile?.current_streak_days ?? profile?.streak_days ?? 0}</p>
                <p className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">Day Streak</p>
              </div>
              <div className="h-8 w-[1px] bg-slate-200" />
              <div className="text-center">
                <p className="text-xl font-bold text-slate-900">🏆 {profile?.longest_streak_days ?? 0}</p>
                <p className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">Best Streak</p>
              </div>
            </div>
            <Button variant="secondary" size="sm" className="mt-6 w-full" onClick={() => logout()}>
              Log out
            </Button>
          </div>
        </Card>

        {/* Learning Profile & Details */}
        <div className="space-y-6 lg:col-span-2">
          {/* Active Membership Box */}
          <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden">
            <div className="h-1.5 w-full bg-blue-600" />
            <div className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wider bg-blue-50 px-2 py-0.5 rounded">
                    ACTIVE TIER
                  </span>
                  <h3 className="mt-2 text-lg font-bold text-slate-900">
                    Full Access · Agentic AI Curriculum
                  </h3>
                  <p className="text-xs text-slate-500 mt-1">
                    Unlimited access to 13 courses, diagnostic assessments, AI tutor, and project evaluations.
                  </p>
                </div>
                <Badge tone="green">Active</Badge>
              </div>
              <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span>Account status: <b>Active Learner</b></span>
                <span className="text-blue-600 font-semibold">Standard Access</span>
              </div>
            </div>
          </div>

          {loading && <LoadingState label="Loading profile..." />}
          {!loading && error && <ErrorState message={error} onRetry={load} />}
          {!loading && !error && profile && (
            <>
              <Card className="rounded-2xl border-slate-200">
                <h3 className="text-base font-bold text-slate-900">Learning Profile</h3>
                <dl className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <dt className="text-xs font-semibold text-slate-400">Career Goal</dt>
                    <dd className="mt-1 text-sm text-slate-800 font-medium">
                      {profile.career_goal || "AI Engineer / Agent Builder"}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs font-semibold text-slate-400">Target Role</dt>
                    <dd className="mt-1 text-sm text-slate-800 font-medium">
                      {profile.target_role || "Agentic AI Developer"}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs font-semibold text-slate-400">Preferred Pace</dt>
                    <dd className="mt-1 text-sm text-slate-800 font-medium">
                      {profile.preferred_pace ? titleCase(profile.preferred_pace) : "Standard"}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs font-semibold text-slate-400">Hours / Week</dt>
                    <dd className="mt-1 text-sm text-slate-800 font-medium">
                      {profile.available_hours_per_week ?? "15"} hrs
                    </dd>
                  </div>
                </dl>
                <div className="mt-5 flex gap-2">
                  <Badge tone={profile.onboarding_completed ? "green" : "gray"}>
                    {profile.onboarding_completed ? "Onboarding complete" : "Onboarding pending"}
                  </Badge>
                  <Badge tone={profile.diagnostic_completed ? "green" : "gray"}>
                    {profile.diagnostic_completed ? "Diagnostic complete" : "Diagnostic pending"}
                  </Badge>
                </div>
              </Card>

              <Card className="rounded-2xl border-slate-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-bold text-slate-900">Certificates & Credentials</h3>
                  <Badge tone={profile.certificates && profile.certificates.length > 0 ? "blue" : "gray"}>
                    {profile.certificates?.length ?? 0} Issued
                  </Badge>
                </div>
                {!profile.certificates || profile.certificates.length === 0 ? (
                  <p className="mt-3 text-sm text-slate-400">
                    No certificates issued yet. Complete all lessons in any course to automatically receive an official completion certificate.
                  </p>
                ) : (
                  <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                    {profile.certificates.map((cert) => (
                      <div
                        key={cert.id}
                        className="relative overflow-hidden rounded-xl border border-blue-200/80 bg-gradient-to-br from-blue-50/50 via-white to-sky-50/30 p-4 shadow-xs"
                      >
                        <div className="flex items-start justify-between">
                          <span className="text-2xl">🎓</span>
                          <span className="rounded bg-blue-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-blue-700">
                            Verified
                          </span>
                        </div>
                        <h4 className="mt-2 text-sm font-bold text-slate-900">
                          {cert.course_title || "Course Mastery Certificate"}
                        </h4>
                        <p className="mt-1 font-mono text-[11px] text-slate-500">
                          ID: {cert.certificate_number}
                        </p>
                        {cert.issued_at && (
                          <p className="mt-2 text-[11px] text-slate-400">
                            Issued: {new Date(cert.issued_at).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <AppLayout pageTitle="Profile & Settings">
        <ProfileContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
