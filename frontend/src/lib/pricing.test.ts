import { describe, expect, it } from "vitest";

import { currency, daysBetween, defaultEndDate, monthsBetween } from "./pricing";

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
