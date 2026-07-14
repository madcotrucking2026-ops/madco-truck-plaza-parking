import { cn } from "@/lib/utils";

// A tinted chip carries its own words, so the words must use the -ink twin of the
// hue, never the bright fill colour. Measured on the cream card: --success as text
// is 2.5:1, and --warning is 1.7:1 — a yellow "Expiring Soon" chip was effectively
// unreadable, which is the one status a manager most needs to catch at a glance.
const STATUS_STYLE: Record<string, { label: string; className: string }> = {
  active: { label: "Active", className: "bg-[var(--success)]/15 text-[var(--success-ink)]" },
  expiring_soon: { label: "Expiring Soon", className: "bg-[var(--warning)]/20 text-[var(--warning-ink)]" },
  expired: { label: "Expired", className: "bg-[var(--danger)]/15 text-[var(--danger-ink)]" },
  cancelled: { label: "Cancelled", className: "bg-black/[0.06] text-[var(--cream-foreground)]/70" },
};

export function StatusBadge({ status }: { status: string }) {
  const style = STATUS_STYLE[status] ?? {
    label: status,
    className: "bg-black/[0.06] text-[var(--cream-foreground)]/70",
  };
  return (
    <span className={cn("rounded-full px-2.5 py-1 text-xs font-semibold", style.className)}>{style.label}</span>
  );
}
