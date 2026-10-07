"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";

const NAV_LINKS = [
  { label: "Home", href: "/" },
  { label: "Courses", href: "/courses" },
  { label: "How It Works", href: "/#how-it-works" },
  { label: "AI Learning", href: "/learning-path" },
  { label: "Projects", href: "/projects" },
  { label: "Resources", href: "/#resources" },
  { label: "About", href: "/#about" },
  { label: "Contact", href: "/#contact" },
];

// Not shown in the navbar on the landing page; every other page keeps the full set.
const HIDDEN_ON_HOME = new Set(["/courses", "/learning-path", "/projects"]);

export function Navbar() {
  const pathname = usePathname();
  const { user } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const navLinks = pathname === "/" ? NAV_LINKS.filter((link) => !HIDDEN_ON_HOME.has(link.href)) : NAV_LINKS;

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur">
      <div className="hidden border-b border-ink-100 bg-ink-100/60 sm:block">
        <div className="container-lms flex items-center justify-between py-1.5 text-xs text-ink-500">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <PhoneIcon /> +1 (555) 013-9200
            </span>
            <span className="flex items-center gap-1">
              <MailIcon /> hello@agenticai-lms.com
            </span>
          </div>
          <div className="flex items-center gap-3">
            <SocialIcon label="X" />
            <SocialIcon label="LinkedIn" />
            <SocialIcon label="YouTube" />
          </div>
        </div>
      </div>

      <div className="container-lms flex items-center justify-between py-3">
        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-blue text-white font-bold">
            A
          </span>
          <span className="text-lg font-bold text-ink-900">
            Agentic<span className="text-brand-cyan">AI</span> LMS
          </span>
        </Link>

        <nav className="hidden items-center gap-1 rounded-full border border-ink-100 bg-ink-100/50 p-1 lg:flex">
          {navLinks.map((link) => {
            // In-page anchors (/#how-it-works) share a pathname with Home, so they are never "active".
            const active = link.href.includes("#") ? false : link.href === "/" ? pathname === "/" : !!pathname?.startsWith(link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "rounded-full px-4 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-brand-cyan text-white shadow-sm"
                    : "text-ink-700 hover:bg-white hover:text-brand-blue"
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>

        <div className="hidden items-center gap-4 lg:flex">
          {user ? (
            <Button href="/dashboard" size="md">
              Dashboard
            </Button>
          ) : (
            <>
              <Link href="/login" className="text-sm font-semibold text-ink-700 hover:text-brand-blue">
                Log in
              </Link>
              <Button href="/signup" size="md">
                Sign up
              </Button>
            </>
          )}
        </div>

        <button
          className="rounded-lg p-2 text-ink-700 lg:hidden"
          onClick={() => setMobileOpen((o) => !o)}
          aria-label="Toggle menu"
        >
          <MenuIcon />
        </button>
      </div>

      {mobileOpen && (
        <div className="border-t border-ink-100 bg-white lg:hidden">
          <div className="container-lms flex flex-col gap-1 py-3">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileOpen(false)}
                className="rounded-lg px-3 py-2 text-sm font-medium text-ink-700 hover:bg-ink-100"
              >
                {link.label}
              </Link>
            ))}
            <div className="mt-2 flex gap-3 border-t border-ink-100 pt-3">
              {user ? (
                <Button href="/dashboard" fullWidth>
                  Dashboard
                </Button>
              ) : (
                <>
                  <Button href="/login" variant="secondary" fullWidth>
                    Log in
                  </Button>
                  <Button href="/signup" fullWidth>
                    Sign up
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
}

function PhoneIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z" />
    </svg>
  );
}

function MailIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M4 4h16v16H4z" opacity="0" />
      <path d="M22 6l-10 7L2 6" />
      <path d="M2 6h20v12H2z" />
    </svg>
  );
}

function MenuIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M3 6h18M3 12h18M3 18h18" />
    </svg>
  );
}

function SocialIcon({ label }: { label: string }) {
  return (
    <span
      className="flex h-5 w-5 items-center justify-center rounded-full bg-white text-[9px] font-bold text-ink-500"
      aria-label={label}
    >
      {label[0]}
    </span>
  );
}
