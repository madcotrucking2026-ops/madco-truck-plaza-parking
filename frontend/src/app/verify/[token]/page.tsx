"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { CheckCircle2, XCircle, AlertTriangle, ShieldAlert, ShieldCheck, Truck } from "lucide-react";
import { api, type PassVerifyResult } from "@/lib/api";

const currency = (n: number) => n.toLocaleString("en-US", { style: "currency", currency: "USD" });

type Look = {
  label: string;
  sub: string;
  Icon: typeof CheckCircle2;
  // inline styles so the big status color can't be purged/overridden
  bg: string;
  fg: string;
};

function lookFor(result: PassVerifyResult | null): Look {
  if (!result || !result.valid) {
    return { label: "NOT A VALID PASS", sub: "This code isn't recognized.", Icon: ShieldAlert, bg: "#6B7280", fg: "#fff" };
  }
  switch (result.status) {
    case "active":
      return { label: "PAID · VALID", sub: "This pass is active.", Icon: CheckCircle2, bg: "var(--success)", fg: "#fff" };
    case "expiring_soon":
      return { label: "EXPIRES SOON", sub: "Still valid — renewal due shortly.", Icon: AlertTriangle, bg: "var(--warning)", fg: "var(--forest-700)" };
    case "expired":
      return { label: "EXPIRED", sub: "This pass is no longer valid.", Icon: XCircle, bg: "var(--danger)", fg: "#fff" };
    case "cancelled":
      return { label: "CANCELLED", sub: "This pass was cancelled.", Icon: XCircle, bg: "var(--danger)", fg: "#fff" };
    default:
      return { label: "UNKNOWN", sub: "Status unavailable.", Icon: ShieldAlert, bg: "#6B7280", fg: "#fff" };
  }
}

export default function VerifyPage() {
  const params = useParams<{ token: string }>();
  const [result, setResult] = useState<PassVerifyResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = params?.token;
    if (!token) return;
    api
      .get<PassVerifyResult>(`/api/verify/${encodeURIComponent(token)}`)
      .then(setResult)
      .catch(() => setResult({ valid: false } as PassVerifyResult))
      .finally(() => setLoading(false));
  }, [params]);

  const look = lookFor(result);
  const Icon = look.Icon;

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <header className="mx-auto mb-6 flex max-w-md items-center gap-3">
        <div className="btn-embossed flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--amber-500)] text-[var(--forest-950)]">
          <Truck className="h-5 w-5" strokeWidth={2.5} />
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate font-semibold leading-tight tracking-tight text-foreground">Madco Truck Plaza</p>
          <p className="text-xs text-muted-foreground">Pass Verification</p>
        </div>
        <span className="flex items-center gap-1 whitespace-nowrap rounded-full bg-[var(--forest-700)]/10 px-2.5 py-1 text-[11px] font-medium text-[var(--forest-700)] dark:text-[var(--ivory-100)]">
          <ShieldCheck className="h-3.5 w-3.5" />
          Secure
        </span>
      </header>

      {loading ? (
        <div className="animate-rise card-paper mx-auto max-w-md rounded-2xl p-8 text-center text-sm text-muted-foreground">
          Checking…
        </div>
      ) : (
        <div className="animate-rise mx-auto max-w-md space-y-4">
          <div
            className="flex flex-col items-center gap-2 rounded-2xl px-6 py-10 text-center shadow-lg"
            style={{ backgroundColor: look.bg, color: look.fg }}
          >
            <Icon className="h-16 w-16" strokeWidth={2} />
            <p className="text-2xl font-bold tracking-tight">{look.label}</p>
            <p className="text-sm opacity-90">{look.sub}</p>
          </div>

          {result?.valid && (
            <div className="card-paper rounded-2xl p-6">
              <Row label="Company" value={result.company_name ?? "—"} />
              <Row label="Truck / Vehicle" value={result.truck_number ?? result.trailer_number ?? result.license_plate ?? "—"} mono />
              <Row label="Pass Type" value={result.pass_type ? result.pass_type[0].toUpperCase() + result.pass_type.slice(1) : "—"} />
              <Row label="Issued" value={result.issue_date ?? "—"} mono />
              <Row label="Expires" value={result.expiration_date ?? "—"} mono />
              {result.price != null && <Row label="Price" value={currency(result.price)} mono />}
              <Row label="Receipt #" value={result.receipt_number ?? "—"} mono last />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function Row({ label, value, mono, last }: { label: string; value: string; mono?: boolean; last?: boolean }) {
  return (
    <div className={`flex items-center justify-between gap-4 py-2.5 ${last ? "" : "border-b border-black/5"}`}>
      <span className="text-sm text-[var(--cream-foreground)]/60">{label}</span>
      <span className={`text-right font-semibold text-[var(--cream-foreground)] ${mono ? "font-mono" : ""}`}>{value}</span>
    </div>
  );
}
