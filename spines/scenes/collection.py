"""Your Collection — a gallery of purchased books (not in the original spec;
the title menu links here). Reads profile.collection."""

import pygame

from .. import theme, fonts, primitives as pr, widgets, content
from .. import scene as sc
from .base import starfield

_PAD = 60
_COLS = 6
_COVER_W, _COVER_H = 104, 150
_ROW_PITCH = 212
_MAX = _COLS * 2   # two rows fit the frame cleanly


class CollectionScene(sc.Scene):
    def on_enter(self, ctx):
        self.back_rect = pygame.Rect(theme.CANVAS_W // 2 - 110, theme.CANVAS_H - 52, 220, 24)

    def handle_event(self, e, ctx):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            ctx.go(sc.TITLE)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.back_rect.collidepoint(ctx.mouse):
                ctx.go(sc.TITLE)

    def draw(self, surf, ctx):
        pr.page_bg(surf)
        starfield().draw(surf, ctx.t)

        books = [b for b in (content.find(i) for i in ctx.profile.collection) if b]
        h = pr.draw_text(surf, "Your Collection", fonts.display(theme.Size.SECTION, bold=True),
                         theme.CREAM, (_PAD, 56))
        n = len(books)
        pr.draw_text(surf, f"{n} tale{'s' if n != 1 else ''} collected",
                     fonts.body(theme.Size.SMALL), theme.TEXT_MUTED,
                     (_PAD + h.width / theme.SCALE + 16, 92))
        pr.alpha_rect(surf, (_PAD, 116, theme.CANVAS_W - 2 * _PAD, 1), (*theme.GOLD, 90))

        if not books:
            pr.draw_text(surf, "Your collection is empty.", fonts.display(theme.Size.PANEL_HEAD),
                         theme.TEXT_MUTED, (theme.CANVAS_W // 2, 320), center=True)
            pr.draw_text(surf, "Tales you buy at the desk will be shelved here.",
                         fonts.body(theme.Size.BODY), theme.TEXT_FAINT,
                         (theme.CANVAS_W // 2, 362), center=True)
        else:
            col_w = (theme.CANVAS_W - 2 * _PAD) / _COLS
            for i, b in enumerate(books[:_MAX]):
                cx = _PAD + (i % _COLS) * col_w + col_w / 2
                y = 168 + (i // _COLS) * _ROW_PITCH
                widgets.draw_thumb(surf, (round(cx - _COVER_W / 2), y, _COVER_W, _COVER_H), b)
                title = widgets._ellipsize(b.title, fonts.body(theme.Size.SMALL), col_w - 12)
                pr.draw_text(surf, title, fonts.body(theme.Size.SMALL), theme.CREAM,
                             (cx, y + _COVER_H + 10), center=True)
                pr.draw_text(surf, b.author, fonts.body(theme.Size.EYEBROW), theme.TEXT_MUTED,
                             (cx, y + _COVER_H + 32), center=True)
            if n > _MAX:
                pr.draw_text(surf, f"+ {n - _MAX} more", fonts.body(theme.Size.BODY),
                             theme.TEXT_FAINT, (theme.CANVAS_W // 2, 168 + 2 * _ROW_PITCH - 20),
                             center=True)

        hover = self.back_rect.collidepoint(ctx.mouse)
        pr.draw_text(surf, "Back to the menu · [Esc]", fonts.body(12),
                     theme.GOLD if hover else theme.TEXT_FAINT,
                     self.back_rect.center, center=True)


sc.register(sc.COLLECTION, CollectionScene)
