import Link from "next/link";
import { ExternalLink, Settings as SettingsIcon } from "lucide-react";
import { ComingSoon } from "@/components/coming-soon";
import { AddStaffCard } from "@/components/settings/add-staff-card";
import { StaffListCard } from "@/components/settings/staff-list-card";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div className="card-paper flex items-center justify-between gap-4 rounded-2xl p-5">
        <div>
          <p className="font-semibold text-[var(--cream-foreground)]">Customer Self-Checkout Kiosk</p>
          <p className="text-sm text-[var(--cream-foreground)]/60">
            A simplified, no-login payment screen for customers — truck number, company, phone, parking type, and payment only.
          </p>
        </div>
        <Link
          href="/book"
          target="_blank"
          className="btn-embossed flex h-11 shrink-0 items-center gap-2 rounded-lg bg-[var(--forest-700)] px-4 py-2 text-sm font-semibold text-[var(--ivory-100)] hover:bg-[var(--forest-600)] sm:h-9"
        >
          Open Kiosk <ExternalLink className="h-3.5 w-3.5" />
        </Link>
      </div>

      <StaffListCard />
      <AddStaffCard />

      <ComingSoon
        icon={SettingsIcon}
        title="Settings"
        description="Pricing defaults, parking capacity, employees, and roles."
        planned={[
          "Daily / weekly / default monthly pricing",
          "Parking capacity",
          "SMS reminder settings and business hours",
          "Employees, roles, and permissions",
        ]}
      />
    </div>
  );
}
