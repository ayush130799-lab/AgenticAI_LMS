"use client";

import type { ReactNode } from "react";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { useAuth } from "@/hooks/useAuth";

interface ProtectedRouteProps {
  children: ReactNode;
  adminOnly?: boolean;
}

export function ProtectedRoute({ children, adminOnly }: ProtectedRouteProps) {
  const { user, isLoading, unreachable } = useRequireAuth({ adminOnly });
  const { refreshUser } = useAuth();

  if (unreachable && !user) {
    return (
      <div className="mx-auto max-w-xl px-4 py-16">
        <ErrorState
          title="Can't reach the server"
          message="We couldn't verify your session. Your progress is safe. Check your connection and try again."
          onRetry={() => refreshUser()}
        />
      </div>
    );
  }

  if (isLoading || !user) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <LoadingState label="Checking your session..." />
      </div>
    );
  }

  if (adminOnly && user.role !== "admin") {
    return null;
  }

  return <>{children}</>;
}
