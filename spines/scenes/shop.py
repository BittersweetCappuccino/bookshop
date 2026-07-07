"""Screen 02 — The Bookshop (Genre Aisles). The hub (spec: screen-02-bookshop.md)."""

import pygame

from .. import theme, fonts, primitives as pr, widgets, content, actors, furniture, audio
from .. import scene as sc
from .base import starfield, draw_hints

# Aisle layout, logical 1280x720 (spec §2-4). Aisles sit right of / below the
# top-left quest panel so nothing collides with it.
_LABEL_R = 336           # right edge of the genre-label column
_SHELF_X0 = 360          # first spine x
_PLANK_X, _PLANK_W = 300, 928
_TOP = 150
_SPINE_MAX = 100
_ROW_PITCH = 104
_PROXIMITY = 130         # how near Mira must be to hover/add a spine


def _plank_y(aisle):
    return _TOP + aisle * _ROW_PITCH + _SPINE_MAX


class ShopScene(sc.Scene):
    def on_enter(self, ctx):
        self.order = [g.id for g in sorted(content.GENRES.values(), key=lambda g: g.order)]
        self.spines = []
        for a, gid in enumerate(self.order):
            x = _SHELF_X0
            py = _plank_y(a)
            for i, book in enumerate(content.books_by_genre(gid)):
                w, h = theme.spine_geometry(i)
                self.spines.append({"book": book, "rect": pygame.Rect(x, py - h, w, h)})
                x += w + 6
        self.mira = actors.Mira(x=520, floor_y=632, min_x=370, max_x=1120)
        self.pops = []
        self.hovered = None
        self.add_rect = None
        self.cart_rect = None
        self.badge_plus = 0
        self.badge_timer = 0

    # -- input --------------------------------------------------------
    def handle_event(self, e, ctx):
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                ctx.go(sc.TITLE)
            elif e.key == pygame.K_c:
                ctx.go(sc.CART)
            elif e.key == pygame.K_e and self.hovered:
                self._add(ctx, self.hovered)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            pos = ctx.mouse
            if self.cart_rect and self.cart_rect.collidepoint(pos):
                ctx.go(sc.CART)
            elif self.add_rect and self.hovered and self.add_rect.collidepoint(pos):
                self._add(ctx, self.hovered)
            elif self.hovered:
                ctx.push(sc.DETAIL, book=self.hovered["book"])
                self.hovered = None   # don't draw a ghost tooltip under the overlay

    def _add(self, ctx, sp):
        book = sp["book"]
        if ctx.cart.has(book):
            return
        ctx.cart.add(book)
        self.mira.reach()
        audio.play_ding()
        self.pops.append(widgets.Pop(sp["rect"].centerx, sp["rect"].y - 10, "Added", theme.GOLD))
        self.badge_plus += 1
        self.badge_timer = 90
        self.hovered = None

    # -- per-frame ----------------------------------------------------
    def update(self, dt, ctx):
        self.mira.update(pygame.key.get_pressed())
        mx, my = ctx.mouse
        self.hovered = None
        for sp in self.spines:
            if ctx.cart.has(sp["book"]):
                continue
            if abs(self.mira.x - sp["rect"].centerx) < _PROXIMITY and sp["rect"].collidepoint(mx, my):
                self.hovered = sp
        for p in self.pops:
            p.update()
        self.pops = [p for p in self.pops if not p.dead]
        if self.badge_timer > 0:
            self.badge_timer -= 1
        else:
            self.badge_plus = 0

    # -- render -------------------------------------------------------
    def draw(self, surf, ctx):
        pr.night_bg(surf)
        starfield().draw(surf, ctx.t)
        furniture.lantern(surf, 300, 44, 38, 52, ctx.t, phase=0)
        furniture.lantern(surf, 980, 30, 34, 46, ctx.t, phase=120)

        for a, gid in enumerate(self.order):
            genre = content.GENRES[gid]
            py = _plank_y(a)
            pr.blit(surf, fonts.display(theme.Size.GENRE_HEADER).render(
                genre.name, True, theme.GENRE_LABEL[gid]), (_LABEL_R, py - 52), anchor="topright")
            dim = tuple(int(c * 0.62) for c in theme.GENRE_LABEL[gid])
            pr.blit(surf, pr.render_tracked(genre.subtitle.upper(), fonts.body(10), dim, 2.5),
                    (_LABEL_R, py - 20), anchor="topright")
            furniture.shelf_plank(surf, (_PLANK_X, py, _PLANK_W, 15))

        hov = self.hovered
        for sp in self.spines:
            if ctx.cart.has(sp["book"]) or sp is hov:
                continue
            widgets.draw_spine(surf, sp["rect"], sp["book"])
        if hov and not ctx.cart.has(hov["book"]):
            widgets.draw_spine(surf, hov["rect"], hov["book"], hovered=True)

        furniture.floor_fade(surf, height=120)
        actors.draw_cart(surf, self.mira, ctx.cart.items)
        self.mira.draw(surf, ctx.t)

        # HUD
        widgets.draw_quest(surf, ctx.quest, ctx.cart, (24, 22, 300, 140))
        widgets.coin_pill(surf, (theme.CANVAS_W - 24 - 96 - 8 - 96, 22), ctx.wallet.coins)
        self.cart_rect = widgets.cart_badge(surf, (theme.CANVAS_W - 24 - 96, 22),
                                            ctx.cart.count, self.badge_plus or None)

        self.add_rect = None
        if hov and not ctx.cart.has(hov["book"]):
            self.add_rect = widgets.draw_tooltip(
                surf, hov["book"], (hov["rect"].centerx, hov["rect"].y - 6))

        for p in self.pops:
            p.draw(surf)

        if ctx.quest.complete(ctx.cart):
            pr.draw_text(surf, "Your tales are gathered — press C for the cart.",
                         fonts.display(theme.Size.CARD_TITLE), theme.GOLD,
                         (theme.CANVAS_W // 2, theme.CANVAS_H - 54), center=True)

        draw_hints(surf, ("←→ walk", "hover + [E] add", "click to read", "[C] cart", "[Esc] leave"))


sc.register(sc.SHOP, ShopScene)
