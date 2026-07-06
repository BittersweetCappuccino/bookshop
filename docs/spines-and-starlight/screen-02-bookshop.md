# Screen 02 — The Bookshop (Genre Aisles)

> *Third-person browsing. Hover any spine for its details; picked books drop into
> the cart.* Scene id **`SHOP`** — the hub of the game.
> Coordinates are concept px (1280×720); ×0.75 for 960×600.
> Tokens: [`01-design-system.md`](01-design-system.md) · widgets:
> [`04-components.md`](04-components.md) · data: [`02-data-model.md`](02-data-model.md)
> · flow: [`03-screen-flow.md`](03-screen-flow.md).

This is the largest screen and the direct successor to the current game's single
shop view ([`bookstore.py`](../../bookstore.py)). Reuse walking, cart-follow, and
`Pop` feedback; replace coloured rectangles with genre-hued, data-driven spines.

---

## 1. Purpose

Browse four genre aisles, walk Mira along them, hover a spine to see its info,
and add books to the cart — tracked against the quest ("gather five tales"). The
launch point for the Detail screen (05) and the Cart (03).

## 2. Layout map (1280×720)

```
┌──────────────────────────────────────────────────────────────┐
│ ┌─Quest──────────┐        · stars ·           ┌120◉┐┌🛒5 +2┐ │
│ │◆ CURRENT QUEST │      ●lantern      ●lantern └────┘└──────┘ │
│ │ Gather five... │                                            │
│ │ ▓▓▓▓▓▓░░░ 3/5  │                                            │
│ └────────────────┘   ● ← tooltip dot   ┌─Tooltip──────────┐   │
│                                        │ [Fantasy]         │   │
│      Fantasy  │ ▐▐▌▐▐▌▐▐▐▌▐▐  spines   │ The Ashen Crown   │   │
│    Epic & High│ ═══════ shelf plank ═══│ ★★★★☆ · Add·[E]  │   │
│      Romance  │ ▐▐▌▐▐▐▌▐▐▌▐▐          └──────────────────┘   │
│  Love&Longing │ ═══════════════════════════════════════      │
│      Mystery  │ ▐▐▐▌▐▐▌▐▐▐▌▐  spines                          │
│   Whodunnit   │ ═══════════════════════════════════════      │
│   Sci-Fi      │ ▐▐▌▐▐▐▌▐▐▌▐▐                                  │
│   Far Futures │ ═══════════════════════════════════════      │
│                       🧍‍♀️+🛒 (Mira from behind + cart)         │
│░░░░░░░░░░░░░░░░░░░░░░ floor ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
└──────────────────────────────────────────────────────────────┘
```

## 3. Background & furniture

| # | Element | Position / size | Spec |
|---|---------|-----------------|------|
| 1 | Frame | 1280×720 | Radius 18, border, shadow (as all screens) |
| 2 | Night background | fill | `NIGHT_TOP`→`NIGHT_BOTTOM` + warm top radial glow + fixed stars |
| 3 | Lantern (left) | cord left 280 top 0 h52; lamp left 262 top 44, 38×52 | Radial `LANTERN_LIGHT`→`LANTERN_DARK`, `pulse` glow, **4 s** period |
| 4 | Lantern (right) | cord right 340 top 0 h38; lamp right 322 top 30, 34×46 | Same, `pulse` **5 s** (offset phase) |
| 5 | Shelf wrapper | left 52, right 52, top 70 | Contains the 4 aisle rows |
| 6 | Floor | bottom 0, full width, 150 tall | Gradient transparent→dark wood, over the shelves |

## 4. Aisles (the four genre rows)

Rendered top→bottom in order Fantasy, Romance, Mystery, Sci-Fi
([`02-data-model.md`](02-data-model.md) §1). Each row = a **label block** + a
**spine row**, followed by a **shelf plank**. Rows are separated by 24px.

### 4a. Genre label block
- Flex width **158**, right-aligned, padding-bottom 12.
- **Name:** Cormorant 600, 27, genre-tinted (`GENRE_HUE` label colour, e.g.
  Fantasy `(246,227,184)`).
- **Subtitle:** 10px, tracked 2.5, uppercase, dimmer genre tint
  (e.g. "EPIC & HIGH").

### 4b. Spine row
- Flex row, gap **6**, bottom-aligned, right padding 6.
- **12 spines** per genre, drawn from `books_by_genre(genre)` in order; each spine
  via `draw_spine` with `spine_shades(hue, shelf_index)`
  ([`04-components.md`](04-components.md) §3, [`01-design-system.md`](01-design-system.md) §2).
- Geometry per index `i`: width `21+(i*17)%13`, height `66+(i*41)%42`.

