"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import {
  DollarSign,
  CalendarClock,
  TrendingUp,
  FilePlus2,
  Search,
  UserPlus,
  ClipboardList,
  AlarmClock,
  Send,
  RefreshCcw,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";
import {
  api,
  ApiError,
  type ConversionLeads,
  type DashboardStats,
  type PassListItem,
  type PassRead,
  type RemindersOverview,
  type SendReminderResult,
  type StrandedCharge,
} from "@/lib/api";
import { toast } from "sonner";
import { StatCard } from "@/components/dashboard/stat-card";
import { StatusBadge } from "@/components/passes/status-badge";
import { RenewDialog } from "@/components/passes/renew-dialog";
import { BulkRenewDialog } from "@/components/passes/bulk-renew-dialog";
import { Button } from "@/components/ui/button";
import { LoadError } from "@/components/common/load-error";
import { SkeletonRows } from "@/components/common/skeleton-rows";
import { InfoTip } from "@/components/common/info-tip";
import { addDaysISO, todayISO } from "@/lib/pricing";

const QUICK_ACTIONS = [
  { label: "Issue Pass", href: "/passes/issue", icon: FilePlus2 },
  { label: "Search a Truck", href: "/lot-check", icon: Search },
  { label: "Add Monthly Customer", href: "/passes/issue?type=monthly", icon: UserPlus },
  { label: "All Passes", href: "/passes", icon: ClipboardList },
];

const currency = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

