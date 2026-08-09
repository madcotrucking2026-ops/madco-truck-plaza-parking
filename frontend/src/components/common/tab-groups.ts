export type SubTab = { label: string; href: string };

// The groupings that fold four old menu items into two parents. Kept in this
// plain (non-component) module so the SubTabs component file exports only a
// component — mixing the two trips React Fast Refresh in `next dev`.
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
