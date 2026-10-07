"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AppLayout } from "@/components/layout/AppLayout";
import { AdminNav } from "@/components/admin/AdminNav";
import { AdminPageHeader } from "@/components/admin/AdminPageHeader";
import { DataTable, type Column } from "@/components/admin/DataTable";
import { LoadingState } from "@/components/ui/LoadingState";
import { ErrorState } from "@/components/ui/ErrorState";
import { Badge } from "@/components/ui/Badge";
import { api, ApiError } from "@/lib/api";
import type { UserOut } from "@/types";

function AdminUsersContent() {
  const [users, setUsers] = useState<UserOut[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await api.admin.users.list();
      setUsers(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Unable to load users.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const columns: Column<UserOut>[] = [
    { header: "Name", render: (u) => <span className="font-semibold text-ink-900">{u.full_name}</span> },
    { header: "Email", render: (u) => <span className="text-ink-500">{u.email}</span> },
    { header: "Role", render: (u) => <Badge tone={u.role === "admin" ? "purple" : "blue"}>{u.role}</Badge> },
    {
      header: "Status",
      render: (u) => <Badge tone={u.is_active ? "green" : "gray"}>{u.is_active ? "Active" : "Inactive"}</Badge>,
    },
  ];

  return (
    <div>
      <AdminPageHeader title="Users" description="All registered users on the platform." />
      <AdminNav />

      <div className="mt-6">
        {loading && <LoadingState label="Loading users..." />}
        {!loading && error && <ErrorState message={error} onRetry={load} />}
        {!loading && !error && users && (
          <DataTable columns={columns} rows={users} keyField={(u) => u.id} emptyTitle="No users yet" />
        )}
      </div>
    </div>
  );
}

export default function AdminUsersPage() {
  return (
    <ProtectedRoute adminOnly>
      <AppLayout pageTitle="Admin · Users">
        <AdminUsersContent />
      </AppLayout>
    </ProtectedRoute>
  );
}
