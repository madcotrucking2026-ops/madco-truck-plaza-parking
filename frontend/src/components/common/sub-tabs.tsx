"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { SubTab } from "@/components/common/tab-groups";

/** Segmented links that group related screens under a single menu entry, so the
 *  sidebar stays short without hiding anything. The active tab is the one whose
 *  href matches the current path. 44px tall on phones (the desk taps in gloves),
 *  snapping to the tighter desktop rhythm at sm — same control as the payments
 *  period switcher. The tab sets live in ./tab-groups. */
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
