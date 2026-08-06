"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { clearToken, getToken } from "@/lib/auth";
import { SidebarNav } from "@/components/layout/sidebar-nav";
import { MobileNav } from "@/components/layout/mobile-nav";
import { CommandPalette } from "@/components/command-palette";

// /login is the only bare experience — no manager nav, no auth requirement.
// Everything else is the staff app and requires a signed-in session. (The
// customer kiosk, pay-links, and pass-QR verify page were all retired when the
// plaza went staff-only.)
function isPublicPath(pathname: string | null): boolean {
  if (!pathname) return false;
  return pathname === "/login";
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const isPublic = isPublicPath(pathname);
  // Read the token synchronously on every render so a CLEARED token (e.g. right
  // after Log Out, then browser-Back to a protected page) blanks + redirects
  // immediately, with no flash of the manager shell. This alone covers the
  // logout case — no need to re-blank the whole app on every navigation.
  const hasToken = isPublic || Boolean(getToken());
  // Verified once per session. Stays true across navigations, so moving between
  // pages never flashes a blank screen while /me re-checks in the background.
  const [authOk, setAuthOk] = useState(false);

  useEffect(() => {
    if (isPublic) return;
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    let cancelled = false;
    api
      .get("/api/auth/me")
      .then(() => {
        if (!cancelled) setAuthOk(true);
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 401) {
          clearToken();
        }
        router.replace("/login");
      });
    return () => {
      cancelled = true;
    };
  }, [pathname, isPublic, router]);

  if (isPublic) {
    return <>{children}</>;
  }

  // Token gone → redirecting (no flash). Otherwise only blank on the very first
  // load, before the first /me succeeds — never on later navigations.
  if (!hasToken || !authOk) {
    return null;
  }

  return (
    <div className="flex min-h-screen w-full">
      <SidebarNav />
      {/* min-w-0 so a wide child (e.g. the Payments/Passes table) scrolls
          inside its own overflow container instead of expanding this flex
          column past the viewport and pushing the sidebar off-screen. */}
      <div className="flex min-h-screen min-w-0 flex-1 flex-col">
        <MobileNav />
        <main className="min-w-0 flex-1 overflow-y-auto p-4 md:p-8">{children}</main>
      </div>
      <CommandPalette />
    </div>
  );
}
