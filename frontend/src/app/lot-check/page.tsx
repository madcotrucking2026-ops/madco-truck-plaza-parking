"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Search } from "lucide-react";
import { api, type LotCheckResult } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const STATUS_STYLE: Record<string, { bg: string; label: string }> = {
  active: { bg: "bg-[var(--success)]", label: "ACTIVE" },
  expiring_soon: { bg: "bg-[var(--warning)]", label: "EXPIRING SOON" },
  expired: { bg: "bg-[var(--danger)]", label: "EXPIRED" },
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

  const style = result?.found && result.status ? STATUS_STYLE[result.status] : { bg: "bg-[var(--stone-500)]", label: "NOT FOUND" };

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Lot Check</h1>
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
          <div className={`${style.bg} rounded-2xl py-10 text-center shadow-lg`}>
            <p className="text-4xl font-extrabold tracking-wide text-white">{style.label}</p>
          </div>

          {result.found && (
            <div className="card-paper space-y-2 rounded-2xl p-5 text-sm">
              <DetailRow label="Company" value={result.company_name} />
              <DetailRow label="Phone" value={result.phone} />
              <DetailRow label="Truck Number" value={result.truck_number} />
              <DetailRow label="Trailer Number" value={result.trailer_number} />
              <DetailRow label="License Plate" value={result.license_plate} />
              <DetailRow label="Pass Type" value={result.pass_type} className="capitalize" />
              <DetailRow label="Expiration" value={result.expiration_date} />
              {result.notes && <DetailRow label="Notes" value={result.notes} />}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function DetailRow({ label, value, className }: { label: string; value?: string; className?: string }) {
  if (!value) return null;
  return (
    <div className="flex items-center justify-between border-b border-black/10 py-1 last:border-none">
      <span className="text-[var(--cream-foreground)]/60">{label}</span>
      <span className={`font-medium text-[var(--cream-foreground)] ${className ?? ""}`}>{value}</span>
    </div>
  );
}
