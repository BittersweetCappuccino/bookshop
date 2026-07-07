# Screen 03 — Your Cart

> *Review the night's finds against a starlight budget before heading to the
> desk.* Scene id **`CART`**. Coordinates are concept px (1280×720); ×0.75 for
> 960×600. Tokens: [`01-design-system.md`](01-design-system.md) · widgets:
> [`04-components.md`](04-components.md) · data: [`02-data-model.md`](02-data-model.md)
> · flow: [`03-screen-flow.md`](03-screen-flow.md).

---

## 1. Purpose

A quiet review step between browsing and paying: list every book in the cart,
let the player remove any, and show the ledger — subtotal, member's charm
discount, total, and what the "star-purse" balance will be afterward. Gate to
Checkout.

## 2. Layout map (1280×720)

Two columns inside a 44×48 padded frame, gap 40: **list** (flex) left, **ledger**
(fixed 336) right.

```
┌──────────────────────────────────────────────────────────────┐
│  Your Cart   5 volumes gathered            ┌── Ledger ──────┐ │
│  ────────────────────────────────          │ Ledger         │ │
│  ┌──────────────────────────────┐          │ Subtotal    75 │ │
│  │ [📕] [Fantasy]  ◉18           │          │ Member's charm │ │
│  │      The Ashen Crown  Remove  │          │            −5  │ │
│  │      by E. Vale               │          │ ────────────── │ │
│  └──────────────────────────────┘          │ Total    ◉ 70  │ │
│  ┌──────────────────────────────┐          │ ┌────────────┐ │ │
│  │ [📗] [Romance]  ◉14  ...      │          │ │Star-purse120│ │
│  └──────────────────────────────┘          │ │▓▓▓▓▓░░ 58% │ │ │
│  ┌──────────────────────────────┐          │ │Remaining 50│ │ │
│  │ ... 5 rows total ...          │          │ └────────────┘ │ │
│  └──────────────────────────────┘          │ [Proceed→Desk] │ │
│                                             │ Keep browsing  │ │
│                                             └────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## 3. Background

Night gradient `NIGHT_TOP`→`NIGHT_BOTTOM` with a few fixed stars (sparser than
the shop — concept uses ~3 dots). Frame radius 18, border, shadow. This screen is
UI-forward; keep the backdrop calm.

## 4. Left column — the list

| # | Element | Position / size | Spec |
|---|---------|-----------------|------|
| 1 | **Heading** | top-left | "Your Cart" — Cormorant 700, 44, `CREAM` |
| 2 | **Sub-count** | baseline-aligned right of heading | "{n} volumes gathered" — 14, `TEXT_MUTED` |
| 3 | **Divider** | under heading | 1px gold→transparent gradient line |
| 4 | **Rows** | stacked, gap 12 | One per `cart.items`; see §4a |

### 4a. Cart row
- Flex row, gap 18, padding 12×14, radius 14, fill `ROW_BG` α .55, 1px faint
  border.
- **Thumbnail** (left): 58×84 book cover, genre-hued
  ([`04-components.md`](04-components.md) §4b) — inset frame, small ring motif,
  tiny title.
- **Middle** (flex): genre pill ([§8 pill](04-components.md)) → title (Cormorant
  600, 23, `CREAM`) → "by {author}" (italic 12, `TEXT_MUTED`).
- **Right:** price — coin glyph + number (Cormorant 24, gold) — above a
  **"Remove"** action (11px, uppercase, tracked, `TEXT_FAINT`; hover → brighter).

Concept demo rows (the 5 books, in order): Ashen Crown 18 · A Kiss at Dusk 14 ·
The Ninth Guest 16 · The Quantum Garden 15 · Nightbloom 12
([`02-data-model.md`](02-data-model.md) §3).

## 5. Right column — the ledger

Glass card `PANEL_BG2` α .70, radius 18, padding 26, width 336
([`04-components.md`](04-components.md) §12).

| Line | Value (demo) | Style |
|------|--------------|-------|
| Heading "Ledger" | — | Cormorant 600, 26, `CREAM` |
| Subtotal | 75 | 15, `TEXT_MUTED` ↔ value right |
| Member's charm | −5 | value in gold `MEMBER_CHARM` |
| *(divider)* | | 1px `PANEL_BORDER` |
| **Total** | ◉ 70 | "Total" Cormorant 22 ↔ coin glyph + 34px gold number |
| **Budget box** (inset `PANEL_BG` α .6) | | radius 12, padding 14 |
| ↳ Star-purse | 120 | 12, `TEXT_MUTED` |
| ↳ progress bar | 58% | `TRACK_BG` track, `PROGRESS_A`→`PROGRESS_B` fill = `total/coins` |
| ↳ Remaining after | 50 coins | gold, bold |
| **Proceed to the Desk →** | — | Primary gold button ([§2a](04-components.md)) |
| Keep browsing the aisles | — | sub-link, 12, `TEXT_FAINT` |

Values are **live** from `ctx`: `Ledger(cart).subtotal/total`,
`wallet.coins`, `ledger.remaining(wallet)`. The budget bar fraction is
`total / coins` (spent share). See [`02-data-model.md`](02-data-model.md) §4.

## 6. Interactions

| Input | Condition | Result |
|-------|-----------|--------|
| Hover a row / Remove | — | Row/Remove highlights |
| Click **Remove** | — | `cart.remove(book)`; the book's spine returns to the shelf in `SHOP`; list, counts, and ledger recompute; row animates out (or just redraws) |
| Click **Proceed to the Desk →** | `ledger.affordable(wallet)` | `ctx.go(CHECKOUT)` |
| Proceed when unaffordable | `total > coins` | Button disabled/dimmed; optional hint "Not enough coins" |
| Click **Keep browsing** | — | `ctx.go(SHOP)` |
| **Esc** | — | `ctx.go(SHOP)` (back one level) |
| Empty cart | `cart.count == 0` | Empty state (§7); Proceed hidden/disabled |

## 7. States

| State | Trigger | Visual |
|-------|---------|--------|
| Default | ≥1 item | List + ledger as specced |
| Removing | Remove clicked | Item drops out; totals recount; if it was quest-relevant, quest bar in HUD reflects it next time in `SHOP` |
| Unaffordable | `total > coins` | Total shown in a warning tint; Proceed disabled |
| Empty | 0 items | "Your cart is empty" message + a "Back to the aisles" link; no ledger totals |

## 8. Motion

Minimal by design. Optional: row remove slide/fade, and a brief number tween on
the total/remaining when the cart changes. Starfield twinkle continues. No
required animation.

## 9. Implementation notes

- **New screen**, but it's pure layout over existing data — no world simulation.
  Build it as a `Scene` that reads `ctx.cart`/`ctx.wallet` and renders two
  columns.
- Reuse `draw_cover` (thumbnail mode), `draw_pill`, `coin_value`, `progress_bar`,
  and `draw_ledger` from the component library — this screen is mostly composition.
- Removing here and adding in `SHOP` are the same `Cart` mutation from opposite
  directions; keep the shelf's `taken` flag in sync so a removed book reappears.
- If the list can exceed the frame height (more than ~5–6 rows once the cart grows
  past the quest target), add simple scroll (wheel / drag) — the concept only
  shows 5 and doesn't scroll.

## 10. Acceptance checklist

- [x] Two-column layout: item list left, ledger card right.
- [x] One row per cart book: genre-hued thumbnail, pill, title, author, price, Remove.
- [x] Heading with live "{n} volumes gathered" count.
- [x] Ledger shows subtotal, member's charm (−5), total with coin glyph.
- [x] Budget box: star-purse balance, spent-fraction progress bar, remaining-after.
- [x] All ledger values are live from `ctx` (demo cart totals 70, remaining 50).
- [x] Remove deletes the row, recomputes totals, and returns the spine to the shelf.
- [x] Proceed → Checkout (disabled when unaffordable); Keep browsing / Esc → Shop.
- [x] Empty-cart state handled.
