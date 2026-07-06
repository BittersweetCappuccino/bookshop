# Spines & Starlight — Data Model & Content

> The structures behind every screen: books, genres, the cart, the economy, the
> quest, and save data — plus the **full catalog** transcribed from the concept.
> Colors/hues come from [`01-design-system.md`](01-design-system.md).

The concept is data-driven: a `renderVals()` block defines 48 books across 4
genres, 5 cart items with prices, and the economy figures shown in the HUD and
ledger. This doc turns that into concrete types for the pygame build.

---

## 1. Genre

Four fixed genres. Each owns a hue (drives every color for its books) and a
shelf subtitle.

| Genre | `id` | Hue | Shelf subtitle | Aisle order |
|-------|------|-----|----------------|-------------|
| Fantasy | `fantasy` | 288 | "Epic & High" | 1 |
| Romance | `romance` | 18 | "Love & Longing" | 2 |
| Mystery | `mystery` | 210 | "Whodunnit & Noir" | 3 |
| Science Fiction | `scifi` | 238 | "Far Futures" | 4 |

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Genre:
    id: str
    name: str
    hue: int
    subtitle: str

GENRES = {
    "fantasy": Genre("fantasy", "Fantasy",         288, "Epic & High"),
    "romance": Genre("romance", "Romance",          18, "Love & Longing"),
    "mystery": Genre("mystery", "Mystery",         210, "Whodunnit & Noir"),
    "scifi":   Genre("scifi",   "Science Fiction", 238, "Far Futures"),
}
```

---

## 2. Book

The core entity. In the concept a book is a title + author + genre; the tooltip
and detail screens add price, rating, page count, review count, blurb, and
shelf-copy count. Spine geometry/color are **derived**, not stored (see
`spine_shades()` in the design system).

```python
@dataclass
class Book:
    id: str            # stable slug, e.g. "ashen-crown"
    title: str
    author: str
    genre: str         # key into GENRES
    price: int         # in coins
    # --- detail/tooltip fields (optional; sensible defaults) ---
    pages: int = 0
    rating: float = 0.0        # 0..5, shown as ★ to one decimal
    reviews: int = 0
    copies: int = 4            # "N copies on the shelf"
    blurb: str = ""            # 1-2 sentence description
    shelf_index: int = 0       # position in its aisle -> drives spine_shades()

    @property
    def hue(self) -> int:
        return GENRES[self.genre].hue
```

### Fields that are authored vs. derived

| Field | Source |
|-------|--------|
| title, author, genre | Concept catalog (§5) |
| price | §4 pricing (5 canonical from concept, rest assigned) |
| pages, rating, reviews, blurb, copies | Only **The Ashen Crown** is fully authored in the concept; others need filling (§6) |
| spine width/height/colors, band | Derived from `genre.hue` + `shelf_index` via `spine_shades()` |

---

## 3. Cart

An ordered list of the books the player has added. The concept cart holds 5.

```python
@dataclass
class Cart:
    items: list = field(default_factory=list)   # list[Book], insertion order

    @property
    def subtotal(self) -> int:
        return sum(b.price for b in self.items)

    @property
    def count(self) -> int:
        return len(self.items)

    def add(self, book):    # tooltip "Add · [E]" / detail "Add to Cart"
        if book not in self.items:
            self.items.append(book)

    def remove(self, book): # cart-row "Remove"
        if book in self.items:
            self.items.remove(book)
```

The concept's 5 cart items (canonical demo state, used by screens 03 & 04):

| # | Title | Author | Genre | Price |
|---|-------|--------|-------|-------|
| 1 | The Ashen Crown | E. Vale | Fantasy | 18 |
| 2 | A Kiss at Dusk | E. Bell | Romance | 14 |
| 3 | The Ninth Guest | L. Poe | Mystery | 16 |
| 4 | The Quantum Garden | N. Okafor | Sci-Fi | 15 |
| 5 | Nightbloom | R. Sable | Fantasy | 12 |

Subtotal = **75**.

---

## 4. Economy

The player spends **coins** ("star-purse"). All figures below are exactly the
concept's.

| Concept term | Meaning | Value in demo |
|--------------|---------|---------------|
| Star-purse | Coin balance | **120** |
| Subtotal | Sum of cart prices | 75 |
| Member's charm | Flat discount | **−5** |
| Total | Subtotal − discount | 70 |
| Remaining after | Balance − total | 50 |

```python
@dataclass
class Wallet:
    coins: int = 120

