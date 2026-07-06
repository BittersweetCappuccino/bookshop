# Spines & Starlight — Screen Flow & State Machine

> How the five screens connect: the scene graph, every transition and its
> trigger, the global input model, and how this replaces the single loop in
> [`bookstore.py`](../../bookstore.py). Screens are specced individually in
> `screen-01…05`; this doc is the glue.

---

## 1. Scenes

| Scene id | Screen | Doc |
|----------|--------|-----|
| `TITLE` | 01 Title & Start Menu | [`screen-01-title.md`](screen-01-title.md) |
| `SHOP` | 02 Genre Aisles | [`screen-02-bookshop.md`](screen-02-bookshop.md) |
| `DETAIL` | 05 Book Close-Up | [`screen-05-book-detail.md`](screen-05-book-detail.md) |
| `CART` | 03 Your Cart | [`screen-03-cart.md`](screen-03-cart.md) |
| `CHECKOUT` | 04 Checkout Desk | [`screen-04-checkout.md`](screen-04-checkout.md) |

`SHOP` is the hub. `DETAIL` is a modal-like overlay opened from `SHOP` (and
optionally from `CART`). `CART` → `CHECKOUT` is the purchase funnel.

---

## 2. Flow graph

```
                    ┌──────────────────────────────────────────────┐
                    │                                              │
              ┌─────▼─────┐                                        │
   boot ─────▶│   TITLE   │                                        │
              └─────┬─────┘                                        │
       New Story /  │  (Continue restores saved scene)            │
       Continue     ▼                                              │
              ┌───────────┐   select spine / "Read"   ┌──────────┐│
              │           │──────────────────────────▶│  DETAIL  ││
              │   SHOP    │◀──────────────────────────│          ││
              │  (hub)    │   Esc / Back to the aisle  └────┬─────┘│
              │           │        Add to Cart ────────────┘      │
              └──┬─────▲──┘                                        │
     open cart   │     │ Keep browsing the aisles                 │
      (C / icon) ▼     │                                          │
              ┌───────────┐                                       │
              │   CART    │                                       │
              └─────┬─────┘                                       │
   Proceed to the   │  ▲  Keep browsing → SHOP                    │
        Desk        ▼  │                                          │
              ┌───────────┐                                       │
              │ CHECKOUT  │                                       │
              └─────┬─────┘                                       │
    Complete        │                                            │
    Purchase        ▼                                            │
              (receipt → return to TITLE) ──────────────────────┘
```

---

## 3. Transitions

Every edge, its trigger, and its effect. "Push"/"pop" note whether the origin
scene stays alive underneath (for overlay-style returns).

| From | To | Trigger | Effect / notes |
|------|----|---------|----------------|
| boot | `TITLE` | app start | Load `Profile`; play title music |
| `TITLE` | `SHOP` | "New Story" button / any key | Fresh cart & quest; enter shop |
| `TITLE` | `SHOP`* | "Continue" button | Restore `continue_state`; jump to its saved scene (usually `SHOP` or `CART`). Greyed if no save |
| `TITLE` | `COLLECTION`† | "Your Collection" | Out of scope — stub for now |
| `TITLE` | `SETTINGS`† | "Settings" | Out of scope — stub for now |
| `SHOP` | `DETAIL` | click/select a spine, or "Read" on tooltip | Push `DETAIL` with that `Book`; `SHOP` stays underneath |
| `DETAIL` | `SHOP` | "← Back to the aisle" / **Esc** | Pop back to `SHOP` unchanged |
| `DETAIL` | `SHOP` | "Add to Cart · N" | `cart.add(book)`, spend nothing yet, pop to `SHOP`; spine now `taken`; `+1`/coin feedback |
| `SHOP` | `CART` | cart icon / **C** | Open cart |
| `SHOP` | `SHOP` | add via tooltip "Add · [E]" | In-place: `cart.add`, spine `taken`, HUD updates; no scene change |
| `CART` | `SHOP` | "Keep browsing the aisles" / **Esc** | Return to shop |
| `CART` | `CHECKOUT` | "Proceed to the Desk →" | Only if `ledger.affordable(wallet)`; else disabled |
| `CART` | `SHOP` | "Remove" on a row | In-place: `cart.remove`; spine returns to shelf |
| `CHECKOUT` | `TITLE` | "Complete Purchase" → receipt → key | Commit purchase (see §6), clear cart, return to title |
| `CHECKOUT` | `CART` | **Esc** / back | Return to cart without paying |
| any | `TITLE` | (quit-to-menu, optional) | Not in the concept; add if desired |
| any | exit | **Esc** at `TITLE`, or window close | Quit (matches current `QUIT`/`K_ESCAPE`) |

\* Continue targets whatever scene the save recorded.
† Collection/Settings are named in the title menu but not specced as screens.

### Esc ladder

Esc always steps **one level back**, never straight to quit except at the top:

