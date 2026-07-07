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

    def __init__(self, x, floor_y, min_x, max_x, scale=1.0):
        self.x = x
        self.floor_y = floor_y
        self.min_x, self.max_x = min_x, max_x
        self.scale = scale
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
        x, y, s = self.x, self.floor_y, self.scale
        bob = math.sin(self.walk_t) * 2
        swing = math.sin(self.walk_t) * 5
        lift = -12 if self.reaching > 0 else 0

        def P(dx, dy):
            return (x + dx * s, y + dy * s)

        pr.ellipse_alpha(surf, (x - 26 * s, y + 2, 52 * s, 14 * s), (0, 0, 0, 70))
        # legs
        pr.line(surf, P(-6, -30), (x + (-6 - swing) * s, y), _PLUM_DARK, 7 * s)
        pr.line(surf, P(6, -30), (x + (6 + swing) * s, y), _PLUM_DARK, 7 * s)
        # cloak body
        pr.polygon(surf, [P(-15, -64), P(15, -64), P(21, -26), P(-21, -26)], _PLUM, 0)
        pr.polygon(surf, [P(-15, -64), P(15, -64), P(21, -26), P(-21, -26)], _PLUM_DARK, 2 * s)
        # arms (one lifts when reaching for a book)
        pr.line(surf, P(-14, -60), (x - 18 * s, y + (-42 + lift) * s), _PLUM, 6 * s)
        pr.line(surf, P(14, -60), (x + 18 * s, y + (-42 + lift) * s), _PLUM, 6 * s)
        # back of the head: hair + a low bun
        hy = y - 74 * s + bob
        pr.circle(surf, (x, hy + 1 * s), 13 * s, _HAIR)
        pr.circle(surf, (x, hy - 11 * s), 6 * s, _HAIR)
        # warm rim light on the facing side
        pr.glow(surf, (x + 12 * s * self.facing, hy), 18 * s, (*theme.LANTERN_LIGHT, 55))


def draw_reader(surf, cx, feet_y, scale=1.7):
    """A distant reader silhouette on the title screen — a simpler cousin of
    behind-view Mira: two plum blobs + a gold rim-light (screen-01 §3.6)."""
    s = scale
    plum = (52, 36, 66)
    bw, bh = 56 * s, 112 * s
    pr.glow(surf, (cx - bw * 0.42, feet_y - bh * 0.6), 40 * s, (*theme.GOLD, 70))  # left rim-light
    body = pygame.Rect(round(cx - bw / 2), round(feet_y - bh), round(bw), round(bh))
    pr.round_rect(surf, body, plum, bw / 2)
    hw, hh = 34 * s, 40 * s
    head = pygame.Rect(round(cx - hw / 2), round(feet_y - bh - hh * 0.5), round(hw), round(hh))
    pr.ellipse(surf, head, plum)


def draw_keeper(surf, x, feet_y, t):
    """The shopkeeper behind the desk — a simple robed figure, front-facing (§6)."""
    pr.ellipse_alpha(surf, (x - 30, feet_y + 2, 60, 16), (0, 0, 0, 60))
    body = [(x - 24, feet_y - 96), (x + 24, feet_y - 96), (x + 34, feet_y), (x - 34, feet_y)]
    pr.polygon(surf, body, (66, 46, 80), 0)
    pr.polygon(surf, body, (40, 26, 50), 2)
    hy = feet_y - 112
    pr.glow(surf, (x - 16, hy), 22, (*theme.LANTERN_LIGHT, 60))
    pr.circle(surf, (x, hy), 16, (232, 196, 168))     # face
    pr.circle(surf, (x, hy - 10), 15, _HAIR)          # hair cap over the crown
    pr.circle(surf, (x - 6, hy + 1), 1.6, (40, 26, 20))   # eyes
    pr.circle(surf, (x + 6, hy + 1), 1.6, (40, 26, 20))


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
