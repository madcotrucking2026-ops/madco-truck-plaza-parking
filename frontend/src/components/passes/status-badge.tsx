import { cn } from "@/lib/utils";

const STATUS_STYLE: Record<string, { label: string; className: string }> = {
  active: { label: "Active", className: "bg-[var(--success)]/15 text-[var(--success)]" },
  expiring_soon: { label: "Expiring Soon", className: "bg-[var(--warning)]/15 text-[var(--warning)]" },
  expired: { label: "Expired", className: "bg-[var(--danger)]/15 text-[var(--danger-ink)]" },
  cancelled: { label: "Cancelled", className: "bg-muted text-muted-foreground" },
};

export function StatusBadge({ status }: { status: string }) {
  const style = STATUS_STYLE[status] ?? { label: status, className: "bg-muted text-muted-foreground" };
  return (
    <span className={cn("rounded-full px-2.5 py-1 text-xs font-semibold", style.className)}>
      {style.label}
    </span>
  );
}
