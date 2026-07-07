"""
Spines & Starlight — draw primitives.

Low-level helpers used by every widget and screen: gradients, glass panels,
glows, shadows, letter-spaced text, and the shared starfield/night background.
See docs/spines-and-starlight/04-components.md §0 and design system §6.

Scaling convention: every public helper takes LOGICAL (1280x720) coordinates and
scales them to device pixels internally (theme.SCALE), so callers author in the
spec's coordinate space and get native-crisp output. Fonts already come back at
device size from `fonts`, so text is sharp, not upscaled.
"""

import math

import pygame

from . import theme


# ----------------------------------------------------------------------
# Logical -> device scaling (reads theme.SCALE live, so a runtime rescale works)
# ----------------------------------------------------------------------
def sv(v):
    """Scale a scalar logical measurement to device pixels."""
    return round(v * theme.SCALE)


def sp(pos):
    """Scale a logical point to device pixels."""
    return (round(pos[0] * theme.SCALE), round(pos[1] * theme.SCALE))


def sr(rect):
    """Scale a logical rect to a device pygame.Rect."""
    S = theme.SCALE
    r = pygame.Rect(rect)
    return pygame.Rect(round(r.x * S), round(r.y * S), round(r.w * S), round(r.h * S))


# ----------------------------------------------------------------------
# Gradients & rounded rects
# ----------------------------------------------------------------------
_grad_cache: dict = {}


def clear_caches():
    """Drop scale-dependent caches — call after a rescale."""
    _grad_cache.clear()


def vgradient(surf, rect, top, bottom):
    """Vertical gradient fill. Caches a 1xH strip and scales it to width."""
    rect = sr(rect)
    if rect.h <= 0 or rect.w <= 0:
        return
    key = (rect.h, top, bottom)
    strip = _grad_cache.get(key)
    if strip is None:
        strip = pygame.Surface((1, rect.h))
        for y in range(rect.h):
            f = y / max(1, rect.h - 1)
            strip.set_at((0, y), (
                round(top[0] + (bottom[0] - top[0]) * f),
                round(top[1] + (bottom[1] - top[1]) * f),
                round(top[2] + (bottom[2] - top[2]) * f),
            ))
        _grad_cache[key] = strip
    surf.blit(pygame.transform.scale(strip, (rect.w, rect.h)), rect.topleft)


def round_rect(surf, rect, color, radius, width=0):
    w = width if width == 0 else max(1, sv(width))
    pygame.draw.rect(surf, color, sr(rect), width=w, border_radius=sv(radius))


# ----------------------------------------------------------------------
# Scaled wrappers for raw pygame.draw shapes (logical coords in)
# ----------------------------------------------------------------------
def circle(surf, center, r, color, width=0):
    w = 0 if width == 0 else max(1, sv(width))
    pygame.draw.circle(surf, color, sp(center), max(1, sv(r)), w)


def line(surf, a, b, color, width=1):
    pygame.draw.line(surf, color, sp(a), sp(b), max(1, sv(width)))


def ellipse(surf, rect, color, width=0):
    w = 0 if width == 0 else max(1, sv(width))
    pygame.draw.ellipse(surf, color, sr(rect), w)


def polygon(surf, points, color, width=0):
    w = 0 if width == 0 else max(1, sv(width))
    pygame.draw.polygon(surf, color, [sp(p) for p in points], w)


