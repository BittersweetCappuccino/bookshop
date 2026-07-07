# Spines & Starlight

A cozy fantasy bookshop game, lit by falling stars. Walk the genre aisles, pull
volumes off the shelf to read them, fill a cart against a "star-purse" coin
budget, and pay the shopkeeper at a lamplit desk — all in deep-plum night, gold
starlight, and serif type.

*Spines & Starlight* is a complete five-screen game written in Python with
[pygame](https://www.pygame.org/). It started as a concept-art board and written
spec (under [`docs/`](docs/)) and is now fully implemented in the
[`spines/`](spines/) package.

> **Why this exists.** As someone who loves books — reading them, buying far too
> many, and even writing — and who is genuinely fascinated by AI, I wanted a
> project that brought both worlds together. *Spines & Starlight* was built as an
> exploration of Claude Code's (Anthropic's agentic coding tool) ability to design
> and implement a complete game in Python — from concept art to a playable build.

---

## Running the game

Requires **Python 3.10+**. The only dependency — pygame (the maintained
`pygame-ce` fork) — is pinned in [`requirements.txt`](requirements.txt).

**1. Clone the project and create a virtual environment.**

_Windows (PowerShell):_

```powershell
git clone https://github.com/BittersweetCappuccino/bookshop.git
cd bookshop
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

_macOS / Linux:_

```bash
git clone https://github.com/BittersweetCappuccino/bookshop.git
cd bookshop
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

**2. Run the game** using the virtual environment's Python:

```text
.venv\Scripts\python.exe -m spines     # Windows
.venv/bin/python -m spines             # macOS / Linux
```

> Tip: if you `activate` the environment first (`.venv\Scripts\activate` on
> Windows, `source .venv/bin/activate` on macOS/Linux), you can just run
> `python -m spines`.

The window sizes itself to fit your display and is resizable; **F11** toggles
fullscreen. No asset files are needed — the art is drawn in code, the fonts are
bundled, and the music and chimes are generated procedurally.

### Controls

| Input | Action |
|-------|--------|
| Arrow keys / A, D | Walk Mira along the aisles (in the Bookshop) |
| Hover a nearby spine | Preview a book in a tooltip |
| **E** | Add the hovered book to your cart |
| Click a spine | Open its close-up — cover, blurb, price |
| **C** | Open your cart |
| Enter / Click | Confirm: start, add, proceed, complete purchase |
| **Esc** | Back one screen (and quit from the title) |
| **M** | Mute / unmute music |
| **F11** | Toggle fullscreen |

---

## The game

Five screens, plus two menu screens, sharing one cart, wallet, and quest:

- **Title & Start Menu** — the threshold as the stars begin to fall: *New Story*,
  *Continue*, *Your Collection*, *Settings*.
- **The Bookshop (Genre Aisles)** — the hub. Walk Mira (seen from behind) past
  four genre aisles — Fantasy, Romance, Mystery, Science Fiction — each a shelf of
  colour-coded spines. Hover a nearby spine for its tooltip, press **E** to drop
  it in the cart, or click to read it. A quest ("gather five tales"), your coin
  balance, and a cart badge sit in the HUD.
- **Book Close-Up** — a large genre-hued cover with tags, a star rating, blurb,
  page count, stock, and *Add to Cart*.
- **Your Cart** — review your finds with a ledger: subtotal, a member's-charm
  discount, the total, and what your star-purse balance becomes after. Remove any
  book; proceed to the desk if you can afford it.
- **The Checkout Desk** — a lamplit desk with the shopkeeper and a paper receipt.
  *Complete Purchase* spends your coins, shelves the books in your Collection, and
  clears the cart.
- **Your Collection** & **Settings** — a gallery of the books you own, and a small
  options panel (music toggle, fullscreen hint).

Under the hood: a 48-book catalog across four genres, a coin economy, a
scene-stack state machine, a soft procedural music-box score with chimes, and the
**Cormorant Garamond** + **Spectral** serif fonts (SIL Open Font License) bundled
in [`spines/assets/fonts/`](spines/assets/fonts/).

---

## The concept we built toward

The game was designed against a concept-art board — these five screens are the
targets the build reproduces. The full board is in
[`docs/Spines_and_Starlight_UI_Concept.html`](docs/Spines_and_Starlight_UI_Concept.html).

**1. Title & Start Menu** — the threshold, as the stars begin to fall.

![Title screen: the words "Spines & Starlight" in gold serif type over a deep-plum starlit night, a floating open book on the right, and a menu of New Story / Continue / Your Collection / Settings](docs/images/concept-01-title.png)

**2. The Bookshop (Genre Aisles)** — browse Fantasy, Romance, Mystery, and Sci-Fi
shelves; hover a spine for its details.

![Bookshop screen: four genre shelves of coloured book spines, a quest tracker and coin/cart HUD, Mira seen from behind with a cart, and a hover tooltip showing "The Ashen Crown"](docs/images/concept-02-bookshop.png)

**3. Your Cart** — review your finds against a starlight budget.

![Cart screen: a list of five books with covers, genres, authors, and prices on the left, and a "Ledger" panel on the right showing subtotal, member's charm discount, total, and remaining coins](docs/images/concept-03-cart.png)

**4. The Checkout Desk** — the shopkeeper stamps each flyleaf by lamplight.

![Checkout screen: a lamplit wooden desk with a shopkeeper silhouette, stacked books, and a paper receipt listing the purchase with a "Complete Purchase" button](docs/images/concept-04-checkout.png)

**5. Book Close-Up** — pull a single volume to read its cover, blurb, and price.

![Book detail screen: a large violet cover for "The Ashen Crown" on the left, with genre tags, title, rating, blurb, and an "Add to Cart" button on the right](docs/images/concept-05-book-detail.png)

### Documentation

[`docs/spines-and-starlight/`](docs/spines-and-starlight/) is the full spec behind
the five screens:

| Doc | Covers |
|-----|--------|
| [`00-overview.md`](docs/spines-and-starlight/00-overview.md) | Vision, the five-screen map, and scope |
| [`01-design-system.md`](docs/spines-and-starlight/01-design-system.md) | Palette (oklch → pygame RGB), typography, spacing, motion |
| [`02-data-model.md`](docs/spines-and-starlight/02-data-model.md) | Book / cart / economy / quest types and the full book catalog |
| [`03-screen-flow.md`](docs/spines-and-starlight/03-screen-flow.md) | Scene state machine, transitions, and the main loop |
| [`04-components.md`](docs/spines-and-starlight/04-components.md) | Reusable widgets (buttons, spines, tooltips, panels, actors) |
| `screen-01`…`screen-05` | Per-screen layout specs with acceptance checklists |

Start with the overview.

---

## Project layout

```
bookshop/
├── README.md
├── requirements.txt                   # pygame-ce
├── spines/                            # the game (run: python -m spines)
│   ├── __main__.py  app.py            # entry point + scene-stack main loop
│   ├── theme.py  content.py  scene.py # tokens, data/catalog, scene framework
│   ├── primitives.py  widgets.py  fonts.py  furniture.py  actors.py  audio.py
│   ├── assets/fonts/                  # bundled Cormorant Garamond + Spectral (OFL)
│   └── scenes/                        # title, shop, detail, cart, checkout, collection, settings
└── docs/
    ├── Spines_and_Starlight_UI_Concept.html   # concept art board (5 screens)
    ├── images/                                # concept screenshots
    └── spines-and-starlight/                  # implementation spec (10 docs)
```

## Status

*Spines & Starlight* is playable end-to-end (`python -m spines`) — Title → Shop →
Detail → Cart → Checkout, and back to the menu with your purchases collected.


