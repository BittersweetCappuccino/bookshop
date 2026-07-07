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
