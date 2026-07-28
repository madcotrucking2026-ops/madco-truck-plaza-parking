"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { toast } from "sonner";
import { api, type SpotState } from "@/lib/api";
import { Button } from "@/components/ui/button";

const STATE_CLASS: Record<SpotState["state"], string> = {
  free: "bg-[var(--success)]/20 text-[var(--cream-foreground)]/60",
  occupied: "bg-[var(--forest-700)] text-[var(--ivory-100)]",
  expiring: "bg-[var(--warning)]/70 text-[var(--forest-950)]",
  grace: "bg-[var(--amber-500)]/45 text-[var(--forest-950)]",
  overstay: "bg-[var(--danger)] text-white",
  inactive: "bg-black/10 text-[var(--cream-foreground)]/30",
};

const LEGEND: { state: SpotState["state"]; label: string }[] = [
  { state: "free", label: "Free" },
  { state: "occupied", label: "Occupied" },
  { state: "expiring", label: "Expiring" },
  { state: "grace", label: "Grace (monthly)" },
  { state: "overstay", label: "Overstay" },
];

/** The whole lot at a glance: one cell per painted spot, colour = derived state,
 *  tap an occupied cell for the truck sitting on it. */
export function LotGrid() {
  const [spots, setSpots] = useState<SpotState[] | null>(null);

  function load() {
    api.get<SpotState[]>("/api/spots").then(setSpots).catch(() => setSpots(null));
  }
  useEffect(load, []);

  async function clearOverstay(number: number) {
    try {
      await api.post(`/api/spots/${number}/clear-overstay`, {});
      toast.success(`Spot ${number} back in service.`);
      load();
    } catch {
      toast.error("Couldn't clear that spot — try again.");
    }
  }

  if (!spots) return null;
  const overstays = spots.filter((s) => s.state === "overstay");

  return (
    <div className="space-y-3">
      {/* A customer stood in front of a squatting truck and told us — that beats
          every number on this page for urgency. Silent when empty. */}
      {overstays.length > 0 && (
        <div className="space-y-2 rounded-xl border border-[var(--danger)]/40 bg-[var(--danger)]/10 p-4">
          <p className="text-sm font-semibold text-[var(--danger-ink)]">
            {overstays.length === 1 ? "A spot is" : `${overstays.length} spots are`} blocked by an expired truck
          </p>
          <ul className="space-y-1.5">
            {overstays.map((s) => (
              <li key={s.number} className="flex items-center gap-3 text-sm text-[var(--danger-ink)]/90">
                <span className="font-mono font-bold tabular-nums">Spot {s.number}</span>
                <span className="flex-1">go move the truck along, then clear it</span>
                <Button variant="outline" size="sm" className="shrink-0" onClick={() => clearOverstay(s.number)}>
                  Cleared
                </Button>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="card-paper rounded-2xl p-4">
        <div className="grid grid-cols-[repeat(15,minmax(0,1fr))] gap-1 sm:grid-cols-[repeat(20,minmax(0,1fr))]">
          {spots.map((s) => {
            const cell = (
              <div
                title={`Spot ${s.number}${s.company_name ? ` — ${s.company_name}` : ""} (${s.state})`}
                className={`flex aspect-square items-center justify-center rounded font-mono text-[9px] tabular-nums ${STATE_CLASS[s.state]}`}
              >
                {s.number}
              </div>
            );
            return s.truck_number ? (
              <Link key={s.number} href={`/lot-check?q=${encodeURIComponent(s.truck_number)}`}>{cell}</Link>
            ) : (
              <span key={s.number}>{cell}</span>
            );
          })}
        </div>
        <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1">
          {LEGEND.map((l) => (
            <span key={l.state} className="flex items-center gap-1.5 text-xs text-[var(--cream-foreground)]/60">
              <span className={`h-3 w-3 rounded ${STATE_CLASS[l.state].split(" ")[0]}`} />
              {l.label}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
