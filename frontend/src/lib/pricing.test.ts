import { afterEach, describe, expect, it, vi } from "vitest";

import { addDaysISO, currency, daysBetween, defaultEndDate, monthsBetween, todayISO } from "./pricing";

describe("todayISO — the plaza's day, not the device's", () => {
  afterEach(() => vi.useRealTimers());

  it("is still TODAY in Michigan when UTC has already rolled over to tomorrow", () => {
    // 1:30am UTC on the 13th == 9:30pm on the 12th in Michigan. The old code read
    // the UTC date, so an evening pass was issued starting TOMORROW and the truck
    // was left unpaid for the night the driver had just paid for.
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-07-13T01:30:00Z"));

    expect(todayISO()).toBe("2026-07-12");
  });

  it("rolls over when the plaza does, not when UTC does", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-07-13T05:30:00Z")); // 1:30am on the 13th in Michigan

    expect(todayISO()).toBe("2026-07-13");
  });
});

describe("addDaysISO", () => {
  it("does calendar arithmetic without dragging the date through a timezone", () => {
    expect(addDaysISO("2026-07-12", 1)).toBe("2026-07-13");
    expect(addDaysISO("2026-07-31", 1)).toBe("2026-08-01");
    expect(addDaysISO("2026-01-01", -1)).toBe("2025-12-31");
  });
});

describe("daysBetween", () => {
  it("counts calendar days", () => {
    expect(daysBetween("2026-07-01", "2026-07-02")).toBe(1);
    expect(daysBetween("2026-07-01", "2026-07-08")).toBe(7);
    expect(daysBetween("2026-07-01", "2026-07-01")).toBe(0);
  });
});

describe("monthsBetween (must mirror the backend _months_between)", () => {
  it("rounds partial months up, never below 1", () => {
    expect(monthsBetween("2026-07-05", "2026-08-05")).toBe(1);
    expect(monthsBetween("2026-07-05", "2026-09-05")).toBe(2);
    expect(monthsBetween("2026-07-05", "2026-08-06")).toBe(2); // one day over a full month
    expect(monthsBetween("2026-07-05", "2026-07-20")).toBe(1); // partial month floors to 1
    expect(monthsBetween("2026-07-05", "2026-07-05")).toBe(1); // never below 1
  });
});

describe("defaultEndDate", () => {
  it("adds the right span per pass type", () => {
    expect(defaultEndDate("daily", "2026-07-01")).toBe("2026-07-02");
    expect(defaultEndDate("weekly", "2026-07-01")).toBe("2026-07-08");
    expect(defaultEndDate("monthly", "2026-07-01")).toBe("2026-08-01");
  });
});

describe("currency", () => {
  it("formats USD", () => {
    expect(currency(20)).toBe("$20.00");
    expect(currency(2500)).toBe("$2,500.00");
  });
});
