import type { LucideIcon } from "lucide-react";

export function ComingSoon({
  icon: Icon,
  title,
  description,
  planned,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
  planned: string[];
}) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground">{title}</h1>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>

      <div className="card-paper flex flex-col items-center gap-4 rounded-2xl p-12 text-center">
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[var(--forest-700)]/10 text-[var(--forest-700)]">
          <Icon className="h-7 w-7" strokeWidth={2} />
        </div>
        <div>
          <p className="font-semibold text-[var(--cream-foreground)]">Coming soon</p>
          <p className="mx-auto mt-1 max-w-md text-sm text-[var(--cream-foreground)]/60">
            This screen isn&apos;t built yet. Here&apos;s what&apos;s planned:
          </p>
        </div>
        <ul className="mx-auto max-w-md space-y-1.5 text-left text-sm text-[var(--cream-foreground)]/80">
          {planned.map((item) => (
            <li key={item} className="flex items-start gap-2">
              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-[var(--amber-500)]" />
              {item}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
