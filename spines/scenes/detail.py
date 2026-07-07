"""Screen 05 — Book Close-Up (overlay). Stub (full spec: screen-05-book-detail.md)."""

import pygame

from .. import theme, fonts, primitives as pr, widgets
from .. import scene as sc


class DetailScene(sc.Scene):
    overlay = True   # drawn over a dimmed SHOP

    def __init__(self, book=None):
        self.book = book

    def handle_event(self, e, ctx):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_b):
                ctx.pop()
            elif e.key == pygame.K_a and self.book:
                ctx.cart.add(self.book)
                ctx.pop()

    def draw(self, surf, ctx):
        # dim the SHOP beneath
        pr.alpha_rect(surf, surf.get_rect(), (6, 2, 9, 180))
        card = pygame.Rect(0, 0, 620, 360)
        card.center = (theme.CANVAS_W // 2, theme.CANVAS_H // 2)
        pr.glass_panel(surf, card, radius=18)
        b = self.book
        if not b:
            return
        x, y = card.x + 36, card.y + 32
        pr.draw_text(surf, b.title, fonts.display(theme.Size.SCREEN_TITLE, bold=True),
                     theme.CREAM, (x, y))
        pr.draw_text(surf, f"by {b.author}", fonts.body(theme.Size.BODY, italic=True),
                     theme.TEXT_MUTED, (x, y + 68))
        pr.draw_text(surf, f"{b.rating:.1f} ★   ·   {b.pages} pp   ·   {b.reviews} reviews",
                     fonts.body(theme.Size.SMALL), theme.STAR_RATING, (x, y + 98))
        # blurb, wrapped
        self._wrapped(surf, b.blurb, theme.Size.BODY, theme.TEXT,
                      (x, y + 134), card.width - 72)
        widgets.coin_value(surf, (x, card.bottom - 60), b.price, size=26, color=theme.GOLD)
        pr.draw_text(surf, "[A] Add to Cart      [Esc] Back to the aisle",
                     fonts.body(theme.Size.SMALL), theme.TEXT_FAINT,
                     (card.right - 36, card.bottom - 48), anchor="topright")

    @staticmethod
    def _wrapped(surf, text, size, color, pos, width):
        """Word-wrap in logical units; `size` is the logical font size."""
        font = fonts.body(size)
        max_w = pr.sv(width)         # font metrics are device-sized
        line_h = size + 5            # logical line height
        x, y = pos
        line = ""
        for w in text.split():
            trial = f"{line} {w}".strip()
            if font.size(trial)[0] > max_w and line:
                pr.draw_text(surf, line, font, color, (x, y))
                line, y = w, y + line_h
            else:
                line = trial
        if line:
            pr.draw_text(surf, line, font, color, (x, y))


sc.register(sc.DETAIL, DetailScene)
