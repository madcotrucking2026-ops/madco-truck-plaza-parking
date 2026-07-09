"use client";

import { useEffect, useState } from "react";
import { QRCodeSVG } from "qrcode.react";
import { toast } from "sonner";
import { CheckCircle2, Copy, Smartphone } from "lucide-react";
import { api, type PaymentRequestCreated, type PaymentRequestStatus } from "@/lib/api";
import { currency } from "@/lib/pricing";

// Shown on the MANAGER screen after they pick "Card — customer pays". The
// customer scans the QR (or opens the link) on their own phone and pays by
// card; this polls the request status and calls onPaid once it flips to paid.
export function PaymentRequestQR({
  request,
  onPaid,
}: {
  request: PaymentRequestCreated;
  onPaid: (receiptNumber: string | null) => void;
}) {
  const [status, setStatus] = useState<PaymentRequestStatus["status"]>("pending");

  useEffect(() => {
    let stop = false;
    const tick = async () => {
      try {
        const s = await api.get<PaymentRequestStatus>(`/api/payment-requests/${request.token}`);
        if (stop) return;
        setStatus(s.status);
        if (s.status === "paid") {
          onPaid(s.receipt_number);
          return; // stop polling
        }
      } catch {
        /* transient — keep polling */
      }
      if (!stop) timer = setTimeout(tick, 3000);
    };
    let timer = setTimeout(tick, 2000);
    return () => {
      stop = true;
      clearTimeout(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [request.token]);

  if (status === "paid") {
    return (
      <div className="flex flex-col items-center gap-2 rounded-xl bg-[var(--success)]/12 p-6 text-center">
        <CheckCircle2 className="h-12 w-12 text-[var(--success)]" />
        <p className="font-semibold text-[var(--success)]">Paid</p>
      </div>
    );
  }

  return (
    <div className="space-y-4 text-center">
      <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
        <Smartphone className="h-4 w-4" />
        Have the customer scan to pay {currency(request.amount)} by card
      </div>
      <div className="flex justify-center rounded-xl bg-white p-4">
        <QRCodeSVG value={request.pay_url} size={180} />
      </div>
      <button
        type="button"
        onClick={() => {
          navigator.clipboard?.writeText(request.pay_url);
          toast.success("Payment link copied");
        }}
        className="mx-auto flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground"
      >
        <Copy className="h-3.5 w-3.5" />
        Copy payment link
      </button>
      <p className="text-xs text-muted-foreground">Waiting for payment…</p>
    </div>
  );
}
