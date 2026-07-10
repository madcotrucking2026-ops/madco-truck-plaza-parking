"use client";

import { useEffect, useState } from "react";
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
  Truck,
} from "lucide-react";
import {
  api,
  type ConversionLeads,
  type DashboardStats,
  type PassListItem,
  type RemindersOverview,
  type SendReminderResult,
} from "@/lib/api";
import { toast } from "sonner";
import { StatCard } from "@/components/dashboard/stat-card";
import { StatusBadge } from "@/components/passes/status-badge";
import { RenewDialog } from "@/components/passes/renew-dialog";
import { Button } from "@/components/ui/button";

const QUICK_ACTIONS = [
  { label: "Issue Pass", href: "/passes/issue", icon: FilePlus2 },
  { label: "Search a Truck", href: "/lot-check", icon: Search },
  { label: "Add Monthly Customer", href: "/passes/issue?type=monthly", icon: UserPlus },
  { label: "All Passes", href: "/passes", icon: ClipboardList },
];

const currency = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

const todayISO = () => new Date().toISOString().slice(0, 10);
const addDaysISO = (days: number) => {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
};

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [passes, setPasses] = useState<PassListItem[] | null>(null);
  const [reminders, setReminders] = useState<RemindersOverview | null>(null);
  const [leads, setLeads] = useState<ConversionLeads | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [renewingPass, setRenewingPass] = useState<PassListItem | null>(null);
  const [sendingId, setSendingId] = useState<number | null>(null);

  function loadAll() {
    api.get<DashboardStats>("/api/dashboard/stats").then(setStats).catch(() =>
      setError("Could not reach the backend API. Is it running on port 8000?"),
    );
    api.get<PassListItem[]>("/api/passes").then(setPasses).catch(() => setPasses([]));
    api.get<RemindersOverview>("/api/reminders").then(setReminders).catch(() => setReminders(null));
    api.get<ConversionLeads>("/api/insights/conversion-leads").then(setLeads).catch(() => setLeads(null));
  }
  useEffect(loadAll, []);

  const today = todayISO();
  const tomorrow = addDaysISO(1);

  // The action list: passes expiring today or tomorrow (not cancelled), soonest
  // first. This is what the manager actually does something about right now.
  const needsAttention = (passes ?? [])
    .filter((p) => p.status !== "cancelled" && (p.expiration_date === today || p.expiration_date === tomorrow))
    .sort((a, b) => a.expiration_date.localeCompare(b.expiration_date));

  // Upcoming monthly renewals within ~10 days — money to secure.
  const upcomingRenewals = (reminders?.customers ?? [])
    .filter((c) => c.days_until_renewal <= 10)
    .slice(0, 6);

  async function sendReminder(id: number, company: string) {
    setSendingId(id);
    try {
      const res = await api.post<SendReminderResult>(`/api/reminders/${id}/send`, {});
      toast.success(res.sent ? `Text sent to ${company}.` : `Reminder recorded for ${company}.`);
    } catch {
      toast.error("Couldn't send reminder.");
    } finally {
      setSendingId(null);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Dispatch Dashboard</h1>
        <p className="text-sm text-muted-foreground">Madco Truck Plaza &middot; 27416 Ecorse Rd, Romulus, MI</p>
      </div>

      {error && (
        <div className="rounded-xl border border-[var(--danger)]/30 bg-[var(--danger)]/10 px-4 py-3 text-sm text-[var(--danger-ink)]">{error}</div>
      )}

      {/* Quick actions — the few things a manager starts from */}
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

      {/* Money — three real windows */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="Today's Revenue" value={currency(stats?.todays_revenue ?? 0)} icon={DollarSign} accent="orange" />
        <StatCard label="This Week" value={currency(stats?.weekly_revenue ?? 0)} icon={CalendarClock} accent="forest" />
        <StatCard label="This Month" value={currency(stats?.monthly_revenue ?? 0)} icon={TrendingUp} accent="forest" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Needs attention — the actionable centerpiece (2/3 width) */}
        <section className="card-paper rounded-2xl p-5 lg:col-span-2">
          <div className="mb-4 flex items-center gap-2">
            <AlarmClock className="h-4 w-4 text-[var(--danger)]" />
            <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--cream-foreground)]/70">
              Needs Attention — Expiring Today &amp; Tomorrow
            </h2>
            {needsAttention.length > 0 && (
              <span className="ml-auto rounded-full bg-[var(--danger)] px-2 py-0.5 text-xs font-bold text-white">
                {needsAttention.length}
              </span>
            )}
          </div>
          {passes === null ? (
            <p className="text-sm text-[var(--cream-foreground)]/60">Loading…</p>
          ) : needsAttention.length === 0 ? (
            <div className="flex flex-col items-center gap-2 py-8 text-center">
              <CheckCircle2 className="h-8 w-8 text-[var(--success)]" />
              <p className="text-sm text-[var(--cream-foreground)]/70">All caught up — nothing expiring today or tomorrow.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {needsAttention.map((p) => (
                <div
                  key={p.id}
                  className="flex items-center gap-3 rounded-xl border border-black/5 bg-black/[0.015] p-3"
                >
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-[var(--cream-foreground)]">{p.company_name ?? "—"}</p>
                    <p className="font-mono text-xs text-[var(--cream-foreground)]/60">
                      {p.truck_number ?? p.trailer_number ?? p.license_plate ?? "—"} · {p.pass_type}
                    </p>
                  </div>
                  <div className="text-right">
                    <StatusBadge status={p.status} />
                    <p className="mt-0.5 text-xs text-[var(--cream-foreground)]/60">
                      {p.expiration_date === today ? "expires today" : "expires tomorrow"}
                    </p>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => setRenewingPass(p)}>
                    <RefreshCcw className="h-3.5 w-3.5" />
                    Renew
                  </Button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Side column: lot snapshot + upcoming renewals */}
        <div className="space-y-6">
          <section className="card-paper rounded-2xl p-5">
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-[var(--cream-foreground)]/70">
              Lot Snapshot
            </h2>
            <div className="space-y-3">
              <SnapshotRow icon={Truck} label="Trucks on lot" value={stats?.occupied_spaces ?? "—"} />
              <SnapshotRow
                icon={CalendarClock}
                label="Active monthly plans"
                value={stats?.active_monthly_passes ?? "—"}
              />
              <SnapshotRow
                icon={UserPlus}
                label="Companies to follow up"
                value={stats?.companies_needing_follow_up ?? "—"}
              />
            </div>
          </section>

          <section className="card-paper rounded-2xl p-5">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--cream-foreground)]/70">
                Renewals Due Soon
              </h2>
              <Link href="/reminders" className="text-xs text-[var(--amber-600)] hover:underline">
                View all
              </Link>
            </div>
            {upcomingRenewals.length === 0 ? (
              <p className="text-sm text-[var(--cream-foreground)]/60">No monthly renewals in the next 10 days.</p>
            ) : (
              <div className="space-y-2">
                {upcomingRenewals.map((c) => (
                  <div key={c.monthly_customer_id} className="flex items-center gap-2">
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-[var(--cream-foreground)]">{c.company_name}</p>
                      <p className="text-xs text-[var(--cream-foreground)]/60">
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
                      variant="ghost"
                      size="sm"
                      disabled={sendingId === c.monthly_customer_id || !c.phone}
                      title={!c.phone ? "No phone on file" : "Send reminder"}
                      onClick={() => sendReminder(c.monthly_customer_id, c.company_name)}
                    >
                      <Send className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>

      {/* Conversion opportunities — daily/weekly customers worth a monthly pitch */}
      <ConversionOpportunities leads={leads} />

      {renewingPass && (
        <RenewDialog
          pass={renewingPass}
          onOpenChange={(open) => !open && setRenewingPass(null)}
          onRenewed={loadAll}
        />
      )}
    </div>
  );
}

function SnapshotRow({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Truck;
  label: string;
  value: number | string;
}) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-black/5 text-[var(--cream-foreground)]/70">
        <Icon className="h-4 w-4" />
      </div>
      <span className="flex-1 text-sm text-[var(--cream-foreground)]/70">{label}</span>
      <span className="font-mono text-lg font-semibold text-[var(--cream-foreground)]">{value}</span>
    </div>
  );
}

const LEAD_TIER: Record<string, { label: string; className: string }> = {
  hot: { label: "Hot", className: "bg-[var(--amber-500)]/15 text-[var(--amber-600)]" },
  warm: { label: "Warm", className: "bg-[var(--forest-700)]/12 text-[var(--forest-700)]" },
  cold: { label: "Cold", className: "bg-black/5 text-[var(--cream-foreground)]/60" },
};

function ConversionOpportunities({ leads }: { leads: ConversionLeads | null }) {
  const money = (n: number) =>
    n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

  return (
    <section className="card-paper rounded-2xl p-5">
      <div className="mb-1 flex items-center gap-2">
        <TrendingUp className="h-4 w-4 text-[var(--forest-700)]" />
        <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--cream-foreground)]/70">
          Conversion Opportunities
        </h2>
      </div>
      <p className="mb-4 text-xs text-[var(--cream-foreground)]/50">
        Daily &amp; weekly customers who come often enough to pitch a monthly plan.
      </p>
      {leads === null ? (
        <p className="text-sm text-[var(--cream-foreground)]/60">Loading…</p>
      ) : leads.leads.length === 0 ? (
        <p className="text-sm text-[var(--cream-foreground)]/60">
          Nobody to pitch right now — frequent visitors show up here automatically.
        </p>
      ) : (
        <div className="space-y-2">
          {leads.leads.map((l) => {
            const tier = LEAD_TIER[l.tier] ?? LEAD_TIER.cold;
            return (
              <div
                key={l.company_id}
                className="flex items-center gap-3 rounded-xl border border-black/5 bg-black/[0.015] p-3"
              >
                <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${tier.className}`}>
                  {tier.label}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium text-[var(--cream-foreground)]">{l.company_name}</p>
                  <p className="text-xs text-[var(--cream-foreground)]/60">
                    {l.visits} visits · {money(l.total_spent)} in {leads.window_days}d
                    {l.phone ? ` · ${l.phone}` : ""}
                  </p>
                </div>
                <p className="whitespace-nowrap text-right font-mono text-sm font-semibold text-[var(--cream-foreground)]">
                  {money(l.suggested_monthly)}/mo
                </p>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
