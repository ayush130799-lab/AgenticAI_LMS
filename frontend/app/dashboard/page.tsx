"use client";

import Link from "next/link";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { DashboardLayout } from "@/components/layout/AppLayout";
import { ContinueLearningCard } from "@/components/dashboard/ContinueLearningCard";
import { DashboardWidget } from "@/components/dashboard/DashboardWidget";
import { LearningPath } from "@/components/dashboard/LearningPath";
import { RecentActivity } from "@/components/dashboard/RecentActivity";
import { RecommendationCard } from "@/components/dashboard/RecommendationCard";
import { SectionState, Skeleton } from "@/components/dashboard/SectionState";
import { StatCard } from "@/components/dashboard/StatCard";
import { WelcomeSection } from "@/components/dashboard/WelcomeSection";
import { ProjectCard } from "@/components/projects/ProjectCard";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { useAsync } from "@/hooks/useAsync";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import { formatProgress, titleCase } from "@/lib/utils";
import type { CourseSummaryOut, ProjectSummaryOut } from "@/types";

const WEAK_SKILL_THRESHOLD = 0.6;

function ViewAll({ href, label }: { href: string; label: string }) {
  return (
    <Link href={href} className="text-sm font-semibold text-brand-blue hover:underline">
      {label} →
    </Link>
  );
}

function pickProjects(projects: ProjectSummaryOut[]): ProjectSummaryOut[] {
  const started = projects.filter((p) => p.submission_status);
  const rest = projects.filter((p) => !p.submission_status);
  return [...started, ...rest].slice(0, 2);
}

