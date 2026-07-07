"""Screen 03 — Your Cart. Full spec: screen-03-cart.md."""

import pygame

from .. import theme, fonts, primitives as pr, widgets, content
from .. import scene as sc
from .base import starfield

# Two columns in a 44x48 padded frame, gap 40 (spec §2)
_PAD = 44
_LEDGER_W = 336
_LEDGER_X = theme.CANVAS_W - _PAD - _LEDGER_W          # 900
_LIST_X = _PAD
_LIST_W = _LEDGER_X - 40 - _PAD                        # 816
_ROW_H = 92
_ROW_GAP = 12
_ROWS_TOP = 150


class CartScene(sc.Scene):
    def on_enter(self, ctx):
        self.remove_rects = []
        self.proceed_rect = None
        self.browse_rect = None
        self.empty_rect = None

    def handle_event(self, e, ctx):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                ctx.go(sc.SHOP)
            return
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            pos = ctx.mouse
            for book, rect in self.remove_rects:
                if rect.collidepoint(pos):
                    ctx.cart.remove(book)
                    return
            if self.proceed_rect and self.proceed_rect.collidepoint(pos):
                if ctx.ledger.affordable(ctx.wallet):
                    ctx.go(sc.CHECKOUT)
            elif self.browse_rect and self.browse_rect.collidepoint(pos):
                ctx.go(sc.SHOP)
            elif self.empty_rect and self.empty_rect.collidepoint(pos):
                ctx.go(sc.SHOP)

    def draw(self, surf, ctx):
        pr.night_bg(surf)
        starfield().draw(surf, ctx.t)

        # heading + live count
        h = pr.draw_text(surf, "Your Cart", fonts.display(theme.Size.SECTION, bold=True),
                         theme.CREAM, (_PAD, 56))
        n = ctx.cart.count
        pr.draw_text(surf, f"{n} volume{'s' if n != 1 else ''} gathered",
                     fonts.body(theme.Size.SMALL), theme.TEXT_MUTED,
                     (_PAD + h.width / theme.SCALE + 16, 92))
        pr.alpha_rect(surf, (_PAD, 116, _LIST_W, 1), (*theme.GOLD, 90))

        self.remove_rects = []
        if ctx.cart.items:
            self._draw_rows(surf, ctx)
            self.proceed_rect, self.browse_rect = widgets.draw_ledger(
                surf, ctx.ledger, ctx.wallet, (_LEDGER_X, _ROWS_TOP, _LEDGER_W, 434), ctx.mouse)
            self.empty_rect = None
        else:
            self._draw_empty(surf)
            self.proceed_rect = self.browse_rect = None

    def _draw_rows(self, surf, ctx):
        y = _ROWS_TOP
        for book in ctx.cart.items:
            row = pygame.Rect(_LIST_X, y, _LIST_W, _ROW_H)
            pr.glass_panel(surf, row, radius=14, fill=theme.ROW_BG, alpha=theme.A_ROW)
            widgets.draw_thumb(surf, (row.x + 14, row.y + 4, 58, 84), book)
            tx = row.x + 14 + 58 + 18
            widgets.draw_pill(surf, (tx, row.y + 14), content.GENRES[book.genre].name, hue=book.hue)
            pr.draw_text(surf, book.title, fonts.display(theme.Size.CARD_TITLE), theme.CREAM,
                         (tx, row.y + 38))
            pr.draw_text(surf, f"by {book.author}", fonts.body(12, italic=True),
                         theme.TEXT_MUTED, (tx, row.y + 66))
            widgets.coin_value(surf, (row.right - 96, row.y + 16), book.price, size=22, color=theme.GOLD)
            rrect = pygame.Rect(row.right - 92, row.y + 54, 72, 20)
            hover = rrect.collidepoint(ctx.mouse)
            pr.blit(surf, pr.render_tracked("REMOVE", fonts.body(11),
                    theme.TEXT_MUTED if hover else theme.TEXT_FAINT, 1.5),
                    (row.right - 20, row.y + 58), anchor="topright")
            self.remove_rects.append((book, rrect))
            y += _ROW_H + _ROW_GAP

    def _draw_empty(self, surf):
        pr.draw_text(surf, "Your cart is empty", fonts.display(theme.Size.PANEL_HEAD),
                     theme.TEXT_MUTED, (theme.CANVAS_W // 2, 320), center=True)
        pr.draw_text(surf, "Back to the aisles", fonts.display(theme.Size.MENU), theme.GOLD,
                     (theme.CANVAS_W // 2, 372), center=True)
        self.empty_rect = pygame.Rect(theme.CANVAS_W // 2 - 100, 360, 200, 30)


sc.register(sc.CART, CartScene)
