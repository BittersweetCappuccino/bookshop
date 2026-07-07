"""
Spines & Starlight — scene furniture.

Shared background pieces: shelf planks, hanging lanterns, and the floor fade.
See docs/spines-and-starlight/04-components.md §15. Logical coordinates in.
"""

from . import theme, primitives as pr


def shelf_plank(surf, rect):
    """A wood plank the spines sit on (§4c). Generalizes bookstore.py's shelves."""
    import pygame
    rect = pygame.Rect(rect)
    pr.drop_shadow(surf, rect, 3, offset=(0, 5), rgba=(0, 0, 0, 90))
    pr.vgradient(surf, rect, theme.WOOD_TOP, theme.WOOD_BOTTOM)
    pr.round_rect(surf, (rect.x, rect.y, rect.w, 3), theme.WOOD_HI, 1)


def lantern(surf, cx, lamp_y, w, h, t, phase=0):
    """A hanging lantern with a breathing pulse glow (§3, motion §5)."""
    a = theme.pulse_alpha(t, phase)
    lamp_cy = lamp_y + h / 2
    pr.glow(surf, (cx, lamp_cy), h * 1.5, (*theme.LANTERN_LIGHT, int(70 * a)))
    pr.line(surf, (cx, 0), (cx, lamp_y), (64, 48, 32), 2)
    import pygame
    lamp = pygame.Rect(round(cx - w / 2), lamp_y, w, h)
    pr.round_rect(surf, lamp, theme.LANTERN_DARK, 6)
    pr.round_rect(surf, lamp.inflate(-round(w * 0.42), -round(h * 0.42)), theme.LANTERN_LIGHT, 4)
    pr.round_rect(surf, lamp, (28, 18, 8), 6, width=1)


def floor_fade(surf, height=150):
    """Bottom gradient fading the shelves into dark (§3)."""
    rect = (0, theme.CANVAS_H - height, theme.CANVAS_W, height)
    pr.vfade(surf, rect, theme.NIGHT_BOTTOM, 0, 236)


def desk(surf):
    """The checkout desk: a big wood block with a lighter counter lip (§3)."""
    import pygame
    body = pygame.Rect(0, 470, theme.CANVAS_W, 250)
    pr.vgradient(surf, body, theme.DESK_TOP, theme.DESK_BOTTOM)
    pr.vgradient(surf, (0, 470, theme.CANVAS_W, 20), theme.WOOD_HI, theme.DESK_TOP)  # lip
    pr.line(surf, (0, 470), (theme.CANVAS_W, 470), theme.WOOD_HI, 1)
    pr.line(surf, (0, 490), (theme.CANVAS_W, 490), (0, 0, 0), 1)


def desk_lamp(surf, cx, t):
    """Hanging lamp: cord, shade, and a breathing warm glow (§3)."""
    a = theme.pulse_alpha(t)
    pr.line(surf, (cx, 0), (cx, 112), (56, 42, 28), 2)
    for r, base in ((150, 14), (100, 20), (60, 30)):   # soft warm falloff
        pr.glow(surf, (cx, 152), r, (*theme.LANTERN_LIGHT, int(base * a)))
    import pygame
    shade = pygame.Rect(cx - 41, 112, 82, 40)
    pr.vgradient(surf, shade, theme.LANTERN_LIGHT, theme.LANTERN_DARK)
    pr.round_rect(surf, shade, (30, 20, 10), 8, width=1)


def light_pool(surf, cx, cy):
    """The warm pool of lamplight cast over the desk (§5 light cone)."""
    for r, alpha in ((190, 22), (130, 30), (80, 40)):
        pr.ellipse_alpha(surf, (cx - r, cy - r * 0.7, r * 2, r * 1.4), (*theme.LANTERN_LIGHT, alpha))


def stacked_books(surf, x, y):
    """Four flat books stacked on the counter, in genre hues (§9)."""
    for i, hue in enumerate(theme.GENRE_HUE.values()):
        w = 150 - i * 10
        bx = x + i * 5
        by = y - i * 22
        pr.ellipse_alpha(surf, (bx, by - 3, w, 7), (0, 0, 0, 70))
        pr.round_rect(surf, (bx, by - 24, w, 24), theme.oklch_to_rgb(0.42, 0.12, hue), 3)
        pr.round_rect(surf, (bx, by - 24, w, 24), theme.oklch_to_rgb(0.30, 0.10, hue), 3, width=1)
        pr.line(surf, (bx + 6, by - 12), (bx + w - 6, by - 12), (*theme.GOLD, 90), 1)


_blur_cache = {}


def blurred_shelves(surf):
    """Decorative full-bleed row of blurred background spines (§3b, screen 05)."""
    import pygame
    key = (theme.WINDOW_W, theme.WINDOW_H)
    big = _blur_cache.get(key)
    if big is None:
        small = pygame.Surface((320, 180))
        small.fill(theme.NIGHT_BOTTOM)
        hues = list(theme.GENRE_HUE.values())
        x = i = 0
        base = 128
        while x < 320:
            H = hues[(i // 6) % len(hues)]
            w = 6 + (i * 11) % 5
            h = 40 + (i * 31) % 40
            L = 0.30 + ((i * 19) % 12) / 100
            C = 0.06 + ((i * 7) % 4) / 100
            hue = H + ((i * 23) % 14 - 7)
            top = theme.oklch_to_rgb(L + 0.04, C, hue)
            bottom = theme.oklch_to_rgb(L - 0.05, C, hue)
            for yy in range(h):
                f = yy / max(1, h - 1)
                col = tuple(round(top[k] + (bottom[k] - top[k]) * f) for k in range(3))
                pygame.draw.line(small, col, (x, base - h + yy), (x + w - 1, base - h + yy))
            x += w + 2
            i += 1
        big = pygame.transform.smoothscale(small, (theme.WINDOW_W, theme.WINDOW_H))
        big.set_alpha(85)
        _blur_cache[key] = big
    surf.blit(big, (0, 0))
