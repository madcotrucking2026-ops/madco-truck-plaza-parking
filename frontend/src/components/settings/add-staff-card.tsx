"use client";

import { isValidElement, cloneElement, useEffect, useId, useState } from "react";
import { toast } from "sonner";
import { UserPlus } from "lucide-react";
import { api, ApiError, type UserRead } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

type Role = "admin" | "manager" | "attendant";
const ROLES: { value: Role; label: string }[] = [
  { value: "attendant", label: "Attendant" },
  { value: "manager", label: "Manager" },
  { value: "admin", label: "Admin" },
];

export function AddStaffCard() {
  const [me, setMe] = useState<UserRead | null>(null);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("attendant");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api
      .get<UserRead>("/api/auth/me")
      .then(setMe)
      .catch(() => setMe(null));
  }, []);

  if (me?.role !== "admin") return null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name || !email || !password) {
      toast.error("Name, email, and password are required.");
      return;
    }
    if (password.length < 8) {
      toast.error("Password must be at least 8 characters.");
      return;
    }
    setSubmitting(true);
    try {
      await api.post("/api/auth/users", { name, email, password, role });
      toast.success(`${name} can now sign in.`);
      setName("");
      setEmail("");
      setPassword("");
      setRole("attendant");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Could not create that account.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card-paper space-y-4 rounded-2xl p-5">
      <div className="flex items-center gap-2">
        <UserPlus className="h-4 w-4 text-[var(--cream-foreground)]/70" />
        <p className="font-semibold text-[var(--cream-foreground)]">Add a Staff Login</p>
      </div>
      <p className="-mt-2 text-sm text-[var(--cream-foreground)]/60">
        Give another employee their own sign-in instead of sharing your admin account.
      </p>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Name" required>
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Jane Doe" />
        </Field>
        <Field label="Email" required>
          <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="jane@madcotruckplaza.com" />
        </Field>
        <Field label="Temporary Password" required>
          <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </Field>
        <Field label="Role">
          <Select value={role} onValueChange={(v) => setRole(v as Role)}>
            <SelectTrigger className="w-full">
              <SelectValue>{(v: Role) => ROLES.find((r) => r.value === v)?.label ?? v}</SelectValue>
            </SelectTrigger>
            <SelectContent>
              {ROLES.map((r) => (
                <SelectItem key={r.value} value={r.value}>{r.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </Field>
      </div>

      <Button
        type="submit"
        disabled={submitting}
        className="btn-embossed bg-[var(--amber-500)] text-[var(--forest-950)] hover:bg-[var(--amber-600)] disabled:opacity-50"
      >
        {submitting ? "Creating…" : "Create Account"}
      </Button>
    </form>
  );
}

function Field({
  label,
  required,
  children,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  const id = useId();
  const control = isValidElement<{ id?: string }>(children) ? cloneElement(children, { id }) : children;

  return (
    <div>
      <Label htmlFor={id} className="mb-1.5 block text-[var(--cream-foreground)]/80">
        {label}
        {required && <span className="text-[var(--amber-600)]"> *</span>}
      </Label>
      {control}
    </div>
  );
}
