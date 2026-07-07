# Screen 01 — Title & Start Menu

> *The threshold — a lone reader arrives at the shop as the stars begin to fall.*
> Scene id **`TITLE`**. Coordinates are concept px (1280×720); ×0.75 for 960×600.
> Tokens: [`01-design-system.md`](01-design-system.md) · widgets:
> [`04-components.md`](04-components.md) · flow: [`03-screen-flow.md`](03-screen-flow.md).

---

## 1. Purpose

The entry point. Sets the mood (deep plum night, falling starlight, a floating
open book) and offers the start menu. First interactive frame after boot.

## 2. Layout map (1280×720)

```
┌──────────────────────────────────────────────────────────────┐
│  · · ·   star field   · ·        · ·      · ·   (twinkle)     │
│                                            ✧ floating open book│
│   A BOOKSHOP TALE                         (top 190, right 150)│
│   ┌───────────────┐                        ╲ light beam        │
│   │ Spines        │  ← hero title                              │
│   │ & Starlight   │  (Cormorant 700, 96)                       │
│   └───────────────┘                                            │
│   ┌─────────────────────┐                                      │
│   │ ◆ New Story         │  ← primary (gold)                    │
│   ├─────────────────────┤                                      │
│   │ Continue            │                        🧍 reader     │
│   ├─────────────────────┤                     silhouette       │
│   │ Your Collection     │                  (bottom 70,right300)│
│   ├─────────────────────┤          ░░ bottom vignette ░░       │
│   │ Settings            │                                      │
│   └─────────────────────┘                                      │
│              © MIDNIGHT MARGIN STUDIOS · PRESS ANY KEY         │
└──────────────────────────────────────────────────────────────┘
```

## 3. Elements

| # | Element | Position / size | Spec |
|---|---------|-----------------|------|
| 1 | **Frame** | 1280×720 | Radius 18, 1px `PANEL_BORDER`, deep drop shadow |
| 2 | **Background** | fill | Night gradient `NIGHT_TOP`→`NIGHT_BOTTOM` with a warm radial glow near top-right (off-screen light). Furniture piece "night gradient" ([`04-components.md`](04-components.md) §15) |
| 3 | **Starfield** | full | Fixed scatter of `STAR` dots (concept places ~8 base dots high in the frame) |
| 4 | **Twinkle layer** | full, `inset:0` | Second star layer, `tw` animation (α .30↔1 over 300 frames) — see design system §5 |
| 5 | **Floating open book** | top 190, right 150; 300×230 | `fl` float (dy −16↔0 over 420 frames). Sub-parts below |
| 5a | ↳ glow halo | inset −90 | Gold radial `glow` behind the book |
| 5b | ↳ spine | center, 14×150 | Violet vertical gradient, rounded |
| 5c | ↳ pages ×2 | 150×132 each | Cream gradient, `perspective rotateY ±34°` → in pygame fake with a trapezoid (4-point polygon) per page. Each page carries faux text: a gilded heading line (`GOLD`, ~7px) plus several thin brown body lines (`rgba(120,92,58,.3)`, ~4px, varied widths), and a small gold ◆ diamond on the right page — draw as short rounded bars, sheared to match the page's perspective |
| 5d | ↳ light beam | top −30, 120×200 | Gold triangular gradient, `clip-path` cone → a translucent polygon |
| 6 | **Reader silhouette** | bottom 70, ~102×255 (60×150 base × 1.7, grown from bottom-center) | Two plum blobs (body 56×96 + head 34×38 at base scale), gold rim-light `glow` on the left edge. Horizontally centered under the floating book (book center ≈ x 980); enlarged to fill the space between book and footer |
| 7 | **Bottom vignette** | bottom, full width, 130 tall | Gradient transparent→`NIGHT_BOTTOM`, grounds the scene |
| 8 | **Eyebrow** | left 110, top of group | "A BOOKSHOP TALE" — tracked 8px, 13, `EYEBROW_GOLD` (use `render_tracked`). First item of the left group |
| 9 | **Hero title** | left 110, below eyebrow | "Spines" (line 1) + "& Starlight" (line 2, italic, `GOLD_ITALIC`). Cormorant 700, 96, `CREAM`, gold text-glow. Two blits |
| 10 | **Menu** | left 110, top ~+34 below title; width 250, gap 12 | 4 buttons, see §4 |

