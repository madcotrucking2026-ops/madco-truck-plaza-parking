"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { toast } from "sonner";
import { FilePlus2, RefreshCcw, X, QrCode, RotateCw, Search } from "lucide-react";
import { api, ApiError, type PassListItem } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { StatusBadge } from "@/components/passes/status-badge";
import { LoadError } from "@/components/common/load-error";
import { SkeletonRows } from "@/components/common/skeleton-rows";
import { RenewDialog } from "@/components/passes/renew-dialog";
import { PassTicket } from "@/components/passes/pass-ticket";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

const currency = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD" });

export default function PassesPage() {
  const [passes, setPasses] = useState<PassListItem[] | null>(null);
  const [err, setErr] = useState(false);
  const [query, setQuery] = useState("");
  const [renewingPass, setRenewingPass] = useState<PassListItem | null>(null);
  const [viewingPass, setViewingPass] = useState<PassListItem | null>(null);
  const [cancellingId, setCancellingId] = useState<number | null>(null);

  // Desk lookup — filter the already-loaded list by truck/trailer/plate,
  // company, or receipt. (Find a Truck is the separate walk-the-lot tool.)
  const q = query.trim().toLowerCase();
  const filtered = !passes
    ? null
    : !q
      ? passes
      : passes.filter((p) =>
          [p.truck_number, p.trailer_number, p.license_plate, p.company_name, p.receipt_number]
            .some((v) => v?.toLowerCase().includes(q)),
        );

  // Deliberately does NOT null out `passes` — this also runs on window focus, and
  // blanking the list into skeletons every time the manager tabs back is worse
  // than a silent refresh. A failed refresh keeps the last good list on screen;
  // only a failed FIRST load (passes still null) surfaces the error.
  function load() {
    setErr(false);
    api.get<PassListItem[]>("/api/passes").then(setPasses).catch(() => setErr(true));
  }

  // Re-fetch on mount AND whenever the manager returns to this tab/window.
  // A card renewal is often completed by the customer on their own phone
  // (or the manager opens the payment link, leaving this page) — so the list
  // must refresh on focus, not only once on mount, or it shows stale dates.
  useEffect(() => {
    load();
    const refresh = () => document.visibilityState === "visible" && load();
    window.addEventListener("focus", load);
    document.addEventListener("visibilitychange", refresh);
    return () => {
      window.removeEventListener("focus", load);
      document.removeEventListener("visibilitychange", refresh);
    };
  }, []);

  async function cancel(id: number) {
    if (!confirm("Remove this truck from parking? This cancels the pass but keeps its history.")) return;
    setCancellingId(id);
    try {
      await api.post(`/api/passes/${id}/cancel`, {});
      toast.success("Pass cancelled.");
      load();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Failed to cancel pass.");
    } finally {
      setCancellingId(null);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Parking Passes</h1>
          <p className="text-sm text-muted-foreground">Every pass ever issued, newest first.</p>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <Button variant="outline" onClick={load} title="Refresh the list">
            <RotateCw className="h-4 w-4" />
            Refresh
          </Button>
          <Button
            render={<Link href="/passes/issue" />}
            nativeButton={false}
            className="btn-embossed bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)]"
          >
            <FilePlus2 className="h-4 w-4" />
            Issue New Pass
          </Button>
        </div>
      </div>

      <div className="relative max-w-md">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search truck number, company, or receipt…"
          className="h-11 pl-9 sm:h-10"
        />
        {query && (
          <button
            type="button"
            onClick={() => setQuery("")}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      <div className="card-paper overflow-hidden rounded-2xl">
        {err && passes === null ? (
          <div className="p-4">
            <LoadError what="passes" onRetry={load} />
          </div>
        ) : passes === null ? (
          <div className="p-4">
            <SkeletonRows n={5} />
          </div>
        ) : passes.length === 0 ? (
          <p className="p-6 text-sm text-[var(--cream-foreground)]/60">
            No passes issued yet. <Link href="/passes/issue" className="underline">Issue the first one.</Link>
          </p>
        ) : filtered && filtered.length === 0 ? (
          <p className="p-6 text-sm text-[var(--cream-foreground)]/60">
            No pass matches “{query}”.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-black/10 text-left text-xs uppercase tracking-wide text-[var(--cream-foreground)]/60">
                  <th className="px-4 py-3 font-medium">Company</th>
                  <th className="px-4 py-3 font-medium">Truck</th>
                  <th className="px-4 py-3 font-medium">Type</th>
                  <th className="px-4 py-3 font-medium">Price</th>
                  <th className="px-4 py-3 font-medium">Expires</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium" />
                </tr>
              </thead>
              <tbody>
                {(filtered ?? []).map((p) => (
                  <tr key={p.id} className="border-b border-black/5 text-[var(--cream-foreground)] last:border-none">
                    <td className="px-4 py-3">
                      {p.company_id ? (
                        <Link href={`/companies/${p.company_id}`} className="inline-block py-1.5 -my-1.5 hover:underline">
                          {p.company_name ?? "—"}
                        </Link>
                      ) : (
                        p.company_name ?? "—"
                      )}
                    </td>
                    <td className="px-4 py-3 font-mono">{p.truck_number ?? p.trailer_number ?? p.license_plate ?? "—"}</td>
                    <td className="px-4 py-3 capitalize">{p.pass_type}</td>
                    <td className="px-4 py-3 font-mono">{currency(p.price)}</td>
                    <td className="px-4 py-3 font-mono">{p.expiration_date}</td>
                    <td className="px-4 py-3"><StatusBadge status={p.status} /></td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex justify-end gap-2">
                        <Button variant="outline" size="sm" onClick={() => setViewingPass(p)}>
                          <QrCode className="h-3.5 w-3.5" />
                          View
                        </Button>
                        {p.status !== "cancelled" && (
                          <>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setRenewingPass(p)}
                            >
                              <RefreshCcw className="h-3.5 w-3.5" />
                              Renew
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              disabled={cancellingId === p.id}
                              onClick={() => cancel(p.id)}
                              className="text-[var(--danger-ink)] hover:text-[var(--danger-ink)]"
                            >
                              <X className="h-3.5 w-3.5" />
                              Cancel
                            </Button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {renewingPass && (
        <RenewDialog
          pass={renewingPass}
          onOpenChange={(open) => !open && setRenewingPass(null)}
          onRenewed={load}
        />
      )}

      {viewingPass && (
        <Dialog open onOpenChange={(open) => !open && setViewingPass(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Pass</DialogTitle>
            </DialogHeader>
            <PassTicket
              pass={{
                id: viewingPass.id,
                spot_number: viewingPass.spot_number,
                spot_label: viewingPass.spot_label,
                pass_type: viewingPass.pass_type,
                status: viewingPass.status,
                price: viewingPass.price,
                issue_date: viewingPass.issue_date,
                expiration_date: viewingPass.expiration_date,
                receipt_number: viewingPass.receipt_number,
                barcode: null,
                company_name: viewingPass.company_name ?? "—",
                truck_number:
                  viewingPass.truck_number ?? viewingPass.trailer_number ?? viewingPass.license_plate ?? undefined,
              }}
            />
            <Button
              className="btn-embossed w-full bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)]"
              onClick={() => window.print()}
            >
              Print Pass
            </Button>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
