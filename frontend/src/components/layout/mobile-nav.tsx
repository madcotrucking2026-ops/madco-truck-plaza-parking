"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { LogOut, Menu, Truck } from "lucide-react";
import { cn } from "@/lib/utils";
import { navForRole, type Role } from "@/lib/nav";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { ThemeToggle } from "@/components/theme-toggle";
import { api, type UserRead } from "@/lib/api";
import { clearToken } from "@/lib/auth";

export function MobileNav() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<UserRead | null>(null);

  useEffect(() => {
    api.get<UserRead>("/api/auth/me").then(setUser).catch(() => setUser(null));
  }, []);

  function logout() {
    clearToken();
    setOpen(false);
    router.replace("/login");
  }

  return (
    <header className="panel-steel flex items-center justify-between px-4 py-3 md:hidden">
      <div className="flex items-center gap-2">
        <div className="btn-embossed flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--amber-500)] text-[var(--forest-950)]">
          <Truck className="h-4 w-4" strokeWidth={2.5} />
        </div>
        <span className="text-sm font-semibold text-[var(--ivory-100)]">Madco Truck Plaza</span>
      </div>

      <div className="flex items-center gap-1">
        <ThemeToggle className="text-[var(--ivory-100)] hover:bg-white/10" />
        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger render={<Button variant="ghost" size="icon" className="text-[var(--ivory-100)]" />}>
            <Menu className="h-5 w-5" />
          </SheetTrigger>
        <SheetContent side="left" className="panel-steel w-72 border-white/10 p-0">
          <SheetTitle className="px-5 pt-6 text-[var(--ivory-100)]">Navigation</SheetTitle>
          <nav className="space-y-1 px-3 py-4">
            {navForRole((user?.role as Role) ?? null).map((item) => {
              const active = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setOpen(false)}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    active
                      ? "bg-[var(--amber-500)] text-[var(--forest-950)]"
                      : "text-[var(--stone-300)] hover:bg-white/5 hover:text-[var(--ivory-100)]",
                  )}
                >
                  <Icon className="h-4 w-4" strokeWidth={2} />
                  {item.label}
                </Link>
              );
            })}
            <button
              type="button"
              onClick={logout}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-[var(--stone-300)] transition-colors hover:bg-white/5 hover:text-[var(--ivory-100)]"
            >
              <LogOut className="h-4 w-4" strokeWidth={2} />
              Log out
            </button>
          </nav>
        </SheetContent>
        </Sheet>
      </div>
    </header>
  );
}
