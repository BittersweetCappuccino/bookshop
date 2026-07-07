"""
Spines & Starlight — design tokens.

Everything visual is defined once here so every screen imports the same names.
Colors are transcribed from the concept's oklch() values, converted to pygame
sRGB (0-255) tuples. See docs/spines-and-starlight/01-design-system.md.

This module is pure data + math (no pygame), so it is safe to import anywhere.
"""

import math

# ----------------------------------------------------------------------
# Canvas & scaling
# ----------------------------------------------------------------------
# We author every screen in the concept's 1280x720 *logical* space (so the spec
# measurements transcribe directly, overview §5), but render natively crisp at a
# larger *device* resolution. The drawing layer (primitives/fonts/widgets) scales
# logical coordinates and font sizes by SCALE before touching the real surface,
# so text and edges are pixel-sharp rather than upscaled.
CANVAS_W, CANVAS_H = 1280, 720        # logical design space (what scenes use)
FPS = 60

# SCALE maps logical -> device pixels and is chosen at runtime to fit the
# player's display (see app.configure). WINDOW_W/H is the resulting render size.
# These defaults (1.5x -> 1920x1080) apply until app.set_scale() runs.
SCALE = 1.5
WINDOW_W, WINDOW_H = round(CANVAS_W * SCALE), round(CANVAS_H * SCALE)


def set_scale(scale):
    """Set the logical->device scale and recompute the render size."""
    global SCALE, WINDOW_W, WINDOW_H
    SCALE = scale
    WINDOW_W = round(CANVAS_W * scale)
    WINDOW_H = round(CANVAS_H * scale)


def s(v):
    """Scale one logical measurement to device pixels."""
    return round(v * SCALE)


# ----------------------------------------------------------------------
# OKLCH -> sRGB conversion (design system §1.1)
# ----------------------------------------------------------------------
def oklch_to_rgb(L, C, h):
    """OKLCH (h in degrees) -> sRGB (0-255) tuple, gamut-clamped."""
    hr = math.radians(h)
    a, b = C * math.cos(hr), C * math.sin(hr)
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    def gamma(x):
        x = max(0.0, min(1.0, x))
        return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055

    return tuple(round(gamma(v) * 255) for v in (r, g, bl))


# ----------------------------------------------------------------------
# Core palette (design system §1.2)
# ----------------------------------------------------------------------
NIGHT_TOP = (62, 29, 76)        # top of the night-sky gradient
NIGHT_BOTTOM = (11, 1, 19)      # bottom of the night sky
PAGE_BG_TOP = (23, 7, 30)       # board/backdrop behind screens
PAGE_BG_BOTTOM = (6, 2, 9)      # board/backdrop bottom
STAR = (255, 242, 214)          # starfield dots
TEXT = (235, 225, 237)          # primary body text
TEXT_MUTED = (183, 168, 186)    # secondary text
TEXT_FAINT = (143, 129, 146)    # captions, hints
CREAM = (254, 244, 223)         # titles / headings
CREAM_DIM = (251, 241, 220)     # sub-headings

# Gold / starlight accents (§1.3)
GOLD = (242, 185, 102)
GOLD_HOVER = (255, 214, 135)
GOLD_ITALIC = (254, 194, 101)
EYEBROW_GOLD = (206, 162, 106)
SCREEN_NUM = (178, 111, 0)
BTN_GOLD_TOP = (248, 183, 79)
BTN_GOLD_BOT = (208, 133, 31)
BTN_GOLD_TEXT = (41, 13, 0)
PROGRESS_A = (213, 151, 57)
PROGRESS_B = (252, 195, 100)
STAR_RATING = (252, 195, 100)
MEMBER_CHARM = (242, 185, 90)

# Coins & lamps (§1.4)
COIN_LIGHT = (255, 220, 110)
COIN_DARK = (203, 126, 25)
COIN_NUM = (255, 231, 174)
LANTERN_LIGHT = (255, 211, 91)
LANTERN_DARK = (183, 108, 0)

# Surfaces, panels, wood (§1.5) — the α column is the intended alpha (0-255)
PANEL_BG = (19, 8, 25)          # HUD / tooltip panels    (α .82 -> 209)
PANEL_BG2 = (27, 12, 36)        # summary / ledger card   (α .70 -> 179)
ROW_BG = (23, 12, 30)           # list rows               (α .55 -> 140)
PANEL_BORDER = (126, 92, 42)    # gold hairline border    (α .35 -> 89)
TRACK_BG = (47, 35, 56)         # empty progress track
BTN2_BG = (35, 19, 43)          # secondary button fill   (α .55 -> 140)
BTN2_BORDER = (110, 90, 125)    # secondary button border (α .5 -> 128)
BTN2_TEXT = (231, 216, 235)
WOOD_TOP = (88, 58, 42)
WOOD_BOTTOM = (47, 25, 15)
WOOD_HI = (132, 96, 71)
DESK_TOP = (81, 46, 27)
DESK_BOTTOM = (38, 14, 4)

