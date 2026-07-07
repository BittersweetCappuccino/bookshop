"""
Spines & Starlight — audio.

A soft, whimsical procedural score (no audio files): a music-box melody of
bell-like tones over gentle pad chords in a warm major key, plus light chimes on
add / purchase. One persistent loop carries across every scene and respects the
muted state. The track is built on a background thread so startup never blocks;
playback fades in once it's ready. All playback is a safe no-op until then.
"""

import array
import math
import threading

import pygame

_music = None
_ding = None
_cash = None
_muted = False
_ready = False

_MUSIC_VOL = 0.5
_SR = 44100

# Note frequencies (Hz)
_C3, _F2, _G2, _A2 = 130.81, 87.31, 98.00, 110.00
_C4, _D4, _E4, _F3, _A3, _G3, _B3 = 261.63, 293.66, 329.63, 174.61, 220.00, 196.00, 246.94
_B4, _C5, _D5, _E5, _F5, _G5, _A5, _C6 = 493.88, 523.25, 587.33, 659.25, 698.46, 783.99, 880.00, 1046.50


# ----------------------------------------------------------------------
# Procedural synthesis
# ----------------------------------------------------------------------
def _make_music():
    bpm = 92
    beat = 60.0 / bpm
    total_beats = 16
    n = int(_SR * total_beats * beat)
    buf = [0.0] * n

    # I - vi - IV - V in C major: (mid pad triad, low bass root)
    prog = [
        ([_C4, _E4, 392.00], _C3),   # C   (C4 E4 G4)
        ([_A3, _C4, _E4], _A2),      # Am
        ([_F3, _A3, _C4], _F2),      # F
        ([_G3, _B3, _D4], _G2),      # G
    ]
    # music-box melody: (freq | None rest, beats)
    melody = [
        (_E5, 1), (_G5, 1), (_C6, 1), (_G5, 0.5), (_E5, 0.5),
        (_A5, 1), (_E5, 1), (_C5, 1), (_D5, 1),
        (_F5, 1), (_A5, 1), (_C6, 0.5), (_A5, 0.5), (_F5, 1),
        (_G5, 1), (_D5, 1), (_B4, 1), (_D5, 1),
    ]

    def add(start_s, freq, dur_s, kind):
        i0 = int(start_s * _SR)
        for s in range(int(dur_s * _SR)):
            t = s / _SR
            if kind == "mbox":                       # bell: fast attack, long decay
                env = math.exp(-t * 3.0)
                if t < 0.004:
                    env *= t / 0.004
                val = (math.sin(2 * math.pi * freq * t)
                       + 0.5 * math.sin(4 * math.pi * freq * t)
                       + 0.22 * math.sin(6 * math.pi * freq * t)) * env * 0.16
            elif kind == "pad":                      # soft sustained chord
                a, r = 0.14, 0.5
                env = t / a if t < a else (max(0.0, (dur_s - t) / r) if t > dur_s - r else 1.0)
                val = (math.sin(2 * math.pi * freq * t)
                       + 0.28 * math.sin(4 * math.pi * freq * t)) * env * 0.05
            else:                                     # gentle bass
                env = math.exp(-t * 1.4)
                if t < 0.01:
                    env *= t / 0.01
                val = math.sin(2 * math.pi * freq * t) * env * 0.11
            buf[(i0 + s) % n] += val                  # wrap tails for a seamless loop

    for b, (triad, bassf) in enumerate(prog):
        start = b * 4 * beat
        for f in triad:
            add(start, f, 4 * beat * 0.98, "pad")
        add(start, bassf, 4 * beat * 0.9, "bass")

    t = 0.0
    for note, beats in melody:
        if note:
            add(t, note, min(beats * beat + 0.7, 1.1), "mbox")
        t += beats * beat

    peak = max(1e-6, max(abs(v) for v in buf))
    scale = 0.72 / peak
    out = array.array("h", [0] * (n * 2))
    for i in range(n):
        v = int(max(-1.0, min(1.0, buf[i] * scale)) * 18000)
        out[2 * i] = v
        out[2 * i + 1] = v
    return pygame.mixer.Sound(buffer=out.tobytes())


def _make_chime(freqs, dur=0.2):
    seg = int(_SR * dur)
    buf = array.array("h", [0] * (seg * len(freqs) * 2))
    pos = 0
    for f in freqs:
        for s in range(seg):
            t = s / _SR
            env = math.exp(-t * 7.0)                  # soft bell
            val = (math.sin(2 * math.pi * f * t) + 0.4 * math.sin(4 * math.pi * f * t)) * env * 0.28
            v = int(max(-1.0, min(1.0, val)) * 22000)
            buf[(pos + s) * 2] = v
            buf[(pos + s) * 2 + 1] = v
        pos += seg
    return pygame.mixer.Sound(buffer=buf.tobytes())


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------
def _build_and_play():
    global _music, _ding, _cash, _ready
    try:
        music = _make_music()
        ding = _make_chime([_G5, _C6])
        cash = _make_chime([_C5, _E5, _G5, _C6], 0.14)
    except pygame.error:
        return
    _music, _ding, _cash = music, ding, cash
    _ready = True
    _music.set_volume(0.0 if _muted else _MUSIC_VOL)
    _music.play(loops=-1)


def init(muted=False):
    """Init the mixer and build/start the score on a background thread."""
    global _muted
    _muted = muted
    try:
        pygame.mixer.init(frequency=_SR, size=-16, channels=2)
    except pygame.error:
        return
    threading.Thread(target=_build_and_play, daemon=True).start()


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
