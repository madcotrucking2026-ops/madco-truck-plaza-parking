import type { Metadata } from "next";

// Tokenized one-off payment link — must never be crawled or indexed.
export const metadata: Metadata = {
  title: "Complete Your Payment · Madco Truck Plaza",
  robots: { index: false, follow: false },
};

export default function PayLayout({ children }: { children: React.ReactNode }) {
  return children;
}