> **Left group (eyebrow + hero title + menu)** is one block, left-aligned at
> x 110 and **vertically centered** in the 720 frame (its combined height
> centered on y 360). Position the group as a unit, not each row independently.
| 11 | **Footer** | bottom 22, centered | "© MIDNIGHT MARGIN STUDIOS · PRESS ANY KEY" — tracked 2px, 12, `TEXT_FAINT` |

## 4. Menu

Four stacked buttons, width 250 ([`04-components.md`](04-components.md) §2).

| Order | Label | Kind | Action | Enabled when |
|-------|-------|------|--------|--------------|
| 1 | **New Story** | Primary (gold), leading ◆ (rotated square glyph) | `ctx.go(SHOP)` fresh cart/quest | always |
| 2 | **Continue** | Secondary (ghost) | `ctx.go(saved scene)` from `profile.continue_state` | only if a save exists — else disabled/dimmed |
| 3 | **Your Collection** | Secondary | Open Collection (out of scope → stub / toast "coming soon") | always (stub) |
| 4 | **Settings** | Secondary | Open Settings (out of scope → stub) | always (stub) |

Primary button: gradient `BTN_GOLD_TOP`→`BTN_GOLD_BOT`, text `BTN_GOLD_TEXT`,
radius 11, padding 14×22, warm shadow. Secondary: `BTN2_BG` α .55 fill, 1px
`BTN2_BORDER` α .5, text `BTN2_TEXT`, radius 11.

## 5. Interactions

| Input | Result |
|-------|--------|
| Mouse hover a button | Primary brightens ~8%; secondary raises fill α .55→.70 |
| Click **New Story** | `ctx.go(SHOP)` with a fresh run |
| Click **Continue** | `ctx.go` to saved scene (if enabled) |
| Click Collection / Settings | Stub (toast or no-op) |
| **Any key** / Enter | Activate the default: **Continue** if a save exists, else **New Story** |
| **Esc** / window close | Quit (top of the Esc ladder) |
| **M** | Mute/unmute music (global) |

Keyboard focus (optional polish): up/down arrows move a highlight through the
menu, Enter activates. Not required for a first pass.

## 6. Motion

- **Twinkle** (`tw`) on the star overlay — always running.
- **Float** (`fl`) on the open book — always running.
- Optional: a faint periodic "falling star" streak across the sky (a moving dot
  with a short trailing `glow`) to literalise "the stars begin to fall". Nice-to-
  have, not in the static concept.

## 7. States

| State | Trigger | Visual |
|-------|---------|--------|
| Default | on enter | As specced |
| No-save | `profile.continue_state is None` | Continue button dimmed, non-interactive |
| Hover | pointer over a button | Per §5 |
| Leaving | New Story / Continue chosen | Optional crossfade to `SHOP` (flow §8) |

## 8. Assets & audio

- Fonts: Cormorant Garamond (700, 700 italic), Spectral (400).
- No bitmap assets — everything is drawn (gradients, polygons, glows).
- **Music:** the cozy procedural loop already in the game
  ([`bookstore.py:75`](../../bookstore.py#L75) `make_music`) should start here and
  carry into `SHOP`. Respect `ctx.muted`.

## 9. Implementation notes

- This screen is **new** — no equivalent exists in the current single-screen
  game. Build it as the first `Scene` ([`03-screen-flow.md`](03-screen-flow.md) §4).
- The reader silhouette is a lightweight cousin of the behind-view Mira
  ([`04-components.md`](04-components.md) §14) — two blobs + rim glow; don't
  over-build it.
- Cache the static background (night gradient + fixed stars + book/reader shapes)
  to one surface; only the twinkle layer, book float offset, and button hover
  redraw per frame.
- The rotated-square ◆ glyph on New Story is a `pygame.draw.polygon` diamond, the
  same motif used for the quest eyebrow and the "New Story" marker in the concept.

## 10. Acceptance checklist

- [x] 1280×720 frame with night gradient, fixed stars, and a twinkling overlay.
- [x] Floating open book bobs (`fl`) with a gold halo and light beam.
- [x] Reader silhouette with gold rim-light, bottom vignette present.
- [x] Hero title "Spines / & Starlight" with italic gold second line.
- [x] Four-item menu; New Story is gold, others ghost; Continue disabled without a save.
- [x] Hover states on all buttons; New Story → `SHOP`.
- [x] Any-key advances to the default action; Esc quits.
- [x] Footer line present; music plays and respects mute.  <!-- music via spines/audio.py; audible output not yet confirmed by ear -->

