"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

interface Options {
  adminOnly?: boolean;
}

/**
 * Client-side auth guard. Redirects to /login when there's no authenticated
 * user, or to / when adminOnly is set and the user isn't an admin.
 */
export function useRequireAuth(options: Options = {}) {
  const { user, isLoading, unreachable, sessionExpired } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoading || unreachable) return;
    if (!user) {
      router.replace(sessionExpired ? "/login?expired=1" : "/login");
      return;
    }
    if (options.adminOnly && user.role !== "admin") {
      router.replace("/");
    }
  }, [user, isLoading, unreachable, sessionExpired, options.adminOnly, router]);

  return { user, isLoading, unreachable };
}
