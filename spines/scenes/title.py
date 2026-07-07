"""Screen 01 — Title & Start Menu. A first pass (full spec: screen-01-title.md)."""

import pygame

from .. import theme, fonts, primitives as pr, widgets, content, actors
from .. import scene as sc
from .base import starfield

_VIOLET_TOP = theme.oklch_to_rgb(0.42, 0.13, 288)
_VIOLET_BOT = theme.oklch_to_rgb(0.22, 0.10, 290)


def _page_lines(surf, cx, cy, side, hw, ph):
    """Faux text on one page of the open book (side -1 left / +1 right)."""
    x0 = cx + side * 14
    rows = [(0.18, theme.GOLD, 3, 0.62),      # gilded heading
            (0.36, (176, 148, 112), 2, 1.0),
            (0.48, (176, 148, 112), 2, 0.86),
            (0.60, (176, 148, 112), 2, 1.0),
            (0.72, (176, 148, 112), 2, 0.7)]
    for fy, col, wdt, frac in rows:
        y = cy - ph + fy * (2 * ph)
        x1 = cx + side * (14 + (hw - 28) * frac)
        pr.line(surf, (x0, y), (x1, y), col, wdt)
    if side > 0:  # small gold diamond on the right page
        dx, dy = cx + side * (hw - 26), cy + ph - 22
        pr.polygon(surf, [(dx, dy - 5), (dx + 5, dy), (dx, dy + 5), (dx - 5, dy)], theme.GOLD, 0)


def _open_book(surf, cx, cy):
    """The floating open book: halo, light beam, two pages, spine (§3.5)."""
    pr.glow(surf, (cx, cy), 210, (*theme.GOLD, 85))                       # 5a halo
    pr.polygon_alpha(surf, [(cx, cy - 155), (cx - 92, cy + 78), (cx + 92, cy + 78)],
                     (*theme.GOLD, 26))                                    # 5d light beam
    hw, ph, inset = 140, 66, 18
    left = [(cx, cy - ph), (cx - hw, cy - ph + inset), (cx - hw, cy + ph - inset), (cx, cy + ph)]
    right = [(cx, cy - ph), (cx + hw, cy - ph + inset), (cx + hw, cy + ph - inset), (cx, cy + ph)]
    pr.polygon(surf, left, theme.CREAM_DIM, 0)
    pr.polygon(surf, right, theme.CREAM, 0)
    _page_lines(surf, cx, cy, -1, hw, ph)
    _page_lines(surf, cx, cy, +1, hw, ph)
    pr.polygon(surf, left, (*theme.PANEL_BORDER, 160), 1)
    pr.polygon(surf, right, (*theme.PANEL_BORDER, 160), 1)
    spine = pygame.Rect(round(cx - 7), round(cy - 75), 14, 150)            # 5b spine
    pr.vgradient(surf, spine, _VIOLET_TOP, _VIOLET_BOT)
    pr.round_rect(surf, spine, (*theme.GOLD, 130), 3, width=1)


class TitleScene(sc.Scene):
    def on_enter(self, ctx):
        cx, y = 250, 384
        self.buttons = [
            widgets.Button((cx, y, 300, 56), "New Story", "primary"),
            widgets.Button((cx, y + 68, 300, 56), "Continue", "ghost",
                           enabled=ctx.profile.continue_state is not None),
            widgets.Button((cx, y + 136, 300, 56), "Your Collection", "ghost"),
            widgets.Button((cx, y + 204, 300, 56), "Settings", "ghost"),
        ]

    def handle_event(self, e, ctx):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                ctx.quit()
            else:
                self._new_story(ctx)   # any key starts (§3)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for b in self.buttons:
                if b.hit(ctx.mouse):
                    self._activate(b.label, ctx)

    def _activate(self, label, ctx):
        if label == "New Story":
            self._new_story(ctx)
        elif label == "Continue" and ctx.profile.continue_state:
            saved = ctx.profile.continue_state.get("scene", sc.SHOP)
            ctx.go(saved)

    def _new_story(self, ctx):
        ctx.cart = content.Cart()
        ctx.quest = content.DEFAULT_QUEST
        ctx.go(sc.SHOP)

    def draw(self, surf, ctx):
        pr.page_bg(surf)
        starfield().draw(surf, ctx.t)
        pr.vfade(surf, (0, theme.CANVAS_H - 140, theme.CANVAS_W, 140),
                 theme.NIGHT_BOTTOM, 0, 235)                    # bottom vignette (§3.7)

        # reader silhouette below the floating book, then the book on top
        actors.draw_reader(surf, 980, 660, scale=1.7)
        _open_book(surf, 980, 300 + theme.float_dy(ctx.t))      # bobs (motion §5)

        # left group: eyebrow + hero wordmark
        eye = pr.render_tracked("A BOOKSHOP TALE", fonts.body(theme.Size.EYEBROW),
                                theme.EYEBROW_GOLD, 6)
        pr.blit(surf, eye, (252, 180))
        pr.draw_text(surf, "Spines", fonts.display(theme.Size.HERO, bold=True),
                     theme.CREAM, (248, 200))
        pr.draw_text(surf, "& Starlight", fonts.display(64, bold=True, italic=True),
                     theme.GOLD_ITALIC, (252, 300))

        for b in self.buttons:
            b.draw(surf, ctx.mouse, ctx.t)

        pr.draw_text(surf, "Enter to begin  ·  Esc to close the shop",
                     fonts.body(theme.Size.SMALL), theme.TEXT_FAINT,
                     (theme.CANVAS_W // 2, theme.CANVAS_H - 34), center=True)


sc.register(sc.TITLE, TitleScene)
