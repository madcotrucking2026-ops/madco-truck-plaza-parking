import { Settings as SettingsIcon } from "lucide-react";
import { ComingSoon } from "@/components/coming-soon";
import { AddStaffCard } from "@/components/settings/add-staff-card";
import { StaffListCard } from "@/components/settings/staff-list-card";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
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
