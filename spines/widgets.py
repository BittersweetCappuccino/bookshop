"""
Spines & Starlight — reusable widgets.

The interactive/visual components the per-screen specs compose. This module will
grow to cover the full component library (docs/spines-and-starlight/04-components.md);
for the scaffold it provides the Button used by the title menu, plus the coin
glyph used across HUD/ledger/receipt. All positions are LOGICAL (see primitives).
"""

import pygame

from . import theme, fonts, primitives as pr


class Button:
    """A clickable button. kind in {'primary', 'ghost', 'pill'} (§2).

    `rect` and hit-testing are in logical coordinates; drawing scales to device.
    """

    def __init__(self, rect, label, kind="primary", enabled=True, tracking=1):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.kind = kind
        self.enabled = enabled
        self.tracking = tracking

    def hit(self, pos):
        return self.enabled and self.rect.collidepoint(pos)

    def draw(self, surf, mouse_pos, t=0):
        hovered = self.hit(mouse_pos)
        r = self.rect
        if self.kind == "primary":
            top, bot = theme.BTN_GOLD_TOP, theme.BTN_GOLD_BOT
            if hovered:
                top = tuple(min(255, c + 18) for c in top)
                bot = tuple(min(255, c + 18) for c in bot)
            if self.enabled:
                pr.drop_shadow(surf, r, 12, offset=(0, 12), rgba=(90, 50, 10, 110))
            pr.vgradient(surf, r, top, bot)
            if not self.enabled:
                pr.alpha_rect(surf, r, (20, 10, 25, 150), 12)
            pr.round_rect(surf, r, (*theme.PANEL_BORDER, 255), 12, width=1)
            self._label(surf, theme.BTN_GOLD_TEXT, fonts.display(theme.Size.MENU, bold=True))
        elif self.kind == "ghost":
            alpha = 178 if hovered and self.enabled else theme.A_ROW
            pr.alpha_rect(surf, r, (*theme.BTN2_BG, alpha), 12)
            pr.round_rect(surf, r, (*theme.BTN2_BORDER, 128), 12, width=1)
            color = theme.BTN2_TEXT if self.enabled else theme.TEXT_FAINT
            self._label(surf, color, fonts.display(theme.Size.MENU))
        else:  # pill
            color = theme.GOLD_HOVER if hovered else theme.EYEBROW_GOLD
            pr.round_rect(surf, r, (*color, 128), 20, width=1)
            self._label(surf, color, fonts.body(theme.Size.EYEBROW), upper=True)
        return hovered

    def _label(self, surf, color, font, upper=False):
        text = self.label.upper() if upper else self.label
        img = pr.render_tracked(text, font, color, self.tracking)
        pr.blit(surf, img, self.rect.center, anchor="center")


def coin_glyph(surf, center, r=10):
    """Radial coin disc with an inner ring (§6). center/r are logical."""
    rr = pr.sv(r)
    d = rr * 2
    disc = pygame.Surface((d, d), pygame.SRCALPHA)
    for i in range(rr, 0, -1):
        f = i / rr
        col = tuple(
            round(theme.COIN_LIGHT[k] + (theme.COIN_DARK[k] - theme.COIN_LIGHT[k]) * (1 - f))
            for k in range(3)
        )
        pygame.draw.circle(disc, col, (rr, rr), i)
    pygame.draw.circle(disc, theme.COIN_DARK, (rr, rr), rr - max(1, pr.sv(2)), width=max(1, pr.sv(1)))
    cx, cy = pr.sp(center)
    surf.blit(disc, (cx - rr, cy - rr))


def coin_value(surf, pos, n, size=20, color=theme.COIN_NUM, r=10):
    """Coin glyph + number at a logical position; returns approx logical width."""
    cy = pos[1] + size / 2
    coin_glyph(surf, (pos[0] + r, cy), r)
    img = fonts.display(size, bold=True).render(str(n), True, color)
    pr.blit(surf, img, (pos[0] + r * 2 + 6, cy), anchor="midleft")
    return r * 2 + 6 + round(img.get_width() / theme.SCALE)