@dataclass
class Ledger:
    cart: Cart
    member_charm: int = 5          # flat discount in coins

    @property
    def subtotal(self):  return self.cart.subtotal
    @property
    def total(self):     return max(0, self.subtotal - self.member_charm)
    def remaining(self, wallet): return wallet.coins - self.total
    def affordable(self, wallet): return self.total <= wallet.coins
```

### Pricing model

Only 5 prices are canonical (the cart, §3). Prices range **10–18 coins**. For
the remaining catalog books, assign a price in that band. A deterministic rule
keeps it reproducible and shelf-balanced:

```python
def default_price(book_index_in_genre: int) -> int:
    # 12..18, gently varied; override per-book where the concept is canonical
    return 12 + (book_index_in_genre * 7) % 7   # -> 12..18
```

Keep the 5 canonical prices as explicit overrides so screens 03/04 match the
concept exactly. Prices are a **tuning knob**, not lore — adjust freely for game
balance.

---

## 5. The catalog (48 books, verbatim from the concept)

Transcribed from `renderVals()`. `shelf_index` = position in the aisle (0-based),
which feeds `spine_shades()`.

### Fantasy (hue 288)
| idx | Title | Author |
|-----|-------|--------|
| 0 | The Ashen Crown | E. Vale |
| 1 | Wolves of Winterhold | M. Frost |
| 2 | The Last Cartographer | I. Renn |
| 3 | Emberfall | S. Coe |
| 4 | A Song for Broken Kings | L. Ardent |
| 5 | The Gilded Thorn | N. Bramble |
| 6 | Nightbloom | R. Sable |
| 7 | Court of Cinders | A. Pyre |
| 8 | The Salt Witch | D. Mere |
| 9 | Hollow Kingdom | T. Grey |
| 10 | The Moth King | V. Lune |
| 11 | Thistle & Bone | P. Wren |

### Romance (hue 18)
| idx | Title | Author |
|-----|-------|--------|
| 0 | Letters to No One | J. Wilde |
| 1 | The Summer We Fell | C. Rose |
| 2 | Paper Hearts | M. Lane |
| 3 | A Kiss at Dusk | E. Bell |
| 4 | Meet Me in Verona | S. Marsh |
| 5 | The Florist's Daughter | P. Quinn |
| 6 | Slow Dancing | H. Vero |
| 7 | Love & Other Theorems | K. Ada |
| 8 | The Lighthouse Keeper | O. Bay |
| 9 | Autumn, Again | F. Holt |
| 10 | Wildflower Season | D. June |
| 11 | The Second First Kiss | R. Amos |

### Mystery (hue 210)
| idx | Title | Author |
|-----|-------|--------|
| 0 | The Vanishing Hour | R. Kade |
| 1 | Ink & Ashes | V. Crane |
| 2 | The Ninth Guest | L. Poe |
| 3 | Cold Harbor | B. Slate |
| 4 | The Locked Room | A. Finch |
| 5 | A Study in Rain | G. Mor |
| 6 | Nightingale Court | E. Ash |
| 7 | The Last Alibi | D. Vance |
| 8 | Fog Over Blackwell | H. Roe |
| 9 | Whisper in the Walls | M. Dunn |
| 10 | The Paper Knife | S. Loch |
| 11 | Twelve Bells | T. Wick |

### Science Fiction (hue 238)
| idx | Title | Author |
|-----|-------|--------|
| 0 | Titan Rising | X. Corvin |
| 1 | The Quantum Garden | N. Okafor |
| 2 | Halcyon-7 | J. Reyes |
| 3 | ExoGenesis | A. Vance |
| 4 | The Mars Accord | L. Zhou |
| 5 | Neon Requiem | S. Idris |
| 6 | Signal from Vega | P. Novak |
| 7 | A Thousand Suns | E. Rune |
| 8 | Orbital Decay | T. Solis |
| 9 | The Kepler Paradox | M. Cho |
| 10 | Ghost in the Lattice | K. Ito |
| 11 | The Ludic Engine | R. Bex |

> A ready-to-paste `CATALOG` list literal (with these titles/authors, genre
> keys, `shelf_index`, and prices) should live in `content.py`. Build spines by
> iterating each genre's list in order.

---

## 6. Detail content (blurbs, ratings, pages)

Only **The Ashen Crown** is fully authored in the concept:

| Field | Value |
|-------|-------|
| Pages | 512 |
| Rating | 4.2 (★★★★☆) |
| Reviews | 1,284 |
| Copies on shelf | 4 |
| Tags | "Fantasy", "Epic · Standalone" |
| Cover subtitle | "A Novel of the Star-Court" |
| Blurb (detail) | "A dethroned queen strikes a bargain with the star-court: one kingdom of ash restored, in exchange for a name she swore never to speak again. As constellations rearrange above her ruined city, she learns the crown was never made of gold — but of the debts we inherit." |
| Blurb (tooltip, short) | "A dethroned queen bargains with the star-court to win back a kingdom of ash." |

For the other 47 books there is **no authored blurb/rating**. Options, in order
of recommendation:
1. **Author a one-line blurb per book** as content work (best; ~47 lines).
2. **Procedural defaults** until authored: rating `round(3.6 + (idx%9)*0.15, 1)`
   (3.6–4.8), reviews `120 + idx*37`, pages `280 + (idx*53)%360`, a templated
   blurb per genre. Mark these as placeholder so screen 05 always has something
   to show.

Keep the short (tooltip) and long (detail) blurbs as separate fields; the
tooltip truncates hard at ~2 lines.

---

## 7. Quest / Objective

Screen 02's HUD shows a quest with a progress bar.

| Concept term | Value |
|--------------|-------|
| Title | "Gather five tales for the Solstice Book Club." |
| Target | 5 books |
| Progress shown | "3 of 5 chosen" (bar at 60%) |

```python
@dataclass
class Quest:
    title: str = "Gather five tales for the Solstice Book Club."
    target: int = 5
    def progress(self, cart): return min(cart.count, self.target)
    def fraction(self, cart): return self.progress(cart) / self.target
    def complete(self, cart): return cart.count >= self.target