```
DETAIL → SHOP → (SHOP is hub; Esc here does nothing, or opens a pause menu)
CART   → SHOP
CHECKOUT → CART
TITLE  → quit
```

---

## 4. Scene interface

A tiny scene protocol keeps the main loop clean. Each screen doc implements one.

```python
class Scene:
    def on_enter(self, ctx): ...          # called once when pushed/switched to
    def on_exit(self): ...                # called once when left
    def handle_event(self, e, ctx): ...   # per pygame event; may request a transition
    def update(self, dt, ctx): ...        # per-frame logic (animations, input held)
    def draw(self, surf, ctx): ...        # render to the 1280x720 surface

# A transition is requested by returning/So setting:
#   ctx.go(SceneId, **params)      switch (replace)
#   ctx.push(SceneId, **params)    overlay (DETAIL over SHOP)
#   ctx.pop()                      return from an overlay
```

`ctx` (game context) carries the shared state every scene reads/writes:

```python
@dataclass
class Context:
    profile: Profile
    wallet: Wallet
    cart: Cart
    quest: Quest
    catalog: list          # from content.CATALOG
    t: int = 0             # global frame counter (drives motion)
    muted: bool = False
    # navigation:
    def go(self, scene_id, **params): ...
    def push(self, scene_id, **params): ...
    def pop(self): ...
```

The `cart`, `wallet`, and `quest` live on `ctx`, **not** inside a scene, so the
HUD in `SHOP`, the ledger in `CART`, and the receipt in `CHECKOUT` all read the
same source of truth.

---

## 5. Main loop (replacing the current one)

The current game is one hard-coded loop
([`bookstore.py:370`](../../bookstore.py#L370)). Generalise it to a stack of
scenes:

```python
def main():
    ctx = Context(profile=load_profile(), wallet=Wallet(), cart=Cart(),
                  quest=DEFAULT_QUEST, catalog=CATALOG)
    stack = [make_scene(TITLE)]          # scene stack; top is active
    stack[-1].on_enter(ctx)

    while True:
        dt = clock.tick(FPS)
        ctx.t += 1
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            stack[-1].handle_event(e, ctx)   # active scene only
        stack[-1].update(dt, ctx)

        # draw: overlay scenes (DETAIL) render the scene below first
        for sc in visible_slice(stack):
            sc.draw(screen, ctx)

        # process any navigation the scene requested
        apply_transitions(stack, ctx)
        pygame.display.flip()
```

- **`go`** replaces `stack[-1]` (TITLE→SHOP, CART→CHECKOUT).
- **`push`** appends (SHOP→DETAIL); DETAIL draws SHOP underneath dimmed.
- **`pop`** removes the top (DETAIL→SHOP).

Global keys (**M** mute, window close) are handled in the loop before delegating,
matching today's behaviour ([`bookstore.py:388`](../../bookstore.py#L388)).

---

## 6. Purchase commit (the one state-mutating transition)

"Complete Purchase" on `CHECKOUT` is the only edge that spends money and grows
the collection. Do it once, atomically, on confirm:

```python
def commit_purchase(ctx):
    ledger = Ledger(ctx.cart)
    if not ledger.affordable(ctx.wallet):
        return False
    ctx.wallet.coins -= ledger.total
    ctx.profile.collection += [b.id for b in ctx.cart.items]
    ctx.profile.coins = ctx.wallet.coins
    ctx.cart = Cart()                # empty for next visit
    save_profile(ctx.profile)
    return True
```

Then show the receipt/confirmation, and on any key return to `TITLE`. This is the
richer successor to today's `checked_out` flag + "Thanks for shopping" veil
([`bookstore.py:445`](../../bookstore.py#L445)).

---

## 7. Global input model

| Input | Meaning | Scope |
|-------|---------|-------|
| Mouse move | Hover (spines, buttons, rows) | all |
| Left click | Activate hovered element | all |
| Arrow keys / A,D | Walk Mira | `SHOP` only (reuse [`bookstore.py:181`](../../bookstore.py#L181)) |
| **E** | Add hovered/nearby book | `SHOP` (tooltip "Add · [E]") |
| **C** | Open cart | `SHOP` |
| **Esc** | Back one level (§3 ladder) | all |
| **Enter / any key** | Advance (TITLE start, receipt dismiss) | `TITLE`, receipt |
| **M** | Mute/unmute music | global |
| Window close | Quit | global |

Keep the on-screen control hint pattern the game already draws
([`bookstore.py:439`](../../bookstore.py#L439)), but make it per-scene (each
screen doc lists its own hints).

---

## 8. Transitions & polish (optional)

The concept implies gentle motion but specifies no scene transitions. Suggested,
low-cost:
- **Crossfade** (~0.25 s black or plum wipe) between full scene switches.
- **DETAIL** slides/fades up over a dimmed `SHOP` (it's already drawn beneath).
- Preserve the twinkling starfield across screens so cuts feel continuous.

None are required for a first pass — a hard cut is acceptable.
