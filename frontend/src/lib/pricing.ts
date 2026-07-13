import type { PassType } from "@/lib/api";

export const DAILY_RATE = 20;
export const WEEKLY_RATE = 100;

/** The plaza's timezone — the ONLY clock that decides what day it is here. Mirrors
 *  the backend's TIMEZONE setting. */
export const PLAZA_TZ = process.env.NEXT_PUBLIC_PLAZA_TZ ?? "America/Detroit";

/**
 * Today, at the plaza.
 *
 * This used to be `new Date().toISOString().slice(0, 10)` — which is the UTC date,
 * not the local one. Michigan is UTC-4, so from 8pm onward it already read TOMORROW:
 * a pass sold at 9pm was issued starting the next day, leaving the truck unpaid for
 * the very night the driver had just paid for, and expiring a day late. It also made
 * the dashboard highlight the wrong rows all evening.
 *
 * en-CA formats as YYYY-MM-DD, which is exactly the wire format the API wants.
 */
export const todayISO = () => new Intl.DateTimeFormat("en-CA", { timeZone: PLAZA_TZ }).format(new Date());

export const currency = (n: number) =>
  n.toLocaleString("en-US", { style: "currency", currency: "USD" });

// A calendar day has no timezone. Parsing "2026-07-12" into a local Date and back
// out through toISOString() drags it through UTC and lands a day early for anyone
// east of Greenwich — so all date arithmetic below stays in plain UTC-anchored
// values and never touches the device's zone.
const parseISO = (iso: string) => {
  const [y, m, d] = iso.slice(0, 10).split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d));
};

const formatISO = (d: Date) => d.toISOString().slice(0, 10);

export function addDaysISO(iso: string, days: number): string {
  const d = parseISO(iso);
  d.setUTCDate(d.getUTCDate() + days);
  return formatISO(d);
}

export function defaultEndDate(passType: PassType, startDate: string): string {
  const d = parseISO(startDate);
  if (passType === "daily") d.setUTCDate(d.getUTCDate() + 1);
  else if (passType === "weekly") d.setUTCDate(d.getUTCDate() + 7);
  else d.setUTCMonth(d.getUTCMonth() + 1);
  return formatISO(d);
}

export function daysBetween(start: string, end: string): number {
  return Math.round((parseISO(end).getTime() - parseISO(start).getTime()) / 86_400_000);
}

/** Mirrors the backend's `_months_between` exactly — whole calendar months,
 * rounding UP for any partial overage, never below 1. */
export function monthsBetween(start: string, end: string): number {
  const s = parseISO(start);
  const e = parseISO(end);
  let months = (e.getUTCFullYear() - s.getUTCFullYear()) * 12 + (e.getUTCMonth() - s.getUTCMonth());
  if (e.getUTCDate() > s.getUTCDate()) months += 1;
  return Math.max(months, 1);
}
