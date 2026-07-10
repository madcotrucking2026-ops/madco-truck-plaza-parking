"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Building2, ChevronRight, Search } from "lucide-react";
import { api, type CompanySummary } from "@/lib/api";
import { Input } from "@/components/ui/input";

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<CompanySummary[] | null>(null);
  const [q, setQ] = useState("");

  useEffect(() => {
    api
      .get<CompanySummary[]>("/api/companies")
      .then(setCompanies)
      .catch(() => setCompanies([]));
  }, []);

  const needle = q.trim().toLowerCase();
  const filtered = (companies ?? []).filter(
    (c) => c.name.toLowerCase().includes(needle) || (c.phone ?? "").includes(q.trim()),
  );

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">Companies</h1>
        <p className="text-sm text-muted-foreground">
          Every company that&rsquo;s parked here — open one for its full history.
        </p>
      </div>

      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search company or phone…"
          className="pl-9"
        />
      </div>

      <div className="card-paper rounded-2xl p-2">
        {companies === null ? (
          <p className="p-4 text-sm text-[var(--cream-foreground)]/60">Loading…</p>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center gap-2 p-10 text-center">
            <Building2 className="h-8 w-8 text-[var(--cream-foreground)]/40" />
            <p className="text-sm text-[var(--cream-foreground)]/70">
              {companies.length === 0 ? "No companies yet." : "No matches."}
            </p>
          </div>
        ) : (
          <ul className="divide-y divide-black/5">
            {filtered.map((c) => (
              <li key={c.id}>
                <Link
                  href={`/companies/${c.id}`}
                  className="flex items-center gap-3 rounded-xl p-3 transition-colors hover:bg-black/[0.025]"
                >
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[var(--forest-700)]/10 text-[var(--forest-700)]">
                    <Building2 className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-[var(--cream-foreground)]">{c.name}</p>
                    {c.phone && <p className="text-xs text-[var(--cream-foreground)]/55">{c.phone}</p>}
                  </div>
                  <ChevronRight className="h-4 w-4 shrink-0 text-[var(--cream-foreground)]/40" />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
