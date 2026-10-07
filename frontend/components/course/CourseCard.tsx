import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { CourseIcon } from "@/components/course/CourseIcon";
import { titleCase } from "@/lib/utils";
import type { CourseSummaryOut } from "@/types";

const LEVEL_TONE: Record<string, "green" | "blue" | "purple"> = {
  beginner: "green",
  intermediate: "blue",
  advanced: "purple",
};

interface CourseCardProps {
  course: CourseSummaryOut;
}

export function CourseCard({ course }: CourseCardProps) {
  return (
    <Card className="flex h-full flex-col">
      <div className="flex items-center justify-between gap-2">
        <CourseIcon
          icon={course.icon}
          className="flex h-11 w-11 items-center justify-center rounded-xl bg-surface-tint-blue text-xl text-brand-blue"
        />
        <Badge tone={LEVEL_TONE[course.level] || "blue"}>{titleCase(course.level)}</Badge>
      </div>

      <h3 className="mt-4 text-base font-bold text-ink-900">{course.title}</h3>
      {course.subtitle && <p className="text-sm text-ink-400">{course.subtitle}</p>}
      <p className="mt-2 flex-1 text-sm text-ink-500">{course.description}</p>

      <p className="mt-3 text-xs text-ink-400">
        {course.module_count} modules &middot; {course.lesson_count} lessons &middot;{" "}
        {course.estimated_hours}h
      </p>

      {typeof course.progress_percent === "number" && (
        <ProgressBar value={course.progress_percent} className="mt-3" showValue />
      )}

      <Button href={`/courses/${course.id}`} className="mt-4" fullWidth variant="secondary">
        View course
      </Button>
    </Card>
  );
}
