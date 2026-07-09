"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { toast } from "sonner";
import { CheckCircle2, Truck } from "lucide-react";
import {
  api,
  ApiError,
  type CreateIntentResponse,
  type PassRead,
  type PaymentRequestStatus,
} from "@/lib/api";
import { CardCheckout } from "@/components/checkout/card-checkout";
import { currency } from "@/lib/pricing";

export default function PayPage() {
  const params = useParams<{ token: string }>();
  const token = params?.token;

  const [info, setInfo] = useState<PaymentRequestStatus | null>(null);
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [paidReceipt, setPaidReceipt] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
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
    try {
      const pass = await api.post<PassRead>(`/api/payment-requests/${token}/finalize`, {});
      setPaidReceipt(pass.receipt_number);
    } catch (err) {
      toast.error(
        err instanceof ApiError
          ? `Your card was charged but we couldn't finish (${err.message}). Please see the front desk.`
          : "Your card was charged but we couldn't finish. Please see the front desk.",
      );
    }
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

      <div className="mx-auto max-w-md">
        {loading ? (
          <div className="card-paper rounded-2xl p-8 text-center text-sm text-muted-foreground">Loading…</div>
        ) : paidReceipt !== null || info?.status === "paid" ? (
          <div className="card-paper flex flex-col items-center gap-3 rounded-2xl p-8 text-center">
            <CheckCircle2 className="h-16 w-16 text-[var(--success)]" />
            <p className="text-xl font-bold text-foreground">Payment complete</p>
            <p className="text-sm text-muted-foreground">{info?.summary}</p>
            {paidReceipt && <p className="font-mono text-sm text-foreground">Receipt {paidReceipt}</p>}
            <p className="mt-2 text-xs text-muted-foreground">You're all set. You can close this page.</p>
          </div>
        ) : error ? (
          <div className="card-paper rounded-2xl p-8 text-center text-sm text-[var(--danger)]">{error}</div>
        ) : (
          <div className="card-paper space-y-4 rounded-2xl p-6">
            <div className="rounded-lg bg-[var(--forest-700)]/8 p-3 text-sm">
              <p className="font-semibold text-foreground">{info?.summary}</p>
              <p className="text-muted-foreground">{info ? currency(info.amount) : ""}</p>
            </div>
            {clientSecret && info && (
              <CardCheckout
                clientSecret={clientSecret}
                amount={info.amount}
                onSuccess={handleSuccess}
                onCancel={() => setError("Payment cancelled. Please see the front desk to try again.")}
              />
            )}
            <p className="text-center text-xs text-muted-foreground">
              First come, first served. No reservations, no refunds.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
