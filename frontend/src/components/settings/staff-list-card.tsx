"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { KeyRound, Users } from "lucide-react";
import { api, ApiError, type UserRead } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field } from "@/components/common/field";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

/** Who can sign in, and the fix for "I forgot my password" — handled at the desk
 *  by the owner, because a truck stop has no password-reset email to send. The
 *  owner's OWN lockout is the one case this can't cover; that's
 *  scripts/reset_password.py on the server. */
export function StaffListCard() {
  const [me, setMe] = useState<UserRead | null>(null);
  const [users, setUsers] = useState<UserRead[] | null>(null);
  const [resetting, setResetting] = useState<UserRead | null>(null);
  const [newPassword, setNewPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api.get<UserRead>("/api/auth/me").then(setMe).catch(() => setMe(null));
  }, []);

  const isAdmin = me?.role === "admin";

  useEffect(() => {
    if (!isAdmin) return;
    api.get<UserRead[]>("/api/auth/users").then(setUsers).catch(() => setUsers(null));
  }, [isAdmin]);

  if (!isAdmin) return null;

  async function handleReset() {
    if (!resetting) return;
    if (newPassword.length < 8) {
      toast.error("Password must be at least 8 characters.");
      return;
    }
    setSubmitting(true);
    try {
      await api.post(`/api/auth/users/${resetting.id}/reset-password`, { new_password: newPassword });
      toast.success(`${resetting.name} can sign in with the new password now.`);
      setResetting(null);
      setNewPassword("");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't reset that password.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="card-paper space-y-4 rounded-2xl p-5">
      <div className="flex items-center gap-2">
        <Users className="h-4 w-4 text-[var(--cream-foreground)]/70" />
        <p className="font-semibold text-[var(--cream-foreground)]">Staff Logins</p>
      </div>

      {users === null ? (
        <p className="text-sm text-[var(--cream-foreground)]/60">Loading…</p>
      ) : (
        <ul className="divide-y divide-black/5">
          {users.map((u) => (
            <li key={u.id} className="flex flex-wrap items-center gap-3 py-3">
              <div className="min-w-0 flex-1">
                <p className="font-medium text-[var(--cream-foreground)]">{u.name}</p>
                <p className="truncate text-sm text-[var(--cream-foreground)]/60">{u.email}</p>
              </div>
              <span className="rounded-full bg-[var(--forest-700)]/10 px-2.5 py-1 text-xs font-semibold capitalize text-[var(--forest-700)]">
                {u.role}
              </span>
              <Button variant="outline" size="sm" className="shrink-0" onClick={() => setResetting(u)}>
                <KeyRound className="h-3.5 w-3.5" />
                Reset password
              </Button>
            </li>
          ))}
        </ul>
      )}

      {resetting && (
        <Dialog open onOpenChange={(open) => !open && setResetting(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Reset password</DialogTitle>
              <DialogDescription>
                {resetting.name} ({resetting.email}) — also clears any login lockout.
              </DialogDescription>
            </DialogHeader>
            <Field label="New Password" required labelClassName="text-popover-foreground">
              <Input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                autoFocus
              />
            </Field>
            <DialogFooter>
              <Button variant="outline" onClick={() => setResetting(null)}>
                Cancel
              </Button>
              <Button
                className="btn-embossed bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)]"
                disabled={submitting}
                onClick={handleReset}
              >
                {submitting ? "Saving…" : "Set new password"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
