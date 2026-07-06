# Spines & Starlight — Design System

> Palette, typography, spacing, and motion for all five screens.
> Colours are transcribed from the concept's `oklch()` values and converted to
> pygame **sRGB (0–255)** tuples. See [`00-overview.md`](00-overview.md) for scope.

Everything here is defined once and reused by every screen spec. Where a spec
says "gold button" or "night background," it means the tokens on this page.

---

## 1. Colour

The concept authors colour in `oklch(L C H)`. pygame needs `(r, g, b)`. Every
value below was converted with the exact OKLCH→sRGB pipeline; the helper is
included so you can convert any stragglers yourself.

### 1.1 Conversion helper (drop into the codebase)

```python
import math

def oklch_to_rgb(L, C, h):
    """OKLCH (h in degrees) -> sRGB (0-255) tuple, gamut-clamped."""
    hr = math.radians(h)
    a, b = C * math.cos(hr), C * math.sin(hr)
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_**3, m_**3, s_**3
    r  =  4.0767416621*l - 3.3077115913*m + 0.2309699292*s
    g  = -1.2684380046*l + 2.6097574011*m - 0.3413193965*s
    bl = -0.0041960863*l - 0.7034186147*m + 1.7076147010*s
    def gamma(x):
        x = max(0.0, min(1.0, x))
        return 12.92*x if x <= 0.0031308 else 1.055*x**(1/2.4) - 0.055
    return tuple(round(gamma(v) * 255) for v in (r, g, bl))
```

