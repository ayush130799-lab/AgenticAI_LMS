import type { ReactNode } from "react";
import { Card } from "@/components/ui/Card";
import { cn } from "@/lib/utils";

interface DashboardWidgetProps {
  title?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
  span?: 1 | 2 | 3;
}

export function DashboardWidget({ title, action, children, className, span = 1 }: DashboardWidgetProps) {
  return (
    <Card
      className={cn(
        span === 2 && "lg:col-span-2",
        span === 3 && "lg:col-span-3",
        className
      )}
    >
      {(title || action) && (
        <div className="mb-4 flex items-center justify-between">
          {title && <h3 className="text-base font-bold text-ink-900">{title}</h3>}
          {action}
        </div>
      )}
      {children}
    </Card>
  );
}

export function DashboardGrid({ children }: { children: ReactNode }) {
  return <div className="grid grid-cols-1 gap-5 lg:grid-cols-3">{children}</div>;
}
