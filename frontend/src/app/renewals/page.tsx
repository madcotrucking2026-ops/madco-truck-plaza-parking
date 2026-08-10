"use client";

import { useEffect, useState } from "react";
import { AlarmClock, CheckCircle2, RefreshCcw } from "lucide-react";
import { api, type PassListItem } from "@/lib/api";
import { StatusBadge } from "@/components/passes/status-badge";
import { RenewDialog } from "@/components/passes/renew-dialog";
import { Button } from "@/components/ui/button";
import { LoadError } from "@/components/common/load-error";
import { SkeletonRows } from "@/components/common/skeleton-rows";
import { addDaysISO, todayISO } from "@/lib/pricing";

/** The front-desk renewal screen — the cashier's version of the manager
 *  dashboard's "Needs attention" card: passes expiring today & tomorrow, each
 *  with a Renew button that opens the same dialog the manager uses. */
export default function RenewalsPage() {
  const [passes, setPasses] = useState<PassListItem[] | null>(null);
  const [err, setErr] = useState(false);
  const [renewing, setRenewing] = useState<PassListItem | null>(null);

  function load() {
    setErr(false);
    setPasses(null);
    api.get<PassListItem[]>("/api/passes/expiring").then(setPasses).catch(() => setErr(true));
  }
  useEffect(load, []);

  const today = todayISO();
  const tomorrow = addDaysISO(today, 1);

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Renewals</h1>
        <p className="text-sm text-muted-foreground">
          Passes expiring today &amp; tomorrow — renew them right here.
        </p>
      </div>

      <section className="card-paper rounded-2xl p-6">
        <div className="mb-4 flex items-center gap-3">
          <AlarmClock className="h-5 w-5 shrink-0 text-[var(--danger)]" />
          <h2 className="text-lg font-semibold text-[var(--cream-foreground)]">Expiring soon</h2>
          {passes && passes.length > 0 && (
            <span className="ml-auto rounded-full bg-[var(--danger-strong)] px-2.5 py-1 text-sm font-bold tabular-nums text-white">
              {passes.length}
            </span>
          )}
        </div>

        {err ? (
          <LoadError what="expiring passes" onRetry={load} />
        ) : passes === null ? (
          <SkeletonRows n={4} />
        ) : passes.length === 0 ? (
          <div className="flex flex-col items-center gap-2 py-10 text-center">
            <CheckCircle2 className="h-8 w-8 text-[var(--success)]" />
            <p className="text-sm text-[var(--cream-foreground)]/70">
              All caught up — nothing expiring today or tomorrow.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {passes.map((p) => (
              <div
                key={p.id}
                className="flex items-center gap-3 rounded-xl border border-black/5 bg-black/[0.015] p-3"
              >
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium text-[var(--cream-foreground)]">{p.company_name ?? "—"}</p>
                  <p className="truncate font-mono text-xs text-[var(--cream-foreground)]/60">
                    {p.truck_number ?? p.trailer_number ?? p.license_plate ?? "—"} · {p.pass_type}
                  </p>
                </div>
                <div className="shrink-0 text-right">
                  <StatusBadge status={p.status} />
                  <p className="mt-0.5 text-xs text-[var(--cream-foreground)]/60">
                    {p.expiration_date === today
                      ? "expires today"
                      : p.expiration_date === tomorrow
                        ? "expires tomorrow"
                        : p.expiration_date}
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="min-h-11 shrink-0"
                  onClick={() => setRenewing(p)}
                >
                  <RefreshCcw className="h-3.5 w-3.5" />
                  Renew
                </Button>
              </div>
            ))}
          </div>
        )}
      </section>

      {renewing && (
        <RenewDialog pass={renewing} onOpenChange={(o) => !o && setRenewing(null)} onRenewed={load} />
      )}
    </div>
  );
}