```

This generalizes the current game's color shopping-list
([`bookstore.py:249`](../../bookstore.py#L249) `make_list`): instead of "collect
these 4 colors," the quest is "gather N tales" (optionally constrained by genre
later). The completion gate replaces `all_done`
([`bookstore.py:375`](../../bookstore.py#L375)).

---

## 8. Save data / profile

Screens 01 offers **Continue** and **Your Collection**, implying persistence.
Minimal shape:

```python
@dataclass
class Profile:
    coins: int = 120
    collection: list = field(default_factory=list)  # list[str] book ids owned
    continue_state: dict | None = None  # {scene, cart_ids, quest_progress} or None

# Serialise to JSON at e.g. save/profile.json.
```

- **New Story** → fresh `Profile`, cart empty, quest reset.
- **Continue** → load `continue_state`; disabled/grayed if `None`.
- **Your Collection** → gallery of `collection` book ids (owned after checkout).
  A dedicated Collection screen is **out of scope** for the five specced screens;
  the menu entry can be a stub for now.
- **Complete Purchase** (screen 04) → append cart ids to `collection`, subtract
  `total` from `coins`, clear cart.

---

## 9. Mapping from the current `Book`

Today's `Book` ([`bookstore.py:145`](../../bookstore.py#L145)) stores a color
name and a pygame `Rect`, with `taken`/`hover` flags. Migration:

| Old | New |
|-----|-----|
| `cname` / `color` (named color) | `genre` + derived `spine_shades()` |
| `Rect` position on one shelf | position derived from aisle + `shelf_index` |
| `taken` | still needed (spine removed once added to cart) |
| `hover` | still needed (drives tooltip on screen 02) |
| — | new: `title, author, price, pages, rating, reviews, blurb, copies` |

Keep `taken`/`hover` behavior; replace the color identity with the genre +
catalog identity above.

---

## 10. Suggested content module

```
content.py
├── GENRES              # from §1
├── CATALOG             # 48 Book instances (§5) with prices (§4) & shelf_index
├── DEMO_CART_IDS       # ["ashen-crown","a-kiss-at-dusk","the-ninth-guest",
│                        #  "the-quantum-garden","nightbloom"]  (§3)
├── DEFAULT_QUEST       # Quest(...) (§7)
└── helpers: books_by_genre(), find(book_id), default_price()
```

Screens import `CATALOG` and build their shelves/cart/detail views from it, so
the concept's demo state (screens 03/04 showing exactly those 5 books at total
70) is reproducible.
