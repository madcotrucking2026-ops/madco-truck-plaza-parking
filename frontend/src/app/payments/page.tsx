"use client";

import { useEffect, useMemo, useState } from "react";
import type { LucideIcon } from "lucide-react";
import { Search, X, Banknote, CreditCard, FileCheck2, Wallet } from "lucide-react";
import { api } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { StatCard } from "@/components/dashboard/stat-card";
import { cn } from "@/lib/utils";

type Payment = {
  id: number;
  company_name: string | null;
  truck_number: string | null;
  pass_type: string | null;
  amount: number;
  method: string;
  check_number: string | null;
  receipt_number: string | null;
  employee_name: string | null;
  notes: string | null;
  paid_at: string;
};

const currency = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD" });

const METHOD_STYLE: Record<string, { label: string; className: string; Icon: LucideIcon }> = {
  cash: { label: "Cash", className: "bg-[var(--success)]/15 text-[var(--success)]", Icon: Banknote },
  credit_card: { label: "Credit Card", className: "bg-[var(--amber-500)]/15 text-[var(--amber-600)]", Icon: CreditCard },
  debit_card: { label: "Debit Card", className: "bg-[var(--amber-500)]/15 text-[var(--amber-600)]", Icon: CreditCard },
  phone: { label: "Card / Phone", className: "bg-[var(--amber-500)]/15 text-[var(--amber-600)]", Icon: CreditCard },
  check: { label: "Check", className: "bg-[var(--forest-600)]/15 text-[var(--forest-600)]", Icon: FileCheck2 },
};

function MethodBadge({ method, checkNumber }: { method: string; checkNumber: string | null }) {
  const s = METHOD_STYLE[method] ?? { label: method, className: "bg-muted text-muted-foreground", Icon: Wallet };
  const Icon = s.Icon;
  return (
    <span className={cn("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold", s.className)}>
      <Icon className="h-3.5 w-3.5" />
      {s.label}
      {method === "check" && checkNumber ? ` #${checkNumber}` : ""}
    </span>
  );
}

function bucketOf(method: string): "cash" | "card" | "check" | "other" {
  if (method === "cash") return "cash";
  if (method === "check") return "check";
  if (method === "credit_card" || method === "debit_card" || method === "phone") return "card";
  return "other";
}

type Period = "today" | "week" | "month" | "all";
const PERIODS: { value: Period; label: string }[] = [
  { value: "today", label: "Today" },
  { value: "week", label: "This Week" },
  { value: "month", label: "This Month" },
  { value: "all", label: "All Time" },
];

function inPeriod(dateStr: string, period: Period): boolean {
  if (period === "all") return true;
  const d = new Date(`${dateStr}T00:00:00`);
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  if (period === "today") return d.getTime() === today.getTime();
  if (period === "month") return d.getFullYear() === now.getFullYear() && d.getMonth() === now.getMonth();
  const monday = new Date(today);
  monday.setDate(today.getDate() - ((today.getDay() + 6) % 7));
  return d >= monday && d <= today;
}

