import type { ReactNode } from "react";

export interface NavItem {
  label: string;
  href: string;
  icon: ReactNode;
  adminOnly?: boolean;
}

export interface NavGroup {
  title: string;
  items: NavItem[];
}

function Icon({ children }: { children: ReactNode }) {
  return (
    <svg
      className="h-[18px] w-[18px] shrink-0"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

export const icons = {
  dashboard: (
    <Icon>
      <rect x="3" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="14" width="7" height="7" rx="1.5" />
      <rect x="3" y="14" width="7" height="7" rx="1.5" />
    </Icon>
  ),
  courses: (
    <Icon>
      <path d="M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2z" />
      <path d="M22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7z" />
    </Icon>
  ),
  path: (
    <Icon>
      <circle cx="6" cy="19" r="2" />
      <circle cx="18" cy="5" r="2" />
      <path d="M8 19h6a4 4 0 0 0 0-8h-4a4 4 0 0 1 0-8h6" />
    </Icon>
  ),
  skills: (
    <Icon>
      <path d="M4 20V10M10 20V4M16 20v-8M22 20H2" />
    </Icon>
  ),
  projects: (
    <Icon>
      <path d="m12 3 9 5-9 5-9-5z" />
      <path d="m3 13 9 5 9-5" />
    </Icon>
  ),
  assessments: (
    <Icon>
      <path d="M9 11l3 3 8-8" />
      <path d="M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h9" />
    </Icon>
  ),
  tutor: (
    <Icon>
      <rect x="4" y="8" width="16" height="12" rx="3" />
      <path d="M12 8V4M9 13v1M15 13v1M2 14v2M22 14v2" />
    </Icon>
  ),
  profile: (
    <Icon>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21a8 8 0 0 1 16 0" />
    </Icon>
  ),
  admin: (
    <Icon>
      <path d="M12 3 4 6v6c0 4.5 3.4 8.3 8 9 4.6-.7 8-4.5 8-9V6z" />
      <path d="m9 12 2 2 4-4" />
    </Icon>
  ),
  bell: (
    <Icon>
      <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" />
      <path d="M13.7 21a2 2 0 0 1-3.4 0" />
    </Icon>
  ),
  menu: (
    <Icon>
      <path d="M3 6h18M3 12h18M3 18h18" />
    </Icon>
  ),
  logout: (
    <Icon>
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <path d="m16 17 5-5-5-5M21 12H9" />
    </Icon>
  ),
  chevrons: (
    <Icon>
      <path d="m11 17-5-5 5-5M18 17l-5-5 5-5" />
    </Icon>
  ),
  close: (
    <Icon>
      <path d="M18 6 6 18M6 6l12 12" />
    </Icon>
  ),
  check: (
    <Icon>
      <path d="m5 12 5 5 9-10" />
    </Icon>
  ),
  arrow: (
    <Icon>
      <path d="M5 12h14M13 6l6 6-6 6" />
    </Icon>
  ),
  flame: (
    <Icon>
      <path d="M12 3c1 4 5 5 5 10a5 5 0 0 1-10 0c0-2 1-3 2-4 0 2 1 3 2 3 0-3-1-5 1-9z" />
    </Icon>
  ),
  bookmark: (
    <Icon>
      <path d="m19 21-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
    </Icon>
  ),
};

// Only routes that exist in the app. Add an item here when its page ships.
export const NAV_GROUPS: NavGroup[] = [
  {
    title: "Learning",
    items: [
      { label: "Dashboard", href: "/dashboard", icon: icons.dashboard },
      { label: "Courses", href: "/courses", icon: icons.courses },
      { label: "Learning Path", href: "/learning-path", icon: icons.path },
      { label: "Skills", href: "/skills", icon: icons.skills },
      { label: "Bookmarks", href: "/bookmarks", icon: icons.bookmark },
    ],
  },
  {
    title: "Practice & Build",
    items: [
      { label: "Projects", href: "/projects", icon: icons.projects },
      { label: "Assessments", href: "/assessments", icon: icons.assessments },
    ],
  },
  {
    title: "AI Learning",
    items: [{ label: "AI Tutor", href: "/tutor", icon: icons.tutor }],
  },
  {
    title: "Account",
    items: [
      { label: "Profile", href: "/profile", icon: icons.profile },
      { label: "Admin Console", href: "/admin", icon: icons.admin, adminOnly: true },
    ],
  },
];

export function isActive(pathname: string | null, href: string): boolean {
  if (!pathname) return false;
  if (href === "/dashboard") return pathname === "/dashboard";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function pageTitleFor(pathname: string | null): string {
  for (const group of NAV_GROUPS) {
    for (const item of group.items) {
      if (isActive(pathname, item.href)) return item.label;
    }
  }
  return "Agentic AI LMS";
}
