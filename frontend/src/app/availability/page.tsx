"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { RefreshCw, X } from "lucide-react";
import { api, ApiError, type MoveSpotResult, type SpotState } from "@/lib/api";
import { byZone } from "@/lib/zones";
import { Button } from "@/components/ui/button";
import { LoadError } from "@/components/common/load-error";

// Same palette as the dashboard grid, so a spot reads identically everywhere.
const STATE_CLASS: Record<SpotState["state"], string> = {
  free: "bg-[var(--success)]/20 text-[var(--cream-foreground)]/70",
  occupied: "bg-[var(--forest-700)] text-[var(--ivory-100)]",
  expiring: "bg-[var(--warning)]/70 text-[var(--forest-950)]",
  grace: "bg-[var(--amber-500)]/45 text-[var(--forest-950)]",
  overstay: "bg-[var(--danger)] text-white",
  inactive: "bg-black/10 text-[var(--cream-foreground)]/30",
};

const REFRESH_MS = 5000;

export default function AvailabilityPage() {
  const [spots, setSpots] = useState<SpotState[] | null>(null);
  const [err, setErr] = useState(false);
  const [updatedAgo, setUpdatedAgo] = useState(0);
  // When set, the cashier is placing this truck — free cells become tappable.
  const [moving, setMoving] = useState<SpotState | null>(null);
  const [busy, setBusy] = useState(false);
  const lastFetch = useRef<number>(0);

  const load = useCallback(async () => {
    try {
      const data = await api.get<SpotState[]>("/api/spots");
      setSpots(data);
      setErr(false);
      lastFetch.current = Date.now();
      setUpdatedAgo(0);
    } catch {
      setErr(true);
    }
  }, []);

  // Poll every 5s, but pause while the tab is hidden so a forgotten tab doesn't
  // hammer the server; refetch immediately when it becomes visible again.
  useEffect(() => {
    load();
    let timer: ReturnType<typeof setInterval> | null = null;
    const start = () => {
      if (timer) return;
      timer = setInterval(load, REFRESH_MS);
    };
    const stop = () => {
      if (timer) clearInterval(timer);
      timer = null;
    };
    const onVis = () => {
      if (document.hidden) stop();
      else {
        load();
        start();
      }
    };
    start();
    document.addEventListener("visibilitychange", onVis);
    return () => {
      stop();
      document.removeEventListener("visibilitychange", onVis);
    };
  }, [load]);

  // "updated Ns ago" ticker.
  useEffect(() => {
    const t = setInterval(() => setUpdatedAgo(Math.round((Date.now() - lastFetch.current) / 1000)), 1000);
    return () => clearInterval(t);
  }, []);

  async function moveTo(target: SpotState) {
    if (!moving || busy) return;
    if (moving.pass_id === null) return;
    setBusy(true);
    try {
      const res = await api.post<MoveSpotResult>("/api/spots/move", {
        pass_id: moving.pass_id,
        to_number: target.number,
      });
      toast.success(`Moved ${moving.truck_number ?? "truck"} to ${res.spot_label}.`);
      setMoving(null);
      await load();
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : "Couldn't move the truck.");
    } finally {
      setBusy(false);
    }
  }

  if (err && spots === null) return <LoadError onRetry={load} what="the lot" />;

  const zones = spots ? byZone(spots) : [];
  const totalFree = spots?.filter((s) => s.state === "free").length ?? 0;
  const totalActive = spots?.filter((s) => s.state !== "inactive").length ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Open Spots</h1>
          <p className="text-sm text-muted-foreground">
            Live lot map — every zone, refreshing on its own.{" "}
            <span className="inline-flex items-center gap-1 text-[var(--success)]">
              <RefreshCw className="h-3 w-3" />
              {spots ? `updated ${updatedAgo}s ago` : "loading…"}
            </span>
          </p>
        </div>
        <div className="rounded-xl bg-[var(--success)]/15 px-4 py-2 text-right">
          <p className="font-mono text-2xl font-bold tabular-nums text-[var(--cream-foreground)]">{totalFree}</p>
          <p className="text-xs text-[var(--cream-foreground)]/60">free of {totalActive}</p>
        </div>
      </div>

      {moving && (
        <div className="flex items-center justify-between gap-3 rounded-xl border border-[var(--amber-500)]/50 bg-[var(--amber-500)]/15 p-3">
          <p className="text-sm font-medium text-[var(--cream-foreground)]">
            Moving <b>{moving.truck_number ?? "truck"}</b> ({moving.company_name ?? "—"}) — tap a{" "}
            <span className="font-semibold text-[var(--success)]">free</span> spot to place it.
          </p>
          <Button variant="outline" size="sm" onClick={() => setMoving(null)}>
            <X className="h-3.5 w-3.5" />
            Cancel
          </Button>
        </div>
      )}

      {zones.map(({ zone, spots: cells, free }) => (
        <section key={zone} className="card-paper rounded-2xl p-4">
          <div className="mb-3 flex items-baseline justify-between">
            <h2 className="font-mono text-lg font-bold text-[var(--cream-foreground)]">Zone {zone}</h2>
            <span className="text-sm text-[var(--cream-foreground)]/60">
              <b className="text-[var(--cream-foreground)]">{free}</b> free
            </span>
          </div>
          <div className="grid grid-cols-5 gap-1.5 sm:grid-cols-[repeat(13,minmax(0,1fr))]">
            {cells.map((s) => {
              const isMoveTarget = moving !== null && s.state === "free";
              const isOccupied = s.pass_id !== null && s.state !== "inactive";
              const onClick = () => {
                if (moving) {
                  if (s.state === "free") moveTo(s);
                } else if (isOccupied) {
                  setMoving(s);
                }
              };
              const within = /^[A-Z]/.test(s.label) ? s.label.slice(1) : s.label;
              return (
                <button
                  key={s.number}
                  type="button"
                  disabled={busy || (moving ? s.state !== "free" : !isOccupied)}
                  onClick={onClick}
                  title={`${s.label}${s.company_name ? ` — ${s.company_name} (${s.truck_number ?? ""})` : ""} · ${s.state}`}
                  className={`flex aspect-square items-center justify-center rounded font-mono text-[11px] font-semibold tabular-nums transition ${STATE_CLASS[s.state]} ${
                    isMoveTarget ? "ring-2 ring-[var(--amber-500)] hover:brightness-110" : ""
                  } ${!moving && isOccupied ? "hover:ring-2 hover:ring-[var(--forest-700)]/40" : ""} disabled:cursor-default`}
                >
                  {within}
                </button>
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
}
