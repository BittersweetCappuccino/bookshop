# Spines & Starlight — Implementation Overview

> **Source of truth:** [`docs/Spines_and_Starlight_UI_Concept.html`](../Spines_and_Starlight_UI_Concept.html)
> A concept-art board of five game screens for a cozy fantasy bookshop game.
> **Target:** extend the existing pygame game in [`bookstore.py`](../../bookstore.py).

This folder is the implementation spec derived from that concept. Read this
page first, then the design system, then the per-screen specs.

---

## 1. Vision

*Spines & Starlight* is a cozy fantasy bookshop lit by falling stars. The player
browses genre aisles, pulls volumes off the shelf to read them, fills a cart
against a "star-purse" coin budget, and pays a lamplit shopkeeper at the desk.
The mood is warm, quiet, and a little magical — deep plum night, gold starlight,
serif type.

It is a **richer reimagining** of the game that already exists in
[`bookstore.py`](../../bookstore.py) ("The Little Bookshop"), which today is a
single screen: Mira walks a shelf, clicks books that match a colour list, and
wheels a cart to a checkout zone. Spines & Starlight keeps that spine — walk,
gather, checkout — and expands it into five distinct screens with real book
data, an economy, and a menu.

## 2. The five screens

| # | Screen | Working name | One line |
|---|--------|--------------|----------|
| 01 | Title & Start Menu | `TITLE` | The threshold — a lone reader arrives as the stars begin to fall. |
| 02 | The Bookshop — Genre Aisles | `SHOP` | Third-person browsing; hover a spine for details, picked books drop into the cart. |
| 03 | Your Cart | `CART` | Review the night's finds against a starlight budget. |
| 04 | The Checkout Desk | `CHECKOUT` | The shopkeeper stamps each flyleaf by lamplight; a receipt curls across the counter. |
| 05 | Book Close-Up | `DETAIL` | Pull a single volume from the shelf to read its cover, blurb, and price. |

Each screen has its own spec doc (`screen-01-title.md` … `screen-05-book-detail.md`).

## 3. Screen relationships (at a glance)

```
        ┌─────────────┐
        │  01 TITLE   │
        └──────┬──────┘
               │ New Story / Continue
               ▼
        ┌─────────────┐   hover+select a spine   ┌───────────────┐
        │   02 SHOP   │ ───────────────────────▶ │  05 DETAIL    │
        │ (aisles)    │ ◀─────────────────────── │  (close-up)   │
        └──────┬──────┘        Esc / back         └───────┬───────┘
               │ open cart                                │ Add to Cart
               ▼                                          │
        ┌─────────────┐                                   │
        │   03 CART   │ ◀─────────────────────────────────┘
        └──────┬──────┘
               │ Proceed to the Desk
               ▼
        ┌─────────────┐
        │ 04 CHECKOUT │ ── Complete Purchase ──▶ (receipt / back to TITLE)
        └─────────────┘
```

The authoritative version of this flow — with every transition, trigger, and
input — lives in [`03-screen-flow.md`](03-screen-flow.md).

## 4. How this maps onto the existing game

| Concept element | Today in `bookstore.py` | Change needed |
|-----------------|-------------------------|---------------|
| 5 screens | 1 screen (shop only) | Introduce a **scene/state machine** (see flow doc) |
| Books with title/author/genre/price | Books are coloured rectangles keyed by colour name | Replace `Book` colour model with a data-driven catalog ([`02-data-model.md`](02-data-model.md)) |
| Genre aisles (Fantasy/Romance/Mystery/Sci-Fi) | One flat set of shelves | Group shelves by genre, hue per genre |
| Star-purse coins, prices, member's charm | No economy | Add coin balance + per-book prices + discount |
| Quest: "gather 5 tales" | Colour shopping list of 4 | Generalise the objective/quest tracker |
| Mira, walking, cart | `Mira`, `draw_cart`, walking already exist | Reuse; restyle to the night palette |
| Cormorant Garamond / Spectral | `georgia` SysFont | Map to best available serif ([`01-design-system.md`](01-design-system.md)) |
| Hover tooltip / book detail | Hover glow only | New tooltip + full detail screen |

The existing walking, cart, and pop-up feedback code is a good foundation for
screen 02 — reuse it rather than rewriting.

## 5. Resolution & scaling

- **Concept canvas:** every screen is drawn at **1280 × 720**.
- **Current game window:** **960 × 600** (`W, H` in [`bookstore.py:33`](../../bookstore.py#L33)).

**Recommendation: adopt 1280 × 720 as the game canvas.** The concept's layouts,
type sizes, and paddings are all specified in 1280×720 space; matching it lets us
transcribe measurements directly instead of rescaling every value (and risking
crowded HUD/tooltips). 720p is still a safe windowed size.

All measurements in the per-screen specs are given in **concept pixels (1280×720)**.
If you keep 960×600 instead, apply a uniform scale factor of **0.75** (960/1280 =
600/720 = 0.75) to every coordinate, size, and font — noted again in each spec.

## 6. Character naming

The concept shows the browsing character only from behind and never names her.
The existing game calls her **Mira**. These docs keep the name **Mira** for the
player character and **the Shopkeeper** for the figure behind the desk in
screen 04.

## 7. Document index

| Doc | Purpose |
|-----|---------|
| `00-overview.md` | This page — vision, screen map, scope. |
| [`01-design-system.md`](01-design-system.md) | Palette (oklch→RGB), typography, spacing, motion. |
| [`02-data-model.md`](02-data-model.md) | Book/genre/cart/economy structures + the full catalog. |
| [`03-screen-flow.md`](03-screen-flow.md) | Scene state machine, transitions, input model. |
| [`04-components.md`](04-components.md) | Reusable widgets (buttons, spine, tooltip, badges, panels). |
| [`screen-01-title.md`](screen-01-title.md) | Title & Start Menu. |
| [`screen-02-bookshop.md`](screen-02-bookshop.md) | Genre Aisles. |
| [`screen-03-cart.md`](screen-03-cart.md) | Your Cart. |
| [`screen-04-checkout.md`](screen-04-checkout.md) | Checkout Desk. |
| [`screen-05-book-detail.md`](screen-05-book-detail.md) | Book Close-Up. |

## 8. Status

| # | Document | Status |
|---|----------|--------|
| 1 | `00-overview.md` | ✅ Done |
| 2 | `01-design-system.md` | ✅ Done |
| 3 | `02-data-model.md` | ✅ Done |
| 4 | `03-screen-flow.md` | ✅ Done |
| 5 | `04-components.md` | ✅ Done |
| 6 | `screen-01-title.md` | ✅ Done |
| 7 | `screen-02-bookshop.md` | ✅ Done |
| 8 | `screen-03-cart.md` | ✅ Done |
| 9 | `screen-04-checkout.md` | ✅ Done |
| 10 | `screen-05-book-detail.md` | ⬜ Not started |
