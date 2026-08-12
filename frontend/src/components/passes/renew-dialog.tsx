"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { CheckCircle2 } from "lucide-react";
import {
  api,
  ApiError,
  type CompanyLookupResult,
  type PassListItem,
  type PassRead,
  type PaymentMethod,
  type RenewPassRequest,
} from "@/lib/api";
import { PassTicket } from "@/components/passes/pass-ticket";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field } from "@/components/common/field";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogDescription,
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
  addDaysISO,
  catchUpEnd,
  closeOutPrice,
  currency,
  daysBetween,
  monthsBetween,
  todayISO,
} from "@/lib/pricing";

// The cashier/manager records how the renewal was paid at the desk. Card/debit
// go through the plaza's own terminal; the system records the method only.
type PayChoice = "cash" | "credit_card" | "debit_card" | "check" | "tender_card" | "house_account";
const PAY_CHOICES: { value: PayChoice; label: string }[] = [
  { value: "cash", label: "Cash" },
  { value: "credit_card", label: "Credit Card" },
  { value: "debit_card", label: "Debit Card" },
  { value: "check", label: "Check" },
  { value: "tender_card", label: "Tender Card" },
  { value: "house_account", label: "House Account" },
];
const METHOD_LABEL: Record<PayChoice, string> = {
  cash: "Cash",
  credit_card: "Credit Card",
  debit_card: "Debit Card",
  check: "Check",
  tender_card: "Tender Card",
  house_account: "House Account",
};

