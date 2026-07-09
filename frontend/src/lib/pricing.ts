import type { PassType } from "@/lib/api";

export const DAILY_RATE = 20;
export const WEEKLY_RATE = 100;

export const todayISO = () => new Date().toISOString().slice(0, 10);

export const currency = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD" });

export function defaultEndDate(passType: PassType, startDate: string): string {
  const d = new Date(`${startDate}T00:00:00`);
  if (passType === "daily") d.setDate(d.getDate() + 1);
  else if (passType === "weekly") d.setDate(d.getDate() + 7);
  else d.setMonth(d.getMonth() + 1);
  return d.toISOString().slice(0, 10);
}

export function daysBetween(start: string, end: string): number {
  const s = new Date(`${start}T00:00:00`);
  const e = new Date(`${end}T00:00:00`);
  return Math.round((e.getTime() - s.getTime()) / 86_400_000);
}

/** Mirrors the backend's `_months_between` exactly — whole calendar months,
 * rounding UP for any partial overage, never below 1. */
export function monthsBetween(start: string, end: string): number {
  const s = new Date(`${start}T00:00:00`);
  const e = new Date(`${end}T00:00:00`);
  let months = (e.getFullYear() - s.getFullYear()) * 12 + (e.getMonth() - s.getMonth());
  if (e.getDate() > s.getDate()) months += 1;
  return Math.max(months, 1);
}
