"use client";

import { useEffect, useMemo, useState } from "react";
import type { LucideIcon } from "lucide-react";
import { Search, X, Banknote, CreditCard, FileCheck2, Wallet, Ban } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { toast } from "sonner";
import { addDaysISO, todayISO } from "@/lib/pricing";
import { Input } from "@/components/ui/input";
import { StatCard } from "@/components/dashboard/stat-card";
import { LoadError } from "@/components/common/load-error";
import { SkeletonRows } from "@/components/common/skeleton-rows";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { SubTabs } from "@/components/common/sub-tabs";
import { MONEY_TABS } from "@/components/common/tab-groups";

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
  reversal_of_payment_id: number | null;
};

const currency = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD" });

const METHOD_STYLE: Record<string, { label: string; className: string; Icon: LucideIcon }> = {
  cash: { label: "Cash", className: "bg-[var(--success)]/15 text-[var(--success-ink)]", Icon: Banknote },
  credit_card: { label: "Credit Card", className: "bg-[var(--amber-500)]/15 text-[var(--amber-ink)]", Icon: CreditCard },
  debit_card: { label: "Debit Card", className: "bg-[var(--amber-500)]/15 text-[var(--amber-ink)]", Icon: CreditCard },
  phone: { label: "Card / Phone", className: "bg-[var(--amber-500)]/15 text-[var(--amber-ink)]", Icon: CreditCard },
  check: { label: "Check", className: "bg-[var(--forest-600)]/15 text-[var(--forest-600)]", Icon: FileCheck2 },
  tender_card: { label: "Tender Card", className: "bg-[var(--amber-500)]/15 text-[var(--amber-ink)]", Icon: CreditCard },
  house_account: { label: "House Account", className: "bg-black/5 text-[var(--cream-foreground)]/70", Icon: Wallet },
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
  if (method === "credit_card" || method === "debit_card" || method === "phone" || method === "tender_card") return "card";
  return "other";
}

type Period = "today" | "week" | "month" | "all";
const PERIODS: { value: Period; label: string }[] = [
  { value: "today", label: "Today" },
  { value: "week", label: "This Week" },
  { value: "month", label: "This Month" },
  { value: "all", label: "All Time" },
];

/** `dateStr` is a plain YYYY-MM-DD. "Today" is the PLAZA's today — this used to be
 *  the device's, so a tablet left on UTC would show an empty "Today" all evening
 *  while the desk was taking money. ISO dates compare correctly as strings, so none
 *  of this needs to touch a timezone at all. */
function inPeriod(dateStr: string, period: Period): boolean {
  if (period === "all") return true;

  const today = todayISO();
  if (period === "today") return dateStr === today;
  if (period === "month") return dateStr.slice(0, 7) === today.slice(0, 7);

  // This week = Monday through today.
  const mondayOffset = (new Date(`${today}T00:00:00Z`).getUTCDay() + 6) % 7;
  const monday = addDaysISO(today, -mondayOffset);
  return dateStr >= monday && dateStr <= today;
}

