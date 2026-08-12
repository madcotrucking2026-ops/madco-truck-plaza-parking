"use client";

import { useState } from "react";
import { toast } from "sonner";
import { api, ApiError, type PassListItem } from "@/lib/api";
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

/** Manager/owner correction of a pass's dates or price — e.g. fixing a pass left
 *  wrong by the old renewal bug. Money isn't touched (use Void for that); every
 *  edit is audit-logged server-side. */
export function EditPassDialog({
  pass,
  onOpenChange,
  onSaved,
}: {
  pass: PassListItem;
  onOpenChange: (open: boolean) => void;
  onSaved: () => void;
}) {
  const [issueDate, setIssueDate] = useState(pass.issue_date);
  const [endDate, setEndDate] = useState(pass.expiration_date);
  const [price, setPrice] = useState(String(pass.price));
  const [saving, setSaving] = useState(false);

  async function save() {
    setSaving(true);
    try {
      await api.patch(`/api/passes/${pass.id}`, {
        issue_date: issueDate,
        end_date: endDate,
        price: price === "" ? undefined : Number(price),
      });
      toast.success("Pass updated.");
      onSaved();
      onOpenChange(false);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't update the pass.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit pass</DialogTitle>
          <DialogDescription>
            {pass.company_name ?? "—"} · truck{" "}
            {pass.truck_number ?? pass.trailer_number ?? pass.license_plate ?? "—"}
          </DialogDescription>
        </DialogHeader>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Issue date" labelClassName="text-popover-foreground">
            <Input type="date" value={issueDate} onChange={(e) => setIssueDate(e.target.value)} />
          </Field>
          <Field label="Expiration date" labelClassName="text-popover-foreground">
            <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} min={issueDate} />
          </Field>
          <Field label="Price ($)" labelClassName="text-popover-foreground" className="sm:col-span-2">
            <Input type="number" min={0} step="0.01" value={price} onChange={(e) => setPrice(e.target.value)} />
          </Field>
        </div>

        <p className="text-xs text-muted-foreground">
          Corrects the pass only — the money isn&rsquo;t touched. To fix a payment, use Void on the Payments page.
          Every edit is logged.
        </p>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            disabled={saving}
            className="btn-embossed bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)]"
            onClick={save}
          >
            {saving ? "Saving…" : "Save changes"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
