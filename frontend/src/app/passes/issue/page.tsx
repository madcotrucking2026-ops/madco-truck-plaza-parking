"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { api, ApiError, type CompanyLookupResult, type IssuePassRequest, type PassRead, type PassType, type VehicleType, type PaymentMethod, type PaymentRequestCreated } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field } from "@/components/common/field";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { PassTicket } from "@/components/passes/pass-ticket";
import { PaymentRequestQR } from "@/components/checkout/payment-request-qr";
import { stripeConfigured } from "@/lib/stripe";
import { DAILY_RATE, WEEKLY_RATE, todayISO, currency, defaultEndDate, daysBetween, monthsBetween } from "@/lib/pricing";

const VEHICLE_TYPES: VehicleType[] = ["truck", "trailer", "bobtail", "flatbed", "car", "other"];

const IDENTIFIER_FIELD: Record<VehicleType, { key: "truck_number" | "trailer_number" | "license_plate"; label: string }> = {
  truck: { key: "truck_number", label: "Truck Number" },
  bobtail: { key: "truck_number", label: "Truck Number" },
  flatbed: { key: "truck_number", label: "Truck Number" },
  trailer: { key: "trailer_number", label: "Trailer Number" },
  car: { key: "license_plate", label: "License Plate" },
  other: { key: "license_plate", label: "License Plate" },
};

const PASS_TYPES: { value: PassType; label: string; hint: string }[] = [
  { value: "daily", label: "Daily", hint: "$20/day" },
  { value: "weekly", label: "Weekly", hint: "$100 flat" },
  { value: "monthly", label: "Monthly", hint: "custom per company" },
];
// "card_link" is not a real PaymentMethod — it hands the customer a QR/link to
// self-pay by card instead of recording a payment at the desk.
type PayChoice = "cash" | "check" | "card_link";
const PAY_CHOICES: { value: PayChoice; label: string }[] = [
  { value: "cash", label: "Cash (at the desk)" },
  { value: "check", label: "Check (at the desk)" },
  { value: "card_link", label: "Card — customer pays by phone" },
];

export default function IssuePassPage() {
  return (
    <Suspense fallback={null}>
      <IssuePassForm />
    </Suspense>
  );
}

