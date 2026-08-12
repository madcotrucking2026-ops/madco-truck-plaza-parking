"use client";

import { useState } from "react";
import type { TrendBucket, TrendMetric, TrendPoint } from "@/lib/api";

// Hand-rolled SVG line chart (the app uses no chart library). Scales to width via
// a viewBox; the stroke stays crisp with vector-effect regardless of scaling.
const W = 640;
const H = 200;
const PAD_X = 6;
const PAD_Y = 14;

const money = (n: number) => n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

function axisLabel(key: string, bucket: TrendBucket): string {
  if (bucket === "year") return key;
  if (bucket === "month") {
    const [y, m] = key.split("-");
    return new Date(Number(y), Number(m) - 1, 1).toLocaleDateString("en-US", { month: "short" });
  }
  return new Date(`${key}T00:00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function tipLabel(key: string, bucket: TrendBucket): string {
  if (bucket === "year") return key;
  if (bucket === "month") {
    const [y, m] = key.split("-");
    return new Date(Number(y), Number(m) - 1, 1).toLocaleDateString("en-US", { month: "short", year: "numeric" });
  }
  const full = new Date(`${key}T00:00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
  return bucket === "week" ? `week of ${full}` : full;
}

export function TrendChart({ points, bucket, metric }: { points: TrendPoint[]; bucket: TrendBucket; metric: TrendMetric }) {
  const [hover, setHover] = useState<number | null>(null);
  const n = points.length;
  const maxVal = Math.max(...points.map((p) => p.value), metric === "revenue" ? 50 : 1);
  const niceMax = metric === "revenue" ? Math.ceil(maxVal / 50) * 50 : Math.max(Math.ceil(maxVal), 1);
  const x = (i: number) => PAD_X + (n <= 1 ? 0 : (i / (n - 1)) * (W - 2 * PAD_X));
  const y = (v: number) => H - PAD_Y - (v / niceMax) * (H - 2 * PAD_Y);
  const linePts = points.map((p, i) => `${x(i)},${y(p.value)}`).join(" ");
  const areaPts = `${x(0)},${H - PAD_Y} ${linePts} ${x(n - 1)},${H - PAD_Y}`;
  const fmt = (v: number) => (metric === "revenue" ? money(v) : `${Math.round(v)} pass${v === 1 ? "" : "es"}`);

  return (
    <div>
      <div className="relative" style={{ height: H }}>
        <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" style={{ width: "100%", height: H }}>
          <polygon points={areaPts} fill="var(--forest-600)" opacity={0.12} />
          <polyline
            points={linePts}
            fill="none"
            stroke="var(--forest-600)"
            strokeWidth={2}
            strokeLinejoin="round"
            strokeLinecap="round"
            vectorEffect="non-scaling-stroke"
          />
          {hover !== null && (
            <circle cx={x(hover)} cy={y(points[hover].value)} r={4} fill="var(--forest-700)" vectorEffect="non-scaling-stroke" />
          )}
        </svg>
        {/* Invisible per-point hover targets over the chart. */}
        <div className="absolute inset-0 flex">
          {points.map((p, i) => (
            <div
              key={p.label}
              className="h-full flex-1"
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover((c) => (c === i ? null : c))}
            />
          ))}
        </div>
        {hover !== null && (
          <div
            className="pointer-events-none absolute z-10 -translate-x-1/2 -translate-y-full whitespace-nowrap rounded-md bg-[var(--forest-950)] px-2.5 py-1.5 text-xs shadow-lg"
            style={{ left: `${(x(hover) / W) * 100}%`, top: `${(y(points[hover].value) / H) * 100}%` }}
          >
            <p className="font-mono font-semibold text-white">{fmt(points[hover].value)}</p>
            <p className="text-white/60">{tipLabel(points[hover].label, bucket)}</p>
          </div>
        )}
      </div>
      <div className="mt-2 flex justify-between border-t border-[var(--cream-foreground)]/10 pt-1.5 text-[11px] text-[var(--cream-foreground)]/50">
        <span>{n > 0 ? axisLabel(points[0].label, bucket) : ""}</span>
        <span>{n > 2 ? axisLabel(points[Math.floor(n / 2)].label, bucket) : ""}</span>
        <span>{n > 1 ? axisLabel(points[n - 1].label, bucket) : ""}</span>
      </div>
    </div>
  );
}
