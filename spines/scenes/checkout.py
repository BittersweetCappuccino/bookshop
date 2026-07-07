"""Screen 04 — The Checkout Desk. Full spec: screen-04-checkout.md."""

import pygame

from .. import theme, fonts, primitives as pr, widgets, actors, furniture
from .. import scene as sc
from .base import starfield, draw_hints

_RECEIPT_TL = (900, 64)   # top-left of the receipt (top 64, right 60, w320)


class CheckoutScene(sc.Scene):
    def on_enter(self, ctx):
        self.confirmed = False
        self.cta_rect = None
        self.keeper_x = 852
        # Mira on the near side, larger (foreground); she doesn't walk here
        self.mira = actors.Mira(x=470, floor_y=712, min_x=470, max_x=470, scale=1.7)

    def handle_event(self, e, ctx):
        if self.confirmed:
            if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                ctx.go(sc.TITLE)
            return
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                ctx.go(sc.CART)
            elif e.key == pygame.K_RETURN:
                self._commit(ctx)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.cta_rect and self.cta_rect.collidepoint(ctx.mouse):
                self._commit(ctx)

    def _commit(self, ctx):
        if not self.confirmed and sc.commit_purchase(ctx):
            self.confirmed = True

    def draw(self, surf, ctx):
        pr.night_bg(surf, glow_center=(180, -40))
        starfield().draw(surf, ctx.t)
        furniture.blurred_shelves(surf)
        furniture.desk_lamp(surf, 640, ctx.t)
        actors.draw_keeper(surf, self.keeper_x, 470, ctx.t)
        furniture.desk(surf)
        furniture.light_pool(surf, 470, 470)
        furniture.stacked_books(surf, 170, 470)
        self.mira.draw(surf, ctx.t)

        self.cta_rect = widgets.draw_receipt(surf, ctx.cart, ctx.ledger, _RECEIPT_TL, ctx.mouse)
        widgets.coin_pill(surf, (24, 22), ctx.wallet.coins)

        if self.confirmed:
            self._draw_confirm(surf)
        else:
            draw_hints(surf, ("[Enter] complete purchase", "[Esc] back to cart"))

    def _draw_confirm(self, surf):
        pr.alpha_rect(surf, (0, 0, theme.CANVAS_W, theme.CANVAS_H), (30, 16, 34, 170))
        pr.draw_text(surf, "Thank you for reading", fonts.display(theme.Size.SECTION, bold=True),
                     theme.CREAM, (theme.CANVAS_W // 2, theme.CANVAS_H // 2 - 24), center=True)
        pr.draw_text(surf, "Your tales are gathered.", fonts.display(theme.Size.CARD_TITLE),
                     theme.GOLD, (theme.CANVAS_W // 2, theme.CANVAS_H // 2 + 24), center=True)
        pr.draw_text(surf, "Press any key to return to the menu.", fonts.body(theme.Size.SMALL),
                     theme.TEXT_FAINT, (theme.CANVAS_W // 2, theme.CANVAS_H // 2 + 70), center=True)


sc.register(sc.CHECKOUT, CheckoutScene)
