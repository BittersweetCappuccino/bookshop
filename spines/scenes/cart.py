"""Screen 03 — Your Cart. Stub (full spec: screen-03-cart.md)."""

import pygame

from .. import theme, fonts, primitives as pr, widgets, content
from .. import scene as sc
from .base import PlaceholderScene, starfield, draw_hud, draw_hints


class CartScene(PlaceholderScene):
    number = "03"
    name = "Your Cart"

    hints = ("[Enter] proceed to the desk", "[D] fill demo cart",
             "[Esc] keep browsing")

    def handle_event(self, e, ctx):
        if e.type != pygame.KEYDOWN:
            return
        if e.key == pygame.K_ESCAPE:
            ctx.go(sc.SHOP)
        elif e.key == pygame.K_d:
            ctx.cart = content.demo_cart()
        elif e.key == pygame.K_RETURN:
            if ctx.ledger.affordable(ctx.wallet):
                ctx.go(sc.CHECKOUT)

    def draw(self, surf, ctx):
        pr.night_bg(surf)
        starfield().draw(surf, ctx.t)
        pr.draw_text(surf, self.name, fonts.display(theme.Size.SECTION, bold=True),
                     theme.CREAM, (80, 60))

        # item rows
        y = 150
        for b in ctx.cart.items:
            row = pygame.Rect(80, y, 560, 56)
            pr.glass_panel(surf, row, radius=12, fill=theme.ROW_BG, alpha=theme.A_ROW)
            pr.draw_text(surf, b.title, fonts.display(theme.Size.CARD_TITLE), theme.CREAM,
                         (row.x + 16, row.y + 8))
            pr.draw_text(surf, f"{content.GENRES[b.genre].name} · {b.author}",
                         fonts.body(theme.Size.SMALL), theme.TEXT_MUTED, (row.x + 16, row.y + 34))
            widgets.coin_value(surf, (row.right - 70, row.y + 16), b.price, size=20, color=theme.GOLD)
            y += 64
        if not ctx.cart.items:
            pr.draw_text(surf, "Your cart is empty — press [D] for the demo five.",
                         fonts.body(theme.Size.BODY), theme.TEXT_FAINT, (80, 160))

        # ledger card
        led = ctx.ledger
        card = pygame.Rect(720, 150, 460, 320)
        pr.glass_panel(surf, card, radius=18, fill=theme.PANEL_BG2, alpha=theme.A_PANEL2)
        pr.draw_text(surf, "Ledger", fonts.display(theme.Size.PANEL_HEAD), theme.CREAM,
                     (card.x + 28, card.y + 24))
        self._row(surf, card, 80, "Subtotal", str(led.subtotal), theme.TEXT)
        self._row(surf, card, 116, "Member's charm", f"-{led.discount}", theme.MEMBER_CHARM)
        self._row(surf, card, 168, "Total", str(led.total), theme.GOLD, big=True)
        self._row(surf, card, 214, "Star-purse", str(ctx.wallet.coins), theme.TEXT_MUTED)
        self._row(surf, card, 250, "Remaining after", str(led.remaining(ctx.wallet)),
                  theme.GOLD if led.affordable(ctx.wallet) else theme.BADGE_RED)

        draw_hud(surf, ctx)
        draw_hints(surf, self.hints)

    @staticmethod
    def _row(surf, card, dy, label, value, color, big=False):
        size = theme.Size.CARD_TITLE if big else theme.Size.BODY
        pr.draw_text(surf, label, fonts.body(size), theme.TEXT_MUTED, (card.x + 28, card.y + dy))
        img = fonts.display(size + 4, bold=big).render(value, True, color)
        pr.blit(surf, img, (card.right - 28, card.y + dy), anchor="topright")


sc.register(sc.CART, CartScene)
