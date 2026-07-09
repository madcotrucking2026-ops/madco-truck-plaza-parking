import type { LucideIcon } from "lucide-react";
import {
  LayoutDashboard,
  Ticket,
  FilePlus2,
  Users,
  ClipboardCheck,
  CreditCard,
  BarChart3,
  BellRing,
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
  { label: "Lot Check", href: "/lot-check", icon: ClipboardCheck },
  { label: "Payments", href: "/payments", icon: CreditCard },
  { label: "Reports", href: "/reports", icon: BarChart3 },
  { label: "Reminders", href: "/reminders", icon: BellRing },
  { label: "Settings", href: "/settings", icon: Settings },
];
