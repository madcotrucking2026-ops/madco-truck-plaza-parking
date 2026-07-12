"use client";

import { AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";

/** A section that failed to load says so — it must never fall through to the
 *  section's empty state, which would read as a legitimate "nothing here". */
export function LoadError({ what, onRetry }: { what: string; onRetry: () => void }) {
  return (
    <div
      role="alert"
      className="flex items-center gap-3 rounded-xl border border-[var(--danger)]/20 bg-[var(--danger)]/[0.06] p-3"
    >
      <AlertTriangle className="h-4 w-4 shrink-0 text-[var(--danger-ink)]" />
      <p className="flex-1 text-sm text-[var(--danger-ink)]">Couldn&rsquo;t load {what}.</p>
      <Button variant="outline" size="sm" className="min-h-11 shrink-0" onClick={onRetry}>
        Retry
      </Button>
    </div>
  );
}
