"use client";

import { useEffect, useState } from "react";
import { Activity, CalendarDays, Clock3 } from "lucide-react";
import { api, type BusyBar, type BusynessResponse } from "@/lib/api";
import { cn } from "@/lib/utils";
import { LoadError } from "@/components/common/load-error";
import { SkeletonRows } from "@/components/common/skeleton-rows";

// The owner's real question is "what days / what times is my lot busy" — this
// answers it with two bar strips (hour of day, day of week), no money involved.

function hourLabel(h: number): string {
  if (h === 0) return "12 AM";
  if (h === 12) return "12 PM";
  return h < 12 ? `${h} AM` : `${h - 12} PM`;
}

const DAY_FULL: Record<string, string> = {
  Mon: "Monday",
  Tue: "Tuesday",
  Wed: "Wednesday",
  Thu: "Thursday",
  Fri: "Friday",
  Sat: "Saturday",
  Sun: "Sunday",
};

function peakIndex(bars: BusyBar[]): number {
  let best = 0;
  for (let i = 1; i < bars.length; i++) if (bars[i].value > bars[best].value) best = i;
  return best;
}

function BarStrip({
  bars,
  peak,
  perBarLabels,
  ticks,
}: {
  bars: BusyBar[];
  peak: number;
  perBarLabels?: boolean;
  ticks?: string[];
}) {
  const max = Math.max(...bars.map((b) => b.value), 1);
  return (
    <div>
      <div className="flex h-28 items-end gap-[3px] border-b border-[var(--cream-foreground)]/10">
        {bars.map((b, i) => (
          <div key={b.label} className="group relative flex h-full flex-1 items-end">
            <div
              className={cn(
                "bar-grow w-full rounded-t transition-colors",
                // Peak bar solid forest; the rest faded. No amber — that stays
                // reserved for money/primary actions (60-30-10).
                i === peak ? "bg-[var(--forest-700)]" : "bg-[var(--forest-600)]/25",
              )}
              style={{
                height: `${(b.value / max) * 100}%`,
                minHeight: b.value > 0 ? 2 : 0,
                animationDelay: `${i * 14}ms`,
              }}
            />
            <div className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-1 -translate-x-1/2 whitespace-nowrap rounded bg-[var(--forest-950)] px-2 py-1 text-[11px] text-white opacity-0 shadow-lg transition-opacity group-hover:opacity-100">
              {b.value} pass{b.value === 1 ? "" : "es"}
            </div>
          </div>
        ))}
      </div>
      {perBarLabels ? (
        <div className="mt-1.5 flex gap-[3px] text-[11px] text-[var(--cream-foreground)]/50">
          {bars.map((b) => (
            <span key={b.label} className="flex-1 text-center">
              {b.label}
            </span>
          ))}
        </div>
      ) : ticks ? (
        <div className="mt-1.5 flex justify-between text-[11px] text-[var(--cream-foreground)]/50">
          {ticks.map((t) => (
            <span key={t}>{t}</span>
          ))}
        </div>
      ) : null}
    </div>
  );
}

/** "When is my lot busy?" — busiest times of day + busiest days of the week,
 *  from real pass data. Replaces the money trend line on the Dashboard. */
export function BusynessSection() {
  const [data, setData] = useState<BusynessResponse | null>(null);
  const [err, setErr] = useState(false);
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    setErr(false);
    setData(null);
    api.get<BusynessResponse>("/api/reports/busyness").then(setData).catch(() => setErr(true));
  }, [nonce]);

  const hourPeak = data ? peakIndex(data.by_hour) : 0;
  const dayPeak = data ? peakIndex(data.by_weekday) : 0;

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-x-3 gap-y-1">
        <Activity className="h-4 w-4 shrink-0 text-[var(--forest-700)]" />
        <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--cream-foreground)]/60">
          When is my lot busy?
        </h2>
        <span className="text-xs text-[var(--cream-foreground)]/50">last 90 days</span>
      </div>

      {err ? (
        <LoadError what="the busy times" onRetry={() => setNonce((k) => k + 1)} />
      ) : data === null ? (
        <SkeletonRows n={4} />
      ) : data.total === 0 ? (
        <p className="py-10 text-center text-sm text-[var(--cream-foreground)]/60">
          Not enough data yet. As you write passes, your busiest days and times show up here.
        </p>
      ) : (
        <div className="grid grid-cols-1 gap-x-8 gap-y-6 lg:grid-cols-2">
          <div>
            <div className="mb-2 flex items-center gap-2 text-sm font-medium text-[var(--cream-foreground)]">
              <Clock3 className="h-4 w-4 text-[var(--forest-700)]" /> Busiest times
            </div>
            <BarStrip bars={data.by_hour} peak={hourPeak} ticks={["12a", "6a", "12p", "6p", "11p"]} />
            <p className="mt-2 text-sm text-[var(--cream-foreground)]/70">
              Most trucks arrive around{" "}
              <span className="font-semibold text-[var(--cream-foreground)]">{hourLabel(hourPeak)}</span>.
            </p>
          </div>
          <div>
            <div className="mb-2 flex items-center gap-2 text-sm font-medium text-[var(--cream-foreground)]">
              <CalendarDays className="h-4 w-4 text-[var(--forest-700)]" /> Busiest days
            </div>
            <BarStrip bars={data.by_weekday} peak={dayPeak} perBarLabels />
            <p className="mt-2 text-sm text-[var(--cream-foreground)]/70">
              <span className="font-semibold text-[var(--cream-foreground)]">
                {DAY_FULL[data.by_weekday[dayPeak].label]}s
              </span>{" "}
              are your busiest.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
