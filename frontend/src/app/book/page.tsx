"use client";

import { isValidElement, cloneElement, useEffect, useId, useRef, useState } from "react";
import { toast } from "sonner";
import { Truck, CreditCard, Banknote } from "lucide-react";
import {
  api,
  ApiError,
  type CompanyLookupResult,
  type CreateIntentRequest,
  type CreateIntentResponse,
  type FinalizeStripePaymentRequest,
  type PassRead,
  type PassType,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PassTicket } from "@/components/passes/pass-ticket";
import { CardCheckout } from "@/components/checkout/card-checkout";
import { stripeConfigured } from "@/lib/stripe";
import { DAILY_RATE, WEEKLY_RATE, todayISO, currency, defaultEndDate, daysBetween, monthsBetween } from "@/lib/pricing";
import { cn } from "@/lib/utils";

const PASS_TYPES: { value: PassType; label: string; hint: string }[] = [
  { value: "daily", label: "Daily", hint: "$20" },
  { value: "weekly", label: "Weekly", hint: "$100" },
  { value: "monthly", label: "Monthly", hint: "custom rate" },
];

type PayWay = "card" | "cash_check";

export default function BookPage() {
  const [form, setForm] = useState(() => {
    const startDate = todayISO();
    return {
      company_name: "",
      truck_number: "",
      phone: "",
      pass_type: "daily" as PassType,
      start_date: startDate,
      end_date: defaultEndDate("daily", startDate),
    };
  });
  const [payWay, setPayWay] = useState<PayWay>(stripeConfigured() ? "card" : "cash_check");
  const payWayRef = useRef(payWay);
  useEffect(() => {
    payWayRef.current = payWay;
  }, [payWay]);
  const [checkoutStep, setCheckoutStep] = useState<"form" | "card-payment">("form");
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [paymentIntentId, setPaymentIntentId] = useState<string | null>(null);
  const [startingCheckout, setStartingCheckout] = useState(false);
  // Stable per-attempt id forwarded to Stripe as an idempotency key, so a
  // double-click or network retry of the same attempt can never mint two
  // separate PaymentIntents. Regenerated only when a fresh attempt starts
  // (after a cancel or a full reset), never on every render.
  const [checkoutRequestId, setCheckoutRequestId] = useState(() => crypto.randomUUID());
  const [issued, setIssued] = useState<(PassRead & { company_name: string; truck_number?: string }) | null>(null);
  const [companyMatch, setCompanyMatch] = useState<CompanyLookupResult | null>(null);
  const [companyLookupDone, setCompanyLookupDone] = useState(false);

  const set = <K extends keyof typeof form>(key: K, value: (typeof form)[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  function setPassType(passType: PassType) {
    setForm((f) => ({ ...f, pass_type: passType, truck_number: "", end_date: defaultEndDate(passType, f.start_date) }));
  }

  function setStartDate(startDate: string) {
    setForm((f) => ({ ...f, start_date: startDate, end_date: defaultEndDate(f.pass_type, startDate) }));
  }

  // Monthly is self-service only for companies the manager has already set
  // up with a custom rate — the truck picks from that established roster.
  useEffect(() => {
    if (form.pass_type !== "monthly" || !form.company_name.trim()) {
      setCompanyMatch(null);
      setCompanyLookupDone(false);
      return;
    }
    setCompanyLookupDone(false);
    const timeout = setTimeout(() => {
      api
        .get<CompanyLookupResult>(`/api/companies/lookup?name=${encodeURIComponent(form.company_name.trim())}`)
        .then((result) => {
          setCompanyMatch(result.found && result.trucks.length > 0 ? result : null);
          setCompanyLookupDone(true);
        })
        .catch(() => {
          setCompanyMatch(null);
          setCompanyLookupDone(true);
        });
    }, 400);
    return () => clearTimeout(timeout);
  }, [form.company_name, form.pass_type]);

  const monthlyNotSetUp = form.pass_type === "monthly" && companyLookupDone && !companyMatch;
  const days = daysBetween(form.start_date, form.end_date);
  const months = monthsBetween(form.start_date, form.end_date);
  const weeklyInvalid = form.pass_type === "weekly" && days !== 7;
  const finalPrice =
    form.pass_type === "daily"
      ? DAILY_RATE * Math.max(days, 1)
      : form.pass_type === "weekly"
        ? (weeklyInvalid ? null : WEEKLY_RATE)
        : companyMatch?.monthly_price != null
          ? companyMatch.monthly_price * months
          : null;

  function validateForm(): string | null {
    if (!form.company_name || !form.phone || !form.truck_number) {
      return "Truck number, company name, and phone are required.";
    }
    if (monthlyNotSetUp) {
      return `${form.company_name} isn't set up for monthly parking yet — please see the front desk.`;
    }
    if (weeklyInvalid) {
      return `Weekly passes must be exactly 7 days (${form.start_date} → ${form.end_date} is ${days} day${days === 1 ? "" : "s"}). Choose Daily for a custom range.`;
    }
    if (finalPrice === null) {
      return "Could not determine a price for this pass.";
    }
    return null;
  }

  async function startCardCheckout() {
    const error = validateForm();
    if (error) {
      toast.error(error);
      return;
    }
    setStartingCheckout(true);
    try {
      const payload: CreateIntentRequest = {
        client_request_id: checkoutRequestId,
        company_name: form.company_name,
        truck_number: form.truck_number,
        phone: form.phone,
        vehicle_type: "truck",
        pass_type: form.pass_type,
        issue_date: form.start_date,
        end_date: form.end_date || undefined,
      };
      const res = await api.post<CreateIntentResponse>("/api/payments/stripe/create-intent", payload);
      // The customer may have switched to Cash/Check while this was in
      // flight — don't yank them onto a card form they no longer want.
      if (payWayRef.current !== "card") {
        api.post("/api/payments/stripe/cancel-intent", { payment_intent_id: res.payment_intent_id }).catch(() => {});
        return;
      }
      setClientSecret(res.client_secret);
      setPaymentIntentId(res.payment_intent_id);
      setCheckoutStep("card-payment");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Could not start checkout. Please try again.");
    } finally {
      setStartingCheckout(false);
    }
  }

  async function handleCardSuccess(intentId: string) {
    try {
      const payload: FinalizeStripePaymentRequest = { payment_intent_id: intentId };
      const pass = await api.post<PassRead>("/api/payments/stripe/finalize", payload);
      setIssued({ ...pass, company_name: form.company_name, truck_number: form.truck_number });
      toast.success(`Paid — receipt ${pass.receipt_number}`);
      setCheckoutStep("form");
      setClientSecret(null);
      setPaymentIntentId(null);
    } catch (err) {
      // The charge already succeeded (that's what triggered this callback) —
      // keep the payment screen exactly as-is rather than bouncing back to a
      // blank form, so the customer isn't tempted to pay a second time.
      toast.error(
        err instanceof ApiError
          ? `Your card was charged, but we couldn't finish your pass (${err.message}). Please see the front desk.`
          : "Your card was charged, but we couldn't finish your pass. Please see the front desk.",
      );
    }
  }

  async function cancelCardCheckout() {
    const intentId = paymentIntentId;
    if (intentId) {
      try {
        await api.post("/api/payments/stripe/cancel-intent", { payment_intent_id: intentId });
      } catch {
        toast.error("Couldn't cancel that payment attempt — please see the front desk before trying again.");
      }
    }
    setCheckoutStep("form");
    setClientSecret(null);
    setPaymentIntentId(null);
    setCheckoutRequestId(crypto.randomUUID());
  }

  function reset() {
    setIssued(null);
    setCheckoutStep("form");
    setClientSecret(null);
    setPaymentIntentId(null);
    setCheckoutRequestId(crypto.randomUUID());
    const startDate = todayISO();
    setForm({
      company_name: "",
      truck_number: "",
      phone: "",
      pass_type: "daily",
      start_date: startDate,
      end_date: defaultEndDate("daily", startDate),
    });
    setPayWay(stripeConfigured() ? "card" : "cash_check");
  }

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <div className="mx-auto flex max-w-md items-center gap-3 pb-6">
        <div className="btn-embossed flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--amber-500)] text-[var(--forest-950)]">
          <Truck className="h-5 w-5" strokeWidth={2.5} />
        </div>
        <div>
          <p className="font-semibold tracking-tight text-foreground">Madco Truck Plaza</p>
          <p className="text-xs text-muted-foreground">Parking Payment</p>
        </div>
      </div>

      {issued ? (
        <div className="mx-auto max-w-md space-y-4">
          <PassTicket pass={issued} />
          <Button
            className="btn-embossed w-full bg-[var(--amber-500)] py-6 text-base font-semibold text-[var(--forest-950)] hover:bg-[var(--amber-600)]"
            onClick={reset}
          >
            Pay for Another Truck
          </Button>
        </div>
      ) : checkoutStep === "card-payment" && clientSecret ? (
        <div className="card-paper mx-auto max-w-md space-y-4 rounded-2xl p-6">
          <div className="rounded-lg bg-[var(--forest-700)]/8 p-3 text-sm">
            <p className="font-semibold text-foreground">
              {form.truck_number} — {form.company_name}
            </p>
            <p className="text-muted-foreground">
              {PASS_TYPES.find((p) => p.value === form.pass_type)?.label} · {form.start_date} → {form.end_date}
            </p>
          </div>
          <CardCheckout
            clientSecret={clientSecret}
            amount={finalPrice ?? 0}
            onSuccess={handleCardSuccess}
            onCancel={cancelCardCheckout}
          />
        </div>
      ) : (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (payWay === "card") startCardCheckout();
          }}
          className="card-paper mx-auto max-w-md space-y-5 rounded-2xl p-6"
        >
          <Field label="Truck Number" required>
            {form.pass_type === "monthly" && companyMatch ? (
              <Select value={form.truck_number} onValueChange={(v) => set("truck_number", v ?? "")}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select your truck" />
                </SelectTrigger>
                <SelectContent>
                  {companyMatch.trucks
                    .filter((t) => t.truck_number)
                    .map((t) => (
                      <SelectItem key={t.truck_number} value={t.truck_number as string}>
                        {t.truck_number}
                        {companyMatch.monthly_price != null ? ` — ${currency(companyMatch.monthly_price)}/mo` : ""}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            ) : (
              <Input value={form.truck_number} onChange={(e) => set("truck_number", e.target.value)} placeholder="TX-12345" />
            )}
          </Field>

          <Field label="Company Name" required>
            <Input value={form.company_name} onChange={(e) => set("company_name", e.target.value)} placeholder="Acme Trucking" />
          </Field>

          <Field label="Phone Number" required>
            <Input value={form.phone} onChange={(e) => set("phone", e.target.value)} placeholder="313-555-0100" />
          </Field>

          <Field label="Parking Type">
            <Select value={form.pass_type} onValueChange={(v) => setPassType(v as PassType)}>
              <SelectTrigger className="w-full">
                <SelectValue>{(v: PassType) => PASS_TYPES.find((p) => p.value === v)?.label ?? v}</SelectValue>
              </SelectTrigger>
              <SelectContent>
                {PASS_TYPES.map((p) => (
                  <SelectItem key={p.value} value={p.value}>{p.label} ({p.hint})</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>

          <div className="grid grid-cols-2 gap-3">
            <Field label="Start Date">
              <Input type="date" value={form.start_date} onChange={(e) => setStartDate(e.target.value)} />
            </Field>
            <Field label="End Date">
              <Input type="date" value={form.end_date} onChange={(e) => set("end_date", e.target.value)} />
            </Field>
          </div>
          {weeklyInvalid && (
            <p className="rounded-lg bg-[var(--danger)]/10 p-3 text-xs text-[var(--danger)]">
              Weekly passes must be exactly 7 days (currently {days} day{days === 1 ? "" : "s"}). Choose Daily for a custom range.
            </p>
          )}
          {form.pass_type === "monthly" && !monthlyNotSetUp && (
            <p className="text-xs text-[var(--cream-foreground)]/50">
              Paying for more than one month? Push the end date out further — the price scales automatically.
            </p>
          )}

          {monthlyNotSetUp && (
            <p className="rounded-lg bg-[var(--danger)]/10 p-3 text-xs text-[var(--danger)]">
              {`${form.company_name} isn't set up for monthly parking yet. Please see the front desk to get started.`}
            </p>
          )}

          <Field label="How would you like to pay?">
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                disabled={!stripeConfigured() || startingCheckout}
                onClick={() => setPayWay("card")}
                className={cn(
                  "flex flex-col items-center gap-1.5 rounded-xl border-2 p-3 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-40",
                  payWay === "card" ? "border-[var(--amber-500)] bg-[var(--amber-500)]/10" : "border-input",
                )}
              >
                <CreditCard className="h-5 w-5" />
                Card
              </button>
              <button
                type="button"
                disabled={startingCheckout}
                onClick={() => setPayWay("cash_check")}
                className={cn(
                  "flex flex-col items-center gap-1.5 rounded-xl border-2 p-3 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-40",
                  payWay === "cash_check" ? "border-[var(--amber-500)] bg-[var(--amber-500)]/10" : "border-input",
                )}
              >
                <Banknote className="h-5 w-5" />
                Cash / Check
              </button>
            </div>
            {!stripeConfigured() && (
              <p className="mt-1.5 text-xs text-muted-foreground">
                Card payments are being set up — for now, please pay cash or check inside.
              </p>
            )}
          </Field>

          {payWay === "cash_check" ? (
            <p className="rounded-lg bg-[var(--forest-700)]/8 p-3 text-sm text-foreground">
              Please come inside — our team will help you pay by cash or check and get your pass started.
            </p>
          ) : (
            <Button
              type="submit"
              disabled={startingCheckout || monthlyNotSetUp || weeklyInvalid}
              className="btn-embossed w-full bg-[var(--amber-500)] py-6 text-base font-semibold text-[var(--forest-950)] hover:bg-[var(--amber-600)] disabled:opacity-50"
            >
              {startingCheckout ? "Loading…" : `Continue to Payment${finalPrice !== null ? ` — ${currency(finalPrice)}` : ""}`}
            </Button>
          )}
          <p className="text-center text-xs text-muted-foreground">
            First come, first served. No reservations, no refunds.
          </p>
        </form>
      )}
    </div>
  );
}

function Field({
  label,
  required,
  children,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  const id = useId();
  const control = isValidElement<{ id?: string }>(children) ? cloneElement(children, { id }) : children;

  return (
    <div>
      <Label htmlFor={id} className="mb-1.5 block text-[var(--cream-foreground)]/80">
        {label}
        {required && <span className="text-[var(--amber-600)]"> *</span>}
      </Label>
      {control}
    </div>
  );
}
