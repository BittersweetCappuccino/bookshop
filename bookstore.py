"""
The Little Bookshop
A cozy point-and-click game: guide Mira through the bookshop, gather the
books on her shopping list, then wheel her cart to the checkout counter.

Controls:
    Arrow keys / A,D  -> walk Mira left and right
    Click a nearby book -> add it to the cart
    Walk to the glowing counter on the right to check out
    M -> mute / unmute music
    R -> new list & restock
    ESC -> quit

Requires: pygame  (pip install pygame)
"""

import pygame
import sys
import random
import math
import array

pygame.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2)
    AUDIO = True
except pygame.error:
    AUDIO = False

# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------
W, H = 960, 600
FPS = 60
FLOOR_Y = 500
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("The Little Bookshop")
clock = pygame.time.Clock()

CREAM      = (245, 236, 220)
WALL       = (232, 216, 190)
WOOD_DARK  = (110, 74, 48)
WOOD       = (150, 102, 66)
WOOD_LIGHT = (176, 128, 88)
FLOOR_COL  = (198, 160, 118)
INK        = (58, 44, 34)
GOLD       = (214, 170, 92)
GREEN      = (110, 150, 96)
WINDOW_SKY = (198, 220, 232)

# Named palette so the shopping list can refer to books by colour
NAMED_COLORS = {
    "Crimson":  (196, 78, 82),
    "Teal":     (78, 128, 128),
    "Ochre":    (206, 148, 74),
    "Plum":     (150, 96, 140),
    "Slate":    (92, 132, 158),
    "Moss":     (120, 150, 96),
    "Indigo":   (100, 116, 168),
    "Amber":    (210, 178, 96),
}
COLOR_NAMES = list(NAMED_COLORS.keys())

pygame.font.init()
FONT_BIG = pygame.font.SysFont("georgia", 34, bold=True)
FONT     = pygame.font.SysFont("georgia", 20)
FONT_SM  = pygame.font.SysFont("georgia", 15)
FONT_TINY= pygame.font.SysFont("georgia", 12)

COUNTER_X = 850   # centre of checkout zone

