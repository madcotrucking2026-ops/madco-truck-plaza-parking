export type SubTab = { label: string; href: string };

// The groupings that fold old menu items into a shared parent. Kept in this
// plain (non-component) module so the SubTabs component file exports only a
// component — mixing the two trips React Fast Refresh in `next dev`.
// (Money has no tabs now: Reports was removed and its trend graph lives on the
// Dashboard, so Payments stands alone.)
export const COMPANY_TABS: SubTab[] = [
  { label: "Companies", href: "/companies" },
  { label: "Monthly", href: "/monthly-customers" },
];
export const SETTINGS_TABS: SubTab[] = [
  { label: "Settings", href: "/settings" },
  { label: "Activity log", href: "/audit-log" },
];
