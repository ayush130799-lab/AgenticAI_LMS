"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const LINKS = [
  { label: "Overview", href: "/admin" },
  { label: "Courses", href: "/admin/courses" },
  { label: "Lessons", href: "/admin/lessons" },
  { label: "Skills", href: "/admin/skills" },
  { label: "Assessments", href: "/admin/assessments" },
  { label: "Projects", href: "/admin/projects" },
  { label: "Users", href: "/admin/users" },
];

export function AdminNav() {
  const pathname = usePathname();
  return (
    <nav className="flex gap-2 overflow-x-auto border-b border-ink-100 pb-3">
      {LINKS.map((link) => {
        const active = link.href === "/admin" ? pathname === "/admin" : pathname?.startsWith(link.href);
        return (
          <Link
            key={link.href}
            href={link.href}
            className={cn(
              "shrink-0 rounded-full px-4 py-1.5 text-sm font-medium transition-colors",
              active ? "bg-brand-blue text-white" : "bg-ink-100 text-ink-600 hover:bg-ink-200"
            )}
          >
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}
