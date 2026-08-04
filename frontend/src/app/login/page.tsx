"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Truck } from "lucide-react";
import { api, ApiError, type AuthStatus, type TokenResponse, type UserRead } from "@/lib/api";
import { setToken } from "@/lib/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field } from "@/components/common/field";

export default function LoginPage() {
  const router = useRouter();
  const [checkingStatus, setCheckingStatus] = useState(true);
  const [needsSetup, setNeedsSetup] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  useEffect(() => {
    api
      .get<AuthStatus>("/api/auth/status")
      .then((s) => setNeedsSetup(s.needs_setup))
      .catch(() => setNeedsSetup(false))
      .finally(() => setCheckingStatus(false));
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (needsSetup) {
      if (!name || !email || !password) {
        toast.error("Name, email, and password are required.");
        return;
      }
      if (password.length < 8) {
        toast.error("Password must be at least 8 characters.");
        return;
      }
      if (password !== confirmPassword) {
        toast.error("Passwords don't match.");
        return;
      }
    } else if (!email || !password) {
      toast.error("Email and password are required.");
      return;
    }

    setSubmitting(true);
    try {
      const res = needsSetup
        ? await api.post<TokenResponse>("/api/auth/register", { name, email, password })
        : await api.post<TokenResponse>("/api/auth/login", { email, password });
      setToken(res.access_token);
      // Land people on their job: the dashboard is manager-tier (revenue), so an
      // The cashier's whole job is issuing passes, so land them there — the
      // dashboard is manager-tier and would 403.
      const who = await api.get<UserRead>("/api/auth/me").catch(() => null);
      router.replace(who?.role === "attendant" ? "/passes/issue" : "/");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-8">
      <div className="w-full max-w-sm space-y-6">
        <div className="flex items-center justify-center gap-3">
          <div className="btn-embossed flex h-10 w-10 items-center justify-center rounded-xl bg-[var(--amber-500)] text-[var(--forest-950)]">
            <Truck className="h-5 w-5" strokeWidth={2.5} />
          </div>
          <div>
            <p className="font-semibold tracking-tight text-foreground">Madco Truck Plaza</p>
            <p className="text-xs text-muted-foreground">Manager Sign In</p>
          </div>
        </div>

        {checkingStatus ? (
          <div className="card-paper rounded-2xl p-6 text-center text-sm text-muted-foreground">Loading…</div>
        ) : (
          <form onSubmit={handleSubmit} className="card-paper space-y-4 rounded-2xl p-6">
            <div>
              <h1 className="text-lg font-semibold text-foreground">
                {needsSetup ? "Create your admin account" : "Sign in"}
              </h1>
              <p className="text-sm text-muted-foreground">
                {needsSetup
                  ? "One-time setup — you'll use these credentials to sign in going forward."
                  : "Manager access only."}
              </p>
            </div>

            {needsSetup && (
              <Field label="Your Name" required>
                <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Nikhil Ganji" />
              </Field>
            )}
            <Field label="Email" required>
              <Input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@madcotruckplaza.com"
              />
            </Field>
            <Field label="Password" required>
              <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            </Field>
            {needsSetup && (
              <Field label="Confirm Password" required>
                <Input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
              </Field>
            )}

            <Button
              type="submit"
              disabled={submitting}
              className="btn-embossed w-full bg-[var(--amber-500)] py-6 text-base font-semibold text-[var(--forest-950)] hover:bg-[var(--amber-600)] disabled:opacity-50"
            >
              {submitting ? "Please wait…" : needsSetup ? "Create Account & Sign In" : "Sign In"}
            </Button>
          </form>
        )}
      </div>
    </div>
  );
}

