"""Screen 04 — The Checkout Desk. Stub (full spec: screen-04-checkout.md)."""

import pygame

from .. import theme, fonts, primitives as pr, widgets
from .. import scene as sc
from .base import starfield, draw_hints


class CheckoutScene(sc.Scene):
    def __init__(self):
        self.done = False

    def handle_event(self, e, ctx):
        if e.type != pygame.KEYDOWN:
            return
        if self.done:
            ctx.go(sc.TITLE)                     # any key after receipt -> menu
        elif e.key == pygame.K_ESCAPE:
            ctx.go(sc.CART)
        elif e.key == pygame.K_RETURN:
            if sc.commit_purchase(ctx):
                self.done = True

    def draw(self, surf, ctx):
        pr.night_bg(surf)
        starfield().draw(surf, ctx.t)
        if self.done:
            pr.draw_text(surf, "Thank you for reading ★",
                         fonts.display(theme.Size.SECTION, bold=True), theme.CREAM,
                         (theme.CANVAS_W // 2, theme.CANVAS_H // 2 - 20), center=True)
            pr.draw_text(surf, "Press any key to return to the menu.",
                         fonts.body(theme.Size.BODY), theme.GOLD,
                         (theme.CANVAS_W // 2, theme.CANVAS_H // 2 + 30), center=True)
            return

        # a plain receipt card (Phase 3 makes this the rotated paper receipt)
        led = ctx.ledger
        card = pygame.Rect(0, 0, 420, 480)
        card.center = (theme.CANVAS_W // 2, theme.CANVAS_H // 2)
        pr.drop_shadow(surf, card, 16, offset=(0, 14), rgba=(0, 0, 0, 120))
        pr.vgradient(surf, card, theme.RECEIPT_TOP, theme.RECEIPT_BOTTOM)
        pr.round_rect(surf, card, theme.RECEIPT_FAINT, 16, width=1)
        x = card.x + 30
        pr.draw_text(surf, "Spines & Starlight", fonts.display(theme.Size.PANEL_HEAD, bold=True),
                     theme.RECEIPT_INK, (x, card.y + 26))
        eye = pr.render_tracked("EST. BENEATH THE STARS", fonts.body(theme.Size.EYEBROW),
                                theme.RECEIPT_FAINT, 4)
        pr.blit(surf, eye, (x, card.y + 62))
        y = card.y + 110
        for b in ctx.cart.items:
            pr.draw_text(surf, b.title[:26], fonts.body(theme.Size.SMALL), theme.RECEIPT_INK, (x, y))
            pr.draw_text(surf, str(b.price), fonts.body(theme.Size.SMALL), theme.RECEIPT_INK,
                         (card.right - 30, y), anchor="topright")
            y += 26
        y += 10
        pr.draw_text(surf, "Member's charm", fonts.body(theme.Size.SMALL), theme.RECEIPT_FAINT, (x, y))
        pr.draw_text(surf, f"-{led.discount}", fonts.body(theme.Size.SMALL), theme.RECEIPT_FAINT,
                     (card.right - 30, y), anchor="topright")
        y += 40
        pr.draw_text(surf, "Total Due", fonts.display(theme.Size.CARD_TITLE, bold=True),
                     theme.RECEIPT_INK, (x, y))
        pr.draw_text(surf, f"{led.total} ★", fonts.display(30, bold=True), theme.RECEIPT_INK,
                     (card.right - 30, y - 4), anchor="topright")

        btn = pygame.Rect(card.x + 30, card.bottom - 70, card.width - 60, 46)
        pr.vgradient(surf, btn, theme.CHECKOUT_BTN_TOP, theme.CHECKOUT_BTN_BOT)
        pr.round_rect(surf, btn, (*theme.PANEL_BORDER, 200), 11, width=1)
        pr.draw_text(surf, "[Enter] Complete Purchase", fonts.display(theme.Size.MENU),
                     theme.CREAM, btn.center, center=True)

        draw_hints(surf, ("[Enter] pay", "[Esc] back to cart"))


sc.register(sc.CHECKOUT, CheckoutScene)