# ----------------------------------------------------------------------
# Music — procedural cozy loop (gentle arpeggio + soft bass)
# ----------------------------------------------------------------------
def make_music():
    if not AUDIO:
        return None
    sr = 44100
    bpm = 72
    beat = 60.0 / bpm
    # a warm ii-V-I-vi progression in C
    prog = [
        [220.00, 261.63, 329.63],   # Am
        [174.61, 220.00, 261.63],   # F
        [196.00, 246.94, 293.66],   # G
        [261.63, 329.63, 392.00],   # C
    ]
    seq = []
    for chord in prog:
        # arpeggiate each chord across the bar
        pattern = [chord[0], chord[1], chord[2], chord[1]]
        for n in pattern:
            seq.append((n, beat))
    total = sum(d for _, d in seq)
    n_samples = int(sr * total)
    buf = array.array("h", [0] * (n_samples * 2))

    def env(t, dur):
        a, r = 0.02, 0.25
        if t < a:   return t / a
        if t > dur - r: return max(0.0, (dur - t) / r)
        return 1.0

    pos = 0
    for i, (freq, dur) in enumerate(seq):
        dur_s = int(sr * dur)
        bass = prog[(i // 4) % 4][0] / 2.0
        for s in range(dur_s):
            t = s / sr
            e = env(t, dur)
            # soft triangle-ish lead + sine bass
            lead = math.sin(2 * math.pi * freq * t)
            lead += 0.3 * math.sin(2 * math.pi * freq * 2 * t)
            b = 0.5 * math.sin(2 * math.pi * bass * t)
            val = (lead * 0.16 * e + b * 0.14) * 0.8
            v = int(max(-1, min(1, val)) * 26000)
            idx = (pos + s) * 2
            buf[idx] = v
            buf[idx + 1] = v
        pos += dur_s
    return pygame.mixer.Sound(buffer=buf.tobytes())

def make_chime(freqs, dur=0.18):
    if not AUDIO:
        return None
    sr = 44100
    n = int(sr * dur * len(freqs))
    buf = array.array("h", [0] * (n * 2))
    pos = 0
    seg = int(sr * dur)
    for f in freqs:
        for s in range(seg):
            t = s / sr
            e = max(0.0, 1 - t / dur)
            val = math.sin(2 * math.pi * f * t) * 0.3 * e
            v = int(val * 26000)
            idx = (pos + s) * 2
            buf[idx] = v; buf[idx + 1] = v
        pos += seg
    return pygame.mixer.Sound(buffer=buf.tobytes())

# ----------------------------------------------------------------------
# Book
# ----------------------------------------------------------------------
class Book:
    def __init__(self, x, y, w, h, cname):
        self.rect = pygame.Rect(x, y, w, h)
        self.cname = cname
        self.color = NAMED_COLORS[cname]
        self.taken = False
        self.hover = False

    def draw(self, surf):
        if self.taken:
            return
        r = self.rect
        shade = tuple(max(0, c - 30) for c in self.color)
        light = tuple(min(255, c + 25) for c in self.color)
        pygame.draw.rect(surf, self.color, r, border_radius=2)
        pygame.draw.rect(surf, shade, (r.x, r.y, 3, r.h))
        pygame.draw.rect(surf, light, (r.right - 3, r.y, 3, r.h))
        band = GOLD if sum(self.color) < 380 else INK
        pygame.draw.line(surf, band, (r.x + 3, r.y + 10), (r.right - 3, r.y + 10), 2)
        pygame.draw.line(surf, band, (r.x + 3, r.bottom - 12), (r.right - 3, r.bottom - 12), 1)
        if self.hover:
            glow = pygame.Rect(r.x - 3, r.y - 4, r.w + 6, r.h + 8)
            pygame.draw.rect(surf, (255, 244, 200), glow, 2, border_radius=4)

# ----------------------------------------------------------------------
# Mira
# ----------------------------------------------------------------------
class Mira:
    def __init__(self, x):
        self.x = x
        self.y = FLOOR_Y
        self.speed = 3.4
        self.facing = 1
        self.walk_t = 0
        self.reaching = 0

    def update(self, keys):
        moving = False
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed; self.facing = -1; moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed; self.facing = 1; moving = True
        self.x = max(60, min(W - 40, self.x))
        self.walk_t = self.walk_t + 0.22 if moving else self.walk_t * 0.8
        if self.reaching > 0:
            self.reaching -= 1

    def reach(self):
        self.reaching = 18

    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        bob = math.sin(self.walk_t) * 2
        swing = math.sin(self.walk_t) * 6
        f = self.facing
        sh = pygame.Surface((70, 18), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 55), (0, 0, 70, 18))
        surf.blit(sh, (x - 35, y + 4))
        pygame.draw.line(surf, (70, 60, 90), (x - 6, y - 34), (x - 6 - swing, y), 7)
        pygame.draw.line(surf, (70, 60, 90), (x + 6, y - 34), (x + 6 + swing, y), 7)
        pygame.draw.ellipse(surf, INK, (x - 12 - swing, y - 4, 16, 8))
        pygame.draw.ellipse(surf, INK, (x + 2 + swing, y - 4, 16, 8))
        dress = (216, 168, 74)
        pts = [(x - 16, y - 34), (x + 16, y - 34), (x + 22, y - 62), (x - 22, y - 62)]
        pygame.draw.polygon(surf, dress, pts)
        pygame.draw.polygon(surf, tuple(c - 25 for c in dress), pts, 2)
        reach_lift = -26 if self.reaching > 0 else 0
        pygame.draw.line(surf, dress, (x - 14, y - 58), (x - 20 + reach_lift * (f < 0), y - 44 + reach_lift), 6)
        pygame.draw.line(surf, dress, (x + 14, y - 58), (x + 20 + reach_lift * (f > 0), y - 44 + reach_lift), 6)
        skin = (232, 190, 158)
        pygame.draw.circle(surf, skin, (x - 20 + reach_lift * (f < 0), y - 44 + reach_lift), 4)
        pygame.draw.circle(surf, skin, (x + 20 + reach_lift * (f > 0), y - 44 + reach_lift), 4)
        hy = y - 74 + bob
        pygame.draw.circle(surf, skin, (x, int(hy)), 13)
        hair = (96, 62, 42)
        pygame.draw.circle(surf, hair, (x, int(hy) - 3), 15)
        pygame.draw.rect(surf, skin, (x - 13, int(hy) - 2, 26, 14))
        pygame.draw.circle(surf, hair, (x - 12 * f, int(hy) + 2), 6)
        eye_x = x + 3 * f
        pygame.draw.circle(surf, INK, (eye_x, int(hy)), 2)
        pygame.draw.circle(surf, INK, (eye_x + 7 * f, int(hy)), 2)
        pygame.draw.arc(surf, (200, 120, 110), (eye_x, int(hy) + 3, 8, 6), math.pi, 2 * math.pi, 2)

# ----------------------------------------------------------------------
# World
# ----------------------------------------------------------------------
def build_shelves():
    books = []
    furniture = []
    shelf_units = [(70, 150), (330, 150), (590, 150)]
    unit_w = 200
    for ux, uy in shelf_units:
        furniture.append(pygame.Rect(ux, uy, unit_w, 300))
        for row in range(3):
            ry = uy + 30 + row * 92
            bx = ux + 16
            while bx < ux + unit_w - 24:
                bw = random.randint(12, 22)
                bh = random.randint(58, 74)
                cname = random.choice(COLOR_NAMES)
                books.append(Book(bx, ry + (74 - bh), bw, bh, cname))
                bx += bw + random.randint(1, 4)
    return books, furniture, shelf_units

def make_list(books):
    """Pick 4 books that actually exist on the shelves, as (name,color) targets."""
    available = list({b.cname for b in books})
    random.shuffle(available)
    picks = available[:4] if len(available) >= 4 else available
    return [{"cname": c, "done": False} for c in picks]

def draw_background(surf):
    surf.fill(WALL)
    win = pygame.Rect(340, 30, 200, 84)
    pygame.draw.rect(surf, WINDOW_SKY, win)
    pygame.draw.rect(surf, WOOD_DARK, win, 6)
    pygame.draw.line(surf, WOOD_DARK, (win.centerx, win.top), (win.centerx, win.bottom), 4)
    pygame.draw.line(surf, WOOD_DARK, (win.left, win.centery), (win.right, win.centery), 4)
    sign = FONT_BIG.render("The Little Bookshop", True, INK)
    surf.blit(sign, (430 - sign.get_width() // 2, 120))
    pygame.draw.rect(surf, FLOOR_COL, (0, FLOOR_Y - 6, W, H - FLOOR_Y + 6))
    for fx in range(0, W, 60):
        pygame.draw.line(surf, (176, 138, 100), (fx, FLOOR_Y - 6), (fx + 40, H), 1)

def draw_shelf_furniture(surf, furniture):
    for r in furniture:
        pygame.draw.rect(surf, WOOD, r, border_radius=4)
        pygame.draw.rect(surf, WOOD_DARK, r, 4, border_radius=4)
        for i in range(1, 4):
            by = r.y + 22 + i * 92
            pygame.draw.rect(surf, WOOD_LIGHT, (r.x + 4, by, r.w - 8, 8))
            pygame.draw.rect(surf, WOOD_DARK, (r.x + 4, by + 6, r.w - 8, 3))

def draw_counter(surf, active, t):
    """Checkout counter on the right side."""
    base = pygame.Rect(COUNTER_X - 70, FLOOR_Y - 70, 150, 76)
    # glow when Mira can check out
    if active:
        pulse = int(30 + 20 * math.sin(t * 0.1))
        halo = pygame.Surface((190, 130), pygame.SRCALPHA)
        pygame.draw.ellipse(halo, (255, 235, 160, pulse), halo.get_rect())
        surf.blit(halo, (base.centerx - 95, base.centery - 55))
    pygame.draw.rect(surf, WOOD, base, border_radius=6)
    pygame.draw.rect(surf, WOOD_DARK, base, 4, border_radius=6)
    top = pygame.Rect(base.x - 6, base.y - 10, base.w + 12, 14)
    pygame.draw.rect(surf, WOOD_LIGHT, top, border_radius=4)
    pygame.draw.rect(surf, WOOD_DARK, top, 2, border_radius=4)
    # little register
    reg = pygame.Rect(base.centerx - 16, base.y - 34, 34, 26)
    pygame.draw.rect(surf, (120, 84, 56), reg, border_radius=3)
    pygame.draw.rect(surf, INK, reg, 2, border_radius=3)
    pygame.draw.circle(surf, GOLD, (reg.centerx, reg.y + 8), 3)
    label = FONT_SM.render("Checkout", True, INK)
    surf.blit(label, (base.centerx - label.get_width() // 2, base.bottom - 22))

def draw_cart(surf, mira, collected):
    f = mira.facing
    cx = int(mira.x - f * 46)
    cy = FLOOR_Y
    body = pygame.Rect(cx - 26, cy - 46, 52, 34)
    pygame.draw.rect(surf, (120, 84, 56), body, border_radius=4)
    pygame.draw.rect(surf, WOOD_DARK, body, 3, border_radius=4)
    for gx in range(body.x + 8, body.right - 4, 10):
        pygame.draw.line(surf, WOOD_DARK, (gx, body.y + 4), (gx, body.bottom - 4), 1)
    pygame.draw.line(surf, INK, (cx + f * 26, cy - 46), (cx + f * 40, cy - 60), 3)
    pygame.draw.circle(surf, INK, (body.x + 10, cy - 8), 7)
    pygame.draw.circle(surf, INK, (body.right - 10, cy - 8), 7)
    pygame.draw.circle(surf, (90, 90, 90), (body.x + 10, cy - 8), 3)
    pygame.draw.circle(surf, (90, 90, 90), (body.right - 10, cy - 8), 3)
    for i, col in enumerate(collected[-6:]):
        bx = body.x + 6 + (i % 3) * 14
        by = body.bottom - 10 - (i // 3) * 12
        pygame.draw.rect(surf, col, (bx, by, 12, 10), border_radius=1)
        pygame.draw.rect(surf, tuple(max(0, c - 30) for c in col), (bx, by, 12, 10), 1)

def draw_list(surf, shopping):
    """The shopping list note in the top-left."""
    pad = pygame.Rect(16, 16, 210, 40 + len(shopping) * 26)
    note = pygame.Surface((pad.w, pad.h), pygame.SRCALPHA)
    pygame.draw.rect(note, (252, 246, 228, 240), note.get_rect(), border_radius=8)
    pygame.draw.rect(note, (200, 180, 150, 255), note.get_rect(), 2, border_radius=8)
    surf.blit(note, pad.topleft)
    surf.blit(FONT.render("Mira's list", True, INK), (pad.x + 12, pad.y + 8))
    for i, item in enumerate(shopping):
        y = pad.y + 40 + i * 26
        col = NAMED_COLORS[item["cname"]]
        pygame.draw.rect(surf, col, (pad.x + 14, y + 2, 16, 14), border_radius=2)
        pygame.draw.rect(surf, INK, (pad.x + 14, y + 2, 16, 14), 1, border_radius=2)
        txt = f"{item['cname']} book"
        c = (150, 150, 140) if item["done"] else INK
        label = FONT_SM.render(txt, True, c)
        surf.blit(label, (pad.x + 38, y + 2))
        if item["done"]:
            pygame.draw.line(surf, GREEN, (pad.x + 38, y + 10),
                             (pad.x + 38 + label.get_width(), y + 10), 2)
            pygame.draw.line(surf, GREEN, (pad.x + 34, y + 8), (pad.x + 30, y + 12), 2)

class Pop:
    def __init__(self, x, y, color, text="+1"):
        self.x, self.y, self.color, self.life, self.text = x, y, color, 44, text
    def update(self): self.y -= 1.2; self.life -= 1
    def draw(self, surf):
        s = FONT.render(self.text, True, self.color)
        s.set_alpha(max(0, self.life * 6))
        surf.blit(s, (self.x, self.y))

# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main():
    books, furniture, shelf_units = build_shelves()
    shopping = make_list(books)
    mira = Mira(W // 2)
    collected = []
    pops = []
    checked_out = False
    t = 0

    music = make_music()
    ding = make_chime([659, 880])
    cash = make_chime([523, 659, 784, 1047], 0.13)
    muted = False
    if music and AUDIO:
        music.play(loops=-1)

    while True:
        clock.tick(FPS)
        t += 1
        mx, my = pygame.mouse.get_pos()
        needed = [it["cname"] for it in shopping if not it["done"]]
        all_done = all(it["done"] for it in shopping)
        near_counter = abs(mira.x - COUNTER_X) < 90

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if e.key == pygame.K_r:
                    books, furniture, shelf_units = build_shelves()
                    shopping = make_list(books)
                    collected.clear(); checked_out = False
                if e.key == pygame.K_m and music:
                    muted = not muted
                    music.set_volume(0.0 if muted else 1.0)
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and not checked_out:
                for b in books:
                    if not b.taken and b.rect.collidepoint(mx, my):
                        if abs(mira.x - b.rect.centerx) < 130:
                            b.taken = True
                            mira.reach()
                            collected.append(b.color)
                            # tick off the list if this colour was needed
                            matched = False
                            for it in shopping:
                                if not it["done"] and it["cname"] == b.cname:
                                    it["done"] = True; matched = True; break
                            if matched and ding and not muted: ding.play()
                            pops.append(Pop(b.rect.centerx, b.rect.y, b.color,
                                            "On list!" if matched else "+1"))
                        break

        keys = pygame.key.get_pressed()
        mira.update(keys)

        # checkout trigger
        if all_done and near_counter and not checked_out:
            checked_out = True
            if cash and not muted: cash.play()

        for b in books:
            near = abs(mira.x - b.rect.centerx) < 130
            b.hover = (not b.taken and b.rect.collidepoint(mx, my) and near)

        # draw
        draw_background(screen)
        draw_shelf_furniture(screen, furniture)
        for b in books:
            b.draw(screen)
        draw_counter(screen, all_done and not checked_out, t)
        draw_cart(screen, mira, collected)
        mira.draw(screen)
        for p in pops[:]:
            p.update(); p.draw(screen)
            if p.life <= 0: pops.remove(p)
        draw_list(screen, shopping)

        # status line
        if all_done and not checked_out:
            msg = "List complete! Wheel your cart to the checkout ->"
            s = FONT.render(msg, True, (150, 100, 60))
            screen.blit(s, (W // 2 - s.get_width() // 2, 470))

        tip = FONT_SM.render("Arrows to walk   Click a nearby book   M mute   R new list", True, INK)
        screen.blit(tip, (W // 2 - tip.get_width() // 2, H - 24))
        if music:
            mtxt = FONT_TINY.render("music: off (M)" if muted else "music: on (M)", True, INK)
            screen.blit(mtxt, (W - mtxt.get_width() - 12, 12))

        if checked_out:
            veil = pygame.Surface((W, H), pygame.SRCALPHA)
            veil.fill((40, 28, 20, 150))
            screen.blit(veil, (0, 0))
            done = FONT_BIG.render("Thanks for shopping, Mira!", True, CREAM)
            sub = FONT.render("Press R to start a new list.", True, GOLD)
            screen.blit(done, (W // 2 - done.get_width() // 2, 260))
            screen.blit(sub, (W // 2 - sub.get_width() // 2, 310))

        pygame.display.flip()

if __name__ == "__main__":
    main()
