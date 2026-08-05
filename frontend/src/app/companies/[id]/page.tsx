"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Phone, Star, Truck } from "lucide-react";
import { api, ApiError, type CompanyProfile } from "@/lib/api";
import { StatusBadge } from "@/components/passes/status-badge";
import { LoadError } from "@/components/common/load-error";
import { SkeletonRows } from "@/components/common/skeleton-rows";
import { InfoTip } from "@/components/common/info-tip";

const money = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
const money2 = (n: number) => n.toLocaleString("en-US", { style: "currency", currency: "USD" });
const fmtDate = (iso: string | null) =>
  iso ? new Date(`${iso}T00:00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) : "—";
const fmtDateTime = (iso: string) =>
  new Date(iso).toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });

export default function CompanyProfilePage() {
  const params = useParams<{ id: string }>();
  const id = params?.id;
  const [p, setP] = useState<CompanyProfile | null>(null);
  const [err, setErr] = useState(false);
  const [notFound, setNotFound] = useState(false);

  // A network failure is NOT "company not found" — that would tell the manager a
  // real customer doesn't exist just because the API is down.
  const load = useCallback(() => {
    if (!id) return;
    setErr(false);
    setNotFound(false);
    setP(null);
    api
      .get<CompanyProfile>(`/api/companies/${id}/profile`)
      .then(setP)
      .catch((e) => {
        if (e instanceof ApiError && e.status === 404) setNotFound(true);
        else setErr(true);
      });
  }, [id]);
  useEffect(load, [load]);

  if (notFound) return <p className="text-sm text-[var(--danger-ink)]">Company not found.</p>;
  if (err)
    return (
      <div className="max-w-3xl">
        <LoadError what="this company" onRetry={load} />
      </div>
    );
  if (!p)
    return (
      <div className="max-w-3xl">
        <SkeletonRows n={4} />
      </div>
    );

  return (
    <div className="max-w-3xl space-y-6">
      <Link
        href="/companies"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" /> All companies
      </Link>

      <div className="card-paper rounded-2xl p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <h1 className="truncate text-2xl font-semibold tracking-tight text-[var(--cream-foreground)]">{p.name}</h1>
            <div className="mt-1 flex flex-wrap items-center gap-3 text-sm text-[var(--cream-foreground)]/60">
              {p.phone && (
                <span className="inline-flex items-center gap-1">
                  <Phone className="h-3.5 w-3.5" />
                  {p.phone}
                </span>
              )}
              {p.is_monthly && (
                <span className="rounded-full bg-[var(--forest-700)]/12 px-2 py-0.5 text-xs font-semibold text-[var(--forest-700)]">
                  Monthly · {p.monthly_price != null ? money(p.monthly_price) : "—"}/mo
                </span>
              )}
            </div>
          </div>
          <div className="shrink-0 text-right">
            <div className="inline-flex items-center gap-1 text-[var(--amber-ink)]">
              <Star className="h-4 w-4" />
              <span className="font-mono text-lg font-bold tabular-nums">{p.loyalty_score}</span>
              <InfoTip label="How the loyalty score is calculated">
                A rough 0–100 score from how often they park (each visit counts 4) and how many passes they have
                active right now (each counts 10). Higher means a more regular customer — it&rsquo;s a nudge, not a
                credit rating.
              </InfoTip>
            </div>
            <p className="text-xs text-[var(--cream-foreground)]/55">loyalty</p>
          </div>
        </div>
        {p.outstanding_balance > 0 && (
          <p className="mt-3 rounded-lg bg-[var(--danger)]/10 p-2 text-sm text-[var(--danger-ink)]">
            Outstanding balance: {money2(p.outstanding_balance)}
          </p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Stat label="Total Visits" value={String(p.total_visits)} />
        <Stat label="Total Spent" value={money(p.total_spent)} />
        <Stat label="Active Passes" value={String(p.active_passes)} />
        <Stat label="Since" value={fmtDate(p.first_seen)} />
      </div>

      <Section title="Trucks">
        {p.trucks.length === 0 ? (
          <Empty>No vehicles.</Empty>
        ) : (
          <ul className="divide-y divide-black/5">
            {p.trucks.map((t, i) => (
              <li key={i} className="flex items-center gap-3 py-2.5">
                <Truck className="h-4 w-4 shrink-0 text-[var(--cream-foreground)]/50" />
                <span className="flex-1 truncate font-mono text-sm text-[var(--cream-foreground)]">
                  {t.truck_number ?? t.license_plate ?? t.trailer_number ?? "—"}
                </span>
                <span className="shrink-0 text-xs text-[var(--cream-foreground)]/55">
                  {t.visits} visit{t.visits === 1 ? "" : "s"} · last {fmtDate(t.last_seen)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title="Recent Passes">
        {p.recent_passes.length === 0 ? (
          <Empty>No passes yet.</Empty>
        ) : (
          <ul className="divide-y divide-black/5">
            {p.recent_passes.map((pass) => (
              <li key={pass.id} className="flex items-center gap-3 py-2.5">
                <StatusBadge status={pass.status} />
                <div className="min-w-0 flex-1">
                  <p className="text-sm capitalize text-[var(--cream-foreground)]">{pass.pass_type}</p>
                  <p className="text-xs text-[var(--cream-foreground)]/55">
                    {fmtDate(pass.issue_date)} → {fmtDate(pass.expiration_date)}
                  </p>
                </div>
                <span className="shrink-0 font-mono text-sm text-[var(--cream-foreground)]">{money2(pass.price)}</span>
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title="Recent Payments">
        {p.recent_payments.length === 0 ? (
          <Empty>No payments yet.</Empty>
        ) : (
          <ul className="divide-y divide-black/5">
            {p.recent_payments.map((pay, i) => (
              <li key={i} className="flex items-center gap-3 py-2.5">
                <div className="min-w-0 flex-1">
                  <p className="text-sm capitalize text-[var(--cream-foreground)]">{pay.method.replace(/_/g, " ")}</p>
                  <p className="text-xs text-[var(--cream-foreground)]/55">
                    {fmtDateTime(pay.paid_at)}
                    {pay.receipt_number ? ` · ${pay.receipt_number}` : ""}
                  </p>
                </div>
                <span className="shrink-0 font-mono text-sm font-semibold text-[var(--cream-foreground)]">
                  {money2(pay.amount)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Section>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="card-paper rounded-xl p-3">
      <p className="text-xs text-[var(--cream-foreground)]/55">{label}</p>
      <p className="mt-1 font-mono text-lg font-semibold tabular-nums text-[var(--cream-foreground)]">{value}</p>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="card-paper rounded-2xl p-5">
      <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-[var(--cream-foreground)]/70">{title}</h2>
      {children}
    </section>
  );
}

function Empty({ children }: { children: React.ReactNode }) {
  return <p className="py-2 text-sm text-[var(--cream-foreground)]/55">{children}</p>;
}