# Receipt — the one inverted (light-on-dark) surface (§1.6)
RECEIPT_TOP = (242, 234, 221)
RECEIPT_BOTTOM = (225, 214, 194)
RECEIPT_INK = (55, 36, 20)
RECEIPT_FAINT = (117, 94, 76)
CHECKOUT_BTN_TOP = (64, 43, 95)
CHECKOUT_BTN_BOT = (38, 19, 63)

# Misc (§1.7)
BADGE_RED = (249, 119, 114)
PILL_VIOLET = (219, 217, 255)

# Common alpha values used with the SRCALPHA panels above
A_PANEL = 209   # .82
A_PANEL2 = 179  # .70
A_ROW = 140     # .55
A_BORDER = 89   # .35


# ----------------------------------------------------------------------
# Genre hue system (design system §2)
# ----------------------------------------------------------------------
# Each genre owns a hue angle; spines, labels, pills, and glows derive from it.
# Keyed by genre id (matches content.GENRES).
GENRE_HUE = {
    "fantasy": 288,   # violet
    "romance": 18,    # rose
    "mystery": 210,   # slate-teal
    "scifi": 238,     # blue
}

# Genre label colors (design system §2) — the tinted aisle headers.
GENRE_LABEL = {
    "fantasy": (246, 227, 184),
    "romance": (255, 215, 205),
    "mystery": (186, 231, 245),
    "scifi": (197, 226, 254),
}


def spine_shades(H, i):
    """Deterministic per-book spine colors for hue H, shelf index i.

    Returns (top, mid, bottom, band) RGB tuples for the spine gradient plus the
    lighter title band near the top. See design system §2.
    """
    L = 0.30 + ((i * 23) % 13) / 100        # 0.30 .. 0.42 base lightness
    C = 0.06 + ((i * 13) % 5) / 100         # 0.06 .. 0.10 chroma
    hh = H + (((i * 29) % 16) - 8)          # hue jitter +/- 8
    top = oklch_to_rgb(L + 0.05, C, hh)
    mid = oklch_to_rgb(L, C, hh)
    bottom = oklch_to_rgb(L - 0.06, C, hh)
    band = oklch_to_rgb(L + 0.16, C + 0.02, hh)
    return top, mid, bottom, band


def spine_geometry(i):
    """Spine (width, height) in pixels for shelf index i (design system §2)."""
    height = 66 + (i * 41) % 42   # 66 .. 108
    width = 21 + (i * 17) % 13    # 21 .. 34
    return width, height


# ----------------------------------------------------------------------
# Motion (design system §5) — drive from the global frame counter ctx.t @ 60fps
# ----------------------------------------------------------------------
def twinkle_alpha(t, phase=0):
    """Star layer fade, 5s ease-in-out. Returns 0.30 .. 1.0."""
    return 0.30 + 0.70 * (0.5 + 0.5 * math.sin(2 * math.pi * (t + phase) / 300))


def float_dy(t, phase=0):
    """Floating book bob, 7s. Returns -16 .. 0 (a vertical offset)."""
    return -8 + 8 * math.sin(2 * math.pi * (t + phase) / 420)


def pulse_alpha(t, phase=0):
    """Lantern glow breathing, 4s. Returns 0.55 .. 0.95."""
    return 0.55 + 0.40 * (0.5 + 0.5 * math.sin(2 * math.pi * (t + phase) / 240))


# ----------------------------------------------------------------------
# Type scale (design system §3.2), in canvas px @ 1280x720
# ----------------------------------------------------------------------
class Size:
    HERO = 96          # 01 logo "Spines"
    SCREEN_TITLE = 62  # 05 detail book title
    SECTION = 44       # 03 "Your Cart"
    COVER_TITLE = 40   # 05 cover
    GENRE_HEADER = 27  # 02 aisle labels
    PANEL_HEAD = 26    # 03 "Ledger"
    CARD_TITLE = 23    # tooltip / cart row
    MENU = 22          # 01 menu buttons
    BODY = 17          # detail blurb
    SMALL = 14         # prices, meta
    EYEBROW = 12       # tracked uppercase labels
    SPINE = 10         # vertical spine titles