function IssuePassForm() {
  const searchParams = useSearchParams();
  const initialPassType: PassType = searchParams.get("type") === "monthly" ? "monthly" : "daily";

  const [form, setForm] = useState(() => {
    const startDate = todayISO();
    return {
      vehicle_type: "truck" as VehicleType,
      truck_number: "",
      trailer_number: "",
      license_plate: "",
      company_name: "",
      phone: "",
      pass_type: initialPassType as PassType,
      start_date: startDate,
      end_date: defaultEndDate(initialPassType, startDate),
      new_company_monthly_rate: "",
      pay_choice: (stripeConfigured() ? "card_link" : "cash") as PayChoice,
      check_number: "",
    };
  });
  const [submitting, setSubmitting] = useState(false);
  const [issued, setIssued] = useState<(PassRead & { company_name: string; truck_number?: string }) | null>(null);
  const [paymentRequest, setPaymentRequest] = useState<PaymentRequestCreated | null>(null);
  // Keyed by the company name that produced it: a lookup that lands after the
  // manager has retyped the company is no longer "for" what's on screen, so it
  // can't quote her a different company's monthly rate. (The backend recomputes
  // the real rate regardless, so this was never a mis-charge — it was a wrong
  // number to read out to the driver.)
  const [lookup, setLookup] = useState<{ query: string; result: CompanyLookupResult | null }>({
    query: "",
    result: null,
  });

  const set = <K extends keyof typeof form>(key: K, value: (typeof form)[K]) =>
    setForm((f) => ({ ...f, [key]: value }));

  function setVehicleType(vehicleType: VehicleType) {
    setForm((f) => ({ ...f, vehicle_type: vehicleType, truck_number: "", trailer_number: "", license_plate: "" }));
  }

  function setPassType(passType: PassType) {
    setForm((f) => ({ ...f, pass_type: passType, end_date: defaultEndDate(passType, f.start_date) }));
  }

  function setStartDate(startDate: string) {
    setForm((f) => ({ ...f, start_date: startDate, end_date: defaultEndDate(f.pass_type, startDate) }));
  }

  // Always stamps the result with the query it answers, so a slow reply can never
  // be mistaken for the company now on screen.
  const fetchCompany = useCallback(async (query: string) => {
    if (!query) return;
    try {
      const result = await api.get<CompanyLookupResult>(`/api/companies/lookup?name=${encodeURIComponent(query)}`);
      setLookup({ query, result: result.found ? result : null });
    } catch {
      setLookup({ query, result: null });
    }
  }, []);

  // Monthly rates are per-company (set once, then reused for every truck under
  // that company) — look the company up as soon as Monthly + a company name
  // are both present, so the rate never needs to be typed twice.
  const companyQuery = form.pass_type === "monthly" ? form.company_name.trim() : "";

  useEffect(() => {
    if (!companyQuery) return;
    const timeout = setTimeout(() => fetchCompany(companyQuery), 400);
    return () => clearTimeout(timeout);
  }, [companyQuery, fetchCompany]);

  // Derived — while the manager is still typing, the previous company's answer is
  // simply not "done" yet, so nothing stale is ever on screen.
  const companyLookupDone = companyQuery !== "" && lookup.query === companyQuery;
  const companyMatch = companyLookupDone ? lookup.result : null;

  const heading = form.pass_type === "monthly" ? "Add Monthly Customer" : "Issue New Pass";
  const subheading =
    form.pass_type === "monthly"
      ? "Enter the company and truck — the monthly rate is detected automatically, or set once for a new customer."
      : "Everyone must pay before parking. No reserved spots, no refunds.";

  // The on-page heading is dynamic (Monthly vs Daily/Weekly) — the browser tab
  // title should match it, not sit fixed on the root layout's generic title.
  useEffect(() => {
    document.title = `${heading} | Madco Truck Plaza`;
  }, [heading]);

  const identifierField = IDENTIFIER_FIELD[form.vehicle_type];
  const days = daysBetween(form.start_date, form.end_date);
  const months = monthsBetween(form.start_date, form.end_date);
  const weeklyInvalid = form.pass_type === "weekly" && days !== 7;
  const isNewMonthlyCompany = form.pass_type === "monthly" && companyLookupDone && !companyMatch;

  const monthlyRate =
    companyMatch?.monthly_price != null
      ? companyMatch.monthly_price
      : form.new_company_monthly_rate
        ? Number(form.new_company_monthly_rate)
        : null;

  const finalPrice =
    form.pass_type === "daily"
      ? DAILY_RATE * Math.max(days, 1)
      : form.pass_type === "weekly"
        ? (weeklyInvalid ? null : WEEKLY_RATE)
        : monthlyRate != null
          ? monthlyRate * months
          : null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.company_name || !form.phone) {
      toast.error("Company name and phone are required.");
      return;
    }
    if (!form[identifierField.key]) {
      toast.error(`${identifierField.label} is required.`);
      return;
    }
    if (weeklyInvalid) {
      toast.error(
        `Weekly passes must be exactly 7 days (${form.start_date} → ${form.end_date} is ${days} day${days === 1 ? "" : "s"}). Choose Daily for a custom range.`,
      );
      return;
    }
    if (isNewMonthlyCompany && !form.new_company_monthly_rate) {
      toast.error(`${form.company_name} is a new monthly customer — set their monthly rate first.`);
      return;
    }

    setSubmitting(true);
    try {
      const priceOverride = isNewMonthlyCompany ? Number(form.new_company_monthly_rate) : undefined;

      if (form.pay_choice === "card_link") {
        // Customer self-pays by card — create a pending request + show the
        // QR/link. The pass is NOT issued until they actually pay.
        const created = await api.post<PaymentRequestCreated>("/api/payment-requests", {
          kind: "issue",
          issue: {
            company_name: form.company_name,
            truck_number: form.truck_number || undefined,
            trailer_number: form.trailer_number || undefined,
            license_plate: form.license_plate || undefined,
            phone: form.phone,
            vehicle_type: form.vehicle_type,
            pass_type: form.pass_type,
            issue_date: form.start_date,
            end_date: form.end_date || undefined,
            price: priceOverride,
          },
        });
        setPaymentRequest(created);
        return;
      }

      const payload: IssuePassRequest = {
        company_name: form.company_name,
        truck_number: form.truck_number || undefined,
        trailer_number: form.trailer_number || undefined,
        license_plate: form.license_plate || undefined,
        phone: form.phone,
        vehicle_type: form.vehicle_type,
        pass_type: form.pass_type,
        price: priceOverride,
        issue_date: form.start_date,
        end_date: form.end_date || undefined,
        payment_method: form.pay_choice as PaymentMethod,
        check_number: form.pay_choice === "check" ? form.check_number || undefined : undefined,
      };
      const pass = await api.post<PassRead>("/api/passes", payload);
      setIssued({ ...pass, company_name: form.company_name, truck_number: form.truck_number });
      toast.success(`Pass issued — receipt ${pass.receipt_number}`);
      if (form.pass_type === "monthly") {
        // Refresh the roster so the next truck added for this company sees
        // the one we just issued (and its now-established rate).
        fetchCompany(form.company_name.trim());
      }
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to issue pass.");
    } finally {
      setSubmitting(false);
    }
  }

  function afterCardPaid() {
    toast.success("Payment received — pass issued.");
    setPaymentRequest(null);
    if (form.pass_type === "monthly") fetchCompany(form.company_name.trim());
    setForm((f) => ({ ...f, truck_number: "", trailer_number: "", license_plate: "", new_company_monthly_rate: "" }));
  }

  function addAnother() {
    setIssued(null);
    // Keep company/phone/pass type/payment method — only clear what's
    // specific to the truck just issued, so adding a company's 2nd, 3rd,
    // 4th truck never requires retyping the company or phone number.
    setForm((f) => ({
      ...f,
      truck_number: "",
      trailer_number: "",
      license_plate: "",
      new_company_monthly_rate: "",
    }));
  }

  if (paymentRequest) {
    return (
      <div className="mx-auto max-w-md space-y-4">
        <div className="card-paper rounded-2xl p-6">
          <PaymentRequestQR request={paymentRequest} onPaid={afterCardPaid} />
        </div>
        <Button variant="outline" className="w-full" onClick={() => setPaymentRequest(null)}>
          Cancel
        </Button>
      </div>
    );
  }

  if (issued) {
    return (
      <div className="mx-auto max-w-md space-y-4">
        <PassTicket pass={issued} />
        <div className="flex gap-2 print:hidden">
          <Button className="btn-embossed flex-1 bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)]" onClick={() => window.print()}>
            Print Pass
          </Button>
          <Button variant="outline" className="flex-1" onClick={addAnother}>
            {form.pass_type === "monthly" ? `Add Another Truck for ${form.company_name}` : "Issue Another"}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-3xl space-y-6 print:hidden">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">{heading}</h1>
        <p className="text-sm text-muted-foreground">{subheading}</p>
      </div>

      <Card className="card-paper border-none">
        <CardHeader>
          <CardTitle className="text-[var(--cream-foreground)]">Vehicle &amp; Company</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Vehicle Type">
            <Select value={form.vehicle_type} onValueChange={(v) => setVehicleType(v as VehicleType)}>
              <SelectTrigger className="w-full">
                <SelectValue>{(v: VehicleType) => v.charAt(0).toUpperCase() + v.slice(1)}</SelectValue>
              </SelectTrigger>
              <SelectContent>
                {VEHICLE_TYPES.map((v) => (
                  <SelectItem key={v} value={v} className="capitalize">{v}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>
          <Field label={identifierField.label} required>
            <Input
              value={form[identifierField.key]}
              onChange={(e) => set(identifierField.key, e.target.value)}
            />
          </Field>
          <Field label="Company" required className="sm:col-span-2">
            <Input value={form.company_name} onChange={(e) => set("company_name", e.target.value)} placeholder="Acme Trucking" />
            {form.pass_type === "monthly" && companyMatch && companyMatch.trucks.length > 0 && (
              <div className="mt-2 rounded-lg bg-[var(--forest-700)]/8 p-3 text-xs">
                <p className="font-semibold">
                  {form.company_name} already has {companyMatch.trucks.length} truck{companyMatch.trucks.length === 1 ? "" : "s"} on the monthly plan
                  {companyMatch.monthly_price != null ? ` at ${currency(companyMatch.monthly_price)}/truck` : ""}:
                </p>
                <ul className="mt-1 space-y-0.5 font-mono">
                  {companyMatch.trucks.map((t) => (
                    <li key={t.truck_number ?? t.license_plate}>
                      {t.truck_number ?? t.license_plate} — expires {t.expiration_date}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {isNewMonthlyCompany && (
              <div className="mt-2 rounded-lg bg-[var(--amber-500)]/10 p-3">
                <Field label={`Set Monthly Rate for ${form.company_name}`} required className="mb-0">
                  <Input
                    type="number"
                    min={0}
                    step="0.01"
                    value={form.new_company_monthly_rate}
                    onChange={(e) => set("new_company_monthly_rate", e.target.value)}
                    placeholder="e.g. 250"
                  />
                </Field>
                <p className="mt-1.5 text-xs text-[var(--cream-foreground)]/60">
                  New monthly customer — this rate will apply to every truck {form.company_name} parks with us going forward.
                </p>
              </div>
            )}
          </Field>
          <Field label="Phone Number" required>
            <Input value={form.phone} onChange={(e) => set("phone", e.target.value)} placeholder="313-555-0100" />
          </Field>
        </CardContent>
      </Card>

      <Card className="card-paper border-none">
        <CardHeader>
          <CardTitle className="text-[var(--cream-foreground)]">Parking Type &amp; Dates</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-2">
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
          <Field label="Price">
            <div className="flex h-8 items-center rounded-lg border border-input bg-transparent px-2.5 font-mono text-sm">
              {finalPrice !== null
                ? `${currency(finalPrice)}${
                    form.pass_type === "daily"
                      ? ` (${days} day${days === 1 ? "" : "s"} × $${DAILY_RATE})`
                      : form.pass_type === "monthly" && monthlyRate != null
                        ? ` (${months} month${months === 1 ? "" : "s"} × ${currency(monthlyRate)})`
                        : ""
                  }`
                : "—"}
            </div>
          </Field>
          <Field label="Start Date">
            <Input type="date" value={form.start_date} onChange={(e) => setStartDate(e.target.value)} />
          </Field>
          <Field label="End Date">
            <Input type="date" value={form.end_date} onChange={(e) => set("end_date", e.target.value)} />
            {weeklyInvalid && (
              <p className="mt-1.5 text-xs text-[var(--danger-ink)]">
                Weekly passes must be exactly 7 days (currently {days} day{days === 1 ? "" : "s"}). Choose Daily for a custom range.
              </p>
            )}
            {form.pass_type === "monthly" && (
              <p className="mt-1.5 text-xs text-[var(--cream-foreground)]/50">
                Paying for more than one month? Push this date out further — the price scales automatically.
              </p>
            )}
          </Field>
        </CardContent>
      </Card>

      <Card className="card-paper border-none">
        <CardHeader>
          <CardTitle className="text-[var(--cream-foreground)]">Payment</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Payment Method">
            <Select value={form.pay_choice} onValueChange={(v) => set("pay_choice", v as PayChoice)}>
              <SelectTrigger className="w-full">
                <SelectValue>{(v: PayChoice) => PAY_CHOICES.find((p) => p.value === v)?.label ?? v}</SelectValue>
              </SelectTrigger>
              <SelectContent>
                {PAY_CHOICES.map((p) => (
                  <SelectItem key={p.value} value={p.value} disabled={p.value === "card_link" && !stripeConfigured()}>
                    {p.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Field>
          {form.pay_choice === "check" && (
            <Field label="Check Number">
              <Input value={form.check_number} onChange={(e) => set("check_number", e.target.value)} />
            </Field>
          )}
          {form.pay_choice === "card_link" && (
            <p className="text-xs text-[var(--cream-foreground)]/60 sm:col-span-2">
              Next screen shows a QR code + link for the customer to pay by card on their phone. The pass is issued only after they pay.
            </p>
          )}
        </CardContent>
      </Card>

      <Button
        type="submit"
        disabled={submitting || weeklyInvalid}
        className="btn-embossed w-full bg-[var(--amber-500)] py-6 text-base font-semibold text-[var(--forest-950)] hover:bg-[var(--amber-600)] disabled:opacity-50"
      >
        {submitting
          ? "Working…"
          : form.pay_choice === "card_link"
            ? "Show Payment QR"
            : `Issue Pass & Take Payment${finalPrice !== null ? ` — ${currency(finalPrice)}` : ""}`}
      </Button>
    </form>
  );
}