export default function PaymentsPage() {
  const [payments, setPayments] = useState<Payment[] | null>(null);
  const [query, setQuery] = useState("");
  const [period, setPeriod] = useState<Period>("today");

  useEffect(() => {
    api.get<Payment[]>("/api/payments").then(setPayments).catch(() => setPayments([]));
  }, []);

  const filtered = useMemo(() => {
    if (!payments) return null;
    const q = query.trim().toLowerCase();
    return payments.filter((p) => {
      if (!inPeriod(p.paid_at.slice(0, 10), period)) return false;
      if (!q) return true;
      return [p.company_name, p.truck_number, p.receipt_number, p.check_number].some((v) =>
        v?.toLowerCase().includes(q),
      );
    });
  }, [payments, query, period]);

  const buckets = useMemo(() => {
    const b = {
      cash: { total: 0, count: 0 },
      card: { total: 0, count: 0 },
      check: { total: 0, count: 0 },
      other: { total: 0, count: 0 },
    };
    for (const p of filtered ?? []) {
      const k = bucketOf(p.method);
      b[k].total += p.amount;
      b[k].count += 1;
    }
    return b;
  }, [filtered]);

  const grandTotal = buckets.cash.total + buckets.card.total + buckets.check.total + buckets.other.total;
  const grandCount = (filtered ?? []).length;
  const periodLabel = PERIODS.find((p) => p.value === period)?.label.toLowerCase();

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Payments</h1>
          <p className="text-sm text-muted-foreground">
            Reconcile your drawer, card batch, and checks. Every payment is kept forever.
          </p>
        </div>
        {/* Segmented period control */}
        <div className="inline-flex rounded-xl bg-black/[0.05] p-1">
          {PERIODS.map((p) => (
            <button
              key={p.value}
              type="button"
              onClick={() => setPeriod(p.value)}
              className={cn(
                "rounded-lg px-3.5 py-1.5 text-sm font-medium transition",
                period === p.value
                  ? "btn-embossed bg-[var(--forest-700)] text-[var(--ivory-100)]"
                  : "text-[var(--cream-foreground)]/70 hover:text-[var(--cream-foreground)]",
              )}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Reconciliation cards — same StatCard used across Dashboard & Reports */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Total Collected" value={currency(grandTotal)} icon={Wallet} accent="orange" sub={`${grandCount} payment${grandCount === 1 ? "" : "s"}`} />
        <StatCard label="Cash Drawer" value={currency(buckets.cash.total)} icon={Banknote} accent="success" sub={`${buckets.cash.count} payment${buckets.cash.count === 1 ? "" : "s"}`} />
        <StatCard label="Card Batch" value={currency(buckets.card.total)} icon={CreditCard} accent="steel" sub={`${buckets.card.count} payment${buckets.card.count === 1 ? "" : "s"}`} />
        <StatCard label="Checks" value={currency(buckets.check.total)} icon={FileCheck2} accent="forest" sub={`${buckets.check.count} payment${buckets.check.count === 1 ? "" : "s"}`} />
      </div>

      {/* Payment history — a titled section, matching the Reports page layout */}
      <section className="card-paper overflow-hidden rounded-2xl">
        <div className="flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--cream-foreground)]/60">
            Payment History
          </h2>
          <div className="relative sm:w-80">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search company, truck, receipt, check #…"
              className="h-9 pl-9"
            />
            {query && (
              <button
                type="button"
                onClick={() => setQuery("")}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>

        {payments === null ? (
          <p className="p-6 pt-0 text-sm text-[var(--cream-foreground)]/60">Loading…</p>
        ) : (filtered ?? []).length === 0 ? (
          <div className="flex flex-col items-center gap-2 p-12 pt-4 text-center">
            <Wallet className="h-8 w-8 text-[var(--cream-foreground)]/30" />
            <p className="text-sm text-[var(--cream-foreground)]/60">
              No payments {period === "all" ? "recorded yet" : `for ${periodLabel}`}
              {query ? " matching your search" : ""}.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-y border-black/10 bg-black/[0.02] text-left text-xs uppercase tracking-wide text-[var(--cream-foreground)]/60">
                  <th className="px-5 py-3 font-medium">Date &amp; Time</th>
                  <th className="px-5 py-3 font-medium">Company</th>
                  <th className="px-5 py-3 font-medium">Truck</th>
                  <th className="px-5 py-3 text-right font-medium">Amount</th>
                  <th className="px-5 py-3 font-medium">Method</th>
                  <th className="px-5 py-3 font-medium">Receipt #</th>
                </tr>
              </thead>
              <tbody>
                {(filtered ?? []).map((p) => {
                  const dt = new Date(p.paid_at);
                  return (
                    <tr
                      key={p.id}
                      className="border-b border-black/5 text-[var(--cream-foreground)] transition-colors last:border-none hover:bg-black/[0.02]"
                    >
                      <td className="whitespace-nowrap px-5 py-3 font-mono text-xs">
                        {p.paid_at.slice(0, 10)}
                        <span className="text-[var(--cream-foreground)]/40">
                          {" "}
                          {dt.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" })}
                        </span>
                      </td>
                      <td className="px-5 py-3 font-medium">{p.company_name ?? "—"}</td>
                      <td className="whitespace-nowrap px-5 py-3 font-mono text-xs">
                        {p.truck_number ?? "—"}
                        {p.pass_type ? <span className="text-[var(--cream-foreground)]/40"> · {p.pass_type}</span> : ""}
                      </td>
                      <td className="px-5 py-3 text-right font-mono text-base font-bold">{currency(p.amount)}</td>
                      <td className="px-5 py-3">
                        <MethodBadge method={p.method} checkNumber={p.check_number} />
                      </td>
                      <td className="px-5 py-3 font-mono text-xs text-[var(--cream-foreground)]/60">{p.receipt_number ?? "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

