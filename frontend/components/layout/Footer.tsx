import Link from "next/link";

const FOOTER_COLUMNS: { title: string; links: { label: string; href: string }[] }[] = [
  {
    title: "Curriculum",
    links: [
      { label: "Python", href: "/courses" },
      { label: "AI & ML", href: "/courses" },
      { label: "LLMs & RAG", href: "/courses" },
      { label: "AI Agents", href: "/courses" },
      { label: "LangChain / LangGraph", href: "/courses" },
    ],
  },
  {
    title: "Platform",
    links: [
      { label: "AI Learning Path", href: "/learning-path" },
      { label: "AI Tutor", href: "/tutor" },
      { label: "Projects", href: "/projects" },
      { label: "Skill Tracking", href: "/skills" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About", href: "/#about" },
      { label: "Contact", href: "/#contact" },
      { label: "Resources", href: "/#resources" },
    ],
  },
  {
    title: "Account",
    links: [
      { label: "Log in", href: "/login" },
      { label: "Sign up", href: "/signup" },
      { label: "Dashboard", href: "/dashboard" },
    ],
  },
];

export function Footer() {
  return (
    <footer className="border-t border-ink-100 bg-ink-900 text-ink-200">
      <div className="container-lms grid grid-cols-2 gap-8 py-12 sm:grid-cols-2 lg:grid-cols-6">
        <div className="col-span-2">
          <Link href="/" className="flex items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-blue text-white font-bold">
              A
            </span>
            <span className="text-lg font-bold text-white">
              Agentic<span className="text-brand-cyan">AI</span> LMS
            </span>
          </Link>
          <p className="mt-4 max-w-xs text-sm text-ink-400">
            A personalized learning platform for Agentic AI &mdash; Python, LLMs, RAG,
            and multi-agent systems, adapted to how you learn.
          </p>
          <div className="mt-5 flex gap-3">
            {["X", "In", "Yt", "Gh"].map((s) => (
              <span
                key={s}
                className="flex h-8 w-8 items-center justify-center rounded-full bg-white/10 text-xs font-semibold text-white hover:bg-brand-cyan"
              >
                {s}
              </span>
            ))}
          </div>
        </div>

        {FOOTER_COLUMNS.map((col) => (
          <div key={col.title}>
            <h4 className="mb-3 text-sm font-semibold text-white">{col.title}</h4>
            <ul className="space-y-2">
              {col.links.map((link) => (
                <li key={link.label}>
                  <Link href={link.href} className="text-sm text-ink-400 hover:text-brand-cyan">
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t border-white/10">
        <div className="container-lms flex flex-col items-center justify-between gap-2 py-5 text-xs text-ink-400 sm:flex-row">
          <p>&copy; {new Date().getFullYear()} Agentic AI LMS. All rights reserved.</p>
          <p>Built for learners who want to build, not just watch.</p>
        </div>
      </div>
    </footer>
  );
}
