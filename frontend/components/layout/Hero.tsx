import { Button } from "@/components/ui/Button";

const FEATURE_CHIPS = [
  { label: "AI Personalized Learning", icon: "🧠", position: "-top-5 -left-5" },
  { label: "AI Tutor", icon: "💬", position: "-top-5 -right-5" },
  { label: "Skill Tracking", icon: "📊", position: "-bottom-6 -left-6" },
  { label: "Agent Projects", icon: "🤖", position: "-bottom-6 -right-6" },
];

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-b from-surface-tint-blue to-white pb-20 pt-14 sm:pt-20">
      <div className="container-lms grid items-center gap-14 lg:grid-cols-2">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full bg-surface-tint px-4 py-1.5 text-sm font-semibold text-brand-cyan-dark">
            <span className="h-1.5 w-1.5 rounded-full bg-brand-cyan" />
            Trusted by 10,000+ learners building with AI agents
          </div>

          <h1 className="mt-6 text-4xl font-extrabold leading-tight tracking-tight text-ink-900 sm:text-5xl lg:text-6xl">
            Master <span className="text-brand-cyan">Agentic AI</span>. Learn{" "}
            <span className="text-brand-cyan">Smarter</span>. Build Better.
          </h1>

          <p className="mt-4 text-lg font-bold text-ink-500">
            Students <span className="mx-1 text-ink-300">|</span> Builders{" "}
            <span className="mx-1 text-ink-300">|</span> Engineers
          </p>

          <p className="mt-5 max-w-xl text-base leading-relaxed text-ink-500">
            A curriculum that takes you from <span className="font-semibold text-brand-cyan-dark">Python</span> and
            core ML through <span className="font-semibold text-brand-purple">LLMs</span> and{" "}
            <span className="font-semibold text-brand-magenta">RAG</span> to production-grade AI Agents with
            LangGraph &mdash; personalized to your pace with a diagnostic assessment, an AI-recommended learning
            path, and a tutor that actually knows where you are.
          </p>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Button href="/dashboard" size="lg">
              Start Learning
              <ArrowIcon />
            </Button>
            <Button href="/courses" size="lg" variant="secondary">
              Explore Curriculum
            </Button>
          </div>
        </div>

        <div className="relative mx-auto w-full max-w-md lg:max-w-none">
          <div className="relative aspect-[4/5] w-full overflow-hidden rounded-3xl bg-gradient-to-br from-brand-blue via-brand-cyan-dark to-brand-purple shadow-soft">
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 p-8 text-center text-white">
              <span className="text-6xl">🧭</span>
              <p className="text-lg font-semibold">
                Diagnose &rarr; Personalize &rarr; Learn &rarr; Track
              </p>
              <p className="text-sm text-white/80">
                Your Agentic AI learning path, generated for you.
              </p>
            </div>
          </div>

          {FEATURE_CHIPS.map((chip) => (
            <div
              key={chip.label}
              className={`absolute ${chip.position} hidden items-center gap-2 rounded-2xl bg-white px-4 py-2.5 shadow-soft sm:flex`}
            >
              <span className="text-lg">{chip.icon}</span>
              <span className="text-xs font-semibold text-ink-900">{chip.label}</span>
            </div>
          ))}

          <div className="absolute -bottom-8 left-1/2 hidden w-64 -translate-x-1/2 items-center gap-3 rounded-2xl bg-white p-3 shadow-soft sm:flex lg:left-4 lg:translate-x-0">
            <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand-blue text-sm font-bold text-white">
              PS
              <span className="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-white bg-emerald-500" />
            </div>
            <div className="text-left">
              <p className="text-xs font-semibold text-ink-900">Priya S.</p>
              <p className="text-[11px] text-ink-400">
                enrolled in RAG Knowledge Assistant &middot; 2h ago
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function ArrowIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}
