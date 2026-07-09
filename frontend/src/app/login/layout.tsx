import type { Metadata } from "next";

// Manager-only sign-in — never index.
export const metadata: Metadata = {
  title: "Manager Sign In · Madco Truck Plaza",
  robots: { index: false, follow: false },
};

export default function LoginLayout({ children }: { children: React.ReactNode }) {
  return children;
}
