import type { Metadata } from "next";

// /book is a legitimate public entry (a driver may search for it), so it stays
// indexable — with its own title/description instead of inheriting the manager one.
export const metadata: Metadata = {
  title: "Buy a Parking Pass · Madco Truck Plaza",
  description: "Pay for truck, trailer, or car parking at Madco Truck Plaza — daily, weekly, or monthly. Card, cash, or check.",
};

export default function BookLayout({ children }: { children: React.ReactNode }) {
  return children;
}
