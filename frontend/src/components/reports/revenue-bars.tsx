"use client";

import { useEffect, useState } from "react";
import { DollarSign } from "lucide-react";
import { api, type TrendResponse } from "@/lib/api";
import { cn } from "@/lib/utils";
import { LoadError } from "@/components/common/load-error";
import { SkeletonRows } from "@/components/common/skeleton-rows";

// Daily revenue as bars (the owner asked for money as bars, not a line). Reuses
// the Postgres-safe /api/reports/trend endpoint (bucket=day, metric=revenue).

const money = (n: number) => n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
const dayLabel = (iso: string) => new Date(`${iso}T00:00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric" });

export function RevenueBars() {
  const [data, setData] = useState<TrendResponse | null>(null);
  const [err, setErr] = useState(false);
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    setErr(false);
    setData(null);
    api.get<TrendResponse>("/api/reports/trend?bucket=day&metric=revenue").then(setData).catch(() => setErr(true));
  }, [nonce]);

  const pts = data?.points ?? [];
  const max = Math.max(...pts.map((p) => p.value), 1);
  const total = pts.reduce((s, p) => s + p.value, 0);
  let peak = 0;
  for (let i = 1; i < pts.length; i++) if (pts[i].value > pts[peak].value) peak = i;

  return (
    <section className="card-paper rounded-2xl p-5">
      <div className="mb-4 flex flex-wrap items-center gap-x-3 gap-y-1">
        <DollarSign className="h-4 w-4 shrink-0 text-[var(--amber-600)]" />
        <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--cream-foreground)]/60">Revenue</h2>
        <span className="text-xs text-[var(--cream-foreground)]/50">last 30 days</span>
      </div>

      {err ? (
        <LoadError what="revenue" onRetry={() => setNonce((k) => k + 1)} />
      ) : data === null ? (
        <SkeletonRows n={4} />
      ) : total === 0 ? (
        <p className="py-10 text-center text-sm text-[var(--cream-foreground)]/60">
          No revenue in the last 30 days yet. As you take payments, the bars fill in here.
        </p>
      ) : (
        <>
          <div className="flex h-28 items-end gap-[3px]">
            {pts.map((p, i) => (
              <div key={p.label} className="group relative flex h-full flex-1 items-end">
                <div
                  className={cn(
                    "w-full rounded-t transition-colors",
                    // Money highlight is amber (60-30-10); the rest sit back in forest.
                    i === peak ? "bg-[var(--amber-500)]" : "bg-[var(--forest-600)]/30",
                  )}
                  style={{ height: `${(p.value / max) * 100}%`, minHeight: p.value > 0 ? 2 : 0 }}
                />
                <div className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-1 -translate-x-1/2 whitespace-nowrap rounded bg-[var(--forest-950)] px-2 py-1 text-[11px] shadow-lg opacity-0 transition-opacity group-hover:opacity-100">
                  <span className="font-mono font-semibold text-white">{money(p.value)}</span>
                  <span className="ml-1.5 text-white/60">{dayLabel(p.label)}</span>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-1.5 flex justify-between text-[11px] text-[var(--cream-foreground)]/50">
            <span>{pts.length > 0 ? dayLabel(pts[0].label) : ""}</span>
            <span>{pts.length > 1 ? dayLabel(pts[pts.length - 1].label) : ""}</span>
          </div>
          <p className="mt-2 text-sm text-[var(--cream-foreground)]/70">
            Last 30 days:{" "}
            <span className="font-mono font-semibold text-[var(--cream-foreground)]">{money(total)}</span>
            <span className="text-[var(--cream-foreground)]/40"> · </span>
            Best day <span className="font-semibold text-[var(--cream-foreground)]">{dayLabel(pts[peak].label)}</span>{" "}
            <span className="font-mono font-semibold text-[var(--cream-foreground)]">{money(pts[peak].value)}</span>
          </p>
        </>
      )}
    </section>
  );
}
