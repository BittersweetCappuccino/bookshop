# Screen 04 — The Checkout Desk

> *The shopkeeper stamps each flyleaf by lamplight; a receipt curls across the
> counter.* Scene id **`CHECKOUT`**. Coordinates are concept px (1280×720);
> ×0.75 for 960×600. Tokens: [`01-design-system.md`](01-design-system.md) ·
> widgets: [`04-components.md`](04-components.md) · data:
> [`02-data-model.md`](02-data-model.md) · flow: [`03-screen-flow.md`](03-screen-flow.md).

---

## 1. Purpose

The payment step and emotional payoff: a lamplit desk, the shopkeeper, Mira from
the near side, and a warm paper receipt listing the purchase. Confirming here is
the one transaction that spends coins and grows the collection
([`03-screen-flow.md`](03-screen-flow.md) §6). Successor to the current game's
checkout zone + "Thanks for shopping" veil ([`bookstore.py:445`](../../bookstore.py#L445)).

## 2. Layout map (1280×720)

```
┌──────────────────────────────────────────────────────────────┐
│ ┌120◉┐        ░ blurred back shelves ░                        │
│ └────┘              │ lamp cord                               │
│                     ▽ lamp shade      ┌─── Receipt ────────┐  │
│                    ╱ ╲ light cone     │ Spines & Starlight  │ │
│                   ╱   ╲               │ EST. BENEATH STARS  │ │
│                  ╱     ╲    🧍 keeper  │ - - - - - - - - - - │ │
│         📚 stacked books   silhouette │ Ashen Crown     18  │ │
│         on desk                       │ ... 5 items ...     │ │
│    🧍‍♀️ Mira (near side)                │ Member's charm  −5  │ │
│  ══════════════ desk lip ═════════════│ Total Due   70 ★   │ │
│  ▐▐▐▐▐ desk front ▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐│ [Complete Purchase] │ │
│  ▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐│ THANK YOU FOR READING│ │
│  ▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐└─────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## 3. Scene (background → foreground)

| # | Element | Position / size | Spec |
|---|---------|-----------------|------|
| 1 | Frame + night bg | 1280×720 | Radius 18, border; night gradient + fixed stars + warm **top-left** radial glow |
| 2 | **Blurred back shelves** | top 60, left/right 60, h150 | ~26 background spines ([§3b](04-components.md)) + a shelf plank, `blur(3)` opacity .5. Draw to a surface, downscale/upscale to blur |
| 3 | **Lamp cord** | left 640, top 0, h120 | 2px dark line |
| 4 | **Lamp shade** | left 600, top 112, 82×40 | Rounded gradient, big warm `glow` beneath |
| 5 | **Light cone** | left 500, top 150, 280×360 | Radial `LANTERN`-warm ellipse, transparent edges — the pool of lamplight |
| 6 | **Shopkeeper** | top 250, left 760, 130×200 | Plum body + head blobs, gold rim-light `glow`; behind the desk. Simplified [§14 actor](04-components.md) |
| 7 | **Desk** | bottom 0, full width, 250 tall | `DESK_TOP`→`DESK_BOTTOM` gradient, top inset highlight |
| 8 | **Desk lip** | bottom 230, full width, 22 | Lighter wood band, shadow — the counter edge |
| 9 | **Stacked books** | bottom 250, left 150, ~200×120 | 4 books stacked flat, offset, in genre hues (violet/rose/teal/blue), each ~24px tall with shadow |
| 10 | **Mira (near side)** | bottom 20, left 430, 150×230 | From behind, larger than in `SHOP` (foreground). Restyle existing Mira |
| 11 | **Receipt panel** | top 64, right 60, w320 | Light paper, see §4 |
| 12 | **Coin HUD** | top 22, left 24 | Glass pill: coin glyph + `wallet.coins` (demo 120) |

## 4. Receipt / payment panel

The one **light** surface — a paper card, rotated ~1.2°
([`04-components.md`](04-components.md) §13). Draw contents to a sub-surface, then
`pygame.transform.rotate(1.2)` and blit with a drop shadow.

| Row | Content | Style |
|-----|---------|-------|
| Header | "Spines & Starlight" | Cormorant 700, 26, `RECEIPT_INK`, centered |
| Sub-header | "EST. BENEATH THE STARS" | tracked 10, `RECEIPT_FAINT` |
| *(dashed divider)* | | dashed line, `RECEIPT_FAINT` |
| Line items | `{title} … {price}` per `cart.items` | 13, `RECEIPT_INK`; ellipsize long titles |
| *(dashed divider)* | | |
| Member's charm | −5 | 13, `RECEIPT_FAINT` |
| **Total Due** | 70 ★ | "Total Due" Cormorant 700, 22 ↔ "70 ★" Cormorant 700, 30 |
| CTA | **Complete Purchase** | Violet gradient `CHECKOUT_BTN_TOP`→`CHECKOUT_BTN_BOT`, cream text — **not** the gold button |
| Footer | "THANK YOU FOR READING ★" | tracked 10, `RECEIPT_FAINT` |

Items and totals are **live** from `ctx` (`Ledger(cart)`); the concept demo lists
the 5 books totalling 70 ([`02-data-model.md`](02-data-model.md) §3–4).

## 5. Interactions

| Input | Condition | Result |
|-------|-----------|--------|
| Hover **Complete Purchase** | — | Button brightens ~10% |
| Click **Complete Purchase** | `ledger.affordable(wallet)` | Run `commit_purchase(ctx)` ([`03-screen-flow.md`](03-screen-flow.md) §6): spend `total`, add books to `collection`, clear cart, save → show **confirmation** (§6) |
| Click when unaffordable | shouldn't reach here (Cart gates it) | Button disabled as a safety net |
| **Esc** / back | — | `ctx.go(CART)` without paying |
| **M** | — | Mute (global) |

## 6. Purchase confirmation

After a successful commit, present a warm confirmation (the richer successor to
today's veil + "Thanks for shopping, Mira!"):

- Dim the scene with a plum veil (as [`bookstore.py:446`](../../bookstore.py#L446)).
- Message: "Thank you for reading" / "Your tales are gathered." Cormorant `CREAM`.
- Optional: a receipt "stamp" flourish, a coin-spend `Pop`, and the cash chime
  already in the game ([`bookstore.py:365`](../../bookstore.py#L365) `cash`).
- **Any key** → `ctx.go(TITLE)`. (Cart is now empty; a fresh run starts from the
  menu.)

## 7. Motion

- Lamp glow (soft, steady or a gentle `pulse`).
- Twinkling starfield.
- Optional: the receipt curls/settles on enter; coin-spend `Pop` + chime on
  confirm. None required beyond the confirm feedback.

## 8. States

| State | Trigger | Visual |
|-------|---------|--------|
| Ready | on enter (affordable) | Scene + receipt; Complete Purchase active |
| Hover | pointer on CTA | Button brighten |
| Confirmed | Complete Purchase | Veil + thank-you; awaiting any key |
| Returning | any key after confirm | → `TITLE` |

## 9. Implementation notes

- **New screen**; scene furniture (desk, lamp, shopkeeper, blurred shelves) is
  largely decorative — build it once to a cached surface; only the lamp glow,
  twinkle, Mira, receipt hover, and confirm veil redraw per frame.
- The receipt is the only rotated element — render upright to a sub-surface, then
  rotate; hit-test the CTA in the rotated space (or keep the button's hit-rect
  axis-aligned by placing it before rotation and transforming the point).
- Reuse `draw_receipt`, `coin_value`, the `Mira` actor, `Pop`, and the existing
  `cash` chime + veil pattern. This screen is where the most existing checkout
  code (chime, veil, thank-you) carries over.
- Guard `commit_purchase` to run **once** (ignore repeat clicks after confirm).

## 10. Acceptance checklist

- [ ] Lamplit desk scene: blurred back shelves, hanging lamp with a light cone, desk + lip.
- [ ] Shopkeeper silhouette behind the desk; stacked books on the counter; Mira (near side) from behind.
- [ ] Rotated paper receipt: header, dashed dividers, live line items, member's charm, Total Due with ★.
- [ ] "Complete Purchase" uses the violet gradient (not gold); brightens on hover.
- [ ] Confirm runs `commit_purchase` once: coins spent, books added to collection, cart cleared, profile saved.
- [ ] Confirmation veil + thank-you; any key returns to Title.
- [ ] Esc returns to Cart without paying; coin HUD shown; starfield twinkles.
