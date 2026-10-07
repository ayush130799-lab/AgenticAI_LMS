"use client";

import Link from "next/link";
import { icons } from "@/components/layout/nav";
import { roleLabel } from "@/components/layout/UserProfile";
import { initials } from "@/lib/utils";
import type { UserOut } from "@/types";

interface TopHeaderProps {
  title: string;
  user: UserOut | null;
  notificationCount: number;
  onOpenMenu: () => void;
  onOpenNotifications: () => void;
  onOpenSearch?: () => void;
}

export function TopHeader({
  title,
  user,
  notificationCount,
  onOpenMenu,
  onOpenNotifications,
  onOpenSearch,
}: TopHeaderProps) {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-ink-200 bg-white/95 px-4 backdrop-blur sm:px-8">
      <div className="flex min-w-0 items-center gap-3">
        <button
          onClick={onOpenMenu}
          className="-ml-2 rounded-lg p-2 text-ink-700 hover:bg-ink-100 lg:hidden"
          aria-label="Open menu"
        >
          {icons.menu}
        </button>
        <h1 className="truncate text-lg font-bold text-ink-900">{title}</h1>
      </div>

      <div className="flex items-center gap-2 sm:gap-4">
        {onOpenSearch && (
          <button
            onClick={onOpenSearch}
            className="flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-slate-500 hover:border-slate-300 hover:bg-slate-100 transition"
          >
            <span>🔍 Search...</span>
            <kbd className="hidden rounded bg-white px-1.5 py-0.5 text-[10px] font-semibold text-slate-400 border border-slate-200 sm:inline-block">
              Ctrl+K
            </kbd>
          </button>
        )}

        <button
          onClick={onOpenNotifications}
          className="relative rounded-full p-2 text-ink-500 transition-colors hover:bg-ink-100 hover:text-ink-900"
          aria-label={notificationCount > 0 ? `Notifications (${notificationCount})` : "Notifications"}
        >
          {icons.bell}
          {notificationCount > 0 && (
            <span className="absolute right-1 top-1 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-brand-blue px-1 text-[10px] font-bold text-white ring-2 ring-white">
              {notificationCount}
            </span>
          )}
        </button>

        {user && (
          <Link href="/profile" className="flex items-center gap-2.5 rounded-full py-1 pl-1 pr-1 hover:bg-ink-100 sm:pr-3">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-blue text-xs font-bold text-white">
              {initials(user.full_name) || "?"}
            </span>
            <span className="hidden text-sm sm:block">
              <span className="font-semibold text-ink-900">{user.full_name}</span>
              <span className="text-ink-400"> · {roleLabel(user)}</span>
            </span>
          </Link>
        )}
      </div>
    </header>
  );
}
