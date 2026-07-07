"""
Spines & Starlight — application entry point.

The scene-stack main loop that drives the whole game (screen-flow §5).

Display model: scenes always author in 1280x720 logical space. At startup we pick
a scale that fits the player's desktop, render the frame onto a device-resolution
surface at that scale (crisp), then blit it centered into a resizable window
(letterboxed if the window aspect drifts from 16:9). Resizing re-scales live.
Run with `python -m spines`.
"""

import os
import sys

import pygame

from . import theme, fonts, primitives as pr, audio
from . import scene as sc
from . import scenes  # noqa: F401  (registers all scenes on import)
from .scenes import base

# fraction of the desktop we're willing to fill (leaves room for taskbar/titlebar)
_FIT_W, _FIT_H = 0.95, 0.90
_MIN_SCALE, _MAX_SCALE = 0.5, 3.0


def _desktop_size():
    try:
        return pygame.display.get_desktop_sizes()[0]
    except Exception:
        return (0, 0)


def _initial_scale():
    """Largest scale whose 16:9 window comfortably fits the desktop."""
    env = os.environ.get("SPINES_SCALE")
    if env:
        return float(env)
    dw, dh = _desktop_size()
    if dw <= 0 or dh <= 0:
        return 1.5
    scale = min(dw * _FIT_W / theme.CANVAS_W, dh * _FIT_H / theme.CANVAS_H)
    return max(_MIN_SCALE, min(scale, _MAX_SCALE))


def _configure(win_w, win_h):
    """Fit the render surface to the window; returns (render_surface, offset)."""
    scale = min(win_w / theme.CANVAS_W, win_h / theme.CANVAS_H)
    theme.set_scale(scale)
    fonts.clear_cache()
    pr.clear_caches()
    base.reset_starfield()
    render = pygame.Surface((theme.WINDOW_W, theme.WINDOW_H))
    offset = ((win_w - theme.WINDOW_W) // 2, (win_h - theme.WINDOW_H) // 2)
    return render, offset


def run():
    pygame.init()
    pygame.font.init()

    scale0 = _initial_scale()
    win_w, win_h = round(theme.CANVAS_W * scale0), round(theme.CANVAS_H * scale0)
    window = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
    pygame.display.set_caption("Spines & Starlight")
    clock = pygame.time.Clock()
    render, offset = _configure(win_w, win_h)

    fullscreen = False
    windowed_size = (win_w, win_h)
    max_frames = int(os.environ.get("SPINES_MAX_FRAMES", "0"))

    ctx = sc.new_context()
    # Music starts at the title and carries across scenes; skip in headless runs
    # (dummy video) so smoke/screenshot tooling doesn't build the audio buffer.
    if os.environ.get("SDL_VIDEODRIVER") != "dummy":
        audio.init(ctx.muted)

    stack = [sc.make_scene(sc.TITLE)]
    stack[-1].on_enter(ctx)

    frame = 0
    while True:
        dt = clock.tick(theme.FPS)
        ctx.t += 1
        frame += 1

        mx, my = pygame.mouse.get_pos()
        ctx.mouse = ((mx - offset[0]) / theme.SCALE, (my - offset[1]) / theme.SCALE)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.VIDEORESIZE and not fullscreen:
                windowed_size = (e.w, e.h)
                window = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
                render, offset = _configure(e.w, e.h)
                continue
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_m:
                    ctx.muted = not ctx.muted
                    audio.set_muted(ctx.muted)
                    continue
                if e.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        dw, dh = _desktop_size()
                        window = pygame.display.set_mode((dw, dh), pygame.FULLSCREEN)
                        render, offset = _configure(*window.get_size())
                    else:
                        window = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
                        render, offset = _configure(*windowed_size)
                    continue
            stack[-1].handle_event(e, ctx)

        stack[-1].update(dt, ctx)

        for s in sc.visible_slice(stack):
            s.draw(render, ctx)

        window.fill((0, 0, 0))       # letterbox bars
        window.blit(render, offset)

        sc.apply_transitions(stack, ctx)

        if ctx._quit:
            pygame.quit()
            sys.exit()

        pygame.display.flip()

        if max_frames and frame >= max_frames:
            pygame.quit()
            return


if __name__ == "__main__":
    run()
