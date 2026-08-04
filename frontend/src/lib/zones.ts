import type { SpotState } from "@/lib/api";

/** Group the flat lot into ordered zone blocks by the letter in each spot's
 *  label (A1 -> zone A). Spots with no letter (zoning off, bare numbers) fall
 *  into a single "•" block. Within a zone, spots stay in number order. */
export function byZone(spots: SpotState[]): { zone: string; spots: SpotState[]; free: number }[] {
  const map = new Map<string, SpotState[]>();
  for (const s of [...spots].sort((a, b) => a.number - b.number)) {
    const zone = /^[A-Z]/.test(s.label) ? s.label[0] : "•";
    const list = map.get(zone) ?? [];
    list.push(s);
    map.set(zone, list);
  }
  return [...map.entries()].map(([zone, list]) => ({
    zone,
    spots: list,
    free: list.filter((x) => x.state === "free").length,
  }));
}
