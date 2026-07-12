"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { toast } from "sonner";
import { CheckCircle2, Loader2, Truck, ShieldCheck, Lock } from "lucide-react";
import {
  api,
  ApiError,
  type CreateIntentResponse,
  type PassRead,
  type PaymentRequestStatus,
} from "@/lib/api";
import { CardCheckout } from "@/components/checkout/card-checkout";
import { currency } from "@/lib/pricing";
import { SETTLE_RETRY_DELAYS_MS, sleep } from "@/lib/settle";

export default function PayPage() {
  const params = useParams<{ token: string }>();
  const token = params?.token;

  const [info, setInfo] = useState<PaymentRequestStatus | null>(null);
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [paidReceipt, setPaidReceipt] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [settling, setSettling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    (async () => {
      try {
        const status = await api.get<PaymentRequestStatus>(`/api/payment-requests/${token}`);
        setInfo(status);
        if (status.status === "paid") {
          setPaidReceipt(status.receipt_number);
          return;
        }
        if (status.status === "cancelled") {
          setError("This payment request was cancelled. Please see the front desk.");
          return;
        }
        const intent = await api.post<CreateIntentResponse>(`/api/payment-requests/${token}/create-intent`, {});
        setClientSecret(intent.client_secret);
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Could not load this payment. Please see the front desk.");
      } finally {
        setLoading(false);
      }
    })();
  }, [token]);

  async function handleSuccess() {
    // The card is ALREADY charged by the time we get here. So a failure below is
    // OUR problem, not the driver's — and it is very likely temporary: Stripe's
    // webhook finalizes this exact charge server-side within seconds. Watch for
    // that before sending a paying customer inside to argue with the front desk.
    setSettling(true);

    try {
      const pass = await api.post<PassRead>(`/api/payment-requests/${token}/finalize`, {});
      setPaidReceipt(pass.receipt_number);
      setSettling(false);
      return;
    } catch {
      // fall through to the webhook watch
    }

    for (const delay of SETTLE_RETRY_DELAYS_MS) {
      await sleep(delay);
      try {
        const status = await api.get<PaymentRequestStatus>(`/api/payment-requests/${token}`);
        if (status.status === "paid") {
          setInfo(status);
          setPaidReceipt(status.receipt_number);
          setSettling(false);
          return;
        }
      } catch {
        // A failed poll (dropped signal, throttled) says nothing about the charge.
        // Keep waiting — only the deadline below is allowed to give up.
      }
    }

    setSettling(false);
    toast.error(
      "Your card was charged, but we couldn't confirm it on this page. Please see the front desk — do NOT pay again.",
      { duration: 30000 },
    );
  }

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

      <div className="mx-auto max-w-md">
        {loading ? (
          <div className="animate-rise card-paper rounded-2xl p-8 text-center text-sm text-muted-foreground">Loading…</div>
        ) : paidReceipt !== null || info?.status === "paid" ? (
          <div className="animate-rise card-paper flex flex-col items-center gap-3 rounded-2xl p-8 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[var(--success)]/12 text-[var(--success)]">
              <CheckCircle2 className="h-9 w-9" strokeWidth={2} />
            </div>
            <p className="text-xl font-bold text-foreground">Payment complete</p>
            <p className="text-sm text-muted-foreground">{info?.summary}</p>
            {paidReceipt && <p className="font-mono text-sm tabular-nums text-foreground">Receipt {paidReceipt}</p>}
            <p className="mt-2 text-xs text-muted-foreground">You&rsquo;re all set. You can close this page.</p>
          </div>
        ) : settling ? (
          /* Card charged, pass not confirmed yet. Never show a payment form or an
             error here — the driver has already paid, and re-paying is the one
             mistake this screen must not invite. */
          <div className="animate-rise card-paper flex flex-col items-center gap-3 rounded-2xl p-8 text-center">
            <Loader2 className="h-9 w-9 animate-spin text-[var(--forest-700)]" strokeWidth={2} />
            <p className="text-lg font-bold text-[var(--cream-foreground)]">Payment received</p>
            <p className="text-sm text-muted-foreground">Confirming your pass — one moment. Please don&rsquo;t close this page.</p>
          </div>
        ) : error ? (
          <div className="animate-rise card-paper rounded-2xl p-8 text-center text-sm text-[var(--danger-ink)]">{error}</div>
        ) : (
          <div className="animate-rise card-paper space-y-4 rounded-2xl p-6">
            {/* Receipt-style header — summary left, mono tabular total right. */}
            <div className="flex items-start justify-between gap-3 border-b border-black/5 pb-4">
              <p className="min-w-0 break-words font-semibold text-[var(--cream-foreground)]">{info?.summary}</p>
              {info && (
                <span className="whitespace-nowrap font-mono text-lg font-bold tabular-nums text-[var(--cream-foreground)]">
                  {currency(info.amount)}
                </span>
              )}
            </div>
            {clientSecret && info && (
              <CardCheckout
                clientSecret={clientSecret}
                amount={info.amount}
                onSuccess={handleSuccess}
                onCancel={() => setError("Payment cancelled. Please see the front desk to try again.")}
              />
            )}
            <p className="flex items-center justify-center gap-1.5 text-center text-xs text-muted-foreground">
              <Lock className="h-3 w-3" />
              Secured by Stripe · First come, first served · No refunds
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
