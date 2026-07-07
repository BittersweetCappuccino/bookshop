"""Screen 01 — Title & Start Menu. A first pass (full spec: screen-01-title.md)."""

import pygame

from .. import theme, fonts, primitives as pr, widgets, content
from .. import scene as sc
from .base import starfield


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

        # eyebrow + hero wordmark
        eye = pr.render_tracked("A BOOKSHOP TALE", fonts.body(theme.Size.EYEBROW),
                                theme.EYEBROW_GOLD, 6)
        pr.blit(surf, eye, (252, 180))
        pr.draw_text(surf, "Spines", fonts.display(theme.Size.HERO, bold=True),
                     theme.CREAM, (248, 200))
        pr.draw_text(surf, "& Starlight", fonts.display(64, bold=True, italic=True),
                     theme.GOLD_ITALIC, (252, 300))

        for b in self.buttons:
            b.draw(surf, ctx.mouse, ctx.t)

        # floating open-book placeholder on the right, bobbing (motion §5)
        dy = theme.float_dy(ctx.t)
        book = pygame.Rect(880, 250 + dy, 200, 280)
        pr.glow(surf, book.center, 200, (*theme.GOLD, 30))
        pr.vgradient(surf, book, theme.oklch_to_rgb(0.42, 0.13, 288),
                     theme.oklch_to_rgb(0.20, 0.09, 290))
        pr.round_rect(surf, book, (*theme.GOLD, 120), 8, width=2)

        pr.draw_text(surf, "Enter to begin  ·  Esc to close the shop",
                     fonts.body(theme.Size.SMALL), theme.TEXT_FAINT,
                     (theme.CANVAS_W // 2, theme.CANVAS_H - 34), center=True)


sc.register(sc.TITLE, TitleScene)
