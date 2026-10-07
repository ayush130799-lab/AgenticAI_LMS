"use client";

import { useCallback, useEffect, useState, type ReactNode } from "react";
import { usePathname, useRouter } from "next/navigation";
import { AppSidebar } from "@/components/layout/AppSidebar";
import { NotificationsPanel, useNotifications } from "@/components/layout/NotificationsPanel";
import { TopHeader } from "@/components/layout/TopHeader";
import { SearchModal } from "@/components/layout/SearchModal";
import { pageTitleFor } from "@/components/layout/nav";
import { useAuth } from "@/hooks/useAuth";

const COLLAPSED_KEY = "lms_sidebar_collapsed";

interface DashboardLayoutProps {
  children: ReactNode;
  /** Overrides the header title; defaults to the active nav item's label. */
  pageTitle?: string;
}

/** Authenticated app shell: collapsible sidebar + top header + page content. */
export function DashboardLayout({ children, pageTitle }: DashboardLayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const notifications = useNotifications();

  useEffect(() => {
    try {
      setCollapsed(window.localStorage.getItem(COLLAPSED_KEY) === "1");
    } catch {
      // storage unavailable (private mode) - keep default
    }
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  // Global Ctrl+K / Cmd+K keyboard shortcut for Search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setSearchOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    if (!mobileOpen) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setMobileOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [mobileOpen]);

  const toggleCollapsed = useCallback(() => {
    setCollapsed((c) => {
      try {
        window.localStorage.setItem(COLLAPSED_KEY, c ? "0" : "1");
      } catch {
        // ignore
      }
      return !c;
    });
  }, []);

  const handleLogout = useCallback(async () => {
    await logout();
    router.replace("/");
  }, [logout, router]);

  const openNotifications = () => {
    setNotificationsOpen(true);
    notifications.reload();
  };

  return (
    <div className="flex min-h-screen bg-surface-page">
      <AppSidebar
        user={user}
        collapsed={collapsed}
        mobileOpen={mobileOpen}
        onToggleCollapsed={toggleCollapsed}
        onCloseMobile={() => setMobileOpen(false)}
        onLogout={handleLogout}
      />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopHeader
          title={pageTitle ?? pageTitleFor(pathname)}
          user={user}
          notificationCount={notifications.items.length}
          onOpenMenu={() => setMobileOpen(true)}
          onOpenNotifications={openNotifications}
          onOpenSearch={() => setSearchOpen(true)}
        />
        <main className="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-8 sm:py-8">{children}</main>
      </div>
      <NotificationsPanel
        open={notificationsOpen}
        onClose={() => setNotificationsOpen(false)}
        items={notifications.items}
        loading={notifications.loading}
        failed={notifications.failed}
        onRetry={notifications.reload}
      />
      <SearchModal open={searchOpen} onClose={() => setSearchOpen(false)} />
    </div>
  );
}

// Existing pages import this name.
export const AppLayout = DashboardLayout;
