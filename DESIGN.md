# DESIGN.md — Madco Truck Plaza Parking Management System

The design source of truth. This is not aspirational — it describes the system
already implemented in `frontend/src/app/globals.css` and the component library.
Every token below is real. When code and this file disagree, fix the mismatch;
don't let them drift.

**Design tools (`/design-review`, `/design-consultation`) read this file. Keep it current.**

---

## Identity

A premium AI parking system for a truck stop, built so the owner never has to
remember anything. It should feel like an expensive commercial product — Apple /
Linear / Stripe restraint — wearing a **classic truck-stop skin**: warm ivory
paper tickets, forest-green structure, a single amber accent.

**The one thing to remember:** *this is calm, physical software you can read in
one second in a gravel lot, in gloves.*

Every screen earns its place by one of: saves the owner time, prevents a mistake,
makes money, or surfaces an insight. Nothing decorative gets built.

---

## Colour — the 60-30-10 system

Balance is the rule, not the palette size. Break the ratio and the "premium" read
collapses into a generic dashboard.

- **60% — warm ivory / cream.** Page background + `.card-paper` surfaces.
- **30% — forest green.** Structure: sidebar, headings, selected states, secondary
  actions, borders.
- **10% — amber.** The **one** primary action per view + key money highlights.
  Nothing else. Filling many buttons with amber dilutes the 10% — reach for forest
  first; amber is scarce on purpose.

### Brand tokens (light mode `:root`)

| Token | Hex | Use |
|---|---|---|
| `--forest-700` | `#173f35` | **Brand primary.** Sidebar, headings, secondary buttons |
| `--forest-600` | `#1f5445` | Hover/lift of forest surfaces |
| `--forest-800/900/950` | `#1b3129` / `#14251f` / `#0f1b17` | Deep structure, dark-mode surfaces |
| `--ivory-100` | `#f3efe4` | Text/icons on forest |
| `--cream` | `#efe7d8` | Card-paper gradient base (brand secondary `#E6E0D4`, lifted) |
| `--cream-foreground` | `#2a2a22` | Text on cream paper |
| `--amber-500` | `#d6862b` | **Brand accent.** THE primary CTA, money highlight, focus ring |
| `--amber-600` | `#bf7420` | Amber hover |
| `--background` | `#faf6ed` | Page (warm ivory) |

### Semantic state

| Token | Hex | Meaning |
|---|---|---|
| `--success` | `#1faf67` | Paid / free / good |
| `--danger` | `#d74a4a` | Expired / overstay / destructive |
| `--warning` | `#e7b416` | Expiring soon |

### The ink-twin rule (non-negotiable accessibility)

A brand hue bright enough to **fill** a button is never dark enough to **be text**
on cream. So every fill colour has an `-ink` twin that clears WCAG AA 4.5:1:

- `--danger-ink`, `--success-ink`, `--amber-ink`, `--warning-ink`.
- **Use the bright original for fills, borders, dots, icons.**
- **Use the `-ink` twin any time the colour IS the words.**
- `--warning` (yellow) is 1.7:1 on cream — **never** use it as text, only fills/dots/icons.
- Badges that paint their own bg+text use `--danger-strong` and do **not** flip in dark mode.

Dark mode re-pins the ink twins **light** at the page level; inside `.card-paper`
(always cream, both modes) they re-pin **dark** again. Respect that — don't hardcode.

---

## Typography

Two families, one real axis of contrast.

- **Inter** — headings, labels, body, buttons. Self-hosted via `next/font` (`--font-inter`),
  applied to `h1–h6` through `font-heading` and to `body` through `font-sans`.
  Differentiate hierarchy by **weight**, not by swapping faces.
- **JetBrains Mono** (`--font-mono`) — reserved for **what a truck stop reads as data**:
  truck numbers, trailer numbers, plates, receipt numbers, money. This is the
  deliberate contrast. Do not use mono for prose; do not set numbers-that-are-data in Inter.
- Always pair mono numeric columns with `tabular-nums` so digits align.

