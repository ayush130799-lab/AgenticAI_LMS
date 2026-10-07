"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { NAV_GROUPS, icons, isActive } from "@/components/layout/nav";
import { UserProfile } from "@/components/layout/UserProfile";
import { cn } from "@/lib/utils";
import type { UserOut } from "@/types";

interface AppSidebarProps {
  user: UserOut | null;
  collapsed: boolean;
  mobileOpen: boolean;
  onToggleCollapsed: () => void;
  onCloseMobile: () => void;
  onLogout: () => void;
}

export function AppSidebar({ user, collapsed, mobileOpen, onToggleCollapsed, onCloseMobile, onLogout }: AppSidebarProps) {
  const pathname = usePathname();
  const groups = NAV_GROUPS.map((g) => ({
    ...g,
    items: g.items.filter((i) => !i.adminOnly || user?.role === "admin"),
  })).filter((g) => g.items.length > 0);

  return (
    <>
      {mobileOpen && (
        <div className="fixed inset-0 z-40 bg-ink-900/40 lg:hidden" onClick={onCloseMobile} aria-hidden="true" />
      )}
      <aside
        aria-label="Primary"
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex shrink-0 flex-col border-r border-ink-200 bg-white transition-all duration-200 lg:sticky lg:top-0 lg:z-20 lg:h-screen",
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
          collapsed ? "w-72 lg:w-[72px]" : "w-72"
        )}
      >
        <div className="flex h-16 items-center justify-between border-b border-ink-100 px-4">
          <Link href="/dashboard" className="flex min-w-0 items-center gap-3">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand-blue font-bold text-white">
              A
            </span>
            <span className={cn("min-w-0 leading-tight", collapsed && "lg:hidden")}>
              <span className="block truncate text-[15px] font-bold text-ink-900">
                Agentic<span className="text-brand-cyan">AI</span> LMS
              </span>
              <span className="block truncate text-[11px] text-ink-400">AI Learning Platform</span>
            </span>
          </Link>
          <button
            onClick={onCloseMobile}
            className="rounded-lg p-1.5 text-ink-500 hover:bg-ink-100 lg:hidden"
            aria-label="Close menu"
          >
            {icons.close}
          </button>
        </div>

        <nav className="flex-1 space-y-5 overflow-y-auto px-3 py-4">
          {groups.map((group) => (
            <div key={group.title}>
              <p
                className={cn(
                  "mb-1.5 px-3 text-[11px] font-semibold uppercase tracking-wider text-ink-400",
                  collapsed && "lg:hidden"
                )}
              >
                {group.title}
              </p>
              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const active = isActive(pathname, item.href);
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      title={collapsed ? item.label : undefined}
                      aria-current={active ? "page" : undefined}
                      className={cn(
                        "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                        collapsed && "lg:justify-center lg:px-0",
                        active
                          ? "bg-surface-tint-blue text-brand-blue-dark"
                          : "text-ink-500 hover:bg-ink-100 hover:text-ink-900"
                      )}
                    >
                      <span className={active ? "text-brand-blue" : "text-ink-400"}>{item.icon}</span>
                      <span className={cn("truncate", collapsed && "lg:hidden")}>{item.label}</span>
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        <div className="border-t border-ink-100 p-3">
          <UserProfile user={user} collapsed={collapsed} onLogout={onLogout} />
          <button
            onClick={onToggleCollapsed}
            className="mt-2 hidden w-full items-center justify-center gap-2 rounded-lg border border-ink-200 py-1.5 text-xs font-semibold text-ink-500 transition-colors hover:bg-ink-100 lg:flex"
            aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            <span className={cn("transition-transform", collapsed && "rotate-180")}>{icons.chevrons}</span>
            {!collapsed && "Collapse"}
          </button>
        </div>
      </aside>
    </>
  );
}
