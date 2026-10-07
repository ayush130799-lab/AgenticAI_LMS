import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { titleCase } from "@/lib/utils";
import type { StudentSkillOut } from "@/types";

interface SkillCardProps {
  skill: StudentSkillOut;
  locked?: boolean;
}

export function SkillCard({ skill, locked }: SkillCardProps) {
  return (
    <Card className={locked ? "opacity-60" : undefined}>
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-sm font-bold text-ink-900">{skill.skill_name}</p>
          <p className="text-xs text-ink-400">{titleCase(skill.category)}</p>
        </div>
        <Badge tone={locked ? "gray" : "cyan"}>{locked ? "Locked" : titleCase(skill.level)}</Badge>
      </div>

      <div className="mt-4 space-y-3">
        <ProgressBar value={skill.mastery} gradient showValue label="Mastery" />
        <ProgressBar value={skill.confidence * 100} showValue label="Confidence" />
      </div>

      <p className="mt-3 text-xs text-ink-400">
        {skill.attempts} attempt{skill.attempts === 1 ? "" : "s"} recorded
      </p>
    </Card>
  );
}
