"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AlertTriangle, CheckCircle2 } from "lucide-react";
import {
  api,
  ApiError,
  type CompanyLookupResult,
  type PassListItem,
  type PaymentMethod,
  type RenewPassRequest,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DAILY_RATE,
  WEEKLY_RATE,
  currency,
  daysBetween,
  defaultEndDate,
  monthsBetween,
} from "@/lib/pricing";

// Bulk renew is a front-desk action: the manager collects payment for a stack of
// trucks at once, recording ONE method for the batch. Card/debit are swiped on
// the plaza's own terminal; the system records the method only.
type PayChoice = "cash" | "credit_card" | "debit_card" | "check" | "tender_card" | "house_account";
const PAY_CHOICES: { value: PayChoice; label: string }[] = [
  { value: "cash", label: "Cash" },
  { value: "credit_card", label: "Credit Card" },
  { value: "debit_card", label: "Debit Card" },
  { value: "check", label: "Check" },
  { value: "tender_card", label: "Tender Card" },
  { value: "house_account", label: "House Account" },
];

const vehicleOf = (p: PassListItem) =>
  p.truck_number ?? p.trailer_number ?? p.license_plate ?? "—";

export function BulkRenewDialog({
  passes,
  onOpenChange,
  onRenewed,
}: {
  passes: PassListItem[];
  onOpenChange: (open: boolean) => void;
  onRenewed: () => void;
}) {
  const [payChoice, setPayChoice] = useState<PayChoice>("cash");
  const [checkNumber, setCheckNumber] = useState("");
  const [rates, setRates] = useState<Record<string, number | null> | null>(null);
  const [busy, setBusy] = useState(false);
  // Renewals run one at a time, so a stack of eight is eight round-trips. Without
  // this the manager stares at "Renewing…" with no idea whether it's working or
  // wedged — and he's holding the customer's cash while he waits.
  const [progress, setProgress] = useState(0);
  const [done, setDone] = useState<{ ok: number; failed: string[] } | null>(null);

  // Each pass renews from where it ended — the old end date is the new start,
  // even for a lapsed pass (client rule, 2026-08). Same rule the backend applies.
  const plan = passes.map((pass) => {
    const start = pass.expiration_date;
    return { pass, start, end: defaultEndDate(pass.pass_type, start) };
  });

  const monthlyCompanies = Array.from(
    new Set(
      plan
        .filter((x) => x.pass.pass_type === "monthly")
        .map((x) => x.pass.company_name)
        .filter((n): n is string => Boolean(n)),
    ),
  );

  // Monthly passes price at each company's negotiated rate, so look those up.
  useEffect(() => {
    if (monthlyCompanies.length === 0) {
      setRates({});
      return;
    }
    Promise.all(
      monthlyCompanies.map((name) =>
        api
          .get<CompanyLookupResult>(`/api/companies/lookup?name=${encodeURIComponent(name)}`)
          .then((r) => [name, r.found ? r.monthly_price : null] as const)
          .catch(() => [name, null] as const),
      ),
    ).then((entries) => setRates(Object.fromEntries(entries)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function priceOf(x: (typeof plan)[number]): number | null {
    const { pass, start, end } = x;
    if (pass.pass_type === "daily") return DAILY_RATE * Math.max(daysBetween(start, end), 1);
    if (pass.pass_type === "weekly") return WEEKLY_RATE;
    const rate = pass.company_name ? (rates?.[pass.company_name] ?? null) : null;
    return rate != null ? rate * monthsBetween(start, end) : null;
  }

  const prices = plan.map(priceOf);
  const stillLoading = rates === null;
  const anyUnknown = !stillLoading && prices.some((p) => p === null);
  const total = prices.reduce<number>((sum, p) => sum + (p ?? 0), 0);

  async function run() {
    setBusy(true);
    setProgress(0);
    let ok = 0;
    const failed: string[] = [];
    // Sequential on purpose: each renewal writes a payment, and a partial
    // failure must be reportable per-truck rather than lost in a race.
    for (const x of plan) {
      const payload: RenewPassRequest = {
        end_date: x.end,
        payment_method: payChoice as PaymentMethod,
        check_number: payChoice === "check" ? checkNumber || undefined : undefined,
      };
      try {
        await api.post(`/api/passes/${x.pass.id}/renew`, payload);
        ok += 1;
      } catch (e) {
        failed.push(
          `${x.pass.company_name ?? "—"} · ${vehicleOf(x.pass)}${e instanceof ApiError ? ` — ${e.message}` : ""}`,
        );
      }
      setProgress((n) => n + 1);
    }
    setBusy(false);
    setDone({ ok, failed });
    onRenewed();
    if (failed.length === 0) toast.success(`${ok} pass${ok === 1 ? "" : "es"} renewed.`);
  }

  return (
    <Dialog open onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Renew {passes.length} passes</DialogTitle>
          <DialogDescription>
            Each pass extends by its own term — daily by a day, weekly by a week, monthly by a month.
          </DialogDescription>
        </DialogHeader>

        {done ? (
          <div className="space-y-4">
            <div className="flex flex-col items-center gap-1.5 rounded-xl bg-[var(--success)]/12 p-4 text-center">
              <CheckCircle2 className="h-10 w-10 text-[var(--success)]" />
              <p className="font-semibold text-[var(--success)]">
                {done.ok} pass{done.ok === 1 ? "" : "es"} renewed
              </p>
            </div>
            {done.failed.length > 0 && (
              <div className="rounded-xl border border-[var(--danger)]/20 bg-[var(--danger)]/[0.06] p-3">
                <p className="mb-1 flex items-center gap-1.5 text-sm font-semibold text-[var(--danger-ink)]">
                  <AlertTriangle className="h-4 w-4" />
                  {done.failed.length} could not be renewed
                </p>
                <ul className="space-y-0.5 text-xs text-[var(--danger-ink)]">
                  {done.failed.map((f, i) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
                <p className="mt-2 text-xs text-muted-foreground">Renew those individually to see why.</p>
              </div>
            )}
            <DialogFooter>
              <Button
                className="btn-embossed bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)]"
                onClick={() => onOpenChange(false)}
              >
                Done
              </Button>
            </DialogFooter>
          </div>
        ) : (
          <>
            <div className="space-y-4">
              <div className="max-h-56 space-y-1.5 overflow-y-auto">
                {plan.map((x, i) => (
                  <div
                    key={x.pass.id}
                    className="flex items-center gap-3 rounded-lg border border-black/5 bg-black/[0.015] px-3 py-2"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium">{x.pass.company_name ?? "—"}</p>
                      <p className="truncate font-mono text-xs text-muted-foreground">
                        {vehicleOf(x.pass)} · {x.pass.pass_type} → {x.end}
                      </p>
                    </div>
                    <span className="shrink-0 whitespace-nowrap font-mono text-sm">
                      {stillLoading ? "…" : prices[i] !== null ? currency(prices[i]!) : "rate?"}
                    </span>
                  </div>
                ))}
              </div>

              <div>
                <Label className="mb-1.5 block">Payment Method</Label>
                <Select value={payChoice} onValueChange={(v) => setPayChoice(v as PayChoice)}>
                  <SelectTrigger className="w-full">
                    <SelectValue>{(v: PayChoice) => PAY_CHOICES.find((p) => p.value === v)?.label ?? v}</SelectValue>
                  </SelectTrigger>
                  <SelectContent>
                    {PAY_CHOICES.map((p) => (
                      <SelectItem key={p.value} value={p.value}>
                        {p.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="mt-1.5 text-xs text-muted-foreground">
                  Card renewals stay one-at-a-time — each customer pays on their own phone.
                </p>
              </div>

              {payChoice === "check" && (
                <div>
                  <Label className="mb-1.5 block">Check Number</Label>
                  <Input value={checkNumber} onChange={(e) => setCheckNumber(e.target.value)} />
                </div>
              )}

              {anyUnknown && (
                <p className="rounded-lg bg-[var(--danger)]/10 p-2 text-xs text-[var(--danger-ink)]">
                  A monthly company here has no rate on file, so part of this total is unknown — the system will
                  price it at the standard monthly rate. Renew that one on its own so you collect the right amount.
                </p>
              )}

              <div className="flex items-baseline justify-between border-t border-black/5 pt-3">
                <span className="text-sm text-muted-foreground">Total to collect</span>
                {/* Never show a precise figure we know is short — the manager would
                    collect this number while the system records a bigger one. */}
                <span className="font-mono text-2xl font-bold tabular-nums">
                  {stillLoading ? "…" : anyUnknown ? `${currency(total)}+` : currency(total)}
                </span>
              </div>

              {busy && (
                <div role="status" aria-live="polite">
                  <p className="mb-1.5 text-xs text-muted-foreground">
                    Renewing {Math.min(progress + 1, plan.length)} of {plan.length}…
                  </p>
                  {/* The bar's width IS the state — not decoration. */}
                  <div className="h-1.5 overflow-hidden rounded-full bg-black/5">
                    <div
                      className="h-full rounded-full bg-[var(--forest-700)] transition-[width] duration-200 ease-out motion-reduce:transition-none"
                      style={{ width: `${(progress / plan.length) * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => onOpenChange(false)} disabled={busy}>
                Cancel
              </Button>
              <Button
                className="btn-embossed bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)]"
                disabled={busy || stillLoading || anyUnknown}
                onClick={run}
              >
                {busy
                  ? `Renewing ${Math.min(progress + 1, plan.length)} of ${plan.length}…`
                  : anyUnknown
                    ? "Rate missing — renew that one separately"
                    : `Confirm & Take Payment — ${currency(total)}`}
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
