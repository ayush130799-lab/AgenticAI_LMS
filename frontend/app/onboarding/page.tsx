"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { Navbar } from "@/components/layout/Navbar";
import { Card } from "@/components/ui/Card";
import { Select } from "@/components/ui/Select";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { ProgressBar } from "@/components/ui/ProgressBar";
import { api, ApiError } from "@/lib/api";
import type { OnboardingRequest } from "@/types";

const EXPERIENCE_OPTIONS = [
  { value: "none", label: "No experience" },
  { value: "beginner", label: "Beginner" },
  { value: "intermediate", label: "Intermediate" },
  { value: "advanced", label: "Advanced" },
];

const PACE_OPTIONS = [
  { value: "relaxed", label: "Relaxed (2-4 hrs/week)" },
  { value: "standard", label: "Standard (5-8 hrs/week)" },
  { value: "intensive", label: "Intensive (9+ hrs/week)" },
];

const EXPERIENCE_FIELDS: { key: keyof OnboardingRequest; label: string }[] = [
  { key: "programming_experience", label: "General programming" },
  { key: "python_experience", label: "Python" },
  { key: "ai_ml_experience", label: "AI / Machine Learning" },
  { key: "llm_experience", label: "Large Language Models" },
  { key: "rag_experience", label: "Retrieval-Augmented Generation (RAG)" },
  { key: "agent_experience", label: "AI Agents" },
  { key: "langchain_experience", label: "LangChain" },
  { key: "langgraph_experience", label: "LangGraph" },
];

const TOTAL_STEPS = 3;

function OnboardingFlow() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [completed, setCompleted] = useState(false);
  const [startingDiagnostic, setStartingDiagnostic] = useState(false);

  const [form, setForm] = useState<OnboardingRequest>({
    programming_experience: "",
    python_experience: "",
    ai_ml_experience: "",
    llm_experience: "",
    rag_experience: "",
    agent_experience: "",
    langchain_experience: "",
    langgraph_experience: "",
    career_goal: "",
    target_role: "",
    available_hours_per_week: 5,
    preferred_pace: "",
  });

  function update<K extends keyof OnboardingRequest>(key: K, value: OnboardingRequest[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function validateStep(current: number): boolean {
    if (current === 1) {
      return EXPERIENCE_FIELDS.every((f) => Boolean(form[f.key]));
    }
    if (current === 2) {
      return Boolean(form.career_goal.trim()) && Boolean(form.target_role.trim()) && Boolean(form.preferred_pace);
    }
    return true;
  }

  function handleNext() {
    setError(null);
    if (!validateStep(step)) {
      setError("Please fill in every field before continuing.");
      return;
    }
    setStep((s) => Math.min(TOTAL_STEPS, s + 1));
  }

  function handleBack() {
    setError(null);
    setStep((s) => Math.max(1, s - 1));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validateStep(2)) {
      setError("Please fill in every field before continuing.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await api.students.onboarding(form);
      setCompleted(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to save onboarding details.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleStartDiagnostic() {
    setStartingDiagnostic(true);
    setError(null);
    try {
      const diagnostic = await api.assessments.diagnostic();
      router.push(`/assessments/${diagnostic.id}?diagnostic=1`);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to start the diagnostic assessment.");
      setStartingDiagnostic(false);
    }
  }

  if (completed) {
    return (
      <Card className="mx-auto max-w-xl text-center">
        <span className="text-4xl">🩺</span>
        <h1 className="mt-4 text-2xl font-bold text-ink-900">Let&apos;s find your starting point</h1>
        <p className="mt-2 text-sm text-ink-500">
          Take a short diagnostic assessment across Python, ML, LLMs, RAG, and agents. It takes about 15
          minutes and builds your initial skill profile so we can generate your personalized learning path.
        </p>
        {error && <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}
        <Button className="mt-6" size="lg" onClick={handleStartDiagnostic} disabled={startingDiagnostic}>
          {startingDiagnostic ? "Starting..." : "Start diagnostic assessment"}
        </Button>
      </Card>
    );
  }

  return (
    <Card className="mx-auto max-w-2xl">
      <ProgressBar value={step} max={TOTAL_STEPS} showValue className="mb-6" />
      <h1 className="text-2xl font-bold text-ink-900">Tell us about your experience</h1>
      <p className="mt-1 text-sm text-ink-500">
        Step {step} of {TOTAL_STEPS} &mdash; this helps us personalize your curriculum from day one.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-5">
        {step === 1 && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {EXPERIENCE_FIELDS.map((f) => (
              <Select
                key={f.key}
                label={f.label}
                options={EXPERIENCE_OPTIONS}
                placeholder="Select your level"
                value={form[f.key] as string}
                onChange={(e) => update(f.key, e.target.value as never)}
              />
            ))}
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <Input
              label="Career goal"
              placeholder="e.g. Transition into an AI engineering role"
              value={form.career_goal}
              onChange={(e) => update("career_goal", e.target.value)}
            />
            <Input
              label="Target role"
              placeholder="e.g. AI Agent Engineer"
              value={form.target_role}
              onChange={(e) => update("target_role", e.target.value)}
            />
            <Input
              label="Available hours per week"
              type="number"
              min={1}
              max={80}
              value={form.available_hours_per_week}
              onChange={(e) => update("available_hours_per_week", Number(e.target.value))}
            />
            <Select
              label="Preferred pace"
              options={PACE_OPTIONS}
              placeholder="Select a pace"
              value={form.preferred_pace}
              onChange={(e) => update("preferred_pace", e.target.value)}
            />
          </div>
        )}

        {step === 3 && (
          <div className="space-y-3 rounded-xl bg-ink-100/50 p-4 text-sm text-ink-700">
            <p className="font-semibold text-ink-900">Review your details</p>
            {EXPERIENCE_FIELDS.map((f) => (
              <div key={f.key} className="flex justify-between">
                <span className="text-ink-500">{f.label}</span>
                <span className="font-medium">{form[f.key] || "—"}</span>
              </div>
            ))}
            <div className="flex justify-between">
              <span className="text-ink-500">Career goal</span>
              <span className="font-medium">{form.career_goal || "—"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-ink-500">Target role</span>
              <span className="font-medium">{form.target_role || "—"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-ink-500">Hours / week</span>
              <span className="font-medium">{form.available_hours_per_week}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-ink-500">Pace</span>
              <span className="font-medium">{form.preferred_pace || "—"}</span>
            </div>
          </div>
        )}

        {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>}

        <div className="flex justify-between pt-2">
          <Button type="button" variant="secondary" onClick={handleBack} disabled={step === 1}>
            Back
          </Button>
          {step < TOTAL_STEPS ? (
            <Button type="button" onClick={handleNext}>
              Continue
            </Button>
          ) : (
            <Button type="submit" disabled={submitting}>
              {submitting ? "Saving..." : "Finish onboarding"}
            </Button>
          )}
        </div>
      </form>
    </Card>
  );
}

export default function OnboardingPage() {
  return (
    <ProtectedRoute>
      <Navbar />
      <main className="container-lms py-12">
        <OnboardingFlow />
      </main>
    </ProtectedRoute>
  );
}
