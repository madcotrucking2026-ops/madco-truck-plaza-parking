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
import { DAILY_RATE, WEEKLY_RATE, currency, defaultEndDate, daysBetween, monthsBetween } from "@/lib/pricing";

// The cashier/manager records how the renewal was paid at the desk. Card/debit
// go through the plaza's own terminal; the system records the method only.
type PayChoice = "cash" | "credit_card" | "debit_card" | "check";
const PAY_CHOICES: { value: PayChoice; label: string }[] = [
  { value: "cash", label: "Cash" },
  { value: "credit_card", label: "Credit Card" },
  { value: "debit_card", label: "Debit Card" },
  { value: "check", label: "Check" },
];
const METHOD_LABEL: Record<PayChoice, string> = {
  cash: "Cash",
  credit_card: "Credit Card",
  debit_card: "Debit Card",
  check: "Check",
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

  const [endDate, setEndDate] = useState(() => defaultEndDate(pass.pass_type, renewalStart));
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
  const weeklyInvalid = pass.pass_type === "weekly" && days !== 7;

  const finalPrice =
    pass.pass_type === "daily"
      ? DAILY_RATE * Math.max(days, 1)
      : pass.pass_type === "weekly"
        ? (weeklyInvalid ? null : WEEKLY_RATE)
        : monthlyRate != null
          ? monthlyRate * months
          : null;

  async function handleConfirm() {
    if (weeklyInvalid || finalPrice === null) return;
    setSubmitting(true);
    try {
      const payload: RenewPassRequest = {
        end_date: endDate,
        payment_method: payChoice as PaymentMethod,
        check_number: payChoice === "check" ? checkNumber || undefined : undefined,
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
              <Field label="New Expiration Date" labelClassName="text-popover-foreground">
                <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} min={renewalStart} />
                {weeklyInvalid && (
                  <p className="mt-1.5 text-xs text-[var(--danger-ink)]">
                    Weekly passes must be exactly 7 days (currently {days} day{days === 1 ? "" : "s"}).
                  </p>
                )}
              </Field>

              <Field label="Price" labelClassName="text-popover-foreground">
                <div className="flex h-8 items-center rounded-lg border border-input bg-transparent px-2.5 font-mono text-sm">
                  {finalPrice !== null
                    ? `${currency(finalPrice)}${
                        pass.pass_type === "daily"
                          ? ` (${days} day${days === 1 ? "" : "s"} × $${DAILY_RATE})`
                          : pass.pass_type === "monthly" && monthlyRate != null
                            ? ` (${months} month${months === 1 ? "" : "s"} × ${currency(monthlyRate)})`
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
                  : `Confirm & Take Payment${finalPrice !== null ? ` — ${currency(finalPrice)}` : ""}`}
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}

