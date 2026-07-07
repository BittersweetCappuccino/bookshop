"""
Spines & Starlight — reusable widgets.

The interactive/visual components the per-screen specs compose. This module will
grow to cover the full component library (docs/spines-and-starlight/04-components.md);
for the scaffold it provides the Button used by the title menu, plus the coin
glyph used across HUD/ledger/receipt. All positions are LOGICAL (see primitives).
"""

import math

import pygame

from . import theme, fonts, primitives as pr, content


class Button:
    """A clickable button. kind in {'primary', 'ghost', 'pill'} (§2).

    `rect` and hit-testing are in logical coordinates; drawing scales to device.
    """

    def __init__(self, rect, label, kind="primary", enabled=True, tracking=1):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.kind = kind
        self.enabled = enabled
        self.tracking = tracking

    def hit(self, pos):
        return self.enabled and self.rect.collidepoint(pos)

    def draw(self, surf, mouse_pos, t=0):
        hovered = self.hit(mouse_pos)
        r = self.rect
        if self.kind == "primary":
            top, bot = theme.BTN_GOLD_TOP, theme.BTN_GOLD_BOT
            if hovered:
                top = tuple(min(255, c + 18) for c in top)
                bot = tuple(min(255, c + 18) for c in bot)
            if self.enabled:
                pr.drop_shadow(surf, r, 12, offset=(0, 12), rgba=(90, 50, 10, 110))
            pr.vgradient(surf, r, top, bot)
            if not self.enabled:
                pr.alpha_rect(surf, r, (20, 10, 25, 150), 12)
            pr.round_rect(surf, r, (*theme.PANEL_BORDER, 255), 12, width=1)
            self._label(surf, theme.BTN_GOLD_TEXT, fonts.display(theme.Size.MENU, bold=True))
        elif self.kind == "ghost":
            alpha = 178 if hovered and self.enabled else theme.A_ROW
            pr.alpha_rect(surf, r, (*theme.BTN2_BG, alpha), 12)
            pr.round_rect(surf, r, (*theme.BTN2_BORDER, 128), 12, width=1)
            color = theme.BTN2_TEXT if self.enabled else theme.TEXT_FAINT
            self._label(surf, color, fonts.display(theme.Size.MENU))
        else:  # pill
            color = theme.GOLD_HOVER if hovered else theme.EYEBROW_GOLD
            pr.round_rect(surf, r, (*color, 128), 20, width=1)
            self._label(surf, color, fonts.body(theme.Size.EYEBROW), upper=True)
        return hovered

    def _label(self, surf, color, font, upper=False):
        text = self.label.upper() if upper else self.label
        img = pr.render_tracked(text, font, color, self.tracking)
        pr.blit(surf, img, self.rect.center, anchor="center")


def coin_glyph(surf, center, r=10):
    """Radial coin disc with an inner ring (§6). center/r are logical."""
    rr = pr.sv(r)
    d = rr * 2
    disc = pygame.Surface((d, d), pygame.SRCALPHA)
    for i in range(rr, 0, -1):
        f = i / rr
        col = tuple(
            round(theme.COIN_LIGHT[k] + (theme.COIN_DARK[k] - theme.COIN_LIGHT[k]) * (1 - f))
            for k in range(3)
        )
        pygame.draw.circle(disc, col, (rr, rr), i)
    pygame.draw.circle(disc, theme.COIN_DARK, (rr, rr), rr - max(1, pr.sv(2)), width=max(1, pr.sv(1)))
    cx, cy = pr.sp(center)
    surf.blit(disc, (cx - rr, cy - rr))


def coin_value(surf, pos, n, size=20, color=theme.COIN_NUM, r=10):
    """Coin glyph + number at a logical position; returns approx logical width."""
    cy = pos[1] + size / 2
    coin_glyph(surf, (pos[0] + r, cy), r)
    img = fonts.display(size, bold=True).render(str(n), True, color)
    pr.blit(surf, img, (pos[0] + r * 2 + 6, cy), anchor="midleft")
    return r * 2 + 6 + round(img.get_width() / theme.SCALE)