// Both of these used to read the UTC date, so all evening the dashboard's
// "expiring today / tomorrow" lists were a day ahead of the plaza.
const relativeDayISO = (days: number) => addDaysISO(todayISO(), days);

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [passes, setPasses] = useState<PassListItem[] | null>(null);
  const [reminders, setReminders] = useState<RemindersOverview | null>(null);
  const [leads, setLeads] = useState<ConversionLeads | null>(null);
  // Per-section failure flags. A failed fetch must NEVER fall through to the
  // section's empty state — "All caught up" when the API is down is a false
  // all-clear on the one screen whose job is telling the manager what's wrong.
  const [statsErr, setStatsErr] = useState(false);
  const [passesErr, setPassesErr] = useState(false);
  const [remindersErr, setRemindersErr] = useState(false);
  const [leadsErr, setLeadsErr] = useState(false);

  const [stranded, setStranded] = useState<StrandedCharge[]>([]);
  const [repairing, setRepairing] = useState<string | null>(null);

  const [renewingPass, setRenewingPass] = useState<PassListItem | null>(null);
  const [sendingId, setSendingId] = useState<number | null>(null);
  const [confirmingId, setConfirmingId] = useState<number | null>(null);
  const confirmTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  // Clearing the expiring-passes list is this screen's whole job, so it can be
  // done in one pass instead of one dialog per truck.
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [bulkOpen, setBulkOpen] = useState(false);

  function toggleSelected(id: number, on: boolean) {
    setSelected((s) => {
      const next = new Set(s);
      if (on) next.add(id);
      else next.delete(id);
      return next;
    });
  }

  function loadAll() {
    setStatsErr(false);
    setPassesErr(false);
    setRemindersErr(false);
    setLeadsErr(false);
    setStats(null);
    setPasses(null);
    setReminders(null);
    setLeads(null);
    api.get<DashboardStats>("/api/dashboard/stats").then(setStats).catch(() => setStatsErr(true));
    api.get<PassListItem[]>("/api/passes").then(setPasses).catch(() => setPassesErr(true));
    api.get<RemindersOverview>("/api/reminders").then(setReminders).catch(() => setRemindersErr(true));
    api.get<ConversionLeads>("/api/insights/conversion-leads").then(setLeads).catch(() => setLeadsErr(true));
    // Cards Stripe charged that produced no pass. Always expected to be empty, so
    // it stays silent — no card, no zero-state, nothing — unless it isn't.
    api.get<StrandedCharge[]>("/api/payments/stripe/stranded").then(setStranded).catch(() => setStranded([]));
  }
  useEffect(loadAll, []);
  useEffect(() => () => clearTimeout(confirmTimer.current ?? undefined), []);

  const today = todayISO();
  const tomorrow = relativeDayISO(1);

  // The action list: passes expiring today or tomorrow (not cancelled), soonest
  // first. This is what the manager actually does something about right now.
  const needsAttention = (passes ?? [])
    .filter((p) => p.status !== "cancelled" && (p.expiration_date === today || p.expiration_date === tomorrow))
    .sort((a, b) => a.expiration_date.localeCompare(b.expiration_date));

  const upcomingRenewals = (reminders?.customers ?? [])
    .filter((c) => c.days_until_renewal <= 10)
    .slice(0, 6);

  // Texting a customer can't be undone, so it takes two taps: the first arms the
  // button, the second sends. Inline (no modal), auto-disarms after 4s.
  function armConfirm(id: number) {
    setConfirmingId(id);
    clearTimeout(confirmTimer.current ?? undefined);
    confirmTimer.current = setTimeout(() => setConfirmingId(null), 4000);
  }

  async function sendReminder(id: number, company: string) {
    setConfirmingId(null);
    setSendingId(id);
    try {
      const res = await api.post<SendReminderResult>(`/api/reminders/${id}/send`, {});
      toast.success(res.sent ? `Text sent to ${company}.` : `Reminder recorded for ${company}.`);
    } catch {
      toast.error(`Couldn't send the reminder to ${company}.`);
    } finally {
      setSendingId(null);
    }
  }

  async function issueStrandedPass(charge: StrandedCharge) {
    setRepairing(charge.payment_intent_id);
    try {
      const pass = await api.post<PassRead>(
        `/api/payments/stripe/stranded/${charge.payment_intent_id}/issue`,
        {},
      );
      toast.success(`Pass issued — receipt ${pass.receipt_number}`);
      setStranded((list) => list.filter((c) => c.payment_intent_id !== charge.payment_intent_id));
      loadAll();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't issue the pass. Try again.");
    } finally {
      setRepairing(null);
    }
  }

  // Never render a number we don't have — a placeholder $0 reads as "no revenue".
  const money = (v: number | undefined) => (stats ? currency(v ?? 0) : "—");

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Dispatch Dashboard</h1>
        <p className="text-sm text-muted-foreground">Madco Truck Plaza &middot; 27416 Ecorse Rd, Romulus, MI</p>
      </div>

      {/* Above everything else on the screen: a customer who paid and got nothing
          outranks revenue, renewals and leads. Renders only when it has to. */}
      {stranded.length > 0 && (
        <section className="space-y-3 rounded-xl border border-[var(--danger)]/40 bg-[var(--danger)]/10 p-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0 text-[var(--danger-ink)]" />
            <h2 className="text-sm font-semibold text-[var(--danger-ink)]">
              {stranded.length === 1 ? "A card was charged" : `${stranded.length} cards were charged`} with no pass
              issued
            </h2>
          </div>
          <p className="text-sm text-[var(--danger-ink)]/90">
            Stripe took the money but the pass never got created. Issue it now — the customer already paid.
          </p>
          <ul className="space-y-2">
            {stranded.map((charge) => {
              const needsHuman = charge.reason.includes("needs a human");
              return (
                <li
                  key={charge.payment_intent_id}
                  className="flex flex-wrap items-center gap-3 rounded-lg bg-[var(--cream)] p-3"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-[var(--cream-foreground)]">
                      {charge.company_name ?? "Unknown company"}
                      {charge.vehicle ? ` · ${charge.vehicle}` : ""}
                    </p>
                    <p className="text-xs text-[var(--cream-foreground)]/60">{charge.reason}</p>
                  </div>
                  <span className="font-mono text-sm font-bold tabular-nums text-[var(--cream-foreground)]">
                    {currency(charge.amount)}
                  </span>
                  {/* A mismatched amount is the one case a click must not paper over. */}
                  {needsHuman ? (
                    <span className="text-xs font-medium text-[var(--danger-ink)]">Check with Stripe</span>
                  ) : (
                    <Button
                      size="sm"
                      className="min-h-11 shrink-0"
                      disabled={repairing !== null}
                      onClick={() => issueStrandedPass(charge)}
                    >
                      {repairing === charge.payment_intent_id ? "Issuing…" : "Issue the pass"}
                    </Button>
                  )}
                </li>
              );
            })}
          </ul>
        </section>
      )}

      {statsErr && (
        <div className="flex items-center gap-3 rounded-xl border border-[var(--danger)]/30 bg-[var(--danger)]/10 px-4 py-3">
          <AlertTriangle className="h-4 w-4 shrink-0 text-[var(--danger-ink)]" />
          <p className="flex-1 text-sm text-[var(--danger-ink)]">
            Can&rsquo;t reach the system, so today&rsquo;s numbers aren&rsquo;t loading.
          </p>
          <Button variant="outline" size="sm" className="min-h-11 shrink-0" onClick={loadAll}>
            Retry
          </Button>
        </div>
      )}

      {/* Tight group: how you start, and how the day's going. */}
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {QUICK_ACTIONS.map((action) => (
            <Button
              key={action.label}
              render={<Link href={action.href} />}
              nativeButton={false}
              className="btn-embossed h-auto flex-col gap-2 rounded-xl bg-[var(--forest-700)] py-4 text-[var(--ivory-100)] hover:bg-[var(--forest-600)]"
            >
              <action.icon className="h-5 w-5" strokeWidth={2.25} />
              <span className="text-xs font-semibold">{action.label}</span>
            </Button>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatCard label="Today's Revenue" value={money(stats?.todays_revenue)} icon={DollarSign} accent="orange" />
          <StatCard label="This Week" value={money(stats?.weekly_revenue)} icon={CalendarClock} accent="forest" />
          <StatCard label="This Month" value={money(stats?.monthly_revenue)} icon={TrendingUp} accent="forest" />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* THE screen's primary job. Deliberately the loudest thing here. */}
        <section className="card-paper rounded-2xl p-6 lg:col-span-2">
          <div className="mb-4 flex items-start gap-3">
            <AlarmClock className="mt-0.5 h-5 w-5 shrink-0 text-[var(--danger)]" />
            <div className="min-w-0 flex-1">
              <h2 className="text-lg font-semibold leading-tight text-[var(--cream-foreground)]">Needs attention</h2>
              <p className="text-xs text-[var(--cream-foreground)]/55">Passes expiring today &amp; tomorrow</p>
            </div>
            {selected.size > 0 ? (
              <div className="flex shrink-0 items-center gap-2">
                <Button variant="ghost" size="sm" className="min-h-11" onClick={() => setSelected(new Set())}>
                  Clear
                </Button>
                <Button
                  size="sm"
                  className="btn-embossed min-h-11 bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)]"
                  onClick={() => setBulkOpen(true)}
                >
                  <RefreshCcw className="h-3.5 w-3.5" />
                  Renew {selected.size}
                </Button>
              </div>
            ) : (
              needsAttention.length > 0 && (
                <span className="rounded-full bg-[var(--danger)] px-2.5 py-1 text-sm font-bold tabular-nums text-white">
                  {needsAttention.length}
                </span>
              )
            )}
          </div>

          {passesErr ? (
            <LoadError what="expiring passes" onRetry={loadAll} />
          ) : passes === null ? (
            <SkeletonRows n={3} />
          ) : needsAttention.length === 0 ? (
            <div className="flex flex-col items-center gap-2 py-10 text-center">
              <CheckCircle2 className="h-8 w-8 text-[var(--success)]" />
              <p className="text-sm text-[var(--cream-foreground)]/70">
                All caught up — nothing expiring today or tomorrow.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {needsAttention.map((p) => (
                <div key={p.id} className={ROW}>
                  <input
                    type="checkbox"
                    checked={selected.has(p.id)}
                    onChange={(e) => toggleSelected(p.id, e.target.checked)}
                    aria-label={`Select ${p.company_name ?? "this pass"} for bulk renewal`}
                    className="h-5 w-5 shrink-0 cursor-pointer accent-[var(--forest-700)]"
                  />
                  <div className="min-w-0 flex-1">
                    {p.company_id ? (
                      <Link
                        href={`/companies/${p.company_id}`}
                        className={`block truncate font-medium text-[var(--cream-foreground)] ${LINK}`}
                      >
                        {p.company_name ?? "—"}
                      </Link>
                    ) : (
                      <p className="truncate font-medium text-[var(--cream-foreground)]">{p.company_name ?? "—"}</p>
                    )}
                    <p className="truncate font-mono text-xs text-[var(--cream-foreground)]/60">
                      {p.truck_number ?? p.trailer_number ?? p.license_plate ?? "—"} · {p.pass_type}
                    </p>
                  </div>
                  <div className="shrink-0 text-right">
                    <StatusBadge status={p.status} />
                    <p className="mt-0.5 text-xs text-[var(--cream-foreground)]/60">
                      {p.expiration_date === today ? "expires today" : "expires tomorrow"}
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    className="min-h-11 shrink-0"
                    onClick={() => setRenewingPass(p)}
                  >
                    <RefreshCcw className="h-3.5 w-3.5" />
                    Renew
                  </Button>
                </div>
              ))}
            </div>
          )}
        </section>

        <div className="space-y-6">
          <section className="card-paper rounded-2xl p-5">
            <div className="mb-3 flex items-center gap-1">
              <h2 className={SUBHEAD}>Lot snapshot</h2>
              <InfoTip label="How occupancy is measured">
                Counts every pass that hasn&rsquo;t expired yet. The bar runs green, turns amber past 85% full,
                and red once the lot is at or over capacity. Capacity is set with <code>PARKING_CAPACITY</code>.
              </InfoTip>
            </div>

            {statsErr ? (
              <LoadError what="lot status" onRetry={loadAll} />
            ) : (
              <>
                {/* Lead with the number a manager actually needs when a truck
                    pulls in: is there room? Occupied + capacity live under it,
                    so the old duplicate "trucks on lot" row is gone. */}
                <div className="mb-4">
                  <div className="flex items-baseline gap-2">
                    <span className="font-mono text-3xl font-semibold tabular-nums text-[var(--cream-foreground)]">
                      {stats?.available_spaces ?? "—"}
                    </span>
                    <span className="text-sm text-[var(--cream-foreground)]/60">
                      spots free of {stats?.capacity ?? "—"}
                    </span>
                  </div>
                  <div className="mt-2 h-2 overflow-hidden rounded-full bg-black/5">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${Math.min(stats?.occupancy_pct ?? 0, 100)}%`,
                        backgroundColor:
                          (stats?.occupancy_pct ?? 0) >= 100
                            ? "var(--danger)"
                            : (stats?.occupancy_pct ?? 0) >= 85
                              ? "var(--amber-500)"
                              : "var(--forest-700)",
                      }}
                    />
                  </div>
                  <p className="mt-1.5 text-xs text-[var(--cream-foreground)]/55">
                    {stats?.occupied_spaces ?? "—"} parked · {stats?.occupancy_pct ?? 0}% full
                  </p>
                </div>

                <div className="space-y-3">
                  <SnapshotRow
                    icon={CalendarClock}
                    label="Active monthly plans"
                    value={stats?.active_monthly_passes ?? "—"}
                  />
                  <SnapshotRow
                    icon={UserPlus}
                    label="Companies to call"
                    value={stats?.companies_needing_follow_up ?? "—"}
                    hint="Companies you've flagged on their profile as needing a call — unpaid balance, a dispute, anything worth chasing."
                  />
                </div>
              </>
            )}
          </section>

          <section className="card-paper rounded-2xl p-5">
            <div className="mb-3 flex items-center justify-between">
              <h2 className={SUBHEAD}>Renewals due soon</h2>
              <Link href="/reminders" className={`text-xs text-[var(--amber-ink)] ${LINK}`}>
                View all
              </Link>
            </div>
            {remindersErr ? (
              <LoadError what="renewals" onRetry={loadAll} />
            ) : reminders === null ? (
              <SkeletonRows n={2} />
            ) : upcomingRenewals.length === 0 ? (
              <p className="text-sm text-[var(--cream-foreground)]/60">No monthly renewals in the next 10 days.</p>
            ) : (
              <div className="space-y-2">
                {upcomingRenewals.map((c) => {
                  const arming = confirmingId === c.monthly_customer_id;
                  const sending = sendingId === c.monthly_customer_id;
                  return (
                    <div key={c.monthly_customer_id} className={ROW}>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-[var(--cream-foreground)]">{c.company_name}</p>
                        <p className="truncate text-xs text-[var(--cream-foreground)]/60">
                          {c.days_until_renewal < 0
                            ? `${Math.abs(c.days_until_renewal)}d overdue`
                            : c.days_until_renewal === 0
                              ? "renews today"
                              : `in ${c.days_until_renewal}d`}
                          {" · "}
                          {c.renewal_date}
                        </p>
                      </div>
                      <Button
                        variant={arming ? "default" : "outline"}
                        size="sm"
                        className={`min-h-11 shrink-0 ${arming ? "btn-embossed bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)]" : ""}`}
                        disabled={sending || !c.phone}
                        title={!c.phone ? "No phone on file" : undefined}
                        aria-label={
                          !c.phone
                            ? `No phone on file for ${c.company_name}`
                            : arming
                              ? `Confirm sending a renewal text to ${c.company_name}`
                              : `Text a renewal reminder to ${c.company_name}`
                        }
                        onClick={() =>
                          arming
                            ? sendReminder(c.monthly_customer_id, c.company_name)
                            : armConfirm(c.monthly_customer_id)
                        }
                      >
                        {sending ? (
                          "Sending…"
                        ) : arming ? (
                          "Send text?"
                        ) : (
                          <>
                            <Send className="h-3.5 w-3.5" />
                            Remind
                          </>
                        )}
                      </Button>
                    </div>
                  );
                })}
              </div>
            )}
          </section>
        </div>
      </div>

      <ConversionOpportunities leads={leads} failed={leadsErr} onRetry={loadAll} />

      {renewingPass && (
        <RenewDialog
          pass={renewingPass}
          onOpenChange={(open) => !open && setRenewingPass(null)}
          onRenewed={loadAll}
        />
      )}

      {bulkOpen && selected.size > 0 && (
        <BulkRenewDialog
          passes={needsAttention.filter((p) => selected.has(p.id))}
          onOpenChange={(open) => {
            if (!open) {
              setBulkOpen(false);
              setSelected(new Set());
            }
          }}
          onRenewed={loadAll}
        />
      )}
    </div>
  );
}

/* One list-row vocabulary for every list on this screen. */
const ROW = "flex items-center gap-3 rounded-xl border border-black/5 bg-black/[0.015] p-3";
/* Secondary section heading — quieter than "Needs attention" on purpose, and
   deliberately not the uppercase-tracked kicker that every section used to wear. */
const SUBHEAD = "text-sm font-medium text-[var(--cream-foreground)]/70";
/* Links need a visible keyboard focus ring, not just a hover underline. */
const LINK =
  "rounded-sm hover:underline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--amber-500)]";

function SnapshotRow({
  icon: Icon,
  label,
  value,
  hint,
}: {
  icon: typeof CalendarClock;
  label: string;
  value: number | string;
  hint?: React.ReactNode;
}) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-black/5 text-[var(--cream-foreground)]/70">
        <Icon className="h-4 w-4" />
      </div>
      {/* Deliberately NOT truncated: a label clipped to "Companies to foll…"
          has stopped labelling anything. Let it wrap in the narrow column. */}
      <span className="min-w-0 flex-1 text-sm leading-snug text-[var(--cream-foreground)]/70">{label}</span>
      {hint && <InfoTip label={`What "${label}" means`}>{hint}</InfoTip>}
      <span className="font-mono text-lg font-semibold tabular-nums text-[var(--cream-foreground)]">{value}</span>
    </div>
  );
}

const LEAD_TIER: Record<string, { label: string; className: string }> = {
  hot: { label: "Hot", className: "bg-[var(--amber-500)]/15 text-[var(--amber-600)]" },
  warm: { label: "Warm", className: "bg-[var(--forest-700)]/12 text-[var(--forest-700)]" },
  cold: { label: "Cold", className: "bg-black/5 text-[var(--cream-foreground)]/60" },
};

function ConversionOpportunities({
  leads,
  failed,
  onRetry,
}: {
  leads: ConversionLeads | null;
  failed: boolean;
  onRetry: () => void;
}) {
  const money = (n: number) =>
    n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

  return (
    <section className="card-paper rounded-2xl p-5">
      <div className="mb-4 flex items-center gap-2">
        <TrendingUp className="h-4 w-4 shrink-0 text-[var(--forest-700)]" />
        <h2 className={SUBHEAD}>Worth a monthly pitch</h2>
        <InfoTip label="How these leads are ranked">
          Daily &amp; weekly companies with 3+ visits in the last 90 days that aren&rsquo;t already on a monthly plan.
          <strong className="mt-1 block">Hot</strong> — already spends as much as a monthly plan, or 8+ visits.
          <strong className="mt-1 block">Warm</strong> — 5+ visits. <strong className="mt-1 block">Cold</strong> — 3+ visits, on the radar.
        </InfoTip>
      </div>
      {failed ? (
        <LoadError what="conversion leads" onRetry={onRetry} />
      ) : leads === null ? (
        <SkeletonRows n={3} />
      ) : leads.leads.length === 0 ? (
        <p className="text-sm text-[var(--cream-foreground)]/60">
          Nobody to pitch right now — frequent visitors show up here automatically.
        </p>
      ) : (
        <div className="space-y-2">
          {leads.leads.map((l) => {
            const tier = LEAD_TIER[l.tier] ?? LEAD_TIER.cold;
            return (
              <div key={l.company_id} className={ROW}>
                <span className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold ${tier.className}`}>
                  {tier.label}
                </span>
                <div className="min-w-0 flex-1">
                  <Link
                    href={`/companies/${l.company_id}`}
                    className={`block truncate font-medium text-[var(--cream-foreground)] ${LINK}`}
                  >
                    {l.company_name}
                  </Link>
                  <p className="truncate text-xs text-[var(--cream-foreground)]/60">
                    {l.visits} visits · {money(l.total_spent)} in {leads.window_days}d
                    {l.phone ? ` · ${l.phone}` : ""}
                  </p>
                </div>
                {/* Both numbers, side by side — so the owner can see at a glance
                    whether a monthly plan would actually save this customer money. */}
                <p className="shrink-0 whitespace-nowrap text-right font-mono text-sm text-[var(--cream-foreground)]">
                  <span className="text-[var(--cream-foreground)]/55">{money(l.current_monthly_equivalent)}/mo now</span>
                  <span className="mx-1.5 text-[var(--cream-foreground)]/35">→</span>
                  <span className="font-semibold">{money(l.suggested_monthly)}/mo</span>
                </p>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
