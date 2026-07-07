"""
Spines & Starlight — data model & content.

Books, genres, the cart, the economy, the quest, and save data, plus the full
48-book catalog transcribed from the concept. See
docs/spines-and-starlight/02-data-model.md.
"""

import json
import os
import re
from dataclasses import dataclass, field, asdict

from . import theme


# ----------------------------------------------------------------------
# Genre (§1)
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Genre:
    id: str
    name: str
    hue: int
    subtitle: str
    order: int


GENRES = {
    "fantasy": Genre("fantasy", "Fantasy", theme.GENRE_HUE["fantasy"], "Epic & High", 1),
    "romance": Genre("romance", "Romance", theme.GENRE_HUE["romance"], "Love & Longing", 2),
    "mystery": Genre("mystery", "Mystery", theme.GENRE_HUE["mystery"], "Whodunnit & Noir", 3),
    "scifi": Genre("scifi", "Science Fiction", theme.GENRE_HUE["scifi"], "Far Futures", 4),
}


# ----------------------------------------------------------------------
# Book (§2)
# ----------------------------------------------------------------------
@dataclass
class Book:
    id: str
    title: str
    author: str
    genre: str          # key into GENRES
    price: int          # in coins
    # detail / tooltip fields
    pages: int = 0
    rating: float = 0.0
    reviews: int = 0
    copies: int = 4
    blurb: str = ""         # long, for the detail screen
    blurb_short: str = ""   # short, for the tooltip (~2 lines)
    shelf_index: int = 0    # position in its aisle -> drives spine_shades()

    @property
    def hue(self) -> int:
        return GENRES[self.genre].hue

    @property
    def placeholder(self) -> bool:
        """True while detail copy is procedurally generated, not authored."""
        return self._placeholder

    _placeholder: bool = False


# ----------------------------------------------------------------------
# Cart (§3)
# ----------------------------------------------------------------------
@dataclass
class Cart:
    items: list = field(default_factory=list)   # list[Book], insertion order

    @property
    def subtotal(self) -> int:
        return sum(b.price for b in self.items)

    @property
    def count(self) -> int:
        return len(self.items)

    def add(self, book):
        if book not in self.items:
            self.items.append(book)

    def remove(self, book):
        if book in self.items:
            self.items.remove(book)

    def has(self, book):
        return book in self.items


# ----------------------------------------------------------------------
# Economy (§4)
# ----------------------------------------------------------------------
@dataclass
class Wallet:
    coins: int = 120


@dataclass
class Ledger:
    cart: Cart
    member_charm: int = 5   # flat discount in coins

    @property
    def subtotal(self):
        return self.cart.subtotal

    @property
    def discount(self):
        # never discount more than the subtotal
        return min(self.member_charm, self.subtotal)

    @property
    def total(self):
        return max(0, self.subtotal - self.member_charm)

    def remaining(self, wallet):
        return wallet.coins - self.total

    def affordable(self, wallet):
        return self.total <= wallet.coins


def default_price(idx: int) -> int:
    """Deterministic price in 12..18 for a book at aisle index idx.

    (The doc's `12 + (idx*7) % 7` is a no-op — idx*7 is always divisible by 7 —
    so we use a coprime multiplier that actually spreads across the band.)
    """
    return 12 + (idx * 5) % 7


# ----------------------------------------------------------------------
# Quest (§7)
# ----------------------------------------------------------------------
@dataclass
class Quest:
    title: str = "Gather five tales for the Solstice Book Club."
    target: int = 5

    def progress(self, cart):
        return min(cart.count, self.target)

    def fraction(self, cart):
        return self.progress(cart) / self.target

    def complete(self, cart):
        return cart.count >= self.target


DEFAULT_QUEST = Quest()


# ----------------------------------------------------------------------
# The catalog (§5) — 48 books, verbatim titles/authors from the concept
# ----------------------------------------------------------------------
_CATALOG_RAW = {
    "fantasy": [
        ("The Ashen Crown", "E. Vale"),
        ("Wolves of Winterhold", "M. Frost"),
        ("The Last Cartographer", "I. Renn"),
        ("Emberfall", "S. Coe"),
        ("A Song for Broken Kings", "L. Ardent"),
        ("The Gilded Thorn", "N. Bramble"),
        ("Nightbloom", "R. Sable"),
        ("Court of Cinders", "A. Pyre"),
        ("The Salt Witch", "D. Mere"),
        ("Hollow Kingdom", "T. Grey"),
        ("The Moth King", "V. Lune"),
        ("Thistle & Bone", "P. Wren"),
    ],
    "romance": [
        ("Letters to No One", "J. Wilde"),
        ("The Summer We Fell", "C. Rose"),
        ("Paper Hearts", "M. Lane"),
        ("A Kiss at Dusk", "E. Bell"),
        ("Meet Me in Verona", "S. Marsh"),
        ("The Florist's Daughter", "P. Quinn"),
        ("Slow Dancing", "H. Vero"),
        ("Love & Other Theorems", "K. Ada"),
        ("The Lighthouse Keeper", "O. Bay"),
        ("Autumn, Again", "F. Holt"),
        ("Wildflower Season", "D. June"),
        ("The Second First Kiss", "R. Amos"),
    ],
    "mystery": [
        ("The Vanishing Hour", "R. Kade"),
        ("Ink & Ashes", "V. Crane"),
        ("The Ninth Guest", "L. Poe"),
        ("Cold Harbor", "B. Slate"),
        ("The Locked Room", "A. Finch"),
        ("A Study in Rain", "G. Mor"),
        ("Nightingale Court", "E. Ash"),
        ("The Last Alibi", "D. Vance"),
        ("Fog Over Blackwell", "H. Roe"),
        ("Whisper in the Walls", "M. Dunn"),
        ("The Paper Knife", "S. Loch"),
        ("Twelve Bells", "T. Wick"),
    ],
    "scifi": [
        ("Titan Rising", "X. Corvin"),
        ("The Quantum Garden", "N. Okafor"),
        ("Halcyon-7", "J. Reyes"),
        ("ExoGenesis", "A. Vance"),
        ("The Mars Accord", "L. Zhou"),
        ("Neon Requiem", "S. Idris"),
        ("Signal from Vega", "P. Novak"),
        ("A Thousand Suns", "E. Rune"),
        ("Orbital Decay", "T. Solis"),
        ("The Kepler Paradox", "M. Cho"),
        ("Ghost in the Lattice", "K. Ito"),
        ("The Ludic Engine", "R. Bex"),
    ],
}

