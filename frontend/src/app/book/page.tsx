"use client";

import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { Truck, CreditCard, Banknote, ShieldCheck, CheckCircle2, Loader2, Lock } from "lucide-react";
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
import { Field } from "@/components/common/field";
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
import { SETTLE_RETRY_DELAYS_MS, sleep } from "@/lib/settle";

const PASS_TYPES: { value: PassType; label: string; hint: string }[] = [
  { value: "daily", label: "Daily", hint: "$20" },
  { value: "weekly", label: "Weekly", hint: "$100" },
  { value: "monthly", label: "Monthly", hint: "custom" },
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
  // True between "card cleared" and "pass in hand" — the window where the customer
  // has paid but has nothing to show for it yet.
  const [settling, setSettling] = useState(false);
  // Stable per-attempt id forwarded to Stripe as an idempotency key, so a
  // double-click or network retry of the same attempt can never mint two
  // separate PaymentIntents. Regenerated only when a fresh attempt starts
  // (after a cancel or a full reset), never on every render.
  const [checkoutRequestId, setCheckoutRequestId] = useState(() => crypto.randomUUID());
  const [issued, setIssued] = useState<(PassRead & { company_name: string; truck_number?: string }) | null>(null);
  // One record keyed by the query that produced it, rather than two loose flags.
  // A result is only trusted while its `query` still matches what's in the form, so
  // a slow lookup that lands after the driver has typed something else can never be
  // rendered — and clearing the field needs no state reset, which is what used to
  // force a setState in the effect body below.
  const [lookup, setLookup] = useState<{ query: string; result: CompanyLookupResult | null }>({
    query: "",
    result: null,
  });

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
  const companyQuery = form.pass_type === "monthly" ? form.company_name.trim() : "";

  useEffect(() => {
    if (!companyQuery) return;
    const timeout = setTimeout(() => {
      api
        .get<CompanyLookupResult>(`/api/companies/lookup?name=${encodeURIComponent(companyQuery)}`)
        .then((result) =>
          setLookup({ query: companyQuery, result: result.found && result.trucks.length > 0 ? result : null }),
        )
        .catch(() => setLookup({ query: companyQuery, result: null }));
    }, 400);
    return () => clearTimeout(timeout);
  }, [companyQuery]);

  // Derived, so an answer for a company the driver has since re-typed is simply
  // not "done" any more — no reset needed, no stale roster on screen.
  const companyLookupDone = companyQuery !== "" && lookup.query === companyQuery;
  const companyMatch = companyLookupDone ? lookup.result : null;
  const monthlyNotSetUp = companyLookupDone && !companyMatch;
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
    const payload: FinalizeStripePaymentRequest = { payment_intent_id: intentId };
    setSettling(true);

    // The charge already succeeded — that's what triggered this callback. One
    // failed request here used to send a paying customer to the front desk; now we
    // keep trying, because /finalize is idempotent and because Stripe's webhook is
    // finalizing the same charge server-side in parallel. If the webhook wins, this
    // call returns the very pass it created.
    for (let attempt = 0; ; attempt++) {
      try {
        const pass = await api.post<PassRead>("/api/payments/stripe/finalize", payload);
        // Silent success: the PassTicket that replaces the form already shows the
        // receipt number, so a celebratory toast would just repeat what's on screen.
        setIssued({ ...pass, company_name: form.company_name, truck_number: form.truck_number });
        setCheckoutStep("form");
        setClientSecret(null);
        setPaymentIntentId(null);
        setSettling(false);
        return;
      } catch (err) {
        if (attempt >= SETTLE_RETRY_DELAYS_MS.length) {
          // Out of patience. Keep the payment screen as-is rather than bouncing
          // back to a blank form, so nobody is tempted to pay a second time.
          setSettling(false);
          toast.error(
            err instanceof ApiError
              ? `Your card was charged, but we couldn't finish your pass (${err.message}). Please see the front desk — do NOT pay again.`
              : "Your card was charged, but we couldn't finish your pass. Please see the front desk — do NOT pay again.",
            { duration: 30000 },
          );
          return;
        }
        await sleep(SETTLE_RETRY_DELAYS_MS[attempt]);
      }
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

  const selectedPassLabel = PASS_TYPES.find((p) => p.value === form.pass_type)?.label;

  return (
    <div className="min-h-screen bg-background px-4 py-8">
      <header className="mx-auto mb-6 flex max-w-md items-center gap-3">
        <div className="btn-embossed flex h-11 w-11 items-center justify-center rounded-xl bg-[var(--amber-500)] text-[var(--forest-950)]">
          <Truck className="h-5 w-5" strokeWidth={2.5} />
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate font-semibold leading-tight tracking-tight text-foreground">Madco Truck Plaza</p>
          <p className="text-xs text-muted-foreground">Parking Payment</p>
        </div>
        <span className="flex items-center gap-1 whitespace-nowrap rounded-full bg-[var(--forest-700)]/10 px-2.5 py-1 text-[11px] font-medium text-[var(--forest-700)] dark:text-[var(--ivory-100)]">
          <ShieldCheck className="h-3.5 w-3.5" />
          Secure
        </span>
      </header>

      {issued ? (
        <div className="animate-rise mx-auto max-w-md space-y-4">
          <div className="flex flex-col items-center gap-2 pb-1 text-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[var(--success)]/12 text-[var(--success)]">
              <CheckCircle2 className="h-8 w-8" strokeWidth={2} />
            </div>
            <p className="text-lg font-semibold text-foreground">You&rsquo;re all set</p>
            <p className="text-sm text-muted-foreground">Keep this pass handy — show it if an attendant asks.</p>
          </div>
          <PassTicket pass={issued} />
          <Button
            className="btn-embossed w-full bg-[var(--amber-500)] py-6 text-base font-semibold text-[var(--forest-950)] hover:bg-[var(--amber-600)]"
            onClick={reset}
          >
            Pay for Another Truck
          </Button>
        </div>
      ) : checkoutStep === "card-payment" && clientSecret ? (
        <div className="animate-rise card-paper mx-auto max-w-md space-y-4 rounded-2xl p-6">
          <div className="flex items-start justify-between gap-3 border-b border-black/5 pb-4">
            <div className="min-w-0">
              <p className="truncate font-semibold text-[var(--cream-foreground)]">
                {form.truck_number} — {form.company_name}
              </p>
              <p className="text-sm text-[var(--cream-foreground)]/60">
                {selectedPassLabel} · {form.start_date} → {form.end_date}
              </p>
            </div>
            {finalPrice !== null && (
              <span className="whitespace-nowrap font-mono text-lg font-bold tabular-nums text-[var(--cream-foreground)]">
                {currency(finalPrice)}
              </span>
            )}
          </div>
          {settling ? (
            /* Charged, but the pass isn't confirmed yet. Hide the card form —
               the customer has already paid, and the one mistake this screen must
               never invite is paying twice. */
            <div className="flex flex-col items-center gap-3 py-6 text-center">
              <Loader2 className="h-9 w-9 animate-spin text-[var(--forest-700)]" strokeWidth={2} />
              <p className="text-lg font-bold text-[var(--cream-foreground)]">Payment received</p>
              <p className="text-sm text-[var(--cream-foreground)]/60">
                Issuing your pass — one moment. Please don&rsquo;t close this page.
              </p>
            </div>
          ) : (
            <CardCheckout
              clientSecret={clientSecret}
              amount={finalPrice ?? 0}
              onSuccess={handleCardSuccess}
              onCancel={cancelCardCheckout}
            />
          )}
        </div>
      ) : (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (payWay === "card") startCardCheckout();
          }}
          className="animate-rise card-paper mx-auto max-w-md space-y-5 rounded-2xl p-6"
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
            <Input value={form.company_name} onChange={(e) => set("company_name", e.target.value)} placeholder="Bell City Freight" />
          </Field>

          <Field label="Phone Number" required>
            <Input value={form.phone} onChange={(e) => set("phone", e.target.value)} placeholder="313-555-0100" />
          </Field>

          <Field label="Parking Type">
            <div role="group" aria-label="Parking type" className="grid grid-cols-3 gap-2">
              {PASS_TYPES.map((p) => (
                <button
                  key={p.value}
                  type="button"
                  aria-pressed={form.pass_type === p.value}
                  data-selected={form.pass_type === p.value}
                  onClick={() => setPassType(p.value)}
                  className="tile-option flex flex-col items-center gap-0.5 px-2 py-3 text-center"
                >
                  <span className="text-sm font-semibold text-[var(--cream-foreground)]">{p.label}</span>
                  <span className="font-mono text-[11px] tabular-nums text-[var(--cream-foreground)]/60">{p.hint}</span>
                </button>
              ))}
            </div>
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
            <p className="rounded-lg bg-[var(--danger)]/10 p-3 text-xs text-[var(--danger-ink)]">
              Weekly passes must be exactly 7 days (currently {days} day{days === 1 ? "" : "s"}). Choose Daily for a custom range.
            </p>
          )}
          {form.pass_type === "monthly" && !monthlyNotSetUp && (
            <p className="text-xs text-[var(--cream-foreground)]/50">
              Paying for more than one month? Push the end date out further — the price scales automatically.
            </p>
          )}

          {monthlyNotSetUp && (
            <p className="rounded-lg bg-[var(--danger)]/10 p-3 text-xs text-[var(--danger-ink)]">
              {`${form.company_name} isn't set up for monthly parking yet. Please see the front desk to get started.`}
            </p>
          )}

          <Field label="How would you like to pay?">
            <div role="group" aria-label="Payment method" className="grid grid-cols-2 gap-3">
              <button
                type="button"
                aria-pressed={payWay === "card"}
                data-selected={payWay === "card"}
                disabled={!stripeConfigured() || startingCheckout}
                onClick={() => setPayWay("card")}
                className="tile-option flex flex-col items-center gap-1.5 px-2 py-3 text-sm font-medium text-[var(--cream-foreground)] disabled:cursor-not-allowed disabled:opacity-40"
              >
                <CreditCard className="h-5 w-5" />
                Card
              </button>
              <button
                type="button"
                aria-pressed={payWay === "cash_check"}
                data-selected={payWay === "cash_check"}
                disabled={startingCheckout}
                onClick={() => setPayWay("cash_check")}
                className="tile-option flex flex-col items-center gap-1.5 px-2 py-3 text-sm font-medium text-[var(--cream-foreground)] disabled:cursor-not-allowed disabled:opacity-40"
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

          {/* Total — the money made unmistakable, mono + tabular, receipt-style. */}
          {finalPrice !== null && (
            <div className="flex items-baseline justify-between border-t border-black/5 pt-4">
              <span className="text-sm text-[var(--cream-foreground)]/70">
                Total{form.pass_type === "daily" && days > 1 ? ` · ${days} days` : ""}
              </span>
              <span className="font-mono text-2xl font-bold tabular-nums text-[var(--cream-foreground)]">
                {currency(finalPrice)}
              </span>
            </div>
          )}

          {payWay === "cash_check" ? (
            <p className="rounded-lg bg-[var(--forest-700)]/8 p-3 text-sm text-foreground">
              Please come inside — our team will help you pay by cash or check and get your pass started.
            </p>
          ) : (
            <Button
              type="submit"
              disabled={startingCheckout || monthlyNotSetUp || weeklyInvalid}
              className="btn-embossed w-full whitespace-nowrap bg-[var(--amber-500)] py-6 text-base font-semibold text-[var(--forest-950)] hover:bg-[var(--amber-600)] disabled:opacity-50"
            >
              {startingCheckout ? "Loading…" : "Continue to Payment"}
            </Button>
          )}
          {payWay === "card" && stripeConfigured() && (
            <p className="flex items-center justify-center gap-1.5 text-center text-xs text-muted-foreground">
              <Lock className="h-3 w-3" />
              Secured by Stripe · First come, first served · No refunds
            </p>
          )}
          {payWay === "cash_check" && (
            <p className="text-center text-xs text-muted-foreground">
              First come, first served. No reservations, no refunds.
            </p>
          )}
        </form>
      )}
    </div>
  );
}

