"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { SlidersHorizontal } from "lucide-react";
import { api, ApiError, type AppSettings } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field } from "@/components/common/field";

/** Owner-editable defaults: the lot size and the daily/weekly/monthly base
 *  prices. Only an admin can save (the API enforces it); other roles never see
 *  this page. */
export function PlazaSettingsCard() {
  const [form, setForm] = useState<AppSettings | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api.get<AppSettings>("/api/settings").then(setForm).catch(() => setForm(null));
  }, []);

  function set<K extends keyof AppSettings>(key: K, value: string) {
    setForm((f) => (f ? { ...f, [key]: value === "" ? 0 : Number(value) } : f));
  }

  async function save(e: React.FormEvent) {
    e.preventDefault();
    if (!form) return;
    setSaving(true);
    try {
      const saved = await api.put<AppSettings>("/api/settings", form);
      setForm(saved);
      toast.success("Settings saved.");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't save settings — try again.");
    } finally {
      setSaving(false);
    }
  }

  if (!form) return null;

  return (
    <form onSubmit={save} className="card-paper space-y-5 rounded-2xl p-6">
      <div className="flex items-center gap-2">
        <SlidersHorizontal className="h-5 w-5 shrink-0 text-[var(--forest-700)]" />
        <div>
          <h2 className="text-lg font-semibold text-[var(--cream-foreground)]">Pricing &amp; capacity</h2>
          <p className="text-xs text-[var(--cream-foreground)]/60">The size of your lot and the base prices for new passes.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Parking capacity (total spots)" required>
          <Input type="number" min={1} step="1" value={form.parking_capacity}
            onChange={(e) => set("parking_capacity", e.target.value)} />
        </Field>
        <Field label="Daily price ($)" required>
          <Input type="number" min={0} step="0.01" value={form.daily_price}
            onChange={(e) => set("daily_price", e.target.value)} />
        </Field>
        <Field label="Weekly price ($)" required>
          <Input type="number" min={0} step="0.01" value={form.weekly_price}
            onChange={(e) => set("weekly_price", e.target.value)} />
        </Field>
        <Field label="Default monthly price ($)" required>
          <Input type="number" min={0} step="0.01" value={form.monthly_price}
            onChange={(e) => set("monthly_price", e.target.value)} />
        </Field>
      </div>

      <p className="text-xs text-[var(--cream-foreground)]/55">
        Monthly is priced per truck at the register — this is only the starting suggestion. Changing
        capacity repaints the lot: spots above the new number are retired, never deleted.
      </p>

      <Button type="submit" disabled={saving}
        className="btn-embossed bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)]">
        {saving ? "Saving…" : "Save settings"}
      </Button>
    </form>
  );
}
