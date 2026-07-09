"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { CheckCircle2, XCircle, AlertTriangle, ShieldAlert, Truck } from "lucide-react";
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
      return { label: "PAID · VALID", sub: "This pass is active.", Icon: CheckCircle2, bg: "#1FAF67", fg: "#fff" };
    case "expiring_soon":
      return { label: "EXPIRES SOON", sub: "Still valid — renewal due shortly.", Icon: AlertTriangle, bg: "#E7B416", fg: "#173F35" };
    case "expired":
      return { label: "EXPIRED", sub: "This pass is no longer valid.", Icon: XCircle, bg: "#D74A4A", fg: "#fff" };
    case "cancelled":
      return { label: "CANCELLED", sub: "This pass was cancelled.", Icon: XCircle, bg: "#D74A4A", fg: "#fff" };
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
      <div className="mx-auto flex max-w-md items-center gap-3 pb-6">
        <div className="btn-embossed flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--amber-500)] text-[var(--forest-950)]">
          <Truck className="h-5 w-5" strokeWidth={2.5} />
        </div>
        <div>
          <p className="font-semibold tracking-tight text-foreground">Madco Truck Plaza</p>
          <p className="text-xs text-muted-foreground">Pass Verification</p>
        </div>
      </div>

      {loading ? (
        <div className="card-paper mx-auto max-w-md rounded-2xl p-8 text-center text-sm text-muted-foreground">
          Checking…
        </div>
      ) : (
        <div className="mx-auto max-w-md space-y-4">
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
