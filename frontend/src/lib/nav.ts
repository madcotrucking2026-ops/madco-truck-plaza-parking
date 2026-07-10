import type { LucideIcon } from "lucide-react";
import {
  LayoutDashboard,
  Ticket,
  FilePlus2,
  Users,
  Building2,
  ClipboardCheck,
  CreditCard,
  BarChart3,
  BellRing,
  History,
  Settings,
} from "lucide-react";

export type NavItem = {
  label: string;
  href: string;
  icon: LucideIcon;
};

export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Parking Passes", href: "/passes", icon: Ticket },
  { label: "Issue New Pass", href: "/passes/issue", icon: FilePlus2 },
  { label: "Monthly Customers", href: "/monthly-customers", icon: Users },
  { label: "Companies", href: "/companies", icon: Building2 },
  { label: "Lot Check", href: "/lot-check", icon: ClipboardCheck },
  { label: "Payments", href: "/payments", icon: CreditCard },
  { label: "Reports", href: "/reports", icon: BarChart3 },
  { label: "Reminders", href: "/reminders", icon: BellRing },
  { label: "Activity Log", href: "/audit-log", icon: History },
  { label: "Settings", href: "/settings", icon: Settings },
];
