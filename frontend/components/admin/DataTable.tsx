import type { ReactNode } from "react";
import { EmptyState } from "@/components/ui/EmptyState";

export interface Column<T> {
  header: string;
  render: (row: T) => ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  rows: T[];
  keyField: (row: T) => string;
  emptyTitle?: string;
  emptyDescription?: string;
}

export function DataTable<T>({ columns, rows, keyField, emptyTitle, emptyDescription }: DataTableProps<T>) {
  if (rows.length === 0) {
    return (
      <EmptyState
        title={emptyTitle ?? "Nothing here yet"}
        description={emptyDescription ?? "Create the first record to get started."}
      />
    );
  }

  return (
    <div className="overflow-x-auto rounded-2xl border border-ink-200">
      <table className="min-w-full divide-y divide-ink-100 text-sm">
        <thead className="bg-ink-100/60">
          <tr>
            {columns.map((col) => (
              <th
                key={col.header}
                className="whitespace-nowrap px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-ink-500"
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-ink-100 bg-white">
          {rows.map((row) => (
            <tr key={keyField(row)} className="hover:bg-ink-100/40">
              {columns.map((col) => (
                <td key={col.header} className={col.className ?? "whitespace-nowrap px-4 py-3 text-ink-700"}>
                  {col.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
