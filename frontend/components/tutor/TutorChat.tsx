"use client";

import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { cn } from "@/lib/utils";
import { api, ApiError } from "@/lib/api";
import type { TutorMessage } from "@/types";

interface TutorChatProps {
  lessonId?: string;
  className?: string;
  title?: string;
  emptyHint?: string;
  activeConversationId?: string;
  onConversationCreated?: (id: string, title: string) => void;
}

export function TutorChat({
  lessonId,
  className,
  title = "AI Tutor",
  emptyHint,
  activeConversationId,
  onConversationCreated,
}: TutorChatProps) {
  const [messages, setMessages] = useState<TutorMessage[]>([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string | undefined>(activeConversationId);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Load existing messages when activeConversationId changes
  useEffect(() => {
    setConversationId(activeConversationId);
    if (!activeConversationId) {
      setMessages([]);
      return;
    }
    let ignore = false;
    api.tutor.conversation(activeConversationId).then((data) => {
      if (ignore) return;
      const msgs = (data.messages as TutorMessage[]) || [];
      setMessages(msgs);
    }).catch(() => {
      // Ignore or let user start typing
    });
    return () => {
      ignore = true;
    };
  }, [activeConversationId]);

  function scrollToBottom() {
    requestAnimationFrame(() => {
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    });
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || sending) return;

    const userMessage: TutorMessage = { role: "user", content: trimmed };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setSending(true);
    setError(null);
    scrollToBottom();

    try {
      const isNew = !conversationId;
      const res = await api.tutor.chat({
        message: trimmed,
        conversation_id: conversationId,
        lesson_id: lessonId,
      });
      setConversationId(res.conversation_id);
      if (isNew && onConversationCreated) {
        onConversationCreated(res.conversation_id, trimmed.slice(0, 60));
      }
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.reply, citations: res.citations },
      ]);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "The tutor is unavailable right now.");
    } finally {
      setSending(false);
      scrollToBottom();
    }
  }

  return (
    <div className={cn("flex h-full flex-col", className)}>
      <div className="flex items-center gap-2 border-b border-ink-100 px-4 py-3">
        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-blue text-sm text-white">
          🤖
        </span>
        <div>
          <p className="text-sm font-bold text-ink-900">{title}</p>
          <p className="text-[11px] text-ink-400">
            {lessonId ? "Scoped to this lesson" : "Ask about anything in the curriculum"}
          </p>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
        {messages.length === 0 && (
          <p className="rounded-xl bg-ink-100/60 p-3 text-sm text-ink-500">
            {emptyHint ?? "Ask me anything — I can explain concepts, debug your code, or suggest what to study next."}
          </p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={cn(
              "rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
              m.role === "user"
                ? "ml-auto max-w-[85%] bg-brand-blue text-white"
                : "max-w-[95%] overflow-x-auto bg-ink-100 text-ink-800"
            )}
          >
            {m.role === "user" ? (
              m.content
            ) : (
              <div className="prose-lesson">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
              </div>
            )}
            {m.role !== "user" && m.citations && m.citations.length > 0 && (
              <div className="mt-3 border-t border-ink-200 pt-2 text-xs text-ink-500">
                <span className="font-semibold">Sources: </span>
                {m.citations.slice(0, 3).map((c, idx) => (
                  <span key={`${c.lesson_id}-${idx}`}>
                    {idx > 0 && " · "}
                    {c.lesson_id ? (
                      <Link href={`/lessons/${c.lesson_id}`} className="text-brand-blue hover:underline">
                        {c.title}
                      </Link>
                    ) : (
                      c.title
                    )}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
        {sending && (
          <div className="max-w-[70%] rounded-2xl bg-ink-100 px-4 py-2.5 text-sm text-ink-400">
            Thinking...
          </div>
        )}
        {error && <p className="text-xs text-red-600">{error}</p>}
      </div>

      <form onSubmit={handleSubmit} className="flex items-center gap-2 border-t border-ink-100 p-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the AI tutor..."
          className="flex-1 rounded-full border border-ink-200 px-4 py-2 text-sm focus:border-brand-blue focus:outline-none focus:ring-2 focus:ring-brand-blue/20"
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-blue text-white disabled:bg-ink-200"
          aria-label="Send"
        >
          ➤
        </button>
      </form>
    </div>
  );
}
