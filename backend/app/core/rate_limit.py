"""Per-client sliding-window rate limiting, as a FastAPI dependency.

Deliberately dependency-free and in-process: this app runs as a single uvicorn
worker today, so an in-memory window is honest and enough. If it is ever scaled
to multiple workers, each worker would keep its own counters and the effective
limit would multiply — at that point move this to a shared store (Redis) or,
better, enforce it at the edge (nginx / Cloudflare) as well.

Why it exists (all of these are reachable WITHOUT a login):
  * /auth/login — the account lockout is per-account, so it does nothing against
    a spray across many accounts, and it lets an attacker lock the owner out of
    his own account on demand. An IP throttle is what actually blunts both.
  * /payments/stripe/create-intent — public, and every call creates a real
    PaymentIntent on the plaza's Stripe account.
  * /companies/lookup — public, and answers "does this company exist, what is
    its negotiated monthly rate, and which trucks park under it".
"""

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status


def _client_key(request: Request) -> str:
    # request.client.host is the peer address. X-Forwarded-For is NOT trusted
    # here on purpose: it is client-supplied and trivially spoofed unless a
    # proxy we control is guaranteed to overwrite it. When this deploys behind
    # nginx, set the real IP there and revisit.
    return request.client.host if request.client else "unknown"


class RateLimiter:
    """Allow `times` requests per `seconds` per client, else 429."""

    def __init__(self, times: int, seconds: int):
        self.times = times
        self.seconds = seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def __call__(self, request: Request) -> None:
        key = _client_key(request)
        now = time.monotonic()
        cutoff = now - self.seconds

        hits = self._hits[key]
        while hits and hits[0] <= cutoff:
            hits.popleft()

        if len(hits) >= self.times:
            retry_after = max(1, int(self.seconds - (now - hits[0])) + 1)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests — please slow down and try again shortly.",
                headers={"Retry-After": str(retry_after)},
            )

        hits.append(now)
        if len(self._hits) > 10_000:  # keep the table from growing unbounded
            self._prune(cutoff)

    def _prune(self, cutoff: float) -> None:
        for key in [k for k, v in self._hits.items() if not v or v[-1] <= cutoff]:
            self._hits.pop(key, None)

    def reset(self) -> None:
        """Tests only — start from a clean window."""
        self._hits.clear()


# Tight where an attacker gains something, loose enough that a real person at
# the kiosk (or a guard scanning passes) never notices.
login_limiter = RateLimiter(times=10, seconds=60)          # brute force / lockout DoS
register_limiter = RateLimiter(times=5, seconds=60)        # bootstrap only, once ever
checkout_limiter = RateLimiter(times=10, seconds=60)       # creates real Stripe intents
lookup_limiter = RateLimiter(times=30, seconds=60)         # company/rate enumeration
verify_limiter = RateLimiter(times=60, seconds=60)         # guards scanning QR codes
