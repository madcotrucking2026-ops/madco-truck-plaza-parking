"use client";

import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { useCountUp } from "@/lib/use-count-up";

export function StatCard({
  label,
  value,
  icon: Icon,
  accent = "steel",
  sub,
  countTo,
  format,
}: {
  label: string;
  value: string | number;
  icon: LucideIcon;
  accent?: "steel" | "orange" | "forest" | "destructive" | "success";
  sub?: string;
  // When set, the number rolls up to `countTo` (formatted by `format`) instead of
  // rendering `value` statically. `value` is still the pre-data / reduced fallback.
  countTo?: number | null;
  format?: (n: number) => string;
}) {
  const counted = useCountUp(countTo ?? null);
  const display = countTo != null && format ? format(counted) : value;
  return (
    <div className="card-paper rounded-2xl p-4">
      <div className="flex items-start justify-between">
        <p className="text-xs font-medium uppercase tracking-wide text-[var(--cream-foreground)]/70">
          {label}
        </p>
        <div
          className={cn(
            "flex h-8 w-8 items-center justify-center rounded-lg",
            accent === "orange" && "bg-[var(--amber-500)]/20 text-[var(--amber-600)]",
            accent === "forest" && "bg-[var(--forest-600)]/20 text-[var(--forest-600)]",
            accent === "success" && "bg-[var(--success)]/15 text-[var(--success)]",
            accent === "destructive" && "bg-[var(--danger)]/15 text-[var(--danger-ink)]",
            accent === "steel" && "bg-[var(--stone-500)]/15 text-[var(--stone-500)]",
          )}
        >
          <Icon className="h-4 w-4" strokeWidth={2.25} />
        </div>
      </div>
      <p className="mt-3 font-mono text-2xl font-semibold tracking-tight text-[var(--cream-foreground)]">
        {display}
      </p>
      {sub && <p className="mt-0.5 text-xs text-[var(--cream-foreground)]/50">{sub}</p>}
    </div>
  );
}
