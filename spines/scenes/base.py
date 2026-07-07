"""
Shared scene helpers: the lazily-created starfield and a PlaceholderScene that
gives every not-yet-built screen a consistent, navigable look. As each real
screen (Phase 3) lands, it replaces its placeholder here.

All coordinates are LOGICAL (1280x720); the primitives scale to device pixels.
"""

from .. import theme, fonts, primitives as pr, widgets
from ..scene import Scene

_starfield = None


def starfield():
    """Shared twinkling starfield, created on first use (needs a display)."""
    global _starfield
    if _starfield is None:
        _starfield = pr.Starfield()
    return _starfield


def reset_starfield():
    """Force the starfield to rebuild at the current render size (after rescale)."""
    global _starfield
    _starfield = None


def draw_hud(surf, ctx):
    """A small always-on readout of the shared Context state (coins + cart)."""
    widgets.coin_value(surf, (theme.CANVAS_W - 150, 24), ctx.wallet.coins, size=20)
    cart = f"Cart {ctx.cart.count}  ·  {ctx.cart.subtotal}"
    pr.draw_text(surf, cart, fonts.body(theme.Size.SMALL), theme.TEXT_MUTED,
                 (theme.CANVAS_W - 150, 54))


def draw_hints(surf, hints):
    txt = "    ".join(hints)
    pr.draw_text(surf, txt, fonts.body(theme.Size.SMALL), theme.TEXT_FAINT,
                 (theme.CANVAS_W // 2, theme.CANVAS_H - 34), center=True)


class PlaceholderScene(Scene):
    """A themed stand-in: night sky, screen number, title, live HUD, hints."""

    number = "00"
    name = "Screen"
    subtitle = ""
    hints = ()

    def draw(self, surf, ctx):
        pr.night_bg(surf)
        starfield().draw(surf, ctx.t)
        # big screen numeral, top-right
        num = fonts.display(120, bold=True).render(self.number, True, theme.SCREEN_NUM)
        num.set_alpha(80)
        pr.blit(surf, num, (theme.CANVAS_W - 40, 40), anchor="topright")
        # centered title + subtitle
        pr.draw_text(surf, self.name, fonts.display(theme.Size.SECTION, bold=True),
                     theme.CREAM, (theme.CANVAS_W // 2, theme.CANVAS_H // 2 - 24), center=True)
        if self.subtitle:
            pr.draw_text(surf, self.subtitle, fonts.body(theme.Size.BODY), theme.TEXT_MUTED,
                         (theme.CANVAS_W // 2, theme.CANVAS_H // 2 + 20), center=True)
        pr.draw_text(surf, "placeholder — Phase 3 will build this screen",
                     fonts.body(theme.Size.EYEBROW), theme.TEXT_FAINT,
                     (theme.CANVAS_W // 2, theme.CANVAS_H // 2 + 52), center=True)
        draw_hud(surf, ctx)
        if self.hints:
            draw_hints(surf, self.hints)
