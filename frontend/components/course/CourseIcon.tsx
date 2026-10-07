import type { ReactNode } from "react";

/**
 * Renders a course's `icon` field as a glyph instead of raw text.
 *
 * The seed content stores icon *names* ("python", "brain", "message-circle" - see content/seed/courses/*.py) while
 * the admin form also lets someone type an emoji. Recognised names render as inline SVG (dependency-free, same
 * style as components/layout/nav.tsx); anything else (an emoji, an unknown name) is shown as typed; an empty value
 * falls back to a generic book glyph.
 */

function Glyph({ children }: { children: ReactNode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-[55%] w-[55%]"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

const FALLBACK = (
  <Glyph>
    <path d="M12 6.5C10 5.2 7.5 4.5 5 4.5v13c2.5 0 5 .7 7 2 2-1.3 4.5-2 7-2v-13c-2.5 0-5 .7-7 2Z" />
    <path d="M12 6.5v13" />
  </Glyph>
);

const GLYPHS: Record<string, ReactNode> = {
  // Python for AI - a generic code glyph (not the trademarked logo)
  python: (
    <Glyph>
      <path d="m9 8-5 4 5 4" />
      <path d="m15 8 5 4-5 4" />
    </Glyph>
  ),
  // AI & Machine Learning Foundations
  brain: (
    <Glyph>
      <circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none" />
      <ellipse cx="12" cy="12" rx="9" ry="3.6" />
      <ellipse cx="12" cy="12" rx="9" ry="3.6" transform="rotate(60 12 12)" />
      <ellipse cx="12" cy="12" rx="9" ry="3.6" transform="rotate(120 12 12)" />
    </Glyph>
  ),
  // LLM Fundamentals
  "message-circle": (
    <Glyph>
      <path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5 8.4 8.4 0 0 1-4-1L3 21l1.9-5.7a8.5 8.5 0 1 1 16.1-3.8Z" />
    </Glyph>
  ),
  // Prompt Engineering
  terminal: (
    <Glyph>
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <path d="m7 9 3 3-3 3M13 15h4" />
    </Glyph>
  ),
  // Embeddings & Vector Databases
  vector: (
    <Glyph>
      <ellipse cx="12" cy="6" rx="7" ry="3" />
      <path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6" />
      <path d="M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6" />
    </Glyph>
  ),
  // Retrieval Augmented Generation
  search: (
    <Glyph>
      <circle cx="10.5" cy="10.5" r="6.5" />
      <path d="m20 20-4.3-4.3" />
    </Glyph>
  ),
  // AI Agents Fundamentals
  bot: (
    <Glyph>
      <rect x="5" y="9" width="14" height="10" rx="3" />
      <path d="M12 9V5M9 4h6" />
      <circle cx="9.5" cy="14" r="1" fill="currentColor" stroke="none" />
      <circle cx="14.5" cy="14" r="1" fill="currentColor" stroke="none" />
      <path d="M9 17.5h6" />
    </Glyph>
  ),
  // Agent Architecture
  cpu: (
    <Glyph>
      <rect x="6" y="6" width="12" height="12" rx="2" />
      <path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4" />
    </Glyph>
  ),
  // LangChain
  link: (
    <Glyph>
      <path d="M9 15 15 9" />
      <path d="M11 6.5 13 4.5a3.5 3.5 0 0 1 5 5l-2 2" />
      <path d="M13 17.5 11 19.5a3.5 3.5 0 0 1-5-5l2-2" />
    </Glyph>
  ),
  // LangGraph
  workflow: (
    <Glyph>
      <rect x="3" y="4" width="6" height="4" rx="1" />
      <rect x="15" y="4" width="6" height="4" rx="1" />
      <rect x="9" y="16" width="6" height="4" rx="1" />
      <path d="M6 8v4a2 2 0 0 0 2 2h1M18 8v4a2 2 0 0 1-2 2h-1M12 12v4" />
    </Glyph>
  ),
  // Multi-Agent Systems
  network: (
    <Glyph>
      <circle cx="5" cy="6" r="2.3" />
      <circle cx="19" cy="6" r="2.3" />
      <circle cx="12" cy="18" r="2.3" />
      <path d="M6.8 7.6 10.5 16M17.2 7.6 13.5 16M7.3 6h9.4" />
    </Glyph>
  ),
  // Evaluation & Safety
  shield: (
    <Glyph>
      <path d="M12 3 4 6v6c0 4.5 3.4 8.3 8 9 4.6-.7 8-4.5 8-9V6z" />
    </Glyph>
  ),
  // Production AI Agents
  server: (
    <Glyph>
      <rect x="3" y="4" width="18" height="7" rx="1.5" />
      <rect x="3" y="13" width="18" height="7" rx="1.5" />
      <path d="M7 7.5h.01M7 16.5h.01" />
    </Glyph>
  ),
};

export function CourseIcon({ icon, className }: { icon: string | null | undefined; className?: string }) {
  const key = (icon ?? "").trim().toLowerCase();
  if (!key) return <span className={className}>{FALLBACK}</span>;
  const glyph = GLYPHS[key];
  if (glyph) return <span className={className}>{glyph}</span>;
  return <span className={className}>{icon}</span>;
}
