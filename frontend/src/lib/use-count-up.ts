"use client";

import { useEffect, useRef, useState } from "react";

/** Ease a number up to `target` (a fuel-pump roll) on mount and whenever it
 *  changes. Respects prefers-reduced-motion — jumps straight to the value. */
export function useCountUp(target: number | null | undefined, durationMs = 750): number {
  const [value, setValue] = useState(0);
  const fromRef = useRef(0);

  useEffect(() => {
    if (target == null) return;
    const reduce =
      typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      setValue(target);
      fromRef.current = target;
      return;
    }
    const from = fromRef.current;
    let raf = 0;
    let startTs: number | null = null;
    const tick = (now: number) => {
      if (startTs === null) startTs = now;
      const t = Math.min((now - startTs) / durationMs, 1);
      const eased = 1 - Math.pow(1 - t, 3); // easeOutCubic — fast then settles
      setValue(from + (target - from) * eased);
      if (t < 1) raf = requestAnimationFrame(tick);
      else fromRef.current = target;
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, durationMs]);

  return value;
}
