import { afterEach, describe, expect, it, vi } from "vitest";

import {
  addDaysISO,
  catchUpEnd,
  closeOutPrice,
  currency,
  daysBetween,
  defaultEndDate,
  monthsBetween,
  todayISO,
} from "./pricing";

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

describe("catchUpEnd (continue-mode pre-fill)", () => {
  it("on-time renewal = one period from the old end", () => {
    expect(catchUpEnd("monthly", "2026-08-08", "2026-07-01")).toBe("2026-09-08");
    expect(catchUpEnd("daily", "2026-08-06", "2026-08-01")).toBe("2026-08-07");
  });
  it("a late monthly catches up enough whole months to pass today", () => {
    // Jul 8 -> Aug 8 lapsed, today Sep 11 -> 2 months -> Oct 8
    expect(catchUpEnd("monthly", "2026-08-08", "2026-09-11")).toBe("2026-10-08");
  });
});

describe("closeOutPrice (must mirror the backend _close_out_price)", () => {
  const rates = { daily: 20, weekly: 100, monthly: 250 };
  it("monthly: whole months + leftover days at the daily rate", () => {
    // Aug 8 -> Sep 11 = 1 month + 3 days
    expect(closeOutPrice("monthly", "2026-08-08", "2026-09-11", rates)).toBe(250 + 3 * 20);
  });
  it("caps the leftover at one period's rate", () => {
    // Aug 8 -> Sep 5 = 0 whole months + 28 days; capped at one month
    expect(closeOutPrice("monthly", "2026-08-08", "2026-09-05", rates)).toBe(250);
  });
  it("daily: days used at the daily rate", () => {
    expect(closeOutPrice("daily", "2026-08-06", "2026-08-09", rates)).toBe(3 * 20);
  });
  it("weekly: whole weeks + capped leftover", () => {
    // 10 days = 1 week + 3 days -> 100 + min(3*20, 100) = 160
    expect(closeOutPrice("weekly", "2026-08-01", "2026-08-11", rates)).toBe(160);
  });
});
