"""Screen 02 — The Bookshop (hub). Stub (full spec: screen-02-bookshop.md)."""

import pygame

from .. import scene as sc
from .base import PlaceholderScene


class ShopScene(PlaceholderScene):
    number = "02"
    name = "The Bookshop"
    subtitle = "Genre aisles — browse spines, drop finds into the cart."
    hints = ("[Enter] read a book (Detail)", "[A] add a book",
             "[C] cart", "[Esc] to the menu")

    def on_enter(self, ctx):
        self._pick = 0   # which catalog book the demo actions target

    def handle_event(self, e, ctx):
        if e.type != pygame.KEYDOWN:
            return
        if e.key == pygame.K_ESCAPE:
            ctx.go(sc.TITLE)                      # Esc at the hub -> quit to menu
        elif e.key in (pygame.K_c,):
            ctx.go(sc.CART)
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            book = ctx.catalog[self._pick % len(ctx.catalog)]
            ctx.push(sc.DETAIL, book=book)        # overlay, shop stays underneath
        elif e.key == pygame.K_a:
            book = ctx.catalog[self._pick % len(ctx.catalog)]
            ctx.cart.add(book)
            self._pick += 1


sc.register(sc.SHOP, ShopScene)