### 4c. Shelf plank
- Height **15**, radius 3, wood gradient `WOOD_TOP`→`WOOD_BOTTOM`, top highlight
  `WOOD_HI`, drop shadow. Generalises [`bookstore.py:269`](../../bookstore.py#L269).

## 5. Actor: Mira + cart

- Position: bottom 8, **left ~405** (walks horizontally); container 150×210.
- **Mira from behind** + **cart** with book-tops poking out
  ([`04-components.md`](04-components.md) §14). Restyle the existing front-facing
  `Mira`/`draw_cart` to the behind-view night palette; keep the walk bob, arm
  swing, and cart-follow logic.
- **Movement:** arrows / A,D, clamped to the aisle span (reuse
  [`bookstore.py:181`](../../bookstore.py#L181)). Mira's X gates which spines are
  "near" enough to hover/add (proximity ~130px, [`bookstore.py:417`](../../bookstore.py#L417)).

## 6. HUD

| # | Element | Position | Spec |
|---|---------|----------|------|
| 1 | **Quest tracker** | top 22, left 24, max-w 290 | Glass panel: ◆ + "CURRENT QUEST", quest title (Cormorant 20), progress bar at `quest.fraction(cart)`, "N of 5 chosen". Widget [`04-components.md`](04-components.md) §11 |
| 2 | **Coin balance** | top 22, right 24 | Glass pill: coin glyph + `wallet.coins` (Cormorant 600, 22, `COIN_NUM`) |
| 3 | **Cart badge** | top 22, right of coins | Glass pill (violet border): cart icon + `cart.count`; red `+N` notification dot when items were just added ([`04-components.md`](04-components.md) §7) |

Concept demo values: coins **120**, cart **5**, quest **3 of 5** (60%). Live
values come from `ctx`.

## 7. Book tooltip

Shown when a spine is hovered **and** Mira is near it.

- **Anchor dot:** glowing `STAR_RATING` dot on the spine (concept: top 150, left
  512 for a fantasy spine) with an outer `glow`.
- **Card:** ~262px wide, offset up-right of the dot (concept top 120, left 540),
  glass panel radius 14. Contents ([`04-components.md`](04-components.md) §5):
  genre pill → title → `by author` → star row + `rating · pages pp` → short blurb
  → divider → footer (price with coin glyph ↔ **"Add · [E]"** pill).
- Only one tooltip at a time (the hovered spine). Hidden when nothing is hovered
  or Mira is out of range.

## 8. Interactions

| Input | Condition | Result |
|-------|-----------|--------|
| Move mouse over a spine | Mira near it | Spine lifts + glows; **tooltip** appears |
| **Click** a spine | Mira near it | `ctx.push(DETAIL, book)` → open Book Close-Up (screen 05) |
| **E** | a spine hovered & near | Quick-add: `cart.add(book)`, spine `taken`, quest/HUD update, `Pop` "Added", cart `+1` badge — **no scene change** |
| Click **"Add · [E]"** in tooltip | — | Same as E |
| **C** / click cart badge | — | `ctx.go(CART)` |
| Arrows / A,D | — | Walk Mira |
| **Esc** | — | Back one level (hub: no-op or pause menu) |
| **M** | — | Mute (global) |

> **Add vs. open-detail:** clicking the spine **reads** it (opens 05); **E** (or
> the tooltip's Add) **adds** it directly. This matches the flow table
> ([`03-screen-flow.md`](03-screen-flow.md) §3). Adding does **not** spend coins —
> money is spent only at Checkout.

Guardrails: a `taken` spine is removed from the shelf and can't be re-added;
adding when the cart already holds that book is a no-op (`Cart.add` dedupes).

## 9. Motion

- Lantern `pulse` (two lamps, offset phases).
- Twinkling starfield (`tw`).
- Mira walk bob / arm swing (existing).
- Spine hover lift + glow.
- `Pop` "Added" / "Quest +1" feedback on add ([`bookstore.py:342`](../../bookstore.py#L342)).
- Cart `+N` badge fade.

## 10. States

| State | Trigger | Visual |
|-------|---------|--------|
| Browsing | default | Full scene, tooltip hidden |
| Hovering | spine hovered & near | Tooltip + spine highlight |
| Added | E / Add | Spine gone, HUD counts up, Pop feedback |
| Quest complete | `cart.count ≥ 5` | Quest bar full; optional prompt "Head to the cart" (successor to the current "List complete!" line, [`bookstore.py:434`](../../bookstore.py#L434)) |
| Out of range | Mira far from hovered spine | No tooltip; spine not highlighted |

## 11. Implementation notes

- **Reuse heavily:** walking, proximity gating, `hover`/`taken` flags, cart
  drawing, and `Pop` all exist today — this screen is the current game restyled
  and data-driven, plus HUD/tooltip.
- Build spines once per run into a list of `(Book, rect)` laid out along each
  aisle; recompute hover each frame from mouse + Mira proximity (mirrors
  [`bookstore.py:416`](../../bookstore.py#L416)).
- Cache the static layer (background, shelves, planks, floor, lantern bodies);
  redraw per frame only: lantern glow pulse, twinkle, Mira+cart, HUD, tooltip,
  Pops, and spines whose hover/taken state changed.
- The four aisles fit the 1280 width comfortably; at 960×600 (×0.75) verify the
  label block (158→~119) still holds the genre names — shrink the subtitle first.

## 12. Acceptance checklist

- [ ] Four aisles (Fantasy/Romance/Mystery/Sci-Fi) with genre-tinted labels + subtitles.
- [ ] 12 genre-hued spines per aisle from the catalog, on wood planks; two pulsing lanterns.
- [ ] Mira (from behind) + cart walk the aisles; proximity gates interaction.
- [ ] Hovering a near spine shows the info tooltip with price and "Add · [E]".
- [ ] **E**/Add adds in place (spine removed, cart+quest update, Pop); no coin spend.
- [ ] Clicking a spine opens the Detail screen (05).
- [ ] HUD: quest tracker with progress bar, coin balance, cart badge with +N.
- [ ] **C**/cart icon opens the Cart (03); starfield twinkles; music continues.
