import type { Metadata } from "next";

// Tokenized pass-verification link — must never be crawled or indexed.
export const metadata: Metadata = {
  title: "Verify Pass · Madco Truck Plaza",
  robots: { index: false, follow: false },
};

export default function VerifyLayout({ children }: { children: React.ReactNode }) {
  return children;
}