export function RenewDialog({
  pass,
  onOpenChange,
  onRenewed,
}: {
  pass: PassListItem;
  onOpenChange: (open: boolean) => void;
  onRenewed: () => void;
}) {
  // A renewal always continues from where the last pass ended — the old end date
  // is the new start, even when the customer pays late (client rule, 2026-08).
  const renewalStart = pass.expiration_date;
  const today = todayISO();

  // Two ways to renew a (possibly lapsed) customer:
  //  • continue — keep the plan going: pre-fill enough whole periods to reach
  //    past today (a few days late -> 1 period; weeks late -> a catch-up).
  //  • close out — they're leaving: pre-fill today as the leave date and bill
  //    only the time actually used.
  const [mode, setMode] = useState<"continue" | "close_out">("continue");
  const [endDate, setEndDate] = useState(() => catchUpEnd(pass.pass_type, renewalStart, today));

  function switchMode(next: "continue" | "close_out") {
    setMode(next);
    setEndDate(
      next === "close_out"
        ? today > renewalStart
          ? today
          : addDaysISO(renewalStart, 1)
        : catchUpEnd(pass.pass_type, renewalStart, today),
    );
  }
  const [payChoice, setPayChoice] = useState<PayChoice>("cash");
  const [checkNumber, setCheckNumber] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [monthlyRate, setMonthlyRate] = useState<number | null>(null);
  const [rateLookupDone, setRateLookupDone] = useState(pass.pass_type !== "monthly");
  // When set, the renewal is DONE and we show a solid receipt/confirmation
  // (not just a toast) so the manager has proof it was recorded.
  const [confirmed, setConfirmed] = useState<
    (PassRead & { company_name: string; truck_number?: string; methodLabel: string }) | null
  >(null);

  const vehicleId = pass.truck_number ?? pass.trailer_number ?? pass.license_plate ?? undefined;

  useEffect(() => {
    if (pass.pass_type !== "monthly" || !pass.company_name) return;
    api
      .get<CompanyLookupResult>(`/api/companies/lookup?name=${encodeURIComponent(pass.company_name)}`)
      .then((result) => setMonthlyRate(result.found ? result.monthly_price : null))
      .catch(() => setMonthlyRate(null))
      .finally(() => setRateLookupDone(true));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const days = daysBetween(renewalStart, endDate);
  const months = monthsBetween(renewalStart, endDate);
  const weeks = Math.max(Math.floor(days / 7), 1);
  // The pass carries its OWN rate (price ÷ its term). Use it as the fallback for
  // the monthly rate so a renewal is never blocked when the company-rate lookup
  // returns nothing — the backend prices it the same way on confirm.
  const derivedMonthlyRate =
    pass.pass_type === "monthly"
      ? Number(pass.price) / Math.max(monthsBetween(pass.issue_date, pass.expiration_date), 1)
      : null;
  const rate = monthlyRate ?? derivedMonthlyRate;
  // Whole-weeks requirement only applies to a continuing weekly; a close-out can
  // land on any number of days.
  const weeklyInvalid = mode === "continue" && pass.pass_type === "weekly" && (days <= 0 || days % 7 !== 0);

  const finalPrice =
    mode === "close_out"
      ? closeOutPrice(pass.pass_type, renewalStart, endDate, {
          daily: DAILY_RATE,
          weekly: WEEKLY_RATE,
          monthly: rate,
        })
      : pass.pass_type === "daily"
        ? DAILY_RATE * Math.max(days, 1)
        : pass.pass_type === "weekly"
          ? weeklyInvalid
            ? null
            : WEEKLY_RATE * weeks
          : rate != null
            ? rate * months
            : null;

  async function handleConfirm() {
    if (weeklyInvalid || finalPrice === null) return;
    setSubmitting(true);
    try {
      const payload: RenewPassRequest = {
        end_date: endDate,
        payment_method: payChoice as PaymentMethod,
        check_number: payChoice === "check" ? checkNumber || undefined : undefined,
        mode,
      };
      const res = await api.post<PassRead>(`/api/passes/${pass.id}/renew`, payload);
      onRenewed(); // refresh the list behind the dialog immediately
      // Show a real confirmation receipt, not just a toast — proof the
      // front-desk payment was recorded.
      setConfirmed({
        ...res,
        company_name: pass.company_name ?? "—",
        truck_number: vehicleId,
        methodLabel: payChoice === "check" ? `Check${checkNumber ? ` #${checkNumber}` : ""}` : METHOD_LABEL[payChoice],
      });
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to renew pass.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Dialog open onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Renew Pass</DialogTitle>
          <DialogDescription>
            {pass.company_name ?? "—"} · truck {pass.truck_number ?? pass.trailer_number ?? pass.license_plate ?? "—"}
          </DialogDescription>
        </DialogHeader>

        {confirmed ? (
          <div className="space-y-4">
            <div className="flex flex-col items-center gap-1.5 rounded-xl bg-[var(--success)]/12 p-4 text-center">
              <CheckCircle2 className="h-10 w-10 text-[var(--success)]" />
              <p className="font-semibold text-[var(--success)]">Renewed &amp; Paid — {confirmed.methodLabel}</p>
              <p className="text-xs text-muted-foreground">
                Now expires {confirmed.expiration_date} · {currency(confirmed.price)} recorded
              </p>
            </div>
            <PassTicket pass={confirmed} />
            <DialogFooter>
              <Button variant="outline" onClick={() => window.print()}>
                Print
              </Button>
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
              {/* Continue vs close out — the cashier picks what the driver is
                  doing; the date + price pre-fill for each. */}
              <div className="inline-flex w-full rounded-xl bg-black/[0.06] p-1">
                {(["continue", "close_out"] as const).map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => switchMode(m)}
                    className={`flex-1 rounded-lg px-3 py-2 text-sm font-medium transition ${
                      mode === m
                        ? "btn-embossed bg-[var(--forest-700)] text-[var(--ivory-100)]"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {m === "continue" ? "Renew — continuing" : "Close out — leaving"}
                  </button>
                ))}
              </div>

              <Field
                label={mode === "close_out" ? "Leaving Date" : "New Expiration Date"}
                labelClassName="text-popover-foreground"
              >
                <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} min={renewalStart} />
                {weeklyInvalid && (
                  <p className="mt-1.5 text-xs text-[var(--danger-ink)]">
                    Weekly renewals must be whole weeks (currently {days} day{days === 1 ? "" : "s"}).
                  </p>
                )}
                <p className="mt-1.5 text-xs text-muted-foreground">
                  {mode === "close_out"
                    ? `Bills from ${renewalStart} — time used, then the account closes.`
                    : `Continues from ${renewalStart}.`}
                </p>
              </Field>

              <Field label="Price" labelClassName="text-popover-foreground">
                <div className="flex h-11 items-center rounded-lg border border-input bg-transparent px-2.5 font-mono text-sm sm:h-8">
                  {finalPrice !== null
                    ? `${currency(finalPrice)}${
                        mode === "close_out"
                          ? " · time used"
                          : pass.pass_type === "daily"
                            ? ` (${days} day${days === 1 ? "" : "s"} × $${DAILY_RATE})`
                            : pass.pass_type === "weekly"
                              ? ` (${weeks} week${weeks === 1 ? "" : "s"} × $${WEEKLY_RATE})`
                              : pass.pass_type === "monthly" && rate != null
                                ? ` (${months} month${months === 1 ? "" : "s"} × ${currency(rate)})`
                                : ""
                      }`
                    : rateLookupDone
                      ? "—"
                      : "Looking up rate…"}
                </div>
              </Field>

              <Field label="Payment Method" labelClassName="text-popover-foreground">
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
              </Field>
              {payChoice === "check" && (
                <Field label="Check Number" labelClassName="text-popover-foreground">
                  <Input value={checkNumber} onChange={(e) => setCheckNumber(e.target.value)} />
                </Field>
              )}
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button
                className="btn-embossed bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)]"
                disabled={submitting || weeklyInvalid || finalPrice === null}
                onClick={handleConfirm}
              >
                {submitting
                  ? "Working…"
                  : `${mode === "close_out" ? "Close Out" : "Confirm"} & Take Payment${finalPrice !== null ? ` — ${currency(finalPrice)}` : ""}`}
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}

