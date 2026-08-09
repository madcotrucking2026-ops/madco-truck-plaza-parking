"use client";

import { useState } from "react";
import { toast } from "sonner";
import { DatabaseBackup } from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";

/** One-click backup: downloads every record (companies, trucks, passes,
 *  payments) as a ZIP of CSV files the owner keeps on their own drive. The
 *  safety net for the free hosting tier — admin-only, enforced by the API. */
export function BackupCard() {
  const [busy, setBusy] = useState(false);

  async function run() {
    setBusy(true);
    try {
      const today = new Date().toISOString().slice(0, 10);
      await api.download("/api/export", `madco-backup-${today}.zip`);
      toast.success("Backup downloaded — keep it somewhere safe.");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't build the backup — try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card-paper space-y-4 rounded-2xl p-6">
      <div className="flex items-center gap-2">
        <DatabaseBackup className="h-5 w-5 shrink-0 text-[var(--forest-700)]" />
        <div>
          <h2 className="text-lg font-semibold text-[var(--cream-foreground)]">Backup your data</h2>
          <p className="text-xs text-[var(--cream-foreground)]/60">
            Download every record as spreadsheet files to keep on your own computer.
          </p>
        </div>
      </div>

      <p className="text-xs text-[var(--cream-foreground)]/55">
        You get a ZIP with one sheet each for companies, trucks, passes, and payments — openable in
        Excel or Google Sheets. Do this now and then so you always hold your own copy.
      </p>

      <Button
        type="button"
        onClick={run}
        disabled={busy}
        className="btn-embossed bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)]"
      >
        {busy ? "Preparing…" : "Download backup"}
      </Button>
    </section>
  );
}
