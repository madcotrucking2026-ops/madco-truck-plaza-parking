"use client";

import { useState } from "react";

const CHART_HEIGHT = 176;

const currency = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

const formatDate = (iso: string) =>
  new Date(`${iso}T00:00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric" });

export function RevenueChart({ data }: { data: { date: string; amount: number }[] }) {
  const [hoverIdx, setHoverIdx] = useState<number | null>(null);
  const max = Math.max(...data.map((d) => d.amount), 1);
  const niceMax = Math.max(Math.ceil(max / 50) * 50, 50);

  return (
    <div>
      <div className="flex items-end gap-[3px]" style={{ height: CHART_HEIGHT }}>
        {data.map((d, i) => {
          const barHeight = Math.round((d.amount / niceMax) * CHART_HEIGHT);
          return (
            <div
              key={d.date}
              className="group relative flex h-full flex-1 items-end"
              onMouseEnter={() => setHoverIdx(i)}
              onMouseLeave={() => setHoverIdx((cur) => (cur === i ? null : cur))}
            >
              <div
                className="mx-auto w-full max-w-[16px] rounded-t-[4px] bg-[var(--forest-600)] transition-[opacity] group-hover:opacity-80"
                style={{ height: Math.max(barHeight, d.amount > 0 ? 2 : 1) }}
              />
              {hoverIdx === i && (
                <div className="pointer-events-none absolute bottom-full left-1/2 z-10 mb-2 -translate-x-1/2 whitespace-nowrap rounded-md bg-[var(--forest-950)] px-2.5 py-1.5 text-xs shadow-lg">
                  <p className="font-mono font-semibold text-white">{currency(d.amount)}</p>
                  <p className="text-white/60">{formatDate(d.date)}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>
      <div className="mt-2 flex justify-between border-t border-[var(--cream-foreground)]/10 pt-1.5 text-[11px] text-[var(--cream-foreground)]/50">
        <span>{formatDate(data[0]?.date)}</span>
        <span>{formatDate(data[Math.floor(data.length / 2)]?.date)}</span>
        <span>{formatDate(data[data.length - 1]?.date)}</span>
      </div>
    </div>
  );
}
