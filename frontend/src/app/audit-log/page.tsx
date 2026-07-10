"use client";

import { useEffect, useState } from "react";
import { History } from "lucide-react";
import { api, type AuditLogEntry } from "@/lib/api";

const ACTION_STYLE: Record<string, { label: string; className: string }> = {
  created: { label: "Created", className: "bg-[var(--success)]/15 text-[var(--success)]" },
  renewed: { label: "Renewed", className: "bg-[var(--forest-700)]/12 text-[var(--forest-700)]" },
  cancelled: { label: "Cancelled", className: "bg-[var(--danger)]/15 text-[var(--danger-ink)]" },
  reminder_sent: { label: "Reminder", className: "bg-[var(--amber-500)]/15 text-[var(--amber-600)]" },
  edited: { label: "Edited", className: "bg-black/5 text-[var(--cream-foreground)]/70" },
};

function styleFor(action: string) {
  return (
    ACTION_STYLE[action] ?? {
      label: action.replace(/_/g, " "),
      className: "bg-black/5 text-[var(--cream-foreground)]/70",
    }
  );
}

const fmt = (iso: string) =>
  new Date(iso).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });

export default function AuditLogPage() {
  const [entries, setEntries] = useState<AuditLogEntry[] | null>(null);

  useEffect(() => {
    api
      .get<AuditLogEntry[]>("/api/audit-log?limit=200")
      .then(setEntries)
      .catch(() => setEntries([]));
  }, []);

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Activity Log</h1>
        <p className="text-sm text-muted-foreground">
          Every pass issued, renewed, cancelled, and reminder sent — tracked automatically.
        </p>
      </div>

      <div className="card-paper rounded-2xl p-2">
        {entries === null ? (
          <p className="p-4 text-sm text-[var(--cream-foreground)]/60">Loading…</p>
        ) : entries.length === 0 ? (
          <div className="flex flex-col items-center gap-2 p-10 text-center">
            <History className="h-8 w-8 text-[var(--cream-foreground)]/40" />
            <p className="text-sm text-[var(--cream-foreground)]/70">No activity recorded yet.</p>
          </div>
        ) : (
          <ul className="divide-y divide-black/5">
            {entries.map((e) => {
              const s = styleFor(e.action);
              return (
                <li key={e.id} className="flex items-start gap-3 p-3">
                  <span
                    className={`mt-0.5 shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold capitalize ${s.className}`}
                  >
                    {s.label}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm text-[var(--cream-foreground)]">{e.summary}</p>
                    <p className="mt-0.5 text-xs text-[var(--cream-foreground)]/55">
                      {e.entity_type}
                      {e.employee_name ? ` · ${e.employee_name}` : ""} · {fmt(e.created_at)}
                    </p>
                  </div>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