export default function PaymentsPage() {
  const [payments, setPayments] = useState<Payment[] | null>(null);
  const [err, setErr] = useState(false);
  const [query, setQuery] = useState("");
  const [period, setPeriod] = useState<Period>("today");
  const [voiding, setVoiding] = useState<Payment | null>(null);
  const [busy, setBusy] = useState(false);

  function load() {
    setErr(false);
    setPayments(null);
    api.get<Payment[]>("/api/payments").then(setPayments).catch(() => setErr(true));
  }
  useEffect(load, []);

  // Ids of payments that have a reversal pointing at them = the voided originals.
  const voidedIds = new Set(
    (payments ?? []).map((p) => p.reversal_of_payment_id).filter((x): x is number => x != null),
  );

  async function confirmVoid() {
    if (!voiding) return;
    setBusy(true);
    try {
      await api.post(`/api/payments/${voiding.id}/void`, {});
      toast.success("Payment voided — a correction was recorded.");
      setVoiding(null);
      load();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't void — try again.");
    } finally {
      setBusy(false);
    }
  }

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
      <SubTabs items={MONEY_TABS} />
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Payments</h1>
          <p className="text-sm text-muted-foreground">
            Reconcile your drawer, card batch, and checks. Every payment is kept forever.
          </p>
        </div>
        {/* Segmented period control */}
        <div className="inline-flex rounded-xl bg-foreground/[0.06] p-1">
          {PERIODS.map((p) => (
            <button
              key={p.value}
              type="button"
              onClick={() => setPeriod(p.value)}
              className={cn(
                // h-11 on phones (the desk taps this in gloves), snapping to the
                // tight desktop rhythm at sm. Unselected labels use the
                // mode-aware muted token, not the cream-fixed ink, so they don't
                // vanish on the dark page in dark mode.
                "flex h-11 items-center rounded-lg px-3.5 text-sm font-medium transition sm:h-8",
                period === p.value
                  ? "btn-embossed bg-[var(--forest-700)] text-[var(--ivory-100)]"
                  : "text-muted-foreground hover:text-foreground",
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
              className="h-11 pl-9 sm:h-9 sm:pl-9"
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

        {err ? (
          <div className="p-6 pt-0">
            <LoadError what="payments" onRetry={load} />
          </div>
        ) : payments === null ? (
          <div className="p-6 pt-0">
            <SkeletonRows n={5} />
          </div>
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
                  <th className="px-5 py-3 text-right font-medium"></th>
                </tr>
              </thead>
              <tbody>
                {(filtered ?? []).map((p) => {
                  const dt = new Date(p.paid_at);
                  const isReversal = p.reversal_of_payment_id != null;
                  const isVoided = voidedIds.has(p.id);
                  return (
                    <tr
                      key={p.id}
                      className={cn(
                        "border-b border-black/5 text-[var(--cream-foreground)] transition-colors last:border-none hover:bg-black/[0.02]",
                        (isVoided || isReversal) && "text-[var(--cream-foreground)]/50",
                      )}
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
                      <td
                        className={cn(
                          "px-5 py-3 text-right font-mono text-base font-bold",
                          isVoided && "line-through",
                          isReversal && "text-[var(--danger-ink)]",
                        )}
                      >
                        {currency(p.amount)}
                      </td>
                      <td className="px-5 py-3">
                        <MethodBadge method={p.method} checkNumber={p.check_number} />
                      </td>
                      <td className="px-5 py-3 font-mono text-xs text-[var(--cream-foreground)]/60">{p.receipt_number ?? "—"}</td>
                      <td className="px-5 py-3 text-right">
                        {isReversal ? (
                          <span className="whitespace-nowrap rounded-full bg-black/5 px-2 py-0.5 text-xs font-semibold text-[var(--cream-foreground)]/60">
                            Reversal
                          </span>
                        ) : isVoided ? (
                          <span className="whitespace-nowrap rounded-full bg-[var(--danger)]/12 px-2 py-0.5 text-xs font-semibold text-[var(--danger-ink)]">
                            Voided
                          </span>
                        ) : p.amount > 0 ? (
                          <Button variant="outline" size="sm" className="min-h-9" onClick={() => setVoiding(p)}>
                            <Ban className="h-3.5 w-3.5" />
                            Void
                          </Button>
                        ) : null}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {voiding && (
        <Dialog open onOpenChange={(o) => !o && setVoiding(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Void this payment?</DialogTitle>
              <DialogDescription>
                Backs {currency(voiding.amount)} out of revenue by recording a matching correction. The original
                stays on the books for the audit trail. Use this only for a payment entered by mistake — not a real
                no-refund cancellation, where the money is earned.
              </DialogDescription>
            </DialogHeader>
            <div className="rounded-xl bg-black/[0.03] p-3">
              <p className="text-sm font-semibold text-[var(--cream-foreground)]">
                {voiding.company_name ?? "—"} · {currency(voiding.amount)}
              </p>
              <p className="font-mono text-xs text-[var(--cream-foreground)]/60">
                {voiding.truck_number ?? "—"} · {voiding.receipt_number ?? "—"}
              </p>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setVoiding(null)}>
                Cancel
              </Button>
              <Button
                className="btn-embossed bg-[var(--danger)] text-white hover:bg-[var(--danger-strong)]"
                disabled={busy}
                onClick={confirmVoid}
              >
                {busy ? "Voiding…" : `Void ${currency(voiding.amount)}`}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}

