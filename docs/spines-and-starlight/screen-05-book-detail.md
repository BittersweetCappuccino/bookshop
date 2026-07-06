# Screen 05 — Book Close-Up

> *Pull a single volume from the shelf to read its cover, blurb, and price.*
> Scene id **`DETAIL`** — an overlay pushed over `SHOP`. Coordinates are concept
> px (1280×720); ×0.75 for 960×600. Tokens:
> [`01-design-system.md`](01-design-system.md) · widgets:
> [`04-components.md`](04-components.md) · data: [`02-data-model.md`](02-data-model.md)
> · flow: [`03-screen-flow.md`](03-screen-flow.md).

---

## 1. Purpose

The full record for one book: a large cover, genre/format tags, title, author,
page count, rating, blurb, price, shelf stock, and an Add-to-Cart action. Opened
by clicking a spine in `SHOP`; it's a focused overlay, so `SHOP` stays alive
(dimmed) underneath.

## 2. Layout map (1280×720)

Centered row, gap 70, padding 0×90: **big cover** left, **detail panel**
(max-w 520) right, over **blurred shelves**.

```
┌──────────────────────────────────────────────────────────────┐
│ ░░░░░░░░░░░░ blurred shelves (blur 9, opacity .35) ░░░░░░░░░░░ │
│                                                                │
│        ╭───────────────╮     [Fantasy] [Epic · Standalone]     │
│        │ A NOVEL OF THE│                                        │
│        │  STAR-COURT   │     The Ashen Crown                    │
│        │      ✦        │     by E. Vale · 512 pages             │
│        │   (emblem)    │     ★★★★☆  4.2 · 1,284 reviews         │
│        │               │                                        │
│        │  The Ashen    │     A dethroned queen strikes a        │
│        │  Crown        │     bargain with the star-court...     │
│        │  E. VALE      │                                        │
│        ╰───────────────╯     ┌ Add to Cart · 18 ┐  ● 4 copies   │
│         (320×480 cover)      └──────────────────┘  on the shelf │
│                              ← Back to the aisle · [Esc]        │
└──────────────────────────────────────────────────────────────┘
```

## 3. Background

- The `SHOP` scene beneath, **dimmed** (draw a plum veil over it), since this is
  a `push` overlay ([`03-screen-flow.md`](03-screen-flow.md) §5).
- Plus this screen's own **blurred shelves**: full-bleed row of background spines
  ([§3b](04-components.md)), `blur(9)`, opacity .35 — draw to a surface,
  down/upscale to blur. Reinforces "pulled from the shelf".

## 4. Big cover (left)

320×480, radius `6 10 10 6` ([`04-components.md`](04-components.md) §4a). For
The Ashen Crown (Fantasy, hue 288):

| Part | Spec |
|------|------|
| Glow halo | Violet radial `glow` behind (inset −50) |
| Body | Diagonal gradient `oklch(0.42 0.13 288)`→`(0.2 0.09 290)` = ~`(80,63,140)`→`(38,24,62)` |
| Spine shadow | 8px light strip down the left inner edge |
| Frame | Inset 1.5px gold border (inset 20) |
| Eyebrow | "A NOVEL OF THE STAR-COURT" — tracked 4, 10, gold, top |
| Emblem | Crown-ish: outer ring + inner gold disc + 4 rays (up/down/left/right). Concentric `draw.circle` + 4 small rects |
| Title | "The Ashen / Crown" — Cormorant 700, 40, `CREAM`, drop-shadowed, bottom |
| Author | "E. VALE" — tracked 2, 13, gold-dim |

`draw_cover(surf, rect, book, detail=True)` covers this; the emblem is
book/genre-specific (a placeholder motif per genre is fine for non-Ashen books).

## 5. Detail panel (right, max-w 520)

