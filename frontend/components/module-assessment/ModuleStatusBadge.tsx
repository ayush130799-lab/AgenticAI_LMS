import { Badge } from "@/components/ui/Badge";

/** Module progress state (server-derived). "available" (unlocked, not started) shows nothing extra. */
export function ModuleStatusBadge({ status }: { status: string | null | undefined }) {
  switch (status) {
    case "completed":
      return <Badge tone="green">✓ Completed</Badge>;
    case "in_progress":
      return <Badge tone="blue">● In progress</Badge>;
    case "locked":
      return <Badge tone="gray">🔒 Locked</Badge>;
    default:
      return null;
  }
}
