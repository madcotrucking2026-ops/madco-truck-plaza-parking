/**
 * The window between "the card cleared" and "the pass exists".
 *
 * In that window the customer has already been charged, so a failed request on our
 * side is never a reason to show them an error and send them to the front desk —
 * Stripe's webhook is finalizing the same charge server-side and usually wins
 * within a couple of seconds. These delays back off so a driver on weak truck-stop
 * signal still gets ~33 seconds of recovery before we give up.
 */
export const SETTLE_RETRY_DELAYS_MS = [1500, 3000, 4000, 6000, 8000, 10000];

export const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));
