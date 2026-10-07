"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Hero } from "@/components/layout/Hero";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useAuth } from "@/hooks/useAuth";

const CURRICULUM_CATEGORIES = [
  { title: "Python", icon: "🐍", desc: "Core language, data structures, and idiomatic Python for AI engineering." },
  { title: "AI / ML", icon: "📈", desc: "Foundational machine learning theory and applied model building." },
  { title: "LLMs", icon: "🧠", desc: "How large language models work, prompting, and fine-tuning basics." },
  { title: "Prompt Engineering", icon: "✍️", desc: "Design reliable prompts and evaluate model output systematically." },
  { title: "RAG", icon: "📚", desc: "Retrieval-augmented generation: embeddings, vector stores, pipelines." },
  { title: "AI Agents", icon: "🤖", desc: "Tool use, planning, memory, and autonomous agent architectures." },
  { title: "LangChain / LangGraph", icon: "🔗", desc: "Build production agent graphs with state and control flow." },
  { title: "Multi-Agent & Production AI", icon: "🚀", desc: "Multi-agent orchestration, evaluation, and shipping AI to production." },
];

const HOW_IT_WORKS = [
  {
    step: "01",
    title: "Diagnose",
    desc: "Take a short diagnostic assessment so we understand your current skill level across Python, ML, LLMs, and agents.",
    icon: "🩺",
  },
  {
    step: "02",
    title: "Personalize",
    desc: "Our AI builds a skill profile and generates a learning path ordered around your gaps, goals, and available time.",
    icon: "🎯",
  },
  {
    step: "03",
    title: "Learn",
    desc: "Work through lessons, examples, and practice with an AI tutor available in every lesson to unblock you instantly.",
    icon: "📖",
  },
  {
    step: "04",
    title: "Track",
    desc: "Mastery bars, streaks, and recommendations update as you go, so the path keeps adapting to your real progress.",
    icon: "📊",
  },
];

const TESTIMONIALS = [
  {
    name: "Priya S.",
    role: "Backend Engineer → AI Engineer",
    quote:
      "The diagnostic actually skipped me past the Python basics I already knew and put me straight into RAG. Felt respected as a learner, not just a user.",
  },
  {
    name: "Daniel O.",
    role: "CS Student",
    quote:
      "The AI tutor sitting right next to the lesson content is the single best feature — no more tab-switching to ask ChatGPT a random question.",
  },
  {
    name: "Marta K.",
    role: "Data Scientist",
    quote:
      "Watching my skill mastery bars climb after each project kept me honest about what I actually understood versus what I'd just skimmed.",
  },
];

export default function LandingPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && user) {
      router.replace("/dashboard");
    }
  }, [user, isLoading, router]);

  return (
    <>
      <Navbar />
      <main>
        <Hero />

        <section className="container-lms py-20">
          <div className="mx-auto max-w-2xl text-center">
            <Badge tone="cyan">Curriculum</Badge>
            <h2 className="mt-4 text-3xl font-extrabold sm:text-4xl">
              Everything you need to build with Agentic AI
            </h2>
            <p className="mt-3 text-ink-500">
              A standard curriculum spanning Python through multi-agent systems, illustrative of the depth
              covered end to end.
            </p>
          </div>

          <div className="mt-12 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {CURRICULUM_CATEGORIES.map((cat) => (
              <Card key={cat.title} className="transition-shadow hover:shadow-soft">
                <span className="text-3xl">{cat.icon}</span>
                <h3 className="mt-4 text-base font-bold text-ink-900">{cat.title}</h3>
                <p className="mt-2 text-sm text-ink-500">{cat.desc}</p>
              </Card>
            ))}
          </div>
        </section>

        <section id="how-it-works" className="bg-surface-tint-blue py-20">
          <div className="container-lms">
            <div className="mx-auto max-w-2xl text-center">
              <Badge tone="blue">How personalization works</Badge>
              <h2 className="mt-4 text-3xl font-extrabold sm:text-4xl">
                A learning path that&apos;s actually built for you
              </h2>
            </div>

            <div className="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {HOW_IT_WORKS.map((item, idx) => (
                <div key={item.step} className="relative">
                  <Card className="h-full bg-white">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-surface-tint text-2xl">
                      {item.icon}
                    </div>
                    <p className="mt-4 text-xs font-bold tracking-wide text-brand-cyan-dark">
                      STEP {item.step}
                    </p>
                    <h3 className="mt-1 text-lg font-bold text-ink-900">{item.title}</h3>
                    <p className="mt-2 text-sm text-ink-500">{item.desc}</p>
                  </Card>
                  {idx < HOW_IT_WORKS.length - 1 && (
                    <div className="absolute -right-3 top-1/2 hidden -translate-y-1/2 text-ink-300 lg:block">
                      &rarr;
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="resources" className="container-lms py-20">
          <div className="mx-auto max-w-2xl text-center">
            <Badge tone="purple">What learners say</Badge>
            <h2 className="mt-4 text-3xl font-extrabold sm:text-4xl">Loved by builders like you</h2>
            <p className="mt-3 text-sm text-ink-400">Illustrative testimonials.</p>
          </div>

          <div className="mt-12 grid grid-cols-1 gap-6 lg:grid-cols-3">
            {TESTIMONIALS.map((t) => (
              <Card key={t.name}>
                <p className="text-sm leading-relaxed text-ink-700">&ldquo;{t.quote}&rdquo;</p>
                <div className="mt-5 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-blue text-sm font-bold text-white">
                    {t.name[0]}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-ink-900">{t.name}</p>
                    <p className="text-xs text-ink-400">{t.role}</p>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </section>

        <section id="about" className="bg-ink-900 py-20 text-white">
          <div className="container-lms flex flex-col items-center gap-6 text-center">
            <h2 className="text-3xl font-extrabold sm:text-4xl">
              Ready to build your Agentic AI learning path?
            </h2>
            <p id="contact" className="max-w-xl text-ink-300">
              Start with a short diagnostic assessment and get a path personalized to your goals in minutes.
            </p>
            <Button href="/dashboard" size="lg">
              Open Dashboard
            </Button>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
