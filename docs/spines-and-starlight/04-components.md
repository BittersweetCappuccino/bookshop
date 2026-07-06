# Spines & Starlight — Component Library

> The reusable widgets every screen is built from. Each entry gives the concept
> dimensions (1280×720 space; ×0.75 for 960×600), states, and how to draw it in
> pygame. Colors are tokens from [`01-design-system.md`](01-design-system.md);
> data comes from [`02-data-model.md`](02-data-model.md).

Build these once in a `widgets.py` (+ `primitives.py` for the helpers) so the
per-screen specs can just say "a gold button here" and mean exactly this.

---

## 0. Primitives (draw helpers used by everything)

| Helper | Signature | What it does |
|--------|-----------|--------------|
| `oklch_to_rgb` | `(L,C,h) -> (r,g,b)` | Color conversion (see design system §1.1) |
| `vgradient` | `(surf, rect, top, bottom)` | Vertical gradient fill (row-by-row, or a cached 1×H strip scaled) |
| `round_rect` | `(surf, rect, color, radius, width=0)` | `pygame.draw.rect(..., border_radius=radius)` |
| `alpha_rect` | `(surf, rect, rgba, radius)` | Translucent rounded fill via an `SRCALPHA` sub-surface |
| `glow` | `(surf, center, radius, rgba)` | Soft radial halo — big `SRCALPHA` ellipse, low alpha; as in [`bookstore.py:284`](../../bookstore.py#L284) |
| `drop_shadow` | `(surf, rect, radius, blur, rgba)` | Offset dark rounded rect (or stacked low-alpha rects) beneath an element |
| `render_tracked` | `(text, font, color, px) -> Surface` | Letter-spaced text (blit glyph-by-glyph with `+px` gap) — pygame has no tracking |
| `coin_glyph` | `(surf, center, r)` | The coin disc (see §6) |
| `star_row` | `(surf, pos, rating, size)` | `★★★★☆` from a rating float |

`vgradient` is the workhorse — nearly every panel, spine, button, and background
is a vertical gradient. Cache gradients that don't change per frame.

---

## 1. Glass panel (base surface)

The translucent dark card behind HUD, tooltips, ledger, cart rows.

- **Fill:** `PANEL_BG` at α .82 (HUD/tooltip) or `PANEL_BG2` α .70 (ledger) or
  `ROW_BG` α .55 (list rows).
- **Border:** 1px `PANEL_BORDER` (gold hairline) — or a violet variant
  `(110,90,125)` for cart-count chips.
- **Radius:** 12 (chips) · 14 (tooltip/rows) · 16–18 (cards).
- **Draw:** `alpha_rect` for the fill, then `round_rect(..., width=1)` for the
  border. Skip the CSS `backdrop-filter: blur` — the low-alpha fill reads fine.

Everything below that says "on a glass panel" uses this.

---

## 2. Buttons

### 2a. Primary (gold)
Used for: New Story, Proceed to the Desk, Add to Cart, the checkout total CTA.

- **Fill:** vertical gradient `BTN_GOLD_TOP`→`BTN_GOLD_BOT`.
- **Text:** `BTN_GOLD_TEXT` `(41,13,0)`, Cormorant 600, 22–24, tracking .5.
- **Radius:** 11–13. **Padding:** ~14×22.
- **Shadow:** warm `drop_shadow` in gold-brown, offset ~14 down.
- **Optional leading glyph:** small rotated square (New Story) or coin (Add).
- **States:** `hover` → brighten ~8% (`filter:brightness(1.08)`); `disabled` →
  desaturate + lower alpha (e.g. "Proceed" when unaffordable).

### 2b. Secondary (ghost)
Used for: Continue, Your Collection, Settings.

- **Fill:** `BTN2_BG` α .55; **border:** 1px `BTN2_BORDER` α .5.
- **Text:** `BTN2_TEXT` `(231,216,235)`, Cormorant, 22.
- **Hover:** raise fill to α .70 / lighten.
- **Disabled** (e.g. Continue with no save): dim text, no hover.

### 2c. Pill button / tag-action
Small outlined action, e.g. tooltip **"Add · [E]"** and **"← Back to the aisle"**.

- Outline 1px gold α .5, text `EYEBROW_GOLD`, uppercase, tracking ~1.5, radius 20,
  padding 6×12.

Recommended API: `Button(rect, label, kind, on_click, enabled=True)` with
`draw(surf, t, hovered)` and a `hit(pos)` test.

---

## 3. Book spine (shelf)

The vertical book on a shelf (screen 02). Colors/size derived per book — see
`spine_shades()` in design system §2.

- **Geometry:** width `21 + (i*17)%13` (21–34) · height `66 + (i*41)%42` (66–108),
  bottom-aligned on the shelf, gap 6px between spines.
- **Body:** vertical gradient `top→mid(32%)→bottom` from `spine_shades`; radius
  `2px 3px 3px 2px`; inset 1px dark edge.
- **Title band:** 5px bar of `band` color across the top.
- **Title text:** vertical (`writing-mode: vertical-rl` in concept) → in pygame,
  render the title horizontally then `pygame.transform.rotate(surf, 90)` and blit
  centered; Cormorant 600, 10px, genre-tinted near-white, drop-shadowed, clipped
  to the spine.
- **States:**
  - `hover` → lift a few px + soft `glow` behind + show the **tooltip** (§5).
    Only when Mira is near (reuse the proximity gate,
    [`bookstore.py:417`](../../bookstore.py#L417)).
  - `taken` → not drawn (removed from shelf once in cart), like today's
    `Book.taken` ([`bookstore.py:154`](../../bookstore.py#L154)).

### 3b. Background spine (blurred)
Decorative spines behind the checkout desk and detail screen. Flatter 2-stop
gradient, smaller (`w 14–22`, `h 44–59`), drawn onto a surface then blurred
(downscale+upscale) at α .35–.50. No title, no interaction.

---

## 4. Book cover

### 4a. Large cover (screen 05)
- **Size:** 320×480, radius `6 10 10 6`.
- **Fill:** genre-hued diagonal gradient (Ashen Crown: violet
  `oklch(0.42 0.13 288)`→`(0.2 0.09 290)`).
- **Details:** left spine-shadow strip; inset 1.5px gold frame (inset 20);
  centered emblem (ring + 4 rays for Ashen Crown); title Cormorant 700 40,
  author uppercase tracked; top eyebrow "A Novel of the Star-Court".
- **Behind:** big violet `glow` halo.

### 4b. Cart thumbnail (screen 03)
- **Size:** 58×84, radius 3. Same gradient idea, miniature: inset frame, a small
  ring motif, tiny centered title (7px). Genre hue drives color.

Recommend `draw_cover(surf, rect, book, detail=False)` covering both sizes.

---

## 5. Book tooltip / info card

The hover popup on screen 02 (and the essence of screen 05's side panel).

- **Size:** ~262px wide, glass panel (§1), radius 14, padding 16–18.
- **Anchor:** a glowing dot on the spine + the card offset up-right; draw a
  connector or just the dot ([concept: dot at the spine, card at `+28,−30`]).
- **Contents, top→bottom:**
  1. Genre pill (§8)
  2. Title — Cormorant 600, 23, `CREAM`
  3. `by {author}` — italic 12, `TEXT_MUTED`
  4. Star row (§9) + `rating · pages pp`
  5. Short blurb — 12/1.45, `TEXT_MUTED`
  6. Divider (1px `PANEL_BORDER` α .5)
  7. Footer: price (coin glyph + number, Cormorant 20) ↔ **"Add · [E]"** pill (§2c)

API: `draw_tooltip(surf, book, anchor_xy, t)`.

---

## 6. Coin glyph & coin value

- **Glyph:** radial `COIN_LIGHT`→`COIN_DARK` circle, 2px inner ring
  `(203,126,25)`, optional outer `glow`. Sizes: 15 (inline price), 20 (HUD/total).
- **Value:** coin glyph + number in Cormorant 600, color `COIN_NUM` (HUD) or
  `MEMBER_CHARM`/gold (totals). Helper `coin_value(surf, pos, n, size)`.

Used in: HUD balance, tooltip/detail/cart prices, ledger subtotal & total,
receipt total ("70 ★").

---

## 7. Cart badge / count chip

HUD pill showing cart contents (screen 02, top-right).

- Glass pill (violet-tinted border), radius 30, padding 10×16.
- A small **cart icon** (trapezoid basket, `clip-path` in concept → draw a
  4-point polygon) + count in Cormorant 600, 22.
- **Notification dot:** `BADGE_RED` circle top-right, `+N` in Spectral 700 11,
  when items were just added. Fades after a beat (reuse `Pop`-style life).

---

## 8. Genre pill / tag

Small rounded label naming a genre (tooltip, cart row, detail).

- Radius 16–20, padding 2–4 × 8–11, uppercase, tracking 1.5–2, font ~9–10.
- **Color:** genre-hued — text light tint of the hue, fill same hue at α .4–.5.
  (Fantasy shown as violet; use `GENRE_HUE[genre]`.)
- A neutral variant exists too ("Epic · Standalone"): outlined, `TEXT_MUTED`.

`draw_pill(surf, pos, text, hue=None)` — `hue=None` → neutral outline style.

---

## 9. Star rating

`★★★★☆` from a float. `STAR_RATING` color, tracking ~1–2.

- Full/empty stars from `round(rating)`; optionally a half-star. Size 14
  (tooltip) / 20 (detail). Followed by `rating · N reviews`.
- `star_row(surf, pos, rating, size)`.

---

## 10. Progress bar

Quest tracker and ledger budget both use it.

- **Track:** `TRACK_BG`, radius 4–5, height 6 (quest) / 8 (budget).
- **Fill:** gradient `PROGRESS_A`→`PROGRESS_B`, width = `fraction × track_w`.
- `progress_bar(surf, rect, fraction)`.

---

## 11. Quest tracker (objective panel)

Screen 02 top-left. Glass panel (§1), max-width ~290, padding 14×18.

- Eyebrow row: small rotated-square glyph + "CURRENT QUEST" (tracked, gold).
- Quest title — Cormorant 20, `CREAM`, up to 2 lines.
- Progress bar (§10) at `quest.fraction(cart)`.
- Caption `"{progress} of {target} chosen"` — 11, `TEXT_MUTED`.

Reads `ctx.quest` + `ctx.cart`. `draw_quest(surf, quest, cart)`.

---

## 12. Ledger panel (cart summary)

Screen 03 right column. Glass card `PANEL_BG2` α .70, radius 18, padding 26,
width ~336.

- Heading "Ledger" — Cormorant 600, 26.
- Rows: `Subtotal … n`, `Member's charm … −5` (charm value in gold).
- Divider, then **Total** (Cormorant 22) ↔ big coin value (34).
- Inset **budget box** (`PANEL_BG` α .6): "Star-purse … 120", progress bar
  (spent fraction), "Remaining after … {n} coins" (gold).
- Primary button "Proceed to the Desk →" (§2a), disabled if unaffordable.
- Sub-link "Keep browsing the aisles".

Reads `ctx.ledger`/`ctx.wallet`. `draw_ledger(surf, ledger, wallet)`.

---

## 13. Receipt (checkout)

Screen 04 right side — a **light** paper card, the one inverted surface.

- Paper gradient `RECEIPT_TOP`→`RECEIPT_BOTTOM`, radius 16, padding 26, rotated
  ~1.2° (`pygame.transform.rotate` the finished sub-surface), `drop_shadow`.
- Header "Spines & Starlight" (Cormorant 700, 26) + "EST. BENEATH THE STARS"
  (tracked 10).
- Dashed dividers (draw a dashed line helper, color `RECEIPT_FAINT`).
- Line items: `title … price` per cart book (ellipsize long titles).
- "Member's charm … −5", then **Total Due … 70 ★** (Cormorant 700, 30).
- CTA "Complete Purchase" — violet gradient `CHECKOUT_BTN_TOP`→`CHECKOUT_BTN_BOT`,
  cream text (note: **not** the gold button here).
- Footer "THANK YOU FOR READING ★" (tracked 10).

`draw_receipt(surf, cart, ledger)`.

---

## 14. Character: Mira from behind + cart

Reused on screens 02 and 04 (and referenced on 01 as a distant silhouette).

- **Mira (behind):** rounded body gradient in plum `oklch(0.28 0.07 306)`→dark,
  head + hair blobs, warm rim-light glow on one side (`box-shadow` → a `glow`
  offset). ~96–120px tall.
- **Cart:** translucent wire basket (repeating-line texture), handle, two wheels,
  and book-tops poking out (small rounded rects in genre hues). ~120px wide.
- The existing front-facing `Mira` + `draw_cart`
  ([`bookstore.py:172`](../../bookstore.py#L172), [`:300`](../../bookstore.py#L300))
  already handle walking/bob/cart-follow — **restyle** them to this behind-view
  night palette rather than rewriting the motion.
- Distant **reader silhouette** (screen 01) is a simpler two-blob version.

---

## 15. Scene furniture (backgrounds)

Shared background pieces; detailed per-screen but reusable:

| Piece | Where | Notes |
|-------|-------|-------|
| **Starfield** | all | Fixed scatter of `STAR` dots + one `tw`-twinkling overlay layer |
| **Night gradient** | all | `NIGHT_TOP`→`NIGHT_BOTTOM` + warm top radial `glow` |
| **Shelf plank** | 02, 04 | 15px wood gradient bar, radius 3, top highlight — generalizes [`bookstore.py:269`](../../bookstore.py#L269) |
| **Hanging lantern** | 02 | Cord + rounded lamp, radial fill, `pulse` glow (design system §5) |
| **Hanging desk lamp** | 04 | Cone glow pool over the desk |
| **Desk** | 04 | Big wood gradient block `DESK_TOP`→`DESK_BOTTOM`, lip highlight |
| **Floor fade** | 02 | Bottom gradient to dark, over the shelves |

---

## 16. Feedback: `Pop`

Floating "+1" / "On list!" / coin-spend text already exists
([`bookstore.py:342`](../../bookstore.py#L342)) — reuse verbatim for:
- add-to-cart confirmation ("Added"),
- quest tick ("Quest +1"),
- coin changes at checkout.

---

## 17. Suggested module layout

```
primitives.py   §0 helpers (vgradient, glow, drop_shadow, render_tracked, coin_glyph, star_row, dashed_line)
widgets.py      Button, draw_spine, draw_cover, draw_tooltip, draw_pill,
                progress_bar, draw_quest, draw_ledger, draw_receipt,
                coin_value, cart_badge
actors.py       Mira (behind + front), Cart, reader silhouette   (restyled from bookstore.py)
furniture.py    starfield, night_bg, shelf_plank, lantern, desk_lamp, desk, floor_fade
```

Each screen doc composes these; if a screen needs a one-off, it's noted there.
