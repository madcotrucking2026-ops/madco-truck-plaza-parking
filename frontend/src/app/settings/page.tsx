import { AddStaffCard } from "@/components/settings/add-staff-card";
import { StaffListCard } from "@/components/settings/staff-list-card";
import { PlazaSettingsCard } from "@/components/settings/plaza-settings-card";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground">Staff logins, pricing defaults, and lot capacity.</p>
      </div>
      <PlazaSettingsCard />
      <StaffListCard />
      <AddStaffCard />
    </div>
  );
}
