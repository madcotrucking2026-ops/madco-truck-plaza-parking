/** Loading placeholder shaped like the list rows it replaces, so content
 *  arriving doesn't shift the layout. Announces itself to screen readers;
 *  the pulse stops under prefers-reduced-motion (see globals.css). */
export function SkeletonRows({ n = 3, className }: { n?: number; className?: string }) {
  return (
    <div className={`space-y-2 ${className ?? ""}`} role="status" aria-live="polite">
      <span className="sr-only">Loading…</span>
      {Array.from({ length: n }).map((_, i) => (
        <div
          key={i}
          aria-hidden
          className="h-[62px] animate-pulse rounded-xl border border-black/5 bg-black/[0.03]"
        />
      ))}
    </div>
  );
}
