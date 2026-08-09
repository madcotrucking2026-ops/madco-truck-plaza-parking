"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export type SubTab = { label: string; href: string };

/** Segmented links that group related screens under a single menu entry, so the
 *  sidebar stays short without hiding anything. The active tab is the one whose
 *  href matches the current path. 44px tall on phones (the desk taps in gloves),
 *  snapping to the tighter desktop rhythm at sm — same control as the payments
 *  period switcher. */
export function SubTabs({ items }: { items: SubTab[] }) {
  const pathname = usePathname();
  return (
    <nav className="inline-flex rounded-xl bg-foreground/[0.06] p-1">
      {items.map((t) => {
        const active = pathname === t.href;
        return (
          <Link
            key={t.href}
            href={t.href}
            aria-current={active ? "page" : undefined}
            className={
              "flex h-11 items-center rounded-lg px-3.5 text-sm font-medium transition sm:h-8 " +
              (active
                ? "btn-embossed bg-[var(--forest-700)] text-[var(--ivory-100)]"
                : "text-muted-foreground hover:text-foreground")
            }
          >
            {t.label}
          </Link>
        );
      })}
    </nav>
  );
}

// The groupings that fold four old menu items into two parents. Kept here so the
// two pages in each group can never drift out of sync.
export const MONEY_TABS: SubTab[] = [
  { label: "Payments", href: "/payments" },
  { label: "Reports", href: "/reports" },
];
export const COMPANY_TABS: SubTab[] = [
  { label: "Companies", href: "/companies" },
  { label: "Monthly", href: "/monthly-customers" },
];
export const SETTINGS_TABS: SubTab[] = [
  { label: "Settings", href: "/settings" },
  { label: "Activity log", href: "/audit-log" },
];
