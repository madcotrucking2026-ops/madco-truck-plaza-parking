"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { toast } from "sonner";
import { Phone, Printer, Sun, CheckCircle2, Send } from "lucide-react";
import { api, type CallItem, type MorningReport, type SendReminderResult } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { LoadError } from "@/components/common/load-error";
import { SkeletonRows } from "@/components/common/skeleton-rows";

const currency = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

/** A phone number you can actually dial by tapping it. This page is meant to be
 *  worked through with a phone in one hand. */
const telHref = (phone: string) => `tel:${phone.replace(/[^\d+]/g, "")}`;

const GROUPS: { key: CallItem["priority"]; title: string; blurb: string }[] = [
  { key: "now", title: "Call first", blurb: "Money already owed — these renewals have lapsed." },
  { key: "today", title: "Today", blurb: "Renewals due, and passes running out under trucks on the lot." },
  { key: "worth_a_call", title: "Worth a call", blurb: "Regulars who'd be cheaper — and stickier — on a monthly plan." },
];

export default function MorningReportPage() {
  const [report, setReport] = useState<MorningReport | null>(null);
  const [err, setErr] = useState(false);
  const [sendingId, setSendingId] = useState<number | null>(null);

  function load() {
    setErr(false);
    setReport(null);
    api.get<MorningReport>("/api/insights/morning-report").then(setReport).catch(() => setErr(true));
  }
  useEffect(load, []);

  async function sendReminder(item: CallItem) {
    if (item.monthly_customer_id === null) return;
    setSendingId(item.monthly_customer_id);
    try {
      const res = await api.post<SendReminderResult>(`/api/reminders/${item.monthly_customer_id}/send`, {});
      toast.success(res.sent ? `Text sent to ${item.company_name}.` : `Reminder recorded for ${item.company_name}.`);
    } catch {
      toast.error(`Couldn't send the reminder to ${item.company_name}.`);
    } finally {
      setSendingId(null);
    }
  }

  const dayLabel = report
    ? new Date(`${report.generated_for}T00:00:00`).toLocaleDateString("en-US", {
        weekday: "long",
        month: "long",
        day: "numeric",
      })
    : "";

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight text-foreground">
            <Sun className="h-6 w-6 text-[var(--amber-ink)]" />
            Morning Report
          </h1>
          <p className="text-sm text-muted-foreground">
            {dayLabel ? `${dayLabel} · ` : ""}Everything worth your attention today, in the order money is at risk.
          </p>
        </div>
        <Button variant="outline" onClick={() => window.print()} className="print:hidden">
          <Printer className="h-4 w-4" />
          Print
        </Button>
      </div>

      {err && <LoadError onRetry={load} what="this morning's report" />}

      {!report && !err && <SkeletonRows n={5} />}

      {report && (
        <>
          {/* Money and lot — the two numbers he'd ask for before anything else. */}
          <section className="card-paper grid grid-cols-2 gap-px overflow-hidden rounded-2xl sm:grid-cols-4">
            <Figure label="Yesterday" value={currency(report.yesterday_revenue)} />
            <Figure label="Today so far" value={currency(report.todays_revenue)} />
            <Figure label="This month" value={currency(report.month_to_date_revenue)} />
            <Figure
              label="Spots free"
              value={`${report.available_spaces}`}
              sub={`of ${report.capacity} · ${report.occupied_spaces} parked`}
            />
          </section>

          {report.all_clear ? (
            <section className="card-paper flex flex-col items-center gap-3 rounded-2xl p-10 text-center">
              <CheckCircle2 className="h-12 w-12 text-[var(--success-ink)]" strokeWidth={1.75} />
              <p className="text-lg font-bold text-[var(--cream-foreground)]">Nothing needs you this morning.</p>
              <p className="max-w-sm text-sm text-[var(--cream-foreground)]/60">
                No overdue renewals, nothing expiring today, no one worth converting. Go have your coffee.
              </p>
            </section>
          ) : (
            GROUPS.map((group) => {
              const items = report.calls.filter((c) => c.priority === group.key);
              if (items.length === 0) return null;
              return (
                <section key={group.key} className="card-paper overflow-hidden rounded-2xl">
                  <div className="border-b border-black/5 p-5">
                    <h2 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-[var(--cream-foreground)]/60">
                      {group.title}
                      <span className="rounded-full bg-black/[0.06] px-2 py-0.5 text-xs font-bold tabular-nums text-[var(--cream-foreground)]/70">
                        {items.length}
                      </span>
                    </h2>
                    <p className="mt-1 text-sm text-[var(--cream-foreground)]/60">{group.blurb}</p>
                  </div>

                  {/* Rows stack on a phone. Side by side, the buttons squeezed the reason into
                      a column so narrow that every company name wrapped onto two lines. */}
                  <ul className="divide-y divide-black/5">
                    {items.map((item, i) => (
                      <li
                        key={`${item.kind}-${item.company_id ?? item.monthly_customer_id ?? i}`}
                        className="flex flex-col gap-3 p-4 sm:flex-row sm:flex-wrap sm:items-center"
                      >
                        <div className="min-w-0 flex-1">
                          <p className="font-semibold text-[var(--cream-foreground)]">
                            {item.company_id ? (
                              // inline-block + padding: a 40px hit area without changing the row.
                              <Link
                                href={`/companies/${item.company_id}`}
                                className="inline-block py-2.5 -my-2.5 hover:underline"
                              >
                                {item.company_name}
                              </Link>
                            ) : (
                              item.company_name
                            )}
                          </p>
                          <p className="mt-0.5 text-sm text-[var(--cream-foreground)]/60">{item.reason}</p>
                        </div>

                        <div className="flex flex-wrap items-center gap-2">
                          {item.phone ? (
                            <a
                              href={telHref(item.phone)}
                              className="btn-embossed inline-flex h-11 shrink-0 items-center gap-2 rounded-lg bg-[var(--forest-700)] px-3.5 font-mono text-sm font-semibold text-[var(--ivory-100)] hover:bg-[var(--forest-600)] sm:h-9"
                            >
                              <Phone className="h-4 w-4" />
                              {item.phone}
                            </a>
                          ) : (
                            <span className="text-xs text-[var(--cream-foreground)]/45">no phone on file</span>
                          )}

                          {item.monthly_customer_id !== null && (
                            <Button
                              variant="outline"
                              size="sm"
                              className="shrink-0 print:hidden"
                              disabled={sendingId === item.monthly_customer_id}
                              onClick={() => sendReminder(item)}
                            >
                              <Send className="h-3.5 w-3.5" />
                              {sendingId === item.monthly_customer_id ? "Sending…" : "Text"}
                            </Button>
                          )}
                          {/* nativeButton={false} is required when a Base UI button renders as an anchor. */}
                          {item.pass_id !== null && (
                            <Button
                              variant="outline"
                              size="sm"
                              nativeButton={false}
                              className="shrink-0 print:hidden"
                              render={<Link href="/passes" />}
                            >
                              Renew
                            </Button>
                          )}
                        </div>
                      </li>
                    ))}
                  </ul>
                </section>
              );
            })
          )}
        </>
      )}
    </div>
  );
}

function Figure({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="bg-[var(--cream)]/40 p-5">
      <p className="text-xs font-medium uppercase tracking-wide text-[var(--cream-foreground)]/55">{label}</p>
      <p className="mt-1 font-mono text-2xl font-bold tabular-nums text-[var(--cream-foreground)]">{value}</p>
      {sub && <p className="mt-0.5 text-xs text-[var(--cream-foreground)]/50">{sub}</p>}
    </div>
  );
}
