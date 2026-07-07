"""
Spines & Starlight — audio.

Ports the prototype's procedural cozy loop and chimes (bookstore.py `make_music`
/ `make_chime`) so no audio files are needed. The music is one persistent loop
that carries across every scene; chimes fire on add / purchase. Everything
respects the muted state. All playback is a safe no-op until init() succeeds.
"""

import array
import math

import pygame

_music = None
_ding = None
_cash = None
_muted = False
_ready = False

_MUSIC_VOL = 0.55


# ----------------------------------------------------------------------
# Procedural synthesis (ported from bookstore.py)
# ----------------------------------------------------------------------
def _make_music():
    sr, bpm = 44100, 72
    beat = 60.0 / bpm
    prog = [
        [220.00, 261.63, 329.63],   # Am
        [174.61, 220.00, 261.63],   # F
        [196.00, 246.94, 293.66],   # G
        [261.63, 329.63, 392.00],   # C
    ]
    seq = []
    for chord in prog:
        for n in (chord[0], chord[1], chord[2], chord[1]):
            seq.append((n, beat))
    n_samples = int(sr * sum(d for _, d in seq))
    buf = array.array("h", [0] * (n_samples * 2))

    def env(t, dur):
        a, r = 0.02, 0.25
        if t < a:
            return t / a
        if t > dur - r:
            return max(0.0, (dur - t) / r)
        return 1.0

    pos = 0
    for i, (freq, dur) in enumerate(seq):
        dur_s = int(sr * dur)
        bass = prog[(i // 4) % 4][0] / 2.0
        for s in range(dur_s):
            t = s / sr
            e = env(t, dur)
            lead = math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(2 * math.pi * freq * 2 * t)
            b = 0.5 * math.sin(2 * math.pi * bass * t)
            v = int(max(-1, min(1, (lead * 0.16 * e + b * 0.14) * 0.8)) * 26000)
            idx = (pos + s) * 2
            buf[idx] = v
            buf[idx + 1] = v
        pos += dur_s
    return pygame.mixer.Sound(buffer=buf.tobytes())


def _make_chime(freqs, dur=0.18):
    sr = 44100
    seg = int(sr * dur)
    buf = array.array("h", [0] * (seg * len(freqs) * 2))
    pos = 0
    for f in freqs:
        for s in range(seg):
            t = s / sr
            e = max(0.0, 1 - t / dur)
            v = int(math.sin(2 * math.pi * f * t) * 0.3 * e * 26000)
            idx = (pos + s) * 2
            buf[idx] = v
            buf[idx + 1] = v
        pos += seg
    return pygame.mixer.Sound(buffer=buf.tobytes())


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------
def init(muted=False):
    """Build the sounds and start the music loop. Safe if audio is unavailable."""
    global _music, _ding, _cash, _muted, _ready
    _muted = muted
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
    except pygame.error:
        return
    try:
        _music = _make_music()
        _ding = _make_chime([659, 880])
        _cash = _make_chime([523, 659, 784, 1047], 0.13)
    except pygame.error:
        return
    _ready = True
    _music.set_volume(0.0 if muted else _MUSIC_VOL)
    _music.play(loops=-1)


def set_muted(muted):
    global _muted
    _muted = muted
    if _music:
        _music.set_volume(0.0 if muted else _MUSIC_VOL)


def play_ding():
    if _ready and not _muted:
        _ding.play()


def play_cash():
    if _ready and not _muted:
        _cash.play()
