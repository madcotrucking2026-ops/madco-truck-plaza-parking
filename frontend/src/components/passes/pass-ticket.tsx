import type { PassRead } from "@/lib/api";

export function PassTicket({
  pass,
}: {
  pass: PassRead & { company_name: string; truck_number?: string };
}) {
  return (
    <div className="card-paper rounded-2xl p-6 print:shadow-none">
      <div className="flex items-start justify-between border-b border-dashed border-black/15 pb-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-[var(--cream-foreground)]/60">
            Madco Truck Plaza
          </p>
          <h2 className="text-lg font-bold text-[var(--cream-foreground)]">Parking Pass</h2>
        </div>
        <span
          className="rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wide"
          style={{
            background: pass.status === "active" ? "var(--success)" : "var(--amber-500)",
            color: "white",
          }}
        >
          {pass.status.replace("_", " ")}
        </span>
      </div>

      {/* The spot is what the driver actually needs — big enough to read from a cab. */}
      {pass.spot_number != null && (
        <div className="mt-4 rounded-xl bg-[var(--forest-700)] p-4 text-center">
          <p className="text-xs font-semibold uppercase tracking-widest text-[var(--ivory-100)]/70">
            Park in spot
          </p>
          <p className="font-mono text-5xl font-bold tabular-nums text-[var(--ivory-100)]">
            {pass.spot_label ?? pass.spot_number}
          </p>
        </div>
      )}

      <dl className="mt-4 space-y-2 text-sm">
        <Row label="Company" value={pass.company_name} />
        {pass.truck_number && <Row label="Truck Number" value={pass.truck_number} />}
        <Row label="Pass Type" value={pass.pass_type} className="capitalize" />
        <Row label="Issue Date" value={pass.issue_date} />
        <Row label="Expiration Date" value={pass.expiration_date} />
        <Row label="Price" value={`$${pass.price.toFixed(2)}`} />
        <Row label="Receipt #" value={pass.receipt_number ?? "—"} />
      </dl>
    </div>
  );
}

function Row({ label, value, className }: { label: string; value: string; className?: string }) {
  return (
    <div className="flex items-center justify-between">
      <dt className="text-[var(--cream-foreground)]/60">{label}</dt>
      <dd className={`font-medium text-[var(--cream-foreground)] ${className ?? ""}`}>{value}</dd>
    </div>
  );
}