# Canonical prices keyed by (genre, shelf_index) — the 5 cart books (§3) so
# screens 03/04 reproduce the concept's subtotal of 75 exactly.
_PRICE_OVERRIDES = {
    ("fantasy", 0): 18,   # The Ashen Crown
    ("romance", 3): 14,   # A Kiss at Dusk
    ("mystery", 2): 16,   # The Ninth Guest
    ("scifi", 1): 15,     # The Quantum Garden
    ("fantasy", 6): 12,   # Nightbloom
}

# Fully-authored detail copy — only The Ashen Crown exists in the concept (§6).
_AUTHORED = {
    ("fantasy", 0): dict(
        pages=512, rating=4.2, reviews=1284, copies=4,
        blurb=(
            "A dethroned queen strikes a bargain with the star-court: one kingdom "
            "of ash restored, in exchange for a name she swore never to speak "
            "again. As constellations rearrange above her ruined city, she learns "
            "the crown was never made of gold — but of the debts we inherit."
        ),
        blurb_short=(
            "A dethroned queen bargains with the star-court to win back a kingdom "
            "of ash."
        ),
    ),
}

# Placeholder blurb templates per genre, until each book is authored (§6 opt. 2).
_BLURB_TEMPLATE = {
    "fantasy": "A tale of crowns and cinders, where old magic keeps its promises at a price.",
    "romance": "Two hearts circle each other through a long, golden season of almosts.",
    "mystery": "A locked room, an unquiet town, and one truth that refuses to stay buried.",
    "scifi": "Far from home, a fragile crew wagers everything on a signal in the dark.",
}


def _slugify(title: str) -> str:
    s = title.lower().replace("&", "and").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def _build_catalog():
    books = []
    for gid, entries in _CATALOG_RAW.items():
        for idx, (title, author) in enumerate(entries):
            key = (gid, idx)
            price = _PRICE_OVERRIDES.get(key, default_price(idx))
            authored = _AUTHORED.get(key)
            if authored:
                book = Book(
                    id=_slugify(title), title=title, author=author, genre=gid,
                    price=price, shelf_index=idx, **authored,
                )
            else:
                # Procedural defaults so screen 05 always has something to show.
                book = Book(
                    id=_slugify(title), title=title, author=author, genre=gid,
                    price=price, shelf_index=idx,
                    pages=280 + (idx * 53) % 360,
                    rating=round(3.6 + (idx % 9) * 0.15, 1),
                    reviews=120 + idx * 37,
                    copies=4,
                    blurb=_BLURB_TEMPLATE[gid],
                    blurb_short=_BLURB_TEMPLATE[gid],
                )
                book._placeholder = True
            books.append(book)
    return books


CATALOG = _build_catalog()
_BY_ID = {b.id: b for b in CATALOG}

# The concept's canonical 5-item demo cart (§3), by id.
DEMO_CART_IDS = [
    _slugify("The Ashen Crown"),
    _slugify("A Kiss at Dusk"),
    _slugify("The Ninth Guest"),
    _slugify("The Quantum Garden"),
    _slugify("Nightbloom"),
]


# ----------------------------------------------------------------------
# Helpers (§10)
# ----------------------------------------------------------------------
def find(book_id):
    return _BY_ID.get(book_id)


def books_by_genre(genre_id):
    return [b for b in CATALOG if b.genre == genre_id]


def demo_cart():
    """A fresh Cart pre-filled with the concept's five demo books."""
    cart = Cart()
    for bid in DEMO_CART_IDS:
        cart.add(find(bid))
    return cart


# ----------------------------------------------------------------------
# Save data / profile (§8)
# ----------------------------------------------------------------------
SAVE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "save", "profile.json")


@dataclass
class Profile:
    coins: int = 120
    collection: list = field(default_factory=list)   # list[str] book ids owned
    continue_state: dict | None = None               # {scene, cart_ids} or None


def load_profile(path=SAVE_PATH):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return Profile(**data)
    except (FileNotFoundError, ValueError, TypeError):
        return Profile()


def save_profile(profile, path=SAVE_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(asdict(profile), fh, indent=2)
