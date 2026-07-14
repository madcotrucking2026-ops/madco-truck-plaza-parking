"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { navForRole, type Role } from "@/lib/nav";
import { LogOut, Search, Truck } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { openCommandPalette } from "@/lib/command-palette-events";
import { api, type UserRead } from "@/lib/api";
import { clearToken } from "@/lib/auth";

export function SidebarNav() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<UserRead | null>(null);

  useEffect(() => {
    api
      .get<UserRead>("/api/auth/me")
      .then(setUser)
      .catch(() => setUser(null));
  }, []);

  function logout() {
    clearToken();
    router.replace("/login");
  }

  return (
    <aside className="panel-steel hidden w-64 shrink-0 flex-col md:flex">
      <div className="flex items-center gap-3 px-5 py-6">
        <div className="btn-embossed flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--amber-500)] text-[var(--forest-950)]">
          <Truck className="h-5 w-5" strokeWidth={2.5} />
        </div>
        <div className="min-w-0 flex-1 leading-tight">
          <p className="truncate font-semibold tracking-tight text-[var(--ivory-100)]">Madco Truck Plaza</p>
          <p className="text-xs text-[var(--stone-300)]">Parking Management</p>
        </div>
      </div>

      <div className="px-3">
        <button
          type="button"
          onClick={openCommandPalette}
          className="flex w-full items-center gap-2 rounded-lg bg-white/5 px-3 py-2 text-sm text-[var(--stone-300)] transition-colors hover:bg-white/10 hover:text-[var(--ivory-100)]"
        >
          <Search className="h-4 w-4" strokeWidth={2} />
          <span className="flex-1 text-left">Search everywhere</span>
          <kbd className="rounded border border-white/15 px-1.5 py-0.5 font-mono text-[10px]">⌘K</kbd>
        </button>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-2">
        {navForRole((user?.role as Role) ?? null).map((item) => {
          const active = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                active
                  ? "bg-[var(--amber-500)] text-[var(--forest-950)] shadow-sm"
                  : "text-[var(--stone-300)] hover:bg-white/5 hover:text-[var(--ivory-100)]",
              )}
            >
              <Icon className="h-4 w-4" strokeWidth={2} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-white/10 px-5 py-4 text-xs text-[var(--stone-300)]">
        <div className="flex items-center justify-between">
          <span>
            27416 Ecorse Rd
            <br />
            Romulus, MI 48174
          </span>
          <ThemeToggle className="shrink-0 text-[var(--ivory-100)] hover:bg-white/10" />
        </div>
        {user && (
          <div className="mt-3 flex items-center justify-between gap-2 border-t border-white/10 pt-3">
            <span className="truncate text-[var(--ivory-100)]">{user.name}</span>
            <button
              type="button"
              onClick={logout}
              className="flex shrink-0 items-center gap-1 rounded-lg px-2 py-1 text-[var(--stone-300)] transition-colors hover:bg-white/10 hover:text-[var(--ivory-100)]"
            >
              <LogOut className="h-3.5 w-3.5" strokeWidth={2} />
              Log out
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
