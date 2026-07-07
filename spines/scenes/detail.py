"""Screen 05 — Book Close-Up (overlay). Full spec: screen-05-book-detail.md."""

import pygame

from .. import theme, fonts, primitives as pr, widgets, content, furniture
from .. import scene as sc

# Centered row (spec §2): 320 cover + 70 gap + 520 panel = 910, padded in 1280.
_COVER = pygame.Rect(185, 120, 320, 480)
_PANEL_X = 575
_PANEL_W = 520


class DetailScene(sc.Scene):
    overlay = True   # drawn over a dimmed SHOP

    def __init__(self, book=None):
        self.book = book
        self.add_rect = None
        self.back_rect = None

    def handle_event(self, e, ctx):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_b):
                ctx.pop()
            elif e.key == pygame.K_a:
                self._add(ctx)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.add_rect and self.add_rect.collidepoint(ctx.mouse):
                self._add(ctx)
            elif self.back_rect and self.back_rect.collidepoint(ctx.mouse):
                ctx.pop()

    def _add(self, ctx):
        if self.book and not ctx.cart.has(self.book):
            ctx.cart.add(self.book)
            ctx.pop()

    def draw(self, surf, ctx):
        b = self.book
        furniture.blurred_shelves(surf)
        pr.alpha_rect(surf, (0, 0, theme.CANVAS_W, theme.CANVAS_H), (6, 2, 9, 214))  # dim shop
        if not b:
            return

        # a soft dark scrim behind the text column keeps it readable over the shelves
        pr.vfade(surf, (_PANEL_X - 30, 90, _PANEL_W + 90, 540), theme.NIGHT_BOTTOM, 150, 60)

        widgets.draw_cover(surf, _COVER, b)

        x = _PANEL_X
        genre = content.GENRES[b.genre]
        pill = widgets.draw_pill(surf, (x, 122), genre.name, hue=b.hue)
        widgets.draw_pill(surf, (pill.right + 8, 122), "Standalone", None)

        pr.glow(surf, (x + 150, 210), 140, (*theme.oklch_to_rgb(0.6, 0.12, b.hue), 34))
        yy = pr.draw_paragraph(surf, b.title, fonts.display(theme.Size.SCREEN_TITLE, bold=True),
                               theme.CREAM, (x, 156), _PANEL_W, 58, max_lines=2)
        pr.draw_text(surf, f"by {b.author} · {b.pages} pages",
                     fonts.body(theme.Size.BODY, italic=True), theme.TEXT_MUTED, (x, yy + 6))

        yr = yy + 40
        widgets.star_row(surf, (x, yr), b.rating, 20)
        pr.draw_text(surf, f"{b.rating:.1f} · {b.reviews:,} reviews",
                     fonts.body(theme.Size.SMALL), theme.TEXT_MUTED, (x + 140, yr + 3))

        yb = pr.draw_paragraph(surf, b.blurb, fonts.body(16), theme.TEXT, (x, yr + 42), 480, 26)

        self.add_rect = None
        ab = pygame.Rect(x, yb + 24, 250, 52)
        self._draw_add(surf, ctx, ab)

        pr.circle(surf, (x + 6, ab.centery + 68), 4, theme.GOLD)
        pr.draw_text(surf, f"{b.copies} copies on the shelf", fonts.body(theme.Size.SMALL),
                     theme.TEXT_MUTED, (x + 18, ab.centery + 60))

        back = pr.render_tracked("BACK TO THE AISLE · [ESC]", fonts.body(12), theme.TEXT_FAINT, 2)
        self.back_rect = pr.blit(surf, back, (x, ab.centery + 96))

    def _draw_add(self, surf, ctx, rect):
        if ctx.cart.has(self.book):
            pr.alpha_rect(surf, rect, (*theme.BTN2_BG, 150), 12)
            pr.round_rect(surf, rect, (*theme.BTN2_BORDER, 160), 12, width=1)
            pr.draw_text(surf, "In your cart", fonts.display(theme.Size.MENU), theme.TEXT_MUTED,
                         rect.center, center=True)
            return
        hover = rect.collidepoint(ctx.mouse)
        top, bot = theme.BTN_GOLD_TOP, theme.BTN_GOLD_BOT
        if hover:
            top = tuple(min(255, c + 16) for c in top)
            bot = tuple(min(255, c + 16) for c in bot)
        pr.drop_shadow(surf, rect, 12, offset=(0, 10), rgba=(90, 50, 10, 110))
        pr.vgradient(surf, rect, top, bot)
        pr.round_rect(surf, rect, (*theme.PANEL_BORDER, 255), 12, width=1)
        widgets.coin_glyph(surf, (rect.x + 26, rect.centery), 11)
        pr.draw_text(surf, f"Add to Cart · {self.book.price}",
                     fonts.display(theme.Size.MENU, bold=True), theme.BTN_GOLD_TEXT,
                     (rect.x + 46, rect.centery), anchor="midleft")
        self.add_rect = rect


sc.register(sc.DETAIL, DetailScene)