| # | Element | Spec |
|---|---------|------|
| 1 | **Tags** | Genre pill ("Fantasy", genre-hued) + neutral pill ("Epic · Standalone", outlined) — [§8 pill](04-components.md) |
| 2 | **Title** | "The Ashen Crown" — Cormorant 700, 62, `CREAM`, violet text-glow |
| 3 | **Byline** | "by E. Vale · 512 pages" — italic 18, `TEXT_MUTED` |
| 4 | **Rating** | Star row (★★★★☆, size 20) + "4.2 · 1,284 reviews" (14, `TEXT_MUTED`) |
| 5 | **Blurb** | Long blurb — 16/1.65, `TEXT` (soft), max-w 480 |
| 6 | **Add to Cart** | Primary gold button ([§2a](04-components.md)): coin glyph + "Add to Cart · {price}" (Cormorant 600, 24) |
| 7 | **Stock** | "● {copies} copies on the shelf" — dot in gold, 13, `TEXT_MUTED` |
| 8 | **Back link** | "← Back to the aisle · [Esc]" — tracked 2, 12, `TEXT_FAINT` |

All fields come from the `Book` passed in `ctx.push(DETAIL, book)`
([`02-data-model.md`](02-data-model.md) §2). The Ashen Crown is the only
fully-authored book; others use authored or placeholder blurb/rating/pages/copies
([`02-data-model.md`](02-data-model.md) §6).

## 6. Interactions

| Input | Condition | Result |
|-------|-----------|--------|
| Hover **Add to Cart** | book not already in cart | Button brightens ~7% |
| Click **Add to Cart** | not already in cart | `cart.add(book)`; spine becomes `taken` in `SHOP`; quest/HUD update; `Pop` "Added"; then `ctx.pop()` back to `SHOP` |
| Add when already in cart | `book in cart` | Button shows "In cart ✓", disabled |
| Click **Back** / **Esc** | — | `ctx.pop()` → `SHOP`, unchanged |
| **M** | — | Mute (global) |

> Adding here does **not** spend coins (money is spent only at Checkout), matching
> `SHOP`'s quick-add. The difference is only that Detail returns to `SHOP` after
> adding, since it's a modal view.

## 7. States

| State | Trigger | Visual |
|-------|---------|--------|
| Viewing | on enter | Cover + panel over dimmed shop |
| In-cart | `book in cart` | Add button → "In cart ✓" disabled; stock still shown |
| Adding | Add clicked | Pop feedback, then pop back to `SHOP` |
| Out of stock (optional) | `copies == 0` | Add disabled, "Currently shelved elsewhere" |

## 8. Motion

- Enter: cover fades/scales up slightly over the dimmed shop (optional).
- Steady violet glow behind the cover; starfield twinkle continues on the shop
  layer.
- `Pop` "Added" on add. No required animation beyond the dim + optional enter.

## 9. Implementation notes

- **Overlay scene:** pushed, not switched — `SHOP` renders first (dimmed), then
  this. On `pop`, `SHOP` resumes exactly as left (Mira position, scroll, etc.).
- Reuse `draw_cover(detail=True)`, `draw_pill`, `star_row`, the gold `Button`,
  `coin_glyph`, and `Pop`. The panel is composition; the cover is the one bespoke
  drawing (emblem).
- The 62px title may wrap for long names — measure and shrink to fit `max-w 520`,
  or allow two lines.
- Keep the cover emblem generic per genre so every book has *something*; only
  Ashen Crown needs the exact crown motif.
- This screen doubles as the natural home for the tooltip's "Read" affordance from
  `SHOP` ([`screen-02-bookshop.md`](screen-02-bookshop.md) §8).

## 10. Acceptance checklist

- [ ] Opens as an overlay over a dimmed `SHOP`; `Esc`/Back returns to it unchanged.
- [ ] Blurred shelves behind; large 320×480 genre-hued cover with glow, frame, emblem, title, author.
- [ ] Detail panel: genre + format pills, 62px title, byline with page count, star rating + reviews, long blurb.
- [ ] Add to Cart shows the price with a coin glyph; adds the book, marks the spine taken, updates quest/HUD, and returns to `SHOP`.
- [ ] Adding does not spend coins; "In cart ✓" when already added.
- [ ] Stock line and "← Back to the aisle · [Esc]" present.
- [ ] All fields driven by the passed `Book` (demo: The Ashen Crown, 4.2★, 512 pp, 18 coins, 4 copies).