def dashed_line(surf, a, b, color, dash=6, gap=4, width=1):
    ax, ay = a
    bx, by = b
    dist = math.hypot(bx - ax, by - ay)
    if dist == 0:
        return
    ux, uy = (bx - ax) / dist, (by - ay) / dist
    n = int(dist // (dash + gap)) + 1
    for i in range(n):
        s = i * (dash + gap)
        e = min(s + dash, dist)
        line(surf, (ax + ux * s, ay + uy * s), (ax + ux * e, ay + uy * e), color, width)


def ellipse_alpha(surf, rect, rgba):
    """A translucent filled ellipse (e.g. actor shadows)."""
    rect = sr(rect)
    sub = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.ellipse(sub, rgba, sub.get_rect())
    surf.blit(sub, rect.topleft)


def vfade(surf, rect, color, a_top, a_bottom):
    """Vertical alpha fade of one color (e.g. floor fade, glow columns)."""
    rect = sr(rect)
    if rect.h <= 0 or rect.w <= 0:
        return
    strip = pygame.Surface((1, rect.h), pygame.SRCALPHA)
    for y in range(rect.h):
        f = y / max(1, rect.h - 1)
        strip.set_at((0, y), (*color, round(a_top + (a_bottom - a_top) * f)))
    surf.blit(pygame.transform.scale(strip, (rect.w, rect.h)), rect.topleft)


def alpha_rect(surf, rect, rgba, radius=0):
    """Translucent (optionally rounded) fill via an SRCALPHA sub-surface."""
    rect = sr(rect)
    sub = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(sub, rgba, sub.get_rect(), border_radius=sv(radius))
    surf.blit(sub, rect.topleft)


def glass_panel(surf, rect, radius=14, fill=theme.PANEL_BG, alpha=theme.A_PANEL,
                border=theme.PANEL_BORDER, border_alpha=theme.A_BORDER):
    """The translucent dark card behind HUD, tooltips, ledger, rows (§1)."""
    rect = sr(rect)
    sub = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(sub, (*fill, alpha), sub.get_rect(), border_radius=sv(radius))
    if border is not None:
        pygame.draw.rect(sub, (*border, border_alpha), sub.get_rect(),
                         width=max(1, sv(1)), border_radius=sv(radius))
    surf.blit(sub, rect.topleft)


# ----------------------------------------------------------------------
# Glows & shadows
# ----------------------------------------------------------------------
def glow(surf, center, radius, rgba):
    """Soft radial halo — a big low-alpha ellipse."""
    r = sv(radius)
    d = r * 2
    halo = pygame.Surface((d, d), pygame.SRCALPHA)
    pygame.draw.ellipse(halo, rgba, halo.get_rect())
    cx, cy = sp(center)
    surf.blit(halo, (cx - r, cy - r))


def drop_shadow(surf, rect, radius=14, offset=(0, 10), rgba=(0, 0, 0, 90)):
    """Fake box-shadow: an offset dark rounded rect beneath an element."""
    rect = sr(rect)
    sub = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(sub, rgba, sub.get_rect(), border_radius=sv(radius))
    surf.blit(sub, (rect.x + sv(offset[0]), rect.y + sv(offset[1])))


# ----------------------------------------------------------------------
# Text
# ----------------------------------------------------------------------
def render_tracked(text, font, color, px):
    """Letter-spaced text — pygame has no tracking, so blit glyph-by-glyph.

    `font` is already device-sized; `px` (the gap) is logical and scaled here.
    Returns a device-sized surface — blit it with `blit()` for logical position.
    """
    gap = sv(px)
    glyphs = [font.render(ch, True, color) for ch in text]
    width = sum(g.get_width() for g in glyphs) + gap * max(0, len(glyphs) - 1)
    height = font.get_height()
    out = pygame.Surface((max(1, width), height), pygame.SRCALPHA)
    x = 0
    for g in glyphs:
        out.blit(g, (x, 0))
        x += g.get_width() + gap
    return out


def blit(surf, img, pos, anchor="topleft"):
    """Blit a device-sized image at a logical position."""
    rect = img.get_rect()
    setattr(rect, anchor, sp(pos))
    surf.blit(img, rect)
    return rect


def draw_text(surf, text, font, color, pos, center=False, anchor="topleft", alpha=255):
    img = font.render(text, True, color)
    if alpha < 255:
        img.set_alpha(alpha)
    return blit(surf, img, pos, "center" if center else anchor)


def draw_paragraph(surf, text, font, color, pos, width, line_h, max_lines=None):
    """Word-wrap `text` to a logical `width`; returns the y after the last line.

    `font` is device-sized; `width`/`line_h`/`pos` are logical.
    """
    max_w = sv(width)
    x, y = pos
    lines, line = [], ""
    for w in text.split():
        trial = f"{line} {w}".strip()
        if font.size(trial)[0] > max_w and line:
            lines.append(line)
            line = w
        else:
            line = trial
    if line:
        lines.append(line)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip() + "…"
    for ln in lines:
        draw_text(surf, ln, font, color, (x, y))
        y += line_h
    return y


# ----------------------------------------------------------------------
# Background: night gradient + starfield (design system §6, components §15)
# ----------------------------------------------------------------------
class Starfield:
    """A fixed scatter of stars plus one twinkling overlay layer.

    Built at device resolution so the dots stay crisp 1-2px points.
    """

    def __init__(self, count=140, seed=7):
        import random
        rng = random.Random(seed)
        w, h = theme.WINDOW_W, theme.WINDOW_H
        self.base = pygame.Surface((w, h), pygame.SRCALPHA)
        self.twinkle = pygame.Surface((w, h), pygame.SRCALPHA)
        for _ in range(count):
            x, y = rng.randint(0, w), rng.randint(0, int(h * 0.72))
            r = rng.choice([1, 1, 1, 2])
            a = rng.randint(40, 130)
            pygame.draw.circle(self.base, (*theme.STAR, a), (x, y), r)
        for _ in range(count // 3):
            x, y = rng.randint(0, w), rng.randint(0, int(h * 0.72))
            r = rng.choice([1, 2])
            pygame.draw.circle(self.twinkle, (*theme.STAR, 200), (x, y), r)

    def draw(self, surf, t):
        surf.blit(self.base, (0, 0))
        self.twinkle.set_alpha(round(theme.twinkle_alpha(t) * 255))
        surf.blit(self.twinkle, (0, 0))


def night_bg(surf, rect=None, glow_center=None):
    """Vertical night gradient with a warm radial glow near the top."""
    rect = (0, 0, theme.CANVAS_W, theme.CANVAS_H) if rect is None else rect
    vgradient(surf, rect, theme.NIGHT_TOP, theme.NIGHT_BOTTOM)
    if glow_center is None:
        glow_center = (theme.CANVAS_W // 2, -40)
    glow(surf, glow_center, 360, (*theme.NIGHT_TOP, 60))


def page_bg(surf, rect=None):
    """The darker board/backdrop behind screens (title, cart, checkout)."""
    rect = (0, 0, theme.CANVAS_W, theme.CANVAS_H) if rect is None else rect
    vgradient(surf, rect, theme.PAGE_BG_TOP, theme.PAGE_BG_BOTTOM)