Never lead the body stack with `-apple-system`/SF Pro — that lets the OS pick the
body face and the UI renders differently on every machine. Inter is deterministic.

---

## Surfaces — the skeuomorphic signatures

Physical, tactile, warm. Four component classes carry the whole material language
(`globals.css @layer components`). Reuse them; don't reinvent a card.

- **`.card-paper`** — the cream paper ticket. The app's one signature surface, a
  fixed warm tone in **both** light and dark. Soft inset highlight + drop shadow,
  `hover:` lifts `-2px`. Rescopes `--foreground`/ink tokens locally so anything
  inside always renders dark-on-cream.
- **`.tile-option`** — segmented selector tiles (pass-type, pay-method). Same cream
  material. Selected = **forest ring** (structural state = the 30%, never amber),
  amber only on `:focus-visible`.
- **`.panel-steel`** — brushed forest panel for the sidebar/headers.
- **`.btn-embossed`** — physical button press: inset highlight + shadow, `:active`
  translates `+1px`. Wear it on primary/CTA buttons.

### Radius scale

Base `--radius: 0.625rem`, stepped `sm 0.6× → 4xl 2.6×`. Cards use `2xl`, controls
`lg`/`xl`. Nest consistently; don't put one bubbly radius on everything (that reads
AI-generated).

---

## Motion

Restrained and orchestrated, never a fade on every element.

- **`.animate-rise`** — one page entrance: rise+fade, `460ms cubic-bezier(0.16,1,0.3,1)`.
- Surface transitions: `160–180ms ease` on `.card-paper` / `.tile-option`.
- Only animate `transform` / `opacity` / `box-shadow`. Never `transition: all`.
- **`prefers-reduced-motion`** collapses rise, stops skeleton pulse, kills surface
  transitions. Every new animation must have a reduced-motion fallback.

---

## Component conventions

- **Touch targets:** controls are `h-11` (44px, Apple/WCAG floor) on phones,
  snapping to a tight `sm:h-8` desktop rhythm. The owner uses this outdoors,
  one-handed, in gloves — never ship a control under 44px on mobile. When you
  override height on a `flex-col` tile, override **both** `h-*` and `sm:h-*`
  (tailwind-merge keys the `sm:` height separately).
- **Focus:** visible keyboard ring in `--amber-500` (`--ring`). Never `outline: none`
  without a replacement.
- **Buttons:** one amber CTA per view; everything else forest/outline/ghost.
- **Empty states:** icon + warm one-line message + the action (e.g. "All caught up —
  nothing expiring today or tomorrow"), never a bare "No items."
- **Data at a glance beats labels-on-everything.** The lot map is a colour heatmap
  grouped by zone (A–F); it does not print a number on all 150 cells — unreadable
  density is clutter. Identity lives on hover/tap.

### Spot-state colours (lot map / availability)

`free` success · `occupied` forest-700 · `expiring` warning · `grace` amber-500 ·
`overstay` danger · `inactive` black/10. Colour = state; each swatch carries an
inset ring so it reads on cream.

---

## Guardrails — what this brand never does

- No purple/violet/indigo, no blue→purple gradients (the #1 AI-slop tell). The
  palette is forest + ivory + amber, full stop.
- No amber sprayed across many buttons — it's the 10%, one CTA per view.
- No mono for prose; no data-numbers in Inter.
- No `-apple-system`/system-ui as the primary face.
- No decorative blobs, wavy dividers, or icon-in-coloured-circle 3-column grids.
- No uniform bubbly radius on everything; no `border-left: 3px solid accent` cards.
- No colour-only encoding — pair every status colour with a label or icon.
- No text set in a bright fill colour — use the `-ink` twin.

---

## Accessibility

- Body text ≥ 16px; contrast ≥ 4.5:1 (large text ≥ 3:1). The ink-twin tokens exist
  to make this automatic — use them.
- `tabular-nums` on every numeric/money column.
- Both light and dark are first-class; dark uses forest-elevation, not a lightness flip.
- Respect `prefers-reduced-motion`.
