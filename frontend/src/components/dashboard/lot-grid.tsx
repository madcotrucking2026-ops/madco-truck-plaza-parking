"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { toast } from "sonner";
import { api, type SpotState } from "@/lib/api";
import { byZone } from "@/lib/zones";
import { Button } from "@/components/ui/button";

// Cells are a colour-coded heatmap of the lot, one square per painted spot.
// No number is printed on the square: at 150 cells in the dashboard's narrow
// right rail a three-digit number can't fit and the digits collide — the map's
// job here is "how full, and where", read at a glance. The exact spot is on
// hover (title), and the full findable board lives at /availability.
const STATE_BG: Record<SpotState["state"], string> = {
  free: "bg-[var(--success)]/25",
  occupied: "bg-[var(--forest-700)]",
  expiring: "bg-[var(--warning)]/80",
  grace: "bg-[var(--amber-500)]/55",
  overstay: "bg-[var(--danger)]",
  inactive: "bg-black/10",
};

const LEGEND: { state: SpotState["state"]; label: string }[] = [
  { state: "free", label: "Free" },
  { state: "occupied", label: "Occupied" },
  { state: "expiring", label: "Expiring" },
  { state: "grace", label: "Grace (monthly)" },
  { state: "overstay", label: "Overstay" },
];

/** The whole lot at a glance: one cell per painted spot, colour = derived state,
 *  grouped into the lettered zones the lot is actually painted into. Tap an
 *  occupied cell for the truck sitting on it. */
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
  const zones = byZone(spots);

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
                <span className="font-mono font-bold tabular-nums">Spot {s.label}</span>
                <span className="flex-1">go move the truck along, then clear it</span>
                <Button variant="outline" size="sm" className="shrink-0" onClick={() => clearOverstay(s.number)}>
                  Cleared
                </Button>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="card-paper rounded-2xl p-5">
        <h2 className="mb-4 text-sm font-medium text-[var(--cream-foreground)]/70">Lot map</h2>

        <div className="space-y-3.5">
          {zones.map(({ zone, spots: cells, free }) => (
            <div key={zone} className="space-y-1.5">
              <div className="flex items-baseline justify-between">
                <span className="font-mono text-xs font-semibold tracking-wide text-[var(--cream-foreground)]/70">
                  {zone === "•" ? "Lot" : `Zone ${zone}`}
                </span>
                <span className="text-[11px] tabular-nums text-[var(--cream-foreground)]/45">{free} free</span>
              </div>
              <div className="grid grid-cols-[repeat(auto-fill,minmax(0.9rem,1fr))] gap-1">
                {cells.map((s) => {
                  const swatch = (
                    <div
                      title={`Spot ${s.label}${s.company_name ? ` — ${s.company_name}` : ""} (${s.state})`}
                      className={`aspect-square rounded-[3px] ring-1 ring-inset ring-black/[0.06] ${STATE_BG[s.state]} ${
                        s.truck_number
                          ? "cursor-pointer transition hover:ring-2 hover:ring-[var(--forest-600)]"
                          : ""
                      }`}
                    />
                  );
                  return s.truck_number ? (
                    <Link
                      key={s.number}
                      href={`/lot-check?q=${encodeURIComponent(s.truck_number)}`}
                      aria-label={`Spot ${s.label}, ${s.company_name ?? "occupied"}`}
                    >
                      {swatch}
                    </Link>
                  ) : (
                    <span key={s.number}>{swatch}</span>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 flex flex-wrap gap-x-4 gap-y-1 border-t border-black/5 pt-3">
          {LEGEND.map((l) => (
            <span key={l.state} className="flex items-center gap-1.5 text-xs text-[var(--cream-foreground)]/60">
              <span className={`h-3 w-3 rounded-[3px] ring-1 ring-inset ring-black/[0.06] ${STATE_BG[l.state]}`} />
              {l.label}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