# ----------------------------------------------------------------------
# Star rating (§9) — drawn as shapes so it never depends on a font glyph
# ----------------------------------------------------------------------
def _star(surf, center, r, color, filled):
    pts = []
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.42
        pts.append((center[0] + rr * math.cos(ang), center[1] + rr * math.sin(ang)))
    pr.polygon(surf, pts, color, 0 if filled else 1)


def star_row(surf, pos, rating, size=14):
    step = size + 2
    for i in range(5):
        cx = pos[0] + i * step + size / 2
        filled = rating - i >= 0.5
        _star(surf, (cx, pos[1] + size / 2), size / 2,
              theme.STAR_RATING if filled else theme.TEXT_FAINT, filled)
    return 5 * step


# ----------------------------------------------------------------------
# Progress bar (§10)
# ----------------------------------------------------------------------
def progress_bar(surf, rect, fraction):
    rect = pygame.Rect(rect)
    pr.round_rect(surf, rect, theme.TRACK_BG, rect.h / 2)
    frac = max(0.0, min(1.0, fraction))
    if frac <= 0:
        return
    fw = max(rect.h, round(rect.w * frac))
    pr.round_rect(surf, (rect.x, rect.y, fw, rect.h), theme.PROGRESS_B, rect.h / 2)


# ----------------------------------------------------------------------
# Genre pill / tag (§8)
# ----------------------------------------------------------------------
def draw_pill(surf, pos, text, hue=None):
    """Rounded genre tag (hue) or neutral outline (hue=None). Returns its rect."""
    font = fonts.body(10)
    if hue is not None:
        text_col = theme.oklch_to_rgb(0.90, 0.06, hue)
        fill = theme.oklch_to_rgb(0.52, 0.12, hue)
    else:
        text_col, fill = theme.EYEBROW_GOLD, None
    img = pr.render_tracked(text.upper(), font, text_col, 1.5)
    lw = img.get_width() / theme.SCALE
    h = 18
    rect = pygame.Rect(pos[0], pos[1], round(lw + 16), h)
    if fill is not None:
        pr.alpha_rect(surf, rect, (*fill, 150), h // 2)
    else:
        pr.round_rect(surf, rect, (*text_col, 150), h // 2, width=1)
    pr.blit(surf, img, rect.center, anchor="center")
    return rect


# ----------------------------------------------------------------------
# HUD pills (§6, §7)
# ----------------------------------------------------------------------
def coin_pill(surf, pos, coins):
    rect = pygame.Rect(pos[0], pos[1], 96, 40)
    pr.glass_panel(surf, rect, radius=20)
    coin_value(surf, (rect.x + 12, rect.y + 9), coins, size=22)
    return rect


def cart_badge(surf, pos, count, plus=None):
    rect = pygame.Rect(pos[0], pos[1], 96, 40)
    pr.glass_panel(surf, rect, radius=20, border=theme.BTN2_BORDER, border_alpha=180)
    bx, by = rect.x + 16, rect.y + 13
    pr.polygon(surf, [(bx, by), (bx + 18, by), (bx + 15, by + 12), (bx + 3, by + 12)], theme.TEXT, 0)
    pr.circle(surf, (bx + 4, by + 16), 2, theme.TEXT)
    pr.circle(surf, (bx + 13, by + 16), 2, theme.TEXT)
    pr.draw_text(surf, str(count), fonts.display(22, bold=True), theme.CREAM, (rect.x + 52, rect.y + 8))
    if plus:
        pr.circle(surf, (rect.right - 8, rect.y + 8), 9, theme.BADGE_RED)
        pr.draw_text(surf, f"+{plus}", fonts.body(11, bold=True), (40, 12, 16),
                     (rect.right - 8, rect.y + 8), center=True)
    return rect


# ----------------------------------------------------------------------
# Quest tracker (§11)
# ----------------------------------------------------------------------
def draw_quest(surf, quest, cart, rect):
    rect = pygame.Rect(rect)
    pr.glass_panel(surf, rect, radius=14)
    x, y = rect.x + 16, rect.y + 14
    pr.polygon(surf, [(x, y + 5), (x + 5, y), (x + 10, y + 5), (x + 5, y + 10)], theme.GOLD, 0)
    pr.blit(surf, pr.render_tracked("CURRENT QUEST", fonts.body(11), theme.EYEBROW_GOLD, 2), (x + 16, y))
    yy = pr.draw_paragraph(surf, quest.title, fonts.display(theme.Size.CARD_TITLE), theme.CREAM,
                           (x, y + 24), rect.w - 32, 26, max_lines=2)
    progress_bar(surf, (x, yy + 8, rect.w - 32, 6), quest.fraction(cart))
    pr.draw_text(surf, f"{quest.progress(cart)} of {quest.target} chosen",
                 fonts.body(theme.Size.SMALL), theme.TEXT_MUTED, (x, yy + 20))


# ----------------------------------------------------------------------
# Book spine (§3) — colors/size derived from spine_shades
# ----------------------------------------------------------------------
def draw_spine(surf, rect, book, hovered=False):
    r = pygame.Rect(rect)
    if hovered:
        r = r.move(0, -6)
        pr.glow(surf, r.center, r.h * 0.7, (*theme.GENRE_LABEL[book.genre], 45))
    top, mid, bottom, band = theme.spine_shades(book.hue, book.shelf_index)
    pr.vgradient(surf, r, top, bottom)
    pr.round_rect(surf, (r.x, r.y + 4, r.w, 5), band, 1)          # title band
    pr.line(surf, (r.right - 1, r.y), (r.right - 1, r.bottom), (0, 0, 0), 1)   # inset edge
    _spine_title(surf, r, book)
    if hovered:
        pr.round_rect(surf, r, (*theme.GOLD_HOVER, 170), 2, width=1)


def _spine_title(surf, r, book):
    img = fonts.display(10).render(book.title, True, theme.GENRE_LABEL[book.genre])
    img = pygame.transform.rotate(img, 90)
    dev = pr.sr(r)
    prev = surf.get_clip()
    surf.set_clip(dev)
    surf.blit(img, img.get_rect(center=(dev.centerx, dev.centery + pr.sv(8))))
    surf.set_clip(prev)


# ----------------------------------------------------------------------
# Book cover (§4) — the large detail cover; emblem is generic per genre
# ----------------------------------------------------------------------
_COVER_SUBTITLE = {"the-ashen-crown": "A Novel of the Star-Court"}


def draw_cover(surf, rect, book):
    rect = pygame.Rect(rect)
    hue = book.hue
    pr.glow(surf, rect.center, rect.h * 0.62, (*theme.oklch_to_rgb(0.5, 0.12, hue), 60))

    top = theme.oklch_to_rgb(0.42, 0.13, hue)
    bot = theme.oklch_to_rgb(0.20, 0.09, hue + 2)
    pr.round_rect(surf, rect, bot, 10)
    pr.vgradient(surf, rect.inflate(-4, -4), top, bot)
    pr.alpha_rect(surf, (rect.x + 4, rect.y + 4, 8, rect.h - 8), (255, 255, 255, 26), 2)  # spine hi
    pr.round_rect(surf, rect.inflate(-40, -40), (*theme.GOLD, 150), 6, width=1)            # frame

    sub = _COVER_SUBTITLE.get(book.id, content.GENRES[book.genre].subtitle)
    pr.blit(surf, pr.render_tracked(sub.upper(), fonts.body(10), theme.GOLD, 3),
            (rect.centerx, rect.y + 42), anchor="center")

    ec = (rect.centerx, rect.centery - 18)
    pr.circle(surf, ec, 34, theme.GOLD, width=2)
    pr.circle(surf, ec, 15, theme.GOLD)
    for dx, dy in ((-48, 0), (48, 0), (0, -48), (0, 48)):
        pr.line(surf, (ec[0] + dx * 0.55, ec[1] + dy * 0.55), (ec[0] + dx, ec[1] + dy), theme.GOLD, 2)

    _cover_title(surf, book.title, (rect.centerx, rect.bottom - 116), rect.w - 48)
    pr.blit(surf, pr.render_tracked(book.author.upper(), fonts.body(11),
            theme.oklch_to_rgb(0.75, 0.10, hue), 2), (rect.centerx, rect.bottom - 40), anchor="center")


def _cover_title(surf, title, center, maxw):
    font = fonts.display(40, bold=True)
    lines, line = [], ""
    for w in title.split():
        t = f"{line} {w}".strip()
        if font.size(t)[0] > pr.sv(maxw) and line:
            lines.append(line)
            line = w
        else:
            line = t
    if line:
        lines.append(line)
    y = center[1]
    for ln in lines[:2]:
        pr.draw_text(surf, ln, font, (0, 0, 0), (center[0] + 1, y + 2), center=True, alpha=120)  # shadow
        pr.draw_text(surf, ln, font, theme.CREAM, (center[0], y), center=True)
        y += 42


# ----------------------------------------------------------------------
# Cart thumbnail (§4b) — the miniature cover in a cart row
# ----------------------------------------------------------------------
def draw_thumb(surf, rect, book):
    rect = pygame.Rect(rect)
    hue = book.hue
    pr.round_rect(surf, rect, theme.oklch_to_rgb(0.20, 0.09, hue + 2), 3)
    pr.vgradient(surf, rect.inflate(-2, -2), theme.oklch_to_rgb(0.42, 0.13, hue),
                 theme.oklch_to_rgb(0.20, 0.09, hue + 2))
    pr.round_rect(surf, rect.inflate(-8, -8), (*theme.GOLD, 110), 2, width=1)
    # a ring emblem, centered, scaled to the cover — no microtext title (it can't
    # fit a small cover without spilling; callers show the title alongside).
    r = rect.w * 0.16
    pr.circle(surf, rect.center, r, theme.GOLD, width=1)
    pr.circle(surf, rect.center, r * 0.36, theme.GOLD)


# ----------------------------------------------------------------------
# Ledger panel (§12) — the cart's right-column summary card
# ----------------------------------------------------------------------
def draw_ledger(surf, ledger, wallet, rect, mouse):
    """Draw the ledger. Returns (proceed_rect_or_None, browse_rect) for clicks."""
    rect = pygame.Rect(rect)
    pr.glass_panel(surf, rect, radius=18, fill=theme.PANEL_BG2, alpha=theme.A_PANEL2)
    x, w, y = rect.x + 26, rect.w - 52, rect.y + 22
    pr.draw_text(surf, "Ledger", fonts.display(theme.Size.PANEL_HEAD), theme.CREAM, (x, y))
    y += 48

    def row(label, value, color, size=15):
        pr.draw_text(surf, label, fonts.body(size), theme.TEXT_MUTED, (x, y))
        pr.draw_text(surf, value, fonts.body(size), color, (x + w, y), anchor="topright")

    row("Subtotal", str(ledger.subtotal), theme.TEXT)
    y += 30
    row("Member's charm", f"-{ledger.discount}", theme.MEMBER_CHARM)
    y += 32
    pr.line(surf, (x, y), (x + w, y), theme.PANEL_BORDER, 1)
    y += 16
    pr.draw_text(surf, "Total", fonts.display(theme.Size.CARD_TITLE), theme.CREAM, (x, y))
    num = fonts.display(34, bold=True).render(str(ledger.total), True, theme.GOLD)
    pr.blit(surf, num, (x + w, y - 6), anchor="topright")
    coin_glyph(surf, (x + w - num.get_width() / theme.SCALE - 16, y + 12), 11)
    y += 54

    box = pygame.Rect(x, y, w, 92)
    pr.glass_panel(surf, box, radius=12, fill=theme.PANEL_BG, alpha=153)
    bx, bw, by = box.x + 14, box.w - 28, box.y + 14
    pr.draw_text(surf, "Star-purse", fonts.body(12), theme.TEXT_MUTED, (bx, by))
    pr.draw_text(surf, str(wallet.coins), fonts.body(12), theme.TEXT_MUTED, (bx + bw, by), anchor="topright")
    by += 26
    progress_bar(surf, (bx, by, bw, 8), ledger.total / max(1, wallet.coins))
    by += 20
    rem = ledger.remaining(wallet)
    pr.draw_text(surf, "Remaining after", fonts.body(12), theme.TEXT_MUTED, (bx, by))
    pr.draw_text(surf, f"{rem} coins", fonts.body(12, bold=True),
                 theme.GOLD if rem >= 0 else theme.BADGE_RED, (bx + bw, by), anchor="topright")
    y = box.bottom + 20

    affordable = ledger.affordable(wallet) and ledger.subtotal > 0
    pbtn = pygame.Rect(x, y, w, 52)
    if affordable:
        top, bot = theme.BTN_GOLD_TOP, theme.BTN_GOLD_BOT
        if pbtn.collidepoint(mouse):
            top = tuple(min(255, c + 16) for c in top)
            bot = tuple(min(255, c + 16) for c in bot)
        pr.drop_shadow(surf, pbtn, 12, offset=(0, 10), rgba=(90, 50, 10, 110))
        pr.vgradient(surf, pbtn, top, bot)
        pr.round_rect(surf, pbtn, (*theme.PANEL_BORDER, 255), 12, width=1)
        pr.draw_text(surf, "Proceed to the Desk", fonts.display(theme.Size.MENU, bold=True),
                     theme.BTN_GOLD_TEXT, pbtn.center, center=True)
    else:
        pr.alpha_rect(surf, pbtn, (*theme.BTN2_BG, 150), 12)
        pr.round_rect(surf, pbtn, (*theme.BTN2_BORDER, 150), 12, width=1)
        pr.draw_text(surf, "Proceed to the Desk", fonts.display(theme.Size.MENU),
                     theme.TEXT_FAINT, pbtn.center, center=True)
    y += 52 + 20
    pr.draw_text(surf, "Keep browsing the aisles", fonts.body(12), theme.TEXT_FAINT,
                 (rect.centerx, y), center=True)
    browse = pygame.Rect(rect.centerx - 90, y - 2, 180, 22)
    return (pbtn if affordable else None), browse


# ----------------------------------------------------------------------
# Book tooltip / info card (§5)
# ----------------------------------------------------------------------
def draw_tooltip(surf, book, anchor):
    """Hover popup anchored to a spine. Returns the 'Add' pill rect for clicks."""
    pr.glow(surf, anchor, 14, (*theme.STAR_RATING, 120))
    pr.circle(surf, anchor, 4, theme.STAR_RATING)

    W, H = 262, 196
    cx = min(anchor[0] + 18, theme.CANVAS_W - 52 - W)
    cy = max(24, min(anchor[1] - 30, theme.CANVAS_H - 40 - H))
    card = pygame.Rect(cx, cy, W, H)
    pr.glass_panel(surf, card, radius=14)

    x, y = card.x + 16, card.y + 14
    draw_pill(surf, (x, y), content.GENRES[book.genre].name, hue=book.hue)
    y += 26
    pr.draw_text(surf, book.title, fonts.display(theme.Size.CARD_TITLE), theme.CREAM, (x, y))
    y += 30
    pr.draw_text(surf, f"by {book.author}", fonts.body(12, italic=True), theme.TEXT_MUTED, (x, y))
    y += 22
    star_row(surf, (x, y), book.rating, 14)
    pr.draw_text(surf, f"{book.rating:.1f} · {book.pages} pp", fonts.body(12),
                 theme.TEXT_MUTED, (x + 92, y + 1))
    y += 24
    y = pr.draw_paragraph(surf, book.blurb_short, fonts.body(12), theme.TEXT_MUTED,
                          (x, y), W - 32, 17, max_lines=2) + 6
    pr.line(surf, (x, y), (card.right - 16, y), theme.PANEL_BORDER, 1)
    y += 12
    coin_value(surf, (x, y - 2), book.price, size=18, color=theme.GOLD)
    label = pr.render_tracked("ADD · E", fonts.body(10), theme.EYEBROW_GOLD, 1.5)
    lw = label.get_width() / theme.SCALE
    add = pygame.Rect(round(card.right - 16 - (lw + 16)), y - 3, round(lw + 16), 18)
    pr.round_rect(surf, add, (*theme.EYEBROW_GOLD, 160), 9, width=1)
    pr.blit(surf, label, add.center, anchor="center")
    return add


# ----------------------------------------------------------------------
# Receipt (§13) — the one light surface; rendered upright then rotated
# ----------------------------------------------------------------------
def _ellipsize(text, font, max_w_logical):
    if font.size(text)[0] <= pr.sv(max_w_logical):
        return text
    while text and font.size(text + "…")[0] > pr.sv(max_w_logical):
        text = text[:-1]
    return text + "…"


def draw_receipt(surf, cart, ledger, top_left, mouse):
    """Rotated paper receipt. Returns the (axis-aligned) Complete-Purchase rect."""
    W = 320
    H = 300 + 24 * max(1, len(cart.items))
    x, w = 24, W - 48

    # the Complete-Purchase button lives at a known y; compute its screen rect now
    btn_y = H - 92
    cta = pygame.Rect(top_left[0] + x, top_left[1] + btn_y, w, 50)
    hover = cta.collidepoint(mouse)

    sub = pygame.Surface((pr.sv(W), pr.sv(H)), pygame.SRCALPHA)
    pr.vgradient(sub, (0, 0, W, H), theme.RECEIPT_TOP, theme.RECEIPT_BOTTOM)

    y = 22
    pr.draw_text(sub, "Spines & Starlight", fonts.display(theme.Size.PANEL_HEAD, bold=True),
                 theme.RECEIPT_INK, (W / 2, y), center=True)
    y += 34
    pr.blit(sub, pr.render_tracked("EST. BENEATH THE STARS", fonts.body(10), theme.RECEIPT_FAINT, 3),
            (W / 2, y), anchor="center")
    y += 24
    pr.dashed_line(sub, (x, y), (x + w, y), theme.RECEIPT_FAINT)
    y += 14
    for b in cart.items:
        pr.draw_text(sub, _ellipsize(b.title, fonts.body(13), w - 40), fonts.body(13),
                     theme.RECEIPT_INK, (x, y))
        pr.draw_text(sub, str(b.price), fonts.body(13), theme.RECEIPT_INK, (x + w, y), anchor="topright")
        y += 24
    y += 6
    pr.dashed_line(sub, (x, y), (x + w, y), theme.RECEIPT_FAINT)
    y += 14
    pr.draw_text(sub, "Member's charm", fonts.body(13), theme.RECEIPT_FAINT, (x, y))
    pr.draw_text(sub, f"-{ledger.discount}", fonts.body(13), theme.RECEIPT_FAINT, (x + w, y), anchor="topright")
    y += 30
    pr.draw_text(sub, "Total Due", fonts.display(theme.Size.CARD_TITLE, bold=True), theme.RECEIPT_INK, (x, y))
    num = fonts.display(30, bold=True).render(str(ledger.total), True, theme.RECEIPT_INK)
    pr.blit(sub, num, (x + w - 22, y - 6), anchor="topright")
    _star(sub, (x + w - 9, y + 11), 8, theme.RECEIPT_INK, True)
    y += 54

    # Complete Purchase — violet gradient, NOT gold (§4)
    btn = pygame.Rect(x, btn_y, w, 50)
    top, bot = theme.CHECKOUT_BTN_TOP, theme.CHECKOUT_BTN_BOT
    if hover:
        top = tuple(min(255, c + 22) for c in top)
        bot = tuple(min(255, c + 22) for c in bot)
    pr.vgradient(sub, btn, top, bot)
    pr.round_rect(sub, btn, (*theme.PANEL_BORDER, 220), 11, width=1)
    pr.draw_text(sub, "Complete Purchase", fonts.display(theme.Size.MENU, bold=True),
                 theme.CREAM, btn.center, center=True)

    foot = pr.render_tracked("THANK YOU FOR READING", fonts.body(10), theme.RECEIPT_FAINT, 2)
    pr.blit(sub, foot, (W / 2 - 8, H - 26), anchor="center")
    _star(sub, (W / 2 + foot.get_width() / theme.SCALE / 2 + 6, H - 26 + 6), 5, theme.RECEIPT_FAINT, True)

    pr.drop_shadow(surf, (top_left[0], top_left[1], W, H), 12, offset=(0, 14), rgba=(0, 0, 0, 120))
    rot = pygame.transform.rotate(sub, 1.2)
    center = pr.sp((top_left[0] + W / 2, top_left[1] + H / 2))
    surf.blit(rot, rot.get_rect(center=center))
    return cta


# ----------------------------------------------------------------------
# Floating feedback (§16)
# ----------------------------------------------------------------------
class Pop:
    def __init__(self, x, y, text, color=theme.CREAM):
        self.x, self.y, self.text, self.color, self.life = x, y, text, color, 48

    def update(self):
        self.y -= 1.0
        self.life -= 1

    @property
    def dead(self):
        return self.life <= 0

    def draw(self, surf):
        pr.draw_text(surf, self.text, fonts.display(18, bold=True), self.color,
                     (self.x, self.y), center=True, alpha=max(0, min(255, self.life * 6)))
