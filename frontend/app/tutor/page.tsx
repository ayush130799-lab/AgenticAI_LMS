"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { TutorChat } from "@/components/tutor/TutorChat";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import type { ConversationSummaryOut } from "@/types";

export default function TutorPage() {
  const [conversations, setConversations] = useState<ConversationSummaryOut[]>([]);
  const [activeId, setActiveId] = useState<string | undefined>(undefined);
  const [loadingList, setLoadingList] = useState(true);

  async function loadHistory() {
    try {
      const data = await api.tutor.conversations();
      setConversations(data);
    } catch {
      // Ignore
    } finally {
      setLoadingList(false);
    }
  }

  useEffect(() => {
    loadHistory();
  }, []);

  function handleNewChat() {
    setActiveId(undefined);
  }

  function handleConversationCreated(id: string, title: string) {
    setActiveId(id);
    setConversations((prev) => [
      { id, title, lesson_id: null, updated_at: new Date().toISOString() },
      ...prev,
    ]);
  }

  return (
    <ProtectedRoute>
      <AppLayout pageTitle="AI Tutor">
        <div className="space-y-6">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-xs font-bold uppercase tracking-wider text-blue-600 mb-1">
                AI MENTOR & ASSISTANT
              </p>
              <h1 className="text-2xl font-extrabold text-slate-900">AI Tutor</h1>
              <p className="mt-1 text-sm text-slate-500">
                Ask about anything in the Agentic AI curriculum — concepts, code debugging, RAG pipelines, or what to study next.
              </p>
            </div>
            <Button size="sm" onClick={handleNewChat} variant="primary">
              + New Chat
            </Button>
          </div>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-4 h-[74vh]">
            {/* Conversations Sidebar */}
            <div className="hidden lg:flex flex-col rounded-2xl border border-slate-200/90 bg-white p-3 shadow-xs overflow-hidden">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Chat History
                </span>
                <span className="text-[11px] font-semibold text-slate-400">
                  {conversations.length}
                </span>
              </div>
              <div className="mt-2 flex-1 space-y-1 overflow-y-auto">
                {loadingList && (
                  <p className="p-3 text-xs text-slate-400">Loading history...</p>
                )}
                {!loadingList && conversations.length === 0 && (
                  <p className="p-3 text-xs text-slate-400">No previous chats yet.</p>
                )}
                {conversations.map((c) => {
                  const isCurrent = activeId === c.id;
                  return (
                    <button
                      key={c.id}
                      onClick={() => setActiveId(c.id)}
                      className={`w-full text-left rounded-xl p-2.5 text-xs font-medium transition line-clamp-2 ${
                        isCurrent
                          ? "bg-blue-50 text-blue-900 font-bold border border-blue-200"
                          : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                      }`}
                    >
                      💬 {c.title}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Chat Window */}
            <div className="lg:col-span-3 h-full overflow-hidden rounded-2xl border border-slate-200/90 bg-white shadow-xs">
              <TutorChat
                key={activeId || "new"}
                activeConversationId={activeId}
                onConversationCreated={handleConversationCreated}
                className="h-full"
                title="Agentic AI Tutor"
              />
            </div>
          </div>
        </div>
      </AppLayout>
    </ProtectedRoute>
  );
}
