"""Settings — a small options panel (not in the original spec; the title menu
links here). Currently: a working music toggle, plus fullscreen/mute hints."""

import pygame

from .. import theme, fonts, primitives as pr, audio
from .. import scene as sc
from .base import starfield


class SettingsScene(sc.Scene):
    def on_enter(self, ctx):
        self.music_rect = None
        self.back_rect = None

    def handle_event(self, e, ctx):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            ctx.go(sc.TITLE)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.music_rect and self.music_rect.collidepoint(ctx.mouse):
                ctx.muted = not ctx.muted
                audio.set_muted(ctx.muted)
            elif self.back_rect and self.back_rect.collidepoint(ctx.mouse):
                ctx.go(sc.TITLE)

    def draw(self, surf, ctx):
        pr.page_bg(surf)
        starfield().draw(surf, ctx.t)
        pr.draw_text(surf, "Settings", fonts.display(theme.Size.SECTION, bold=True),
                     theme.CREAM, (theme.CANVAS_W // 2, 130), center=True)

        panel = pygame.Rect(0, 0, 560, 270)
        panel.center = (theme.CANVAS_W // 2, 410)
        pr.glass_panel(surf, panel, radius=18, fill=theme.PANEL_BG2, alpha=theme.A_PANEL2)
        x, y = panel.x + 36, panel.y + 40

        # Music: a real toggle wired to the global mute state
        pr.draw_text(surf, "Music", fonts.display(theme.Size.CARD_TITLE), theme.CREAM, (x, y))
        self.music_rect = self._toggle(surf, (panel.right - 36 - 96, y - 6),
                                        "On" if not ctx.muted else "Off", not ctx.muted, ctx.mouse)
        y += 74

        # Fullscreen: handled by the app on F11 (a scene can't own the window)
        pr.draw_text(surf, "Fullscreen", fonts.display(theme.Size.CARD_TITLE), theme.CREAM, (x, y))
        pr.draw_text(surf, "Press F11", fonts.body(theme.Size.BODY), theme.TEXT_MUTED,
                     (panel.right - 36, y + 6), anchor="topright")
        y += 66

        pr.line(surf, (x, y), (panel.right - 36, y), theme.PANEL_BORDER, 1)
        y += 18
        pr.draw_text(surf, "Tip: press M anywhere to mute or unmute.",
                     fonts.body(theme.Size.SMALL), theme.TEXT_FAINT, (x, y))

        self.back_rect = pygame.Rect(panel.centerx - 110, panel.bottom + 28, 220, 26)
        hover = self.back_rect.collidepoint(ctx.mouse)
        pr.draw_text(surf, "Back to the menu · [Esc]", fonts.body(12),
                     theme.GOLD if hover else theme.TEXT_FAINT, self.back_rect.center, center=True)

    def _toggle(self, surf, pos, label, on, mouse):
        rect = pygame.Rect(pos[0], pos[1], 96, 36)
        if on:
            top, bot = theme.BTN_GOLD_TOP, theme.BTN_GOLD_BOT
            if rect.collidepoint(mouse):
                top = tuple(min(255, c + 16) for c in top)
                bot = tuple(min(255, c + 16) for c in bot)
            pr.vgradient(surf, rect, top, bot)
            pr.round_rect(surf, rect, (*theme.PANEL_BORDER, 220), 11, width=1)
            pr.draw_text(surf, label, fonts.display(theme.Size.MENU, bold=True),
                         theme.BTN_GOLD_TEXT, rect.center, center=True)
        else:
            pr.alpha_rect(surf, rect, (*theme.BTN2_BG, 160), 11)
            pr.round_rect(surf, rect, (*theme.BTN2_BORDER, 160), 11, width=1)
            pr.draw_text(surf, label, fonts.display(theme.Size.MENU), theme.TEXT_MUTED,
                         rect.center, center=True)
        return rect


sc.register(sc.SETTINGS, SettingsScene)
