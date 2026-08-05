"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DollarSign, Ticket, Wallet, Building2 } from "lucide-react";
import { api, type ReportsSummary } from "@/lib/api";
import { StatCard } from "@/components/dashboard/stat-card";
import { RevenueChart } from "@/components/reports/revenue-chart";
import { LoadError } from "@/components/common/load-error";
import { SkeletonRows } from "@/components/common/skeleton-rows";

const currency = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD" });

const METHOD_LABEL: Record<string, string> = {
  cash: "Cash",
  credit_card: "Credit Card",
  debit_card: "Debit Card",
  check: "Check",
  phone: "Card over Phone",
};

export default function ReportsPage() {
  const [data, setData] = useState<ReportsSummary | null>(null);
  const [err, setErr] = useState(false);

  // Was: .catch(() => setData(null)) — which left the page stuck on "Loading…"
  // forever, because null is also the loading state.
  function load() {
    setErr(false);
    setData(null);
    api.get<ReportsSummary>("/api/reports/summary").then(setData).catch(() => setErr(true));
  }
  useEffect(load, []);

  if (err) {
    return (
      <div className="max-w-2xl">
        <LoadError what="reports" onRetry={load} />
      </div>
    );
  }
  if (!data) {
    return (
      <div className="max-w-2xl">
        <SkeletonRows n={4} />
      </div>
    );
  }

  const maxMethodTotal = Math.max(...data.payment_methods.map((m) => m.total), 1);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Reports</h1>
        <p className="text-sm text-muted-foreground">Revenue, companies, and vehicle trends — last 30 days.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatCard label="Revenue (30d)" value={currency(data.revenue_30d)} icon={DollarSign} accent="orange" />
        <StatCard label="Passes Issued (30d)" value={data.passes_30d} icon={Ticket} accent="forest" />
        <StatCard label="Avg. Pass Price" value={currency(data.avg_price)} icon={Wallet} accent="steel" />
        <StatCard label="Active Companies" value={data.active_companies} icon={Building2} accent="forest" />
      </div>

      <section className="card-paper rounded-2xl p-5">
        <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-[var(--cream-foreground)]/60">
          Daily Revenue — Last 30 Days
        </h2>
        <RevenueChart data={data.revenue_series} />
      </section>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section className="card-paper rounded-2xl p-5">
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-[var(--cream-foreground)]/60">
            Payment Methods
          </h2>
          {data.payment_methods.length === 0 ? (
            <p className="text-sm text-[var(--cream-foreground)]/60">No payments recorded yet.</p>
          ) : (
            <div className="space-y-3">
              {data.payment_methods.map((m) => (
                <div key={m.method}>
                  <div className="mb-1 flex items-center justify-between text-sm text-[var(--cream-foreground)]">
                    <span>{METHOD_LABEL[m.method] ?? m.method}</span>
                    <span className="font-mono">
                      {currency(m.total)} <span className="text-[var(--cream-foreground)]/50">({m.count})</span>
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-black/5">
                    <div
                      className="h-full rounded-full bg-[var(--forest-700)]"
                      style={{ width: `${Math.max((m.total / maxMethodTotal) * 100, 3)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="card-paper rounded-2xl p-5">
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wide text-[var(--cream-foreground)]/60">
            Most Frequent Trucks
          </h2>
          {data.frequent_trucks.length === 0 ? (
            <p className="text-sm text-[var(--cream-foreground)]/60">No trucks recorded yet.</p>
          ) : (
            <table className="w-full text-sm">
              <tbody>
                {data.frequent_trucks.map((t) => (
                  <tr key={`${t.truck_number}-${t.company_name}`} className="border-b border-black/5 last:border-none">
                    <td className="py-2 font-mono text-[var(--cream-foreground)]">{t.truck_number ?? "—"}</td>
                    <td className="py-2 text-[var(--cream-foreground)]/70">{t.company_name ?? "—"}</td>
                    <td className="py-2 text-right text-[var(--cream-foreground)]">
                      <span className="font-mono tabular-nums">{t.visits}</span> visit{t.visits === 1 ? "" : "s"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </div>

      <section className="card-paper overflow-hidden rounded-2xl">
        <h2 className="p-5 pb-0 text-sm font-semibold uppercase tracking-wide text-[var(--cream-foreground)]/60">
          Top Companies by Revenue
        </h2>
        {data.top_companies.length === 0 ? (
          <p className="p-5 text-sm text-[var(--cream-foreground)]/60">No companies recorded yet.</p>
        ) : (
          <div className="overflow-x-auto p-5">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-black/10 text-left text-xs uppercase tracking-wide text-[var(--cream-foreground)]/60">
                  <th className="pb-2 font-medium">Company</th>
                  <th className="pb-2 font-medium">Visits</th>
                  <th className="pb-2 text-right font-medium">Total Paid</th>
                </tr>
              </thead>
              <tbody>
                {data.top_companies.map((c) => (
                  <tr key={c.company_name} className="border-b border-black/5 text-[var(--cream-foreground)] last:border-none">
                    <td className="py-2">
                      {c.company_id ? (
                        <Link href={`/companies/${c.company_id}`} className="inline-block py-1.5 -my-1.5 hover:underline">
                          {c.company_name}
                        </Link>
                      ) : (
                        c.company_name
                      )}
                    </td>
                    <td className="py-2 font-mono">{c.visits}</td>
                    <td className="py-2 text-right font-mono">{currency(c.total_paid)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {data.outstanding_balances.length > 0 && (
        <section className="card-paper overflow-hidden rounded-2xl">
          <h2 className="p-5 pb-0 text-sm font-semibold uppercase tracking-wide text-[var(--danger-ink)]">
            Outstanding Balances
          </h2>
          <div className="overflow-x-auto p-5">
            <table className="w-full text-sm">
              <tbody>
                {data.outstanding_balances.map((b) => (
                  <tr key={b.company_name} className="border-b border-black/5 text-[var(--cream-foreground)] last:border-none">
                    <td className="py-2">{b.company_name}</td>
                    <td className="py-2 text-right font-mono text-[var(--danger-ink)]">{currency(b.balance)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
