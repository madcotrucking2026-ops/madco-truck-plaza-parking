"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Search } from "lucide-react";
import { api, type LotCheckResult } from "@/lib/api";
import { currency, daysBetween, todayISO } from "@/lib/pricing";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

// Per-status text colour: the amber "expiring" band is light, so white text on
// it fails contrast (~1.7:1) — it wears dark forest ink instead. The dark bands
// (green/red/stone) keep white. Mirrors the /verify status banner.
const STATUS_STYLE: Record<string, { bg: string; fg: string; label: string }> = {
  active: { bg: "bg-[var(--success)]", fg: "text-white", label: "ACTIVE" },
  expiring_soon: { bg: "bg-[var(--warning)]", fg: "text-[var(--forest-950)]", label: "EXPIRING SOON" },
  expired: { bg: "bg-[var(--danger)]", fg: "text-white", label: "EXPIRED" },
};

export default function LotCheckPage() {
  return (
    <Suspense fallback={null}>
      <LotCheckInner />
    </Suspense>
  );
}

function LotCheckInner() {
  const searchParams = useSearchParams();
  const [query, setQuery] = useState(searchParams.get("q") ?? "");
  const [result, setResult] = useState<LotCheckResult | null>(null);
  const [loading, setLoading] = useState(false);

  const runSearch = useCallback(async (value: string) => {
    if (!value.trim()) return;
    setLoading(true);
    try {
      const res = await api.get<LotCheckResult>(`/api/lot-check?q=${encodeURIComponent(value.trim())}`);
      setResult(res);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const initial = searchParams.get("q");
    if (initial) runSearch(initial);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    runSearch(query);
  }

  const style = result?.found && result.status ? STATUS_STYLE[result.status] : { bg: "bg-[var(--stone-500)]", fg: "text-white", label: "NOT FOUND" };

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Find a Truck</h1>
        <p className="text-sm text-muted-foreground">
          Search truck #, trailer #, license plate, company, USDOT, or phone — instantly see payment status.
        </p>
      </div>

      <form onSubmit={handleSearch} className="flex gap-2">
        <Input
          autoFocus
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Truck number, company, phone…"
          className="h-14 text-lg"
        />
        <Button
          type="submit"
          disabled={loading}
          className="btn-embossed h-14 w-14 shrink-0 bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)]"
        >
          <Search className="h-5 w-5" />
        </Button>
      </form>

      {result && (
        <div className="space-y-4">
          <div className={`${style.bg} rounded-2xl px-6 py-10 text-center shadow-lg`}>
            <p className={`text-4xl font-extrabold tracking-wide ${style.fg}`}>{style.label}</p>
            {/* Standing at the truck, the question is "did this one pay?" — so the
                answer goes on the card itself, not three rows down in a table. */}
            {result.found && result.expiration_date && (
              <p className={`mt-2 text-base font-semibold ${style.fg} opacity-90`}>
                {expiryPhrase(result.expiration_date)}
              </p>
            )}
            {result.found && result.amount_paid != null && (
              <p className={`mt-1 font-mono text-sm tabular-nums ${style.fg} opacity-80`}>
                Paid {currency(result.amount_paid)} · {PAYMENT_LABEL[result.payment_method ?? "cash"]}
                {result.paid_at ? ` · ${shortDate(result.paid_at)}` : ""}
              </p>
            )}
          </div>

          {result.found && (
            <div className="card-paper space-y-2 rounded-2xl p-5 text-sm">
              <DetailRow label="Spot" value={result.spot_number != null ? `#${result.spot_number}` : undefined} mono />
              <DetailRow label="Company" value={result.company_name} />
              <DetailRow label="Phone" value={result.phone} mono />
              <DetailRow label="Truck Number" value={result.truck_number} mono />
              <DetailRow label="Trailer Number" value={result.trailer_number} mono />
              <DetailRow label="License Plate" value={result.license_plate} mono />
              <DetailRow
                label="Pass Type"
                value={result.is_monthly_customer ? `${result.pass_type} · monthly customer` : result.pass_type}
                className="capitalize"
              />
              <DetailRow label="Expiration" value={result.expiration_date} />
              {result.notes && <DetailRow label="Notes" value={result.notes} />}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const PAYMENT_LABEL: Record<string, string> = {
  cash: "Cash",
  check: "Check",
  credit_card: "Card",
  debit_card: "Debit",
  phone_payment: "Card by phone",
};

/** "expires tomorrow" beats "2026-07-14" when you're standing in a lot in the dark.
 *  Counted from the PLAZA's day — a tablet left on UTC would otherwise call a pass
 *  expired the evening before it actually is. */
function expiryPhrase(expiration: string): string {
  const days = daysBetween(todayISO(), expiration);
  if (days === 0) return "Expires TODAY";
  if (days === 1) return "Expires tomorrow";
  if (days < 0) return `Expired ${-days} day${days === -1 ? "" : "s"} ago`;
  return `Expires in ${days} days · ${shortDate(expiration)}`;
}

// ISO (2026-08-15) — the plaza's chosen date style everywhere. `iso` is already
// a YYYY-MM-DD (or ISO datetime); take the date part.
function shortDate(iso: string): string {
  return iso.slice(0, 10);
}

function DetailRow({
  label,
  value,
  className,
  mono,
}: {
  label: string;
  value?: string;
  className?: string;
  /** Set on the vehicle identifiers — a truck/trailer/plate/spot is data a truck
   *  stop reads as data, so it belongs in the mono face, not Inter. */
  mono?: boolean;
}) {
  if (!value) return null;
  return (
    <div className="flex items-center justify-between border-b border-black/10 py-1 last:border-none">
      <span className="text-[var(--cream-foreground)]/60">{label}</span>
      <span
        className={`font-medium text-[var(--cream-foreground)] ${mono ? "font-mono tabular-nums" : ""} ${className ?? ""}`}
      >
        {value}
      </span>
    </div>
  );
}
