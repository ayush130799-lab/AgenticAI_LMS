"use client";

import { icons } from "@/components/layout/nav";
import { initials } from "@/lib/utils";
import type { UserOut } from "@/types";

export function roleLabel(user: UserOut | null): string {
  return user?.role === "admin" ? "Admin" : "Learner";
}

interface UserProfileProps {
  user: UserOut | null;
  collapsed?: boolean;
  onLogout: () => void;
}

export function UserProfile({ user, collapsed, onLogout }: UserProfileProps) {
  if (!user) return null;
  return (
    <div className={`flex items-center gap-3 rounded-xl p-2 ${collapsed ? "lg:flex-col lg:gap-2" : ""}`}>
      <div
        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-blue text-xs font-bold text-white"
        title={collapsed ? user.full_name : undefined}
      >
        {initials(user.full_name) || "?"}
      </div>
      <div className={`min-w-0 flex-1 ${collapsed ? "lg:hidden" : ""}`}>
        <p className="truncate text-sm font-semibold text-ink-900">{user.full_name}</p>
        <p className="text-xs text-ink-400">{roleLabel(user)}</p>
      </div>
      <button
        onClick={onLogout}
        className="rounded-lg p-1.5 text-ink-400 transition-colors hover:bg-red-50 hover:text-red-600"
        title="Log out"
        aria-label="Log out"
      >
        {icons.logout}
      </button>
    </div>
  );
}
