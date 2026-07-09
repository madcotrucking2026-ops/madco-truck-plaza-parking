import type { NextConfig } from "next";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// Baseline defense-in-depth: the manager session token lives in localStorage
// (not an httpOnly cookie), which has no protection of its own against a
// malicious script running in-origin — a CSP restricting script-src is the
// backstop. Stripe's Payment Element needs its own script + iframe origins;
// 'unsafe-eval'/'unsafe-inline' are required by Next's dev-mode tooling
// (React Refresh, styled inline attributes) and should be tightened for a
// production build if this ever moves off `next dev`.
const csp = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://js.stripe.com",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self' data:",
  `connect-src 'self' ${apiUrl} https://api.stripe.com`,
  "frame-src https://js.stripe.com https://hooks.stripe.com",
  "base-uri 'self'",
  "form-action 'self'",
].join("; ");

const nextConfig: NextConfig = {
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "Content-Security-Policy", value: csp },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },
};

export default nextConfig;
