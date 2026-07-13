"use client";

import { useEffect, useId, useRef, useState } from "react";
import { HelpCircle } from "lucide-react";

/** Contextual help for a number or label that isn't self-explanatory.
 *
 *  Click/tap to toggle — deliberately NOT hover-only, which would leave touch
 *  and keyboard users with no way to read it. Escape and click-outside close it.
 */
export function InfoTip({ label, children }: { label: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!open) return;
    function onPointerDown(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <span ref={ref} className="relative inline-flex shrink-0">
      <button
        type="button"
        aria-label={label}
        aria-expanded={open}
        aria-controls={id}
        onClick={() => setOpen((o) => !o)}
        // A 24px dot is the right amount of ink, but a thumb needs 44px. The
        // before: pseudo-element grows the tap target without growing the icon.
        className="relative inline-flex h-6 w-6 items-center justify-center rounded-full text-[var(--cream-foreground)]/45 transition-colors before:absolute before:-inset-2.5 before:content-[''] hover:bg-black/5 hover:text-[var(--cream-foreground)]/70 focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-[var(--amber-500)] sm:before:hidden"
      >
        <HelpCircle className="h-3.5 w-3.5" />
      </button>
      {open && (
        // Not role="tooltip": a tooltip is described-by and hover-driven. This is a
        // disclosure the button owns via aria-expanded + aria-controls.
        <span
          id={id}
          className="absolute left-1/2 top-full z-30 mt-1.5 w-60 -translate-x-1/2 rounded-lg border border-black/10 bg-[#fffdf8] p-2.5 text-xs font-normal leading-relaxed text-[var(--cream-foreground)]/80 shadow-lg"
        >
          {children}
        </span>
      )}
    </span>
  );
}
