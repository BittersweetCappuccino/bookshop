"""
Spines & Starlight — actors.

Mira seen from behind and her cart, restyled from bookstore.py's front-facing
Mira/draw_cart to the night palette (components §14). The walk bob, arm swing,
and cart-follow logic carry over; the look is a hooded plum silhouette.
Logical coordinates in.
"""

import math

import pygame

from . import theme, primitives as pr

_PLUM = (78, 54, 92)
_PLUM_DARK = (46, 30, 56)
_HAIR = (74, 48, 34)


class Mira:
    """The browsing character. `x` is her logical position; `floor_y` her feet."""

    def __init__(self, x, floor_y, min_x, max_x):
        self.x = x
        self.floor_y = floor_y
        self.min_x, self.max_x = min_x, max_x
        self.speed = 3.4
        self.facing = 1
        self.walk_t = 0.0
        self.reaching = 0

    def update(self, keys):
        moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
            self.facing = -1
            moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
            self.facing = 1
            moving = True
        self.x = max(self.min_x, min(self.max_x, self.x))
        self.walk_t = self.walk_t + 0.22 if moving else self.walk_t * 0.82
        if self.reaching > 0:
            self.reaching -= 1

    def reach(self):
        self.reaching = 16

    def draw(self, surf, t):
        x, y = self.x, self.floor_y
        bob = math.sin(self.walk_t) * 2
        swing = math.sin(self.walk_t) * 5
        lift = -12 if self.reaching > 0 else 0

        pr.ellipse_alpha(surf, (x - 26, y + 2, 52, 14), (0, 0, 0, 70))
        # legs
        pr.line(surf, (x - 6, y - 30), (x - 6 - swing, y), _PLUM_DARK, 7)
        pr.line(surf, (x + 6, y - 30), (x + 6 + swing, y), _PLUM_DARK, 7)
        # cloak body
        body = [(x - 15, y - 64), (x + 15, y - 64), (x + 21, y - 26), (x - 21, y - 26)]
        pr.polygon(surf, body, _PLUM, 0)
        pr.polygon(surf, body, _PLUM_DARK, 2)
        # arms (one lifts when reaching for a book)
        pr.line(surf, (x - 14, y - 60), (x - 18, y - 42 + lift), _PLUM, 6)
        pr.line(surf, (x + 14, y - 60), (x + 18, y - 42 + lift), _PLUM, 6)
        # back of the head: hair + a low bun
        hy = y - 74 + bob
        pr.circle(surf, (x, hy + 1), 13, _HAIR)
        pr.circle(surf, (x, hy - 11), 6, _HAIR)
        # warm rim light on the facing side
        pr.glow(surf, (x + 12 * self.facing, hy), 18, (*theme.LANTERN_LIGHT, 55))


def draw_cart(surf, mira, books):
    """A translucent wire basket that follows Mira, with book-tops poking out."""
    f = mira.facing
    cx = mira.x - f * 44
    cy = mira.floor_y
    body = pygame.Rect(round(cx - 24), round(cy - 42), 48, 30)
    pr.glass_panel(surf, body, radius=4, fill=(60, 44, 70), alpha=150,
                   border=(150, 120, 160), border_alpha=170)
    for gx in range(8, 44, 8):
        pr.line(surf, (body.x + gx, body.y + 3), (body.x + gx, body.bottom - 3), (150, 120, 160), 1)
    pr.line(surf, (cx + f * 24, cy - 42), (cx + f * 36, cy - 56), (150, 120, 160), 3)
    pr.circle(surf, (body.x + 9, cy - 8), 6, (28, 20, 34))
    pr.circle(surf, (body.right - 9, cy - 8), 6, (28, 20, 34))
    for i, b in enumerate(books[-6:]):
        bx = body.x + 6 + (i % 3) * 13
        by = body.bottom - 8 - (i // 3) * 10
        col = theme.spine_shades(b.hue, b.shelf_index)[1]
        pr.round_rect(surf, (bx, by, 11, 9), col, 1)