> **Note on alpha.** Many concept values carry an alpha (`… / .82`). pygame's
> plain `(r,g,b)` has no alpha; draw translucent fills onto a
> `pygame.Surface((w,h), pygame.SRCALPHA)` with `(r, g, b, a)` where
> `a = round(alpha * 255)`, then `blit`. This is the same pattern the current
> game already uses for the shopping-list note and the checkout veil
> ([`bookstore.py:322`](../../bookstore.py#L322), [`bookstore.py:446`](../../bookstore.py#L446)).

### 1.2 Core palette (converted)

| Token | oklch | RGB | Use |
|-------|-------|-----|-----|
| `NIGHT_TOP` | 0.30 0.09 315 | `(62, 29, 76)` | Top of the night sky gradient |
| `NIGHT_BOTTOM` | 0.12 0.05 312 | `(11, 1, 19)` | Bottom of the night sky |
| `PAGE_BG_TOP` | 0.17 0.05 315 | `(23, 7, 30)` | Board/backdrop behind screens |
| `PAGE_BG_BOTTOM` | 0.10 0.03 312 | `(6, 2, 9)` | Board/backdrop bottom |
| `STAR` | rgba(255,242,214) | `(255, 242, 214)` | Starfield dots |
| `TEXT` | 0.92 0.02 320 | `(235, 225, 237)` | Primary body text |
| `TEXT_MUTED` | 0.75 0.03 320 | `(183, 168, 186)` | Secondary text |
| `TEXT_FAINT` | 0.62 0.03 320 | `(143, 129, 146)` | Captions, hints |
| `CREAM` | 0.97 0.03 86 | `(254, 244, 223)` | Titles/headings |
| `CREAM_DIM` | 0.96 0.03 86 | `(251, 241, 220)` | Sub-headings |

### 1.3 Gold / starlight accents

| Token | oklch | RGB | Use |
|-------|-------|-----|-----|
| `GOLD` | 0.82 0.12 75 | `(242, 185, 102)` | Links, accent text |
| `GOLD_HOVER` | 0.90 0.11 80 | `(255, 214, 135)` | Hover state of gold |
| `GOLD_ITALIC` | 0.85 0.13 76 | `(254, 194, 101)` | "& Starlight" italic in logo |
| `EYEBROW_GOLD` | 0.74 0.09 72 | `(206, 162, 106)` | Small uppercase labels |
| `SCREEN_NUM` | 0.60 0.14 72 | `(178, 111, 0)` | Big "01"–"05" numerals |
| `BTN_GOLD_TOP` | 0.82 0.14 76 | `(248, 183, 79)` | Primary button gradient top |
| `BTN_GOLD_BOT` | 0.68 0.14 68 | `(208, 133, 31)` | Primary button gradient bottom |
| `BTN_GOLD_TEXT` | 0.20 0.06 60 | `(41, 13, 0)` | Text on gold buttons |
| `PROGRESS_A` | 0.72 0.13 74 | `(213, 151, 57)` | Progress-bar fill start |
| `PROGRESS_B` | 0.85 0.13 78 | `(252, 195, 100)` | Progress-bar fill end |
| `STAR_RATING` | 0.85 0.13 78 | `(252, 195, 100)` | ★ rating glyphs |
| `MEMBER_CHARM` | 0.82 0.13 78 | `(242, 185, 90)` | Discount figures |

### 1.4 Coins & lamps

| Token | oklch | RGB | Use |
|-------|-------|-----|-----|
| `COIN_LIGHT` | 0.92 0.14 84 | `(255, 220, 110)` | Coin highlight (radial centre) |
| `COIN_DARK` | 0.66 0.14 66 | `(203, 126, 25)` | Coin shadow (radial edge) |
| `COIN_NUM` | 0.94 0.08 82 | `(255, 231, 174)` | Coin count text |
| `LANTERN_LIGHT` | 0.90 0.15 82 | `(255, 211, 91)` | Lantern/lamp core |
| `LANTERN_DARK` | 0.60 0.14 66 | `(183, 108, 0)` | Lantern/lamp edge |

### 1.5 Surfaces, panels, wood

| Token | oklch | RGB | Use |
|-------|-------|-----|-----|
| `PANEL_BG` | 0.16 0.04 312 @ .82 | `(19, 8, 25)` | HUD / tooltip panels (α .82) |
| `PANEL_BG2` | 0.19 0.05 312 @ .70 | `(27, 12, 36)` | Summary/ledger card (α .70) |
| `ROW_BG` | 0.18 0.04 312 @ .55 | `(23, 12, 30)` | List rows (α .55) |
| `PANEL_BORDER` | 0.50 0.08 74 @ .35 | `(126, 92, 42)` | Gold hairline border (α .35) |
| `TRACK_BG` | 0.28 0.04 310 | `(47, 35, 56)` | Empty progress-bar track |
| `BTN2_BG` | 0.22 0.05 314 @ .55 | `(35, 19, 43)` | Secondary button fill (α .55) |
| `BTN2_BORDER` | 0.50 0.06 310 @ .5 | `(110, 90, 125)` | Secondary button border (α .5) |
| `WOOD_TOP` | 0.38 0.05 50 | `(88, 58, 42)` | Shelf plank top |
| `WOOD_BOTTOM` | 0.24 0.04 44 | `(47, 25, 15)` | Shelf plank bottom |
| `WOOD_HI` | 0.52 0.06 56 | `(132, 96, 71)` | Shelf plank highlight |
| `DESK_TOP` | 0.34 0.06 48 | `(81, 46, 27)` | Checkout desk top |
| `DESK_BOTTOM` | 0.20 0.045 44 | `(38, 14, 4)` | Checkout desk bottom |

### 1.6 Receipt (screen 04, light-on-dark inversion)

| Token | oklch | RGB | Use |
|-------|-------|-----|-----|
| `RECEIPT_TOP` | 0.94 0.02 84 | `(242, 234, 221)` | Paper gradient top |
| `RECEIPT_BOTTOM` | 0.88 0.03 82 | `(225, 214, 194)` | Paper gradient bottom |
| `RECEIPT_INK` | 0.28 0.04 60 | `(55, 36, 20)` | Receipt text |
| `RECEIPT_FAINT` | 0.50 0.04 60 | `(117, 94, 76)` | Receipt sub-text / dashes |
| `CHECKOUT_BTN_TOP` | 0.34 0.09 300 | `(64, 43, 95)` | "Complete Purchase" top |
| `CHECKOUT_BTN_BOT` | 0.24 0.08 300 | `(38, 19, 63)` | "Complete Purchase" bottom |

### 1.7 Misc

| Token | oklch | RGB | Use |
|-------|-------|-----|-----|
| `BADGE_RED` | 0.72 0.16 24 | `(249, 119, 114)` | "+2" cart notification badge |
| `PILL_VIOLET` | 0.90 0.06 288 | `(219, 217, 255)` | Genre pill text |

---

## 2. Genre hue system

Each genre owns a **hue angle**; spines, labels, pills, and glows for that genre
are all derived from it. This is the single most important colour idea in the
concept — keep genres hue-consistent.

| Genre | Hue | Label RGB | Spine mid (L0.42 C0.11) RGB | Pill/tag |
|-------|-----|-----------|-----------------------------|----------|
| Fantasy | **288** (violet) | `(246, 227, 184)` | `(75, 65, 133)` | violet |
| Romance | **18** (rose) | `(255, 215, 205)` | `(126, 47, 54)` | rose |
| Mystery | **210** (slate-teal) | `(186, 231, 245)` | `(0, 91, 110)` | teal |
| Sci-Fi | **238** (blue) | `(197, 226, 254)` | `(0, 83, 129)` | blue |

> Romance labels/headers in the concept drift between hue 18/20/30 and Mystery
> between 210/220; treat the anchor hues above as canonical and vary ±10 freely.

### Deriving a spine's colours (from the concept's `build()`)

Every spine gets deterministic per-book variation. For book index `i` in a genre
of hue `H`:

```python
def spine_shades(H, i):
    L  = 0.30 + ((i * 23) % 13) / 100        # 0.30 .. 0.42 base lightness
    C  = 0.06 + ((i * 13) % 5)  / 100        # 0.06 .. 0.10 chroma
    hh = H + (((i * 29) % 16) - 8)           # hue jitter +/- 8
    top    = oklch_to_rgb(L + 0.05, C, hh)   # gradient top
    mid    = oklch_to_rgb(L,        C, hh)   # gradient middle (32%)
    bottom = oklch_to_rgb(L - 0.06, C, hh)   # gradient bottom
    band   = oklch_to_rgb(L + 0.16, C + 0.02, hh)  # title band near the top
    return top, mid, bottom, band

# spine geometry, also from build():
#   height = 66 + (i * 41) % 42   -> 66..108 px
#   width  = 21 + (i * 17) % 13   -> 21..34  px
```

Blurred **background** spines (checkout & detail screens) use a flatter variant:
`h = 44 + (i*31)%16`, `w = 14 + (i*11)%9`, `L = 0.30 + (i*19)%12/100`,
`C = 0.06 + (i*7)%4/100`, `hue = H + ((i*23)%14 - 7)`, two-stop gradient
`(L+0.04)`→`(L-0.05)`.

---

## 3. Typography

The concept uses two Google serifs. **pygame's `Font` needs TrueType/OpenType,
not woff2**, so bundle the TTFs.

### 3.1 Fonts

| Role | Concept font | Bundle (TTF) | SysFont fallback chain |
|------|--------------|--------------|------------------------|
| Display / headings / titles / buttons | **Cormorant Garamond** (600/700, also italic) | `assets/fonts/CormorantGaramond-*.ttf` | `constantia, cambria, georgia, serif` |
| Body / UI / numerals | **Spectral** (300/400/500/600) | `assets/fonts/Spectral-*.ttf` | `cambria, georgia, serif` |

Download both families from Google Fonts (SIL Open Font License) into
`assets/fonts/`. Load with `pygame.font.Font(path, size)`. If a bundled file is
missing, fall back to `pygame.font.SysFont(chain, size, bold=…, italic=…)`. The
current game already uses `georgia` ([`bookstore.py:65`](../../bookstore.py#L65)),
which is the acceptable last resort.

Suggested loader:

```python
def load_font(path, size, sysfallback, bold=False, italic=False):
    try:
        return pygame.font.Font(path, size)
    except (FileNotFoundError, OSError):
        return pygame.font.SysFont(sysfallback, size, bold=bold, italic=italic)
```

### 3.2 Type scale (concept px @ 1280×720; ×0.75 if you stay at 960×600)

| Style | Font · weight | Size | Tracking | Seen in |
|-------|---------------|------|----------|---------|
| Hero title | Cormorant 700 | 96 | tight | 01 logo "Spines" |
| Screen title (detail book) | Cormorant 700 | 62 | — | 05 |
| Section title | Cormorant 700 | 44 | — | 03 "Your Cart" |
| Book cover title | Cormorant 700 | 40 | — | 05 cover |
| Genre header | Cormorant 600 | 27 | — | 02 aisle labels |
| Panel heading | Cormorant 600 | 26 | — | 03 "Ledger" |
| Card title | Cormorant 600 | 23 | — | tooltip / cart row |
| Menu button | Cormorant 600 | 22–23 | .5 | 01 menu |
| Body | Spectral 400 | 16–18 | — | detail blurb |
| Small / meta | Spectral 400 | 12–15 | — | prices, "512 pp" |
| Eyebrow label | Spectral 400 | 10–13 | 2–8 (letter-spacing) | "SCREEN", "A BOOKSHOP TALE" |
| Spine title (vertical) | Cormorant 600 | 10 | .3 | 02 shelves |

> **Letter-spacing** isn't native to pygame text. For the short uppercase
> eyebrows, render glyph-by-glyph with an added pixel gap, or pre-render the
> label with spaces. A small `render_tracked(text, font, colour, px)` helper is
> worth writing once and lives best in the component library
> ([`04-components.md`](04-components.md)).

---

## 4. Spacing, radius, elevation

- **Screen frame:** each screen is a `1280×720` panel, corner radius **18**,
  1px border `PANEL_BORDER`, deep drop shadow.
- **Panel radius:** cards **14–18**, buttons **11–13**, pills/badges **16–30**
  (fully rounded), progress tracks **4–5**.
- **Panel padding:** cards **26**, HUD chips **10–16**, list rows **12–14**.
- **Gaps:** menu items **12**, HUD chips **10**, list rows **12**, aisle rows
  **24** between shelves.
- **Shadows** (pygame has no box-shadow): fake with a blurred/again-alpha
  ellipse or an offset dark rounded rect beneath the element. The current game
  already fakes a shadow under Mira ([`bookstore.py:200`](../../bookstore.py#L200)).
  A reusable `drop_shadow(surf, rect, ...)` belongs in the component library.
- **Glows/halos:** a soft radial — draw a large `SRCALPHA` ellipse of the accent
  colour at low alpha behind the element (see the counter halo,
  [`bookstore.py:284`](../../bookstore.py#L284)). Coins, lanterns, the floating
  book, and hover highlights all use this.

---

## 5. Motion

The concept defines three CSS keyframe animations. All are subtle and looping.
Drive them from a per-frame counter `t` (the game already increments one,
[`bookstore.py:372`](../../bookstore.py#L372)) at 60 FPS.

| Name | CSS | Meaning | pygame translation |
|------|-----|---------|--------------------|
| `tw` (twinkle) | opacity .30↔1, 5 s ease-in-out | Star layer fades in/out | `alpha = 0.30 + 0.70 * (0.5 + 0.5*sin(2π·t/300))`, apply to a star surface's `set_alpha` |
| `fl` (float) | translateY 0↔−16px, 7 s | Floating open book bobs | `dy = -8 + 8*sin(2π·t/420)` (−16..0), offset the book's blit |
| `pulse` | opacity .55↔.95, 4–5 s | Lantern glow breathes | `alpha = 0.55 + 0.40*(0.5+0.5*sin(2π·t/240))` on the lantern halo |

Timing math: seconds × 60 FPS = period in frames (5 s → 300, 7 s → 420, 4 s →
240, 5 s → 300). Use `math.sin` for the ease-in-out feel; exact easing isn't
worth replicating. Stagger multiple lanterns/stars by adding a per-instance
phase offset to `t`.

**Existing motions to reuse:** Mira's walk bob/arm-swing
([`bookstore.py:197`](../../bookstore.py#L197)), the checkout halo pulse
([`bookstore.py:283`](../../bookstore.py#L283)), and `Pop` floating "+1" text
([`bookstore.py:342`](../../bookstore.py#L342)) — the same `Pop` works for the
"On list!" / coin-spend feedback in the new shop.

---

## 6. Recurring visual motifs (build once, reuse everywhere)

These appear on multiple screens; implement each as one reusable draw function
(detailed in [`04-components.md`](04-components.md)):

1. **Starfield** — scattered `STAR` dots at fixed positions + one twinkling
   overlay layer (`tw`). Present on every screen background.
2. **Night gradient** — vertical `NIGHT_TOP`→`NIGHT_BOTTOM`, often with a warm
   radial glow near the top from an off-screen light source.
3. **Coin** — radial `COIN_LIGHT`→`COIN_DARK` circle with a 2px inner ring; used
   in HUD, prices, ledger, receipt.
4. **Soft glow halo** — low-alpha radial behind books, lanterns, buttons.
5. **Glass panel** — translucent `PANEL_BG` rounded rect + `PANEL_BORDER`
   hairline (CSS `backdrop-filter: blur` has no cheap pygame equivalent; skip
   the blur, the low-alpha fill reads fine).

---

## 7. Suggested constants module

Collect the tokens above into one module, e.g. `theme.py`, so every screen
imports the same names:

```python
# theme.py  (excerpt)
NIGHT_TOP     = (62, 29, 76)
NIGHT_BOTTOM  = (11, 1, 19)
STAR          = (255, 242, 214)
TEXT          = (235, 225, 237)
CREAM         = (254, 244, 223)
GOLD          = (242, 185, 102)
BTN_GOLD_TOP  = (248, 183, 79)
BTN_GOLD_BOT  = (208, 133, 31)
COIN_LIGHT    = (255, 220, 110)
COIN_DARK     = (203, 126, 25)
GENRE_HUE     = {"Fantasy": 288, "Romance": 18, "Mystery": 210, "Sci-Fi": 238}
# ... full set from sections 1.2–1.7 ...
```

The data-model doc ([`02-data-model.md`](02-data-model.md)) references
`GENRE_HUE` for building spines and pills.
