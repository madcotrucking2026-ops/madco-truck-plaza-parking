import type { LucideIcon } from "lucide-react";
import {
  LayoutDashboard,
  Sun,
  Ticket,
  FilePlus2,
  Users,
  Building2,
  ScanSearch,
  Grid3x3,
  CreditCard,
  BarChart3,
  BellRing,
  History,
  Settings,
} from "lucide-react";

export type Role = "attendant" | "manager" | "admin";

export type NavItem = {
  label: string;
  href: string;
  icon: LucideIcon;
  /** Lowest role that can use the screen. Matches the backend's router tiers —
   *  hiding a link is courtesy, the API is what actually enforces it. */
  minRole: Role;
};

const RANK: Record<Role, number> = { attendant: 0, manager: 1, admin: 2 };

export function navForRole(role: Role | null): NavItem[] {
  // Until /me answers, show only what every role can use — a flash of admin
  // links for an attendant is worse than a short delay for the owner.
  const rank = role ? RANK[role] : 0;
  return NAV_ITEMS.filter((item) => RANK[item.minRole] <= rank);
}

export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard, minRole: "manager" },
  // Sits right under the dashboard on purpose: it's the first thing read in the
  // morning, and the only screen that says what to DO rather than what happened.
  { label: "Morning Report", href: "/morning-report", icon: Sun, minRole: "manager" },
  { label: "Parking Passes", href: "/passes", icon: Ticket, minRole: "manager" },
  { label: "Issue New Pass", href: "/passes/issue", icon: FilePlus2, minRole: "attendant" },
  { label: "Monthly Customers", href: "/monthly-customers", icon: Users, minRole: "manager" },
  { label: "Companies", href: "/companies", icon: Building2, minRole: "manager" },
  // "Find a Truck": type a truck / trailer / plate, get the PAID / expiry card.
  // Matches the dashboard's "Search a Truck" tile — same page, same intent.
  { label: "Find a Truck", href: "/lot-check", icon: ScanSearch, minRole: "manager" },
  // The cashier's live open-spots board — front-desk tool, so attendant-visible.
  { label: "Open Spots", href: "/availability", icon: Grid3x3, minRole: "attendant" },
  { label: "Payments", href: "/payments", icon: CreditCard, minRole: "manager" },
  { label: "Reports", href: "/reports", icon: BarChart3, minRole: "manager" },
  { label: "Reminders", href: "/reminders", icon: BellRing, minRole: "manager" },
  { label: "Activity Log", href: "/audit-log", icon: History, minRole: "admin" },
  { label: "Settings", href: "/settings", icon: Settings, minRole: "admin" },
];
