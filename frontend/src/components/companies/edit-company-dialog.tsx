"use client";

import { useState } from "react";
import { toast } from "sonner";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field } from "@/components/common/field";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

/** Fix a company's name or phone after the fact — the cure for a pass issued
 *  with the company left blank. Saving renames the company everywhere, since
 *  every pass and monthly plan links to it by id. */
export function EditCompanyDialog({
  companyId,
  initialName,
  initialPhone,
  onOpenChange,
  onSaved,
}: {
  companyId: string | number;
  initialName: string;
  initialPhone: string | null;
  onOpenChange: (open: boolean) => void;
  onSaved: () => void;
}) {
  const [name, setName] = useState(initialName);
  const [phone, setPhone] = useState(initialPhone ?? "");
  const [saving, setSaving] = useState(false);

  async function save() {
    if (!name.trim()) {
      toast.error("Enter a company name.");
      return;
    }
    setSaving(true);
    try {
      await api.patch<{ id: number }>(`/api/companies/${companyId}`, {
        name: name.trim(),
        phone: phone.trim() || null,
      });
      toast.success("Company updated.");
      onSaved();
      onOpenChange(false);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't save — try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit company</DialogTitle>
          <DialogDescription>
            Fix the name or phone. It updates every pass and monthly plan under this company.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <Field label="Company name" labelClassName="text-popover-foreground">
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. ABC Logistics" autoFocus />
          </Field>
          <Field label="Phone" labelClassName="text-popover-foreground">
            <Input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="Optional" />
          </Field>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            className="btn-embossed bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)]"
            disabled={saving}
            onClick={save}
          >
            {saving ? "Saving…" : "Save"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