function DashboardContent() {
  const { user } = useAuth();
  const dashboard = useAsync(() => api.dashboard.get(), "We couldn't load your dashboard data.");
  const courses = useAsync(() => api.courses.list(), "We couldn't load your courses.");
  const projects = useAsync(() => api.projects.list(), "We couldn't load projects.");
  const activity = useAsync(() => api.students.activity(6), "We couldn't load recent activity.");

  const d = dashboard.data;
  const courseList: CourseSummaryOut[] = courses.data ?? [];
  const projectList: ProjectSummaryOut[] = projects.data ?? [];

  const currentCourseProgress = d?.current_course
    ? courseList.find((c) => c.id === d.current_course?.id)?.progress_percent ?? null
    : null;
  const otherInProgress = courseList
    .filter((c) => (c.progress_percent ?? 0) > 0 && (c.progress_percent ?? 0) < 100 && c.id !== d?.current_course?.id)
    .slice(0, 2);
  const firstCourse = [...courseList].sort((a, b) => a.order_index - b.order_index)[0];

  const assessedSkills = d?.skills.filter((s) => s.attempts > 0).length ?? 0;
  const weakSkills = (d?.weak_skills ?? []).filter((s) => s.mastery < WEAK_SKILL_THRESHOLD).slice(0, 4);
  const submitted = projectList.filter((p) => p.submission_status).length;
  const underReview = projectList.filter((p) => p.submission_status && p.submission_status !== "evaluated").length;

  const nothingStarted = !!d && !d.continue_lesson && !d.pending_module_assessment && !d.current_course && otherInProgress.length === 0;

  return (
    <div className="space-y-8">
      <WelcomeSection name={d?.full_name || user?.full_name} streakDays={d?.learning_streak_days} />

      {/* Overview */}
      <section aria-label="Learning overview" className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Learning progress"
          loading={dashboard.loading}
          error={!!dashboard.error}
          value={formatProgress(d?.curriculum_progress_percent)}
          percent={d?.curriculum_progress_percent ?? 0}
          caption={d?.current_course ? d.current_course.title : "No learning activity yet"}
          action={d?.continue_lesson ? { label: "Continue learning", href: `/lessons/${d.continue_lesson.id}` } : { label: "Browse courses", href: "/courses" }}
        />
        <StatCard
          label="Skill mastery"
          accent="cyan"
          gradient
          loading={dashboard.loading}
          error={!!dashboard.error}
          value={assessedSkills > 0 ? `${Math.round(d?.overall_skill_mastery_percent ?? 0)}%` : "—"}
          percent={assessedSkills > 0 ? d?.overall_skill_mastery_percent ?? 0 : null}
          caption={assessedSkills > 0 ? `${assessedSkills} of ${d?.skills.length ?? 0} skills assessed` : "Take an assessment to build your skill profile"}
          action={{ label: "View skills", href: "/skills" }}
        />
        <StatCard
          label="Projects"
          accent="purple"
          loading={projects.loading}
          error={!!projects.error}
          value={String(submitted)}
          caption={
            projectList.length === 0
              ? "No projects available yet"
              : submitted === 0
                ? `No projects submitted yet · ${projectList.length} available`
                : `submitted of ${projectList.length}${underReview ? ` · ${underReview} under review` : ""}`
          }
          action={{ label: "Open projects", href: "/projects" }}
        />
        <StatCard
          label="Skill assessment"
          accent="amber"
          loading={dashboard.loading}
          error={!!dashboard.error}
          value={d?.recent_assessment ? `${Math.round(d.recent_assessment.score_percent)}%` : "Not taken"}
          caption={
            d?.recent_assessment
              ? `${d.recent_assessment.title} · ${d.recent_assessment.assessment_type === "diagnostic" ? "Baseline set" : d.recent_assessment.passed ? "Passed" : "Needs review"}`
              : d?.upcoming_assessment
                ? d.upcoming_assessment.title
                : "No assessment results yet"
          }
          action={
            d?.upcoming_assessment
              ? { label: d.recent_assessment ? "Next assessment" : "Take assessment", href: `/assessments/${d.upcoming_assessment.assessment_id}` }
              : { label: "View assessments", href: "/assessments" }
          }
        />
      </section>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <DashboardWidget title="Continue learning" action={<ViewAll href="/courses" label="All courses" />}>
            <SectionState
              loading={dashboard.loading || courses.loading}
              error={dashboard.error ?? courses.error}
              onRetry={() => {
                dashboard.reload();
                courses.reload();
              }}
              skeleton={<Skeleton className="h-28 w-full" />}
            >
              {nothingStarted ? (
                <EmptyState
                  title="No learning activity yet"
                  description="Start your first course and your progress will show up here."
                  action={
                    <Button href={firstCourse ? `/courses/${firstCourse.id}` : "/courses"}>
                      {firstCourse ? `Start ${firstCourse.title}` : "Browse courses"} →
                    </Button>
                  }
                  className="py-8"
                />
              ) : (
                <div className="space-y-3">
                  {d?.pending_module_assessment && (
                    <ContinueLearningCard
                      primary
                      eyebrow="Module assessment"
                      title={`${d.pending_module_assessment.module_title} assessment`}
                      subtitle="All lessons done. Pass the assessment to complete this module and unlock the next one."
                      href={`/modules/${d.pending_module_assessment.module_id}/assessment`}
                      cta={d.pending_module_assessment.status === "in_progress" ? "Resume" : "Take assessment"}
                    />
                  )}
                  {d?.continue_lesson && (
                    <ContinueLearningCard
                      primary
                      eyebrow="Resume lesson"
                      title={d.continue_lesson.title}
                      subtitle={d.continue_lesson.course_title}
                      percent={currentCourseProgress}
                      href={`/lessons/${d.continue_lesson.id}`}
                    />
                  )}
                  {otherInProgress.map((c) => (
                    <ContinueLearningCard
                      key={c.id}
                      eyebrow="In progress"
                      title={c.title}
                      subtitle={c.subtitle ?? undefined}
                      percent={c.progress_percent}
                      href={`/courses/${c.id}`}
                    />
                  ))}
                </div>
              )}
            </SectionState>
          </DashboardWidget>

          <DashboardWidget title="Recommended for you" action={<ViewAll href="/learning-path" label="Full learning path" />}>
            <SectionState
              loading={dashboard.loading}
              error={dashboard.error}
              onRetry={dashboard.reload}
              skeleton={<Skeleton className="h-32 w-full" />}
            >
              {d && d.recommendations.length > 0 ? (
                <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                  {d.recommendations.slice(0, 4).map((rec) => (
                    <RecommendationCard key={rec.id} recommendation={rec} />
                  ))}
                </div>
              ) : (
                <EmptyState
                  title="No recommendations yet"
                  description="Your AI learning path turns your skill profile into personalized next steps."
                  action={<Button href="/learning-path">Generate my learning path</Button>}
                  className="py-8"
                />
              )}
            </SectionState>
          </DashboardWidget>

          <DashboardWidget
            title={submitted > 0 ? "Your projects" : "Start building"}
            action={<ViewAll href="/projects" label="All projects" />}
          >
            <SectionState
              loading={projects.loading}
              error={projects.error}
              onRetry={projects.reload}
              skeleton={<Skeleton className="h-40 w-full" />}
            >
              {projectList.length > 0 ? (
                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                  {pickProjects(projectList).map((p) => (
                    <ProjectCard key={p.id} project={p} />
                  ))}
                </div>
              ) : (
                <EmptyState title="No projects available yet" description="Hands-on agent projects will appear here." className="py-8" />
              )}
            </SectionState>
          </DashboardWidget>
        </div>

        <div className="space-y-6">
          <DashboardWidget title="My learning path">
            <SectionState
              loading={courses.loading}
              error={courses.error}
              onRetry={courses.reload}
              skeleton={<Skeleton className="h-64 w-full" />}
            >
              {courseList.length > 0 ? (
                <LearningPath courses={courseList} />
              ) : (
                <EmptyState title="No courses yet" description="The curriculum will appear here once it is published." className="py-8" />
              )}
            </SectionState>
          </DashboardWidget>

          {weakSkills.length > 0 && (
            <DashboardWidget title="Skills to strengthen" action={<ViewAll href="/skills" label="All skills" />}>
              <ul className="space-y-4">
                {weakSkills.map((s) => (
                  <li key={s.skill_slug}>
                    <ProgressBar
                      label={s.skill_name}
                      value={s.mastery * 100}
                      showValue
                      gradient
                    />
                    <p className="mt-1 text-[11px] text-ink-400">{titleCase(s.level)}</p>
                  </li>
                ))}
              </ul>
            </DashboardWidget>
          )}

          <DashboardWidget title="Recent activity">
            <SectionState
              loading={activity.loading}
              error={activity.error}
              onRetry={activity.reload}
              skeleton={<Skeleton className="h-32 w-full" />}
            >
              {activity.data && activity.data.length > 0 ? (
                <RecentActivity items={activity.data} />
              ) : (
                <p className="text-sm text-ink-500">No activity yet. Complete a lesson or assessment and it will show up here.</p>
              )}
            </SectionState>
          </DashboardWidget>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardLayout pageTitle="Dashboard">
        <DashboardContent />
      </DashboardLayout>
    </ProtectedRoute>
  );
}
