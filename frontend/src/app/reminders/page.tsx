"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { BellRing, Send, Info, Zap, CheckCircle2 } from "lucide-react";
import { api, ApiError, type RemindersOverview, type SendReminderResult, type SweepResult } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { LoadError } from "@/components/common/load-error";
import { SkeletonRows } from "@/components/common/skeleton-rows";

const currency = (n: number) => n.toLocaleString("en-US", { style: "currency", currency: "USD" });

function daysBadge(days: number) {
  if (days < 0) return { label: `${Math.abs(days)}d overdue`, bg: "var(--danger)", fg: "#fff" };
  if (days === 0) return { label: "Expires today", bg: "var(--danger)", fg: "#fff" };
  if (days <= 3) return { label: `${days}d left`, bg: "var(--warning)", fg: "var(--forest-950)" };
  if (days <= 7) return { label: `${days}d left`, bg: "var(--amber-500)", fg: "var(--forest-950)" };
  return { label: `${days}d left`, bg: "rgba(0,0,0,0.06)", fg: "var(--cream-foreground)" };
}

export default function RemindersPage() {
  const [data, setData] = useState<RemindersOverview | null>(null);
  const [err, setErr] = useState(false);
  const [sendingId, setSendingId] = useState<number | null>(null);
  const [running, setRunning] = useState(false);

  // Was: fabricating {sms_configured:false, customers:[]} on failure — which told
  // the manager SMS was off and nobody was due, when in truth we just couldn't ask.
  function load() {
    setErr(false);
    setData(null);
    api.get<RemindersOverview>("/api/reminders").then(setData).catch(() => setErr(true));
  }
  useEffect(load, []);

  async function sendReminder(id: number, company: string) {
    setSendingId(id);
    try {
      const res = await api.post<SendReminderResult>(`/api/reminders/${id}/send`, {});
      toast.success(res.sent ? `Text sent to ${company}.` : `Reminder recorded for ${company} (SMS not set up yet).`);
      load();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't send reminder.");
    } finally {
      setSendingId(null);
    }
  }

  async function runNow() {
    setRunning(true);
    try {
      const res = await api.post<SweepResult>("/api/reminders/run-now", {});
      toast.success(`Sweep done — ${res.sent} reminder${res.sent === 1 ? "" : "s"} sent, ${res.skipped} skipped.`);
      load();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't run the sweep.");
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Reminders</h1>
          <p className="text-sm text-muted-foreground">
            Monthly customers, sorted by who renews next. Runs automatically — or send one now.
          </p>
        </div>
        <Button variant="outline" onClick={runNow} disabled={running}>
          <Zap className="h-4 w-4" />
          {running ? "Running…" : "Run reminders now"}
        </Button>
      </div>

      {data?.auto_enabled && (
        <div className="flex items-start gap-2 rounded-xl bg-[var(--success)]/10 p-3 text-sm text-[var(--cream-foreground)]">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-[var(--success)]" />
          <span>
            <b>Automatic reminders are on.</b> Every day the system texts each monthly customer a heads-up 7, 3, and 1
            days before renewal, then daily once overdue — each text has their pay-online link. It stops automatically
            the moment they renew.
          </span>
        </div>
      )}

      {data && !data.sms_configured && (
        <div className="flex items-start gap-2 rounded-xl bg-[var(--amber-500)]/10 p-3 text-sm text-[var(--cream-foreground)]">
          <Info className="mt-0.5 h-4 w-4 shrink-0 text-[var(--amber-600)]" />
          <span>
            Text messaging isn&apos;t set up yet, so reminders are recorded but not texted. Add Twilio credentials
            (backend <code>.env</code>) to send real SMS.
          </span>
        </div>
      )}

      <div className="card-paper overflow-hidden rounded-2xl">
        {err ? (
          <div className="p-4">
            <LoadError what="reminders" onRetry={load} />
          </div>
        ) : data === null ? (
          <div className="p-4">
            <SkeletonRows n={4} />
          </div>
        ) : data.customers.length === 0 ? (
          <div className="flex flex-col items-center gap-2 p-10 text-center">
            <BellRing className="h-8 w-8 text-[var(--cream-foreground)]/40" />
            <p className="text-sm text-[var(--cream-foreground)]/60">No monthly customers yet — reminders are only for monthly plans.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-black/10 text-left text-xs uppercase tracking-wide text-[var(--cream-foreground)]/60">
                  <th className="px-4 py-3 font-medium">Company</th>
                  <th className="px-4 py-3 font-medium">Phone</th>
                  <th className="px-4 py-3 font-medium">Renews</th>
                  <th className="px-4 py-3 font-medium">Rate</th>
                  <th className="px-4 py-3 font-medium">Last Reminder</th>
                  <th className="px-4 py-3 font-medium" />
                </tr>
              </thead>
              <tbody>
                {data.customers.map((c) => {
                  const badge = daysBadge(c.days_until_renewal);
                  return (
                    <tr key={c.monthly_customer_id} className="border-b border-black/5 text-[var(--cream-foreground)] last:border-none">
                      <td className="px-4 py-3 font-medium">{c.company_name}</td>
                      <td className="px-4 py-3 font-mono text-[var(--cream-foreground)]/70">{c.phone ?? "—"}</td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <span className="font-mono">{c.renewal_date}</span>
                          <span
                            className="rounded-full px-2 py-0.5 text-xs font-semibold"
                            style={{ background: badge.bg, color: badge.fg }}
                          >
                            {badge.label}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-3 font-mono">{currency(c.monthly_price)}/mo</td>
                      <td className="px-4 py-3 text-[var(--cream-foreground)]/70">
                        {c.last_reminder_at ? c.last_reminder_at.slice(0, 10) : "Never"}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <Button
                          variant="outline"
                          size="sm"
                          disabled={sendingId === c.monthly_customer_id || !c.phone}
                          title={!c.phone ? "No phone number on file" : "Send renewal reminder"}
                          onClick={() => sendReminder(c.monthly_customer_id, c.company_name)}
                        >
                          <Send className="h-3.5 w-3.5" />
                          {sendingId === c.monthly_customer_id ? "Sending…" : "Send Reminder"}
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
