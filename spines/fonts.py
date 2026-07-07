"""
Spines & Starlight — font loading.

The concept uses Cormorant Garamond (display) and Spectral (body). pygame needs
TrueType/OpenType, so those TTFs belong in spines/assets/fonts/. Until they are
bundled we fall back to the best available system serifs. See design system §3.
"""

import os

import pygame

from . import theme

_FONT_DIR = os.path.join(os.path.dirname(__file__), "assets", "fonts")

# Bundled TTF filenames (drop the real files here to upgrade the look).
_DISPLAY_TTF = {
    (False, False): "CormorantGaramond-SemiBold.ttf",
    (True, False): "CormorantGaramond-Bold.ttf",
    (False, True): "CormorantGaramond-SemiBoldItalic.ttf",
    (True, True): "CormorantGaramond-BoldItalic.ttf",
}
_BODY_TTF = {
    (False, False): "Spectral-Regular.ttf",
    (True, False): "Spectral-SemiBold.ttf",
    (False, True): "Spectral-Italic.ttf",
    (True, True): "Spectral-SemiBoldItalic.ttf",
}

# SysFont fallback chains (comma-separated; pygame tries each in turn).
_DISPLAY_CHAIN = "constantia,cambria,georgia,timesnewroman"
_BODY_CHAIN = "cambria,georgia,timesnewroman"

_cache: dict = {}


def clear_cache():
    """Drop cached fonts — call after a rescale so sizes re-rasterize."""
    _cache.clear()


def _load(role, size, bold, italic):
    ttfs, chain = (_DISPLAY_TTF, _DISPLAY_CHAIN) if role == "display" else (_BODY_TTF, _BODY_CHAIN)
    path = os.path.join(_FONT_DIR, ttfs[(bold, italic)])
    try:
        return pygame.font.Font(path, size)
    except (FileNotFoundError, OSError):
        return pygame.font.SysFont(chain, size, bold=bold, italic=italic)


def display(size, bold=True, italic=False):
    """Cormorant-family font for titles, headings, buttons."""
    return get("display", size, bold, italic)


def body(size, bold=False, italic=False):
    """Spectral-family font for body text, UI, numerals."""
    return get("body", size, bold, italic)


def get(role, size, bold=False, italic=False):
    """Return a font for a LOGICAL point size, rendered at device size.

    Callers pass the spec's 1280x720 size; we scale it up by theme.SCALE so the
    glyphs are rasterized crisply at the native resolution rather than upscaled.
    """
    dev_size = theme.s(size)
    key = (role, dev_size, bold, italic)
    font = _cache.get(key)
    if font is None:
        font = _load(role, dev_size, bold, italic)
        _cache[key] = font
    return font
