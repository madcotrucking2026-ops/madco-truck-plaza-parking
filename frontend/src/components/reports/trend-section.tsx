"use client";

import { useEffect, useState } from "react";
import { TrendingUp } from "lucide-react";
import { api, type TrendBucket, type TrendMetric, type TrendResponse } from "@/lib/api";
import { cn } from "@/lib/utils";
import { LoadError } from "@/components/common/load-error";
import { SkeletonRows } from "@/components/common/skeleton-rows";
import { TrendChart } from "@/components/reports/trend-chart";

const BUCKETS: { value: TrendBucket; label: string }[] = [
  { value: "day", label: "Day" },
  { value: "week", label: "Week" },
  { value: "month", label: "Month" },
  { value: "year", label: "Year" },
];
const METRICS: { value: TrendMetric; label: string }[] = [
  { value: "revenue", label: "Revenue" },
  { value: "passes", label: "Passes" },
];
const RANGE: Record<TrendBucket, string> = {
  day: "last 30 days",
  week: "last 12 weeks",
  month: "last 12 months",
  year: "last 5 years",
};

function Segmented<T extends string>({
  options,
  value,
  onChange,
}: {
  options: { value: T; label: string }[];
  value: T;
  onChange: (v: T) => void;
}) {
  return (
    <div className="inline-flex rounded-xl bg-foreground/[0.06] p-1">
      {options.map((o) => (
        <button
          key={o.value}
          type="button"
          onClick={() => onChange(o.value)}
          className={cn(
            "flex h-9 items-center rounded-lg px-3 text-sm font-medium transition sm:h-8",
            value === o.value
              ? "btn-embossed bg-[var(--forest-700)] text-[var(--ivory-100)]"
              : "text-muted-foreground hover:text-foreground",
          )}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

/** Revenue (or pass count) over time, with a Day/Week/Month/Year zoom and a
 *  Revenue/Passes toggle — the owner's "understand the pattern" line graph. */
export function TrendSection() {
  const [bucket, setBucket] = useState<TrendBucket>("month");
  const [metric, setMetric] = useState<TrendMetric>("revenue");
  const [data, setData] = useState<TrendResponse | null>(null);
  const [err, setErr] = useState(false);
  const [nonce, setNonce] = useState(0);

  useEffect(() => {
    setErr(false);
    setData(null);
    api
      .get<TrendResponse>(`/api/reports/trend?bucket=${bucket}&metric=${metric}`)
      .then(setData)
      .catch(() => setErr(true));
  }, [bucket, metric, nonce]);

  return (
    <section className="card-paper rounded-2xl p-5">
      <div className="mb-4 flex flex-wrap items-center gap-x-3 gap-y-2">
        <TrendingUp className="h-4 w-4 shrink-0 text-[var(--forest-700)]" />
        <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--cream-foreground)]/60">Trend</h2>
        <span className="text-xs text-[var(--cream-foreground)]/50">{RANGE[bucket]}</span>
        <div className="ml-auto flex flex-wrap gap-2">
          <Segmented options={METRICS} value={metric} onChange={setMetric} />
          <Segmented options={BUCKETS} value={bucket} onChange={setBucket} />
        </div>
      </div>

      {err ? (
        <LoadError what="the trend" onRetry={() => setNonce((k) => k + 1)} />
      ) : data === null ? (
        <SkeletonRows n={4} />
      ) : (
        <TrendChart points={data.points} bucket={data.bucket} metric={data.metric} />
      )}
    </section>
  );
}
