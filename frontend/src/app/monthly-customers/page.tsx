"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { UserPlus } from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";

type MonthlyCustomer = {
  id: number;
  company_name: string;
  monthly_price: number;
  number_of_trucks: number;
  renewal_date: string;
  status: string;
  reminder_status: string;
  current_balance: number;
};

const currency = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD" });

const STATUS_LABEL: Record<string, string> = {
  holding_spot: "Holding Spot",
  truck_parked: "Truck Parked",
  trailer_parked: "Trailer Parked",
  away: "Away",
  inactive: "Inactive",
};

export default function MonthlyCustomersPage() {
  const [customers, setCustomers] = useState<MonthlyCustomer[] | null>(null);

  useEffect(() => {
    api
      .get<MonthlyCustomer[]>("/api/monthly-customers")
      .then(setCustomers)
      .catch(() => setCustomers([]));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Monthly Customers</h1>
          <p className="text-sm text-muted-foreground">Companies on a recurring monthly parking plan.</p>
        </div>
        <Button
          render={<Link href="/passes/issue?type=monthly" />}
          nativeButton={false}
          className="btn-embossed shrink-0 bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)]"
        >
          <UserPlus className="h-4 w-4" />
          New Monthly Customer
        </Button>
      </div>

      <div className="card-paper overflow-hidden rounded-2xl">
        {customers === null ? (
          <p className="p-6 text-sm text-[var(--cream-foreground)]/60">Loading…</p>
        ) : customers.length === 0 ? (
          <p className="p-6 text-sm text-[var(--cream-foreground)]/60">
            No monthly customers yet. Click <span className="font-semibold">New Monthly Customer</span> above to add one.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-black/10 text-left text-xs uppercase tracking-wide text-[var(--cream-foreground)]/60">
                  <th className="px-4 py-3 font-medium">Company</th>
                  <th className="px-4 py-3 font-medium">Trucks</th>
                  <th className="px-4 py-3 font-medium">Monthly Price</th>
                  <th className="px-4 py-3 font-medium">Renewal Date</th>
                  <th className="px-4 py-3 font-medium">Spot Status</th>
                  <th className="px-4 py-3 font-medium">Balance</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((c) => (
                  <tr key={c.id} className="border-b border-black/5 text-[var(--cream-foreground)] last:border-none">
                    <td className="px-4 py-3">{c.company_name}</td>
                    <td className="px-4 py-3 font-mono">{c.number_of_trucks}</td>
                    <td className="px-4 py-3 font-mono">{currency(c.monthly_price)}</td>
                    <td className="px-4 py-3 font-mono">{c.renewal_date}</td>
                    <td className="px-4 py-3">{STATUS_LABEL[c.status] ?? c.status}</td>
                    <td className="px-4 py-3 font-mono">{currency(c.current_balance)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
