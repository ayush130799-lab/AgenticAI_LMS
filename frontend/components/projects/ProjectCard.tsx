import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { titleCase } from "@/lib/utils";
import type { ProjectSummaryOut } from "@/types";

const DIFFICULTY_TONE: Record<string, "green" | "blue" | "purple" | "amber"> = {
  beginner: "green",
  intermediate: "blue",
  advanced: "purple",
  expert: "amber",
};

interface ProjectCardProps {
  project: ProjectSummaryOut;
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <Card className="flex h-full flex-col">
      <div className="flex items-center justify-between gap-2">
        <Badge tone={DIFFICULTY_TONE[project.difficulty] || "blue"}>{titleCase(project.difficulty)}</Badge>
        {project.submission_status && (
          <Badge tone={project.submission_status === "evaluated" ? "green" : "gray"}>
            {titleCase(project.submission_status)}
          </Badge>
        )}
      </div>
      <h3 className="mt-3 text-base font-bold text-ink-900">{project.title}</h3>
      <p className="mt-2 flex-1 text-sm text-ink-500">{project.overview}</p>
      <p className="mt-3 text-xs text-ink-400">Estimated {project.estimated_hours}h</p>
      <Button href={`/projects/${project.id}`} className="mt-4" fullWidth variant="secondary">
        View project
      </Button>
    </Card>
  );
}
