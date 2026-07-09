"use client";

import { useState } from "react";
import { Elements, PaymentElement, useElements, useStripe } from "@stripe/react-stripe-js";
import { toast } from "sonner";
import { getStripe } from "@/lib/stripe";
import { currency } from "@/lib/pricing";
import { Button } from "@/components/ui/button";

export function CardCheckout({
  clientSecret,
  amount,
  onSuccess,
  onCancel,
}: {
  clientSecret: string;
  amount: number;
  onSuccess: (paymentIntentId: string) => void;
  onCancel: () => void;
}) {
  const stripePromise = getStripe();
  if (!stripePromise) return null;

  return (
    <Elements stripe={stripePromise} options={{ clientSecret }}>
      <CheckoutForm amount={amount} onSuccess={onSuccess} onCancel={onCancel} />
    </Elements>
  );
}

function CheckoutForm({
  amount,
  onSuccess,
  onCancel,
}: {
  amount: number;
  onSuccess: (paymentIntentId: string) => void;
  onCancel: () => void;
}) {
  const stripe = useStripe();
  const elements = useElements();
  const [submitting, setSubmitting] = useState(false);
  const [cancelling, setCancelling] = useState(false);

  async function handlePay(e: React.FormEvent) {
    e.preventDefault();
    if (!stripe || !elements || submitting) return;
    setSubmitting(true);
    const { error, paymentIntent } = await stripe.confirmPayment({
      elements,
      redirect: "if_required",
    });
    if (error) {
      toast.error(error.message ?? "Payment failed. Please try again or use a different card.");
      setSubmitting(false);
      return;
    }
    if (paymentIntent?.status === "succeeded") {
      onSuccess(paymentIntent.id);
    } else {
      toast.error("Payment did not complete. Please try again.");
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handlePay} className="space-y-4">
      <PaymentElement
        options={{
          // Manual card entry + Apple/Google Pay only. `link: "never"`
          // removes Stripe Link's accelerated-checkout layer, which is what
          // injects the Bank (pay-by-bank) and Klarna tiles — those confuse
          // customers and aren't wanted. Apple/Google Pay render only over
          // HTTPS on supported devices (won't show on localhost HTTP; that's
          // expected, not a bug).
          wallets: { applePay: "auto", googlePay: "auto", link: "never" },
          // Card is the only method now — show its fields inline immediately
          // instead of behind a collapsed accordion row (saves a click).
          layout: { type: "accordion", defaultCollapsed: false, radios: "never", spacedAccordionItems: false },
        }}
      />
      <Button
        type="submit"
        disabled={!stripe || submitting || cancelling}
        className="btn-embossed w-full bg-[var(--amber-500)] py-6 text-base font-semibold text-[var(--forest-950)] hover:bg-[var(--amber-600)] disabled:opacity-50"
      >
        {submitting ? "Processing…" : `Pay ${currency(amount)}`}
      </Button>
      <Button
        type="button"
        variant="ghost"
        disabled={submitting || cancelling}
        onClick={() => {
          setCancelling(true);
          onCancel();
        }}
        className="w-full text-xs text-muted-foreground"
      >
        Cancel and choose a different payment method
      </Button>
    </form>
  );
}
