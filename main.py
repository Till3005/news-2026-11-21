#!/usr/bin/env python3
"""THE WORLD DAILY - front page for Saturday, 21 November 2026.

Renders a broadsheet newspaper front page as a PNG using only the Python
standard library (struct + zlib). No network, no clock, no randomness:
the output is byte-for-byte deterministic.

Usage: MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib

W, H = 1600, 1000

# ---------------------------------------------------------------- palette --
PAPER = (247, 243, 232)
INK = (16, 16, 18)
GREY = (104, 102, 98)
RULE = (24, 24, 26)
RED = (156, 26, 26)
BLUE = (24, 62, 118)
GREEN = (30, 108, 66)
GOLD = (216, 166, 32)
WHITE = (248, 248, 244)

# ------------------------------------------------------------ tiny 5x7 font
# Row-major: 7 bytes per glyph, bit 4 = leftmost column.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1C, 0x12, 0x11, 0x11, 0x11, 0x12, 0x1C),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x11, 0x19, 0x15, 0x13, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x11, 0x0A, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "a": (0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F, 0x00),
    "b": (0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E, 0x00),
    "c": (0x00, 0x0F, 0x10, 0x10, 0x10, 0x0F, 0x00),
    "d": (0x01, 0x0F, 0x11, 0x11, 0x11, 0x0F, 0x00),
    "e": (0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0F, 0x00),
    "f": (0x06, 0x09, 0x08, 0x1C, 0x08, 0x08, 0x00),
    "g": (0x00, 0x0E, 0x11, 0x11, 0x0E, 0x01, 0x06),
    "h": (0x10, 0x1E, 0x11, 0x11, 0x11, 0x11, 0x00),
    "i": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x0E, 0x00),
    "j": (0x06, 0x02, 0x02, 0x02, 0x12, 0x0C, 0x00),
    "k": (0x10, 0x12, 0x14, 0x18, 0x14, 0x12, 0x00),
    "l": (0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E, 0x00),
    "m": (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x00),
    "n": (0x00, 0x00, 0x1E, 0x11, 0x11, 0x11, 0x00),
    "o": (0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E, 0x00),
    "p": (0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10),
    "q": (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x01),
    "r": (0x00, 0x00, 0x1E, 0x10, 0x10, 0x10, 0x00),
    "s": (0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E, 0x00),
    "t": (0x08, 0x08, 0x1C, 0x08, 0x08, 0x09, 0x06),
    "u": (0x00, 0x11, 0x11, 0x11, 0x13, 0x0D, 0x00),
    "v": (0x00, 0x11, 0x11, 0x11, 0x0A, 0x04, 0x00),
    "w": (0x00, 0x11, 0x11, 0x15, 0x15, 0x0A, 0x00),
    "x": (0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x00),
    "y": (0x00, 0x11, 0x11, 0x11, 0x0A, 0x04, 0x04),
    "z": (0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F, 0x00),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    "'": (0x06, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    "-": (0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "%": (0x11, 0x13, 0x02, 0x04, 0x08, 0x19, 0x11),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "*": (0x00, 0x15, 0x0E, 0x1F, 0x0E, 0x15, 0x00),
    "#": (0x0A, 0x1F, 0x0A, 0x0A, 0x1F, 0x0A, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    "<": (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    ">": (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    "|": (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "[": (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    "]": (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    "£": (0x0C, 0x12, 0x10, 0x1E, 0x10, 0x12, 0x0D),
    "\x95": (0x00, 0x00, 0x04, 0x0E, 0x04, 0x00, 0x00),
}

# --------------------------------------------------------- pictogram art ---
# 12x12 character grids; '.' = transparent (paper shows through).
PICO_PALETTE = {
    "K": INK,
    "R": RED,
    "B": BLUE,
    "G": GREEN,
    "Y": GOLD,
    "W": WHITE,
    "g": GREY,
}

PICO = {
    # COP31: the globe, blue oceans, green land
    "globe": (
        "....BBBB....",
        "..BBBBBBBB..",
        ".BBGGGBBBBB.",
        "BGGGGGBBBBBB",
        "BGGGBBBBBBGB",
        "BBBBBBGGGGBB",
        "BGBBBBGGGGBB",
        "BGGBBBBBBBBB",
        "BGGBBBBBGGBB",
        ".BBBBBBGGBB.",
        "..BBBBBBBB..",
        "....BBBB....",
    ),
    # GTA VI: a gamepad with dpad, red buttons and gold trigger
    "pad": (
        "............",
        ".KKKKKKKKKK.",
        ".KKWKKKKRKK.",
        "KKWWWKKKRRKK",
        ".KKWKKKKYKK.",
        ".KKKKKKKKKK.",
        ".KK......KK.",
        "............",
        "............",
        "............",
        "............",
        "............",
    ),
    # F1: side view - rear wing left, nose right, big wheels
    "f1car": (
        ".KKK........",
        ".KKK..KWWKKK",
        "KKKKKKKKKKKK",
        "..KKK...KKK.",
        "..KKK...KKK.",
        "..KKK...KKK.",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
    ),
    # Ukraine: flag over falling snow
    "flag": (
        "KKKKKKKKKKKK",
        "KBBBBBBBBBBK",
        "KBBBBBBBBBBK",
        "KBBBBBBBBBBK",
        "KYYYYYYYYYYK",
        "KYYYYYYYYYYK",
        "KYYYYYYYYYYK",
        "KKKKKKKKKKKK",
        " W    W    W",
        "   W     W  ",
        "............",
        "............",
    ),
    # Tennis: racket and ball
    "racket": (
        "..KKKKKKK...",
        "..KWWWWWK...",
        "..KWWWWWK...",
        "..KWKKKWK...",
        "..KWWWWWK...",
        "...KKKKK....",
        ".....KK.....",
        ".....KK.....",
        ".....KK.....",
        "..YYY.......",
        "..YYY.......",
        "............",
    ),
    # Trade: container ship on the waves
    "ship": (
        "......K.....",
        "......K.....",
        "..BB.RR.GG..",
        "..BB.RR.GG..",
        "..BB.RR.GG..",
        "KKKKKKKKKKKK",
        ".KKKKKKKKKK.",
        ".KKKKKKKKKK.",
        "..KKKKKKKK..",
        "...KKKKKK...",
        "BBBB..BBBB..",
        "..BBB..BBB..",
    ),
    # US politics: ballot paper dropping into a ballot box
    "vote": (
        "....KWWK....",
        "....KWRK....",
        "....KWWK....",
        "....KKKK....",
        "............",
        ".KKKKKKKKKK.",
        ".K........K.",
        ".K........K.",
        ".K........K.",
        ".KKKKKKKKKK.",
        "............",
        "............",
    ),
    # Science: rising emissions bars, red at the top
    "chart": (
        "........RR..",
        "........RR..",
        "........RR..",
        "........RR..",
        ".....gg.RR..",
        ".....gg.RR..",
        ".....gg.RR..",
        "..gg.gg.RR..",
        "..gg.gg.RR..",
        "..gg.gg.RR..",
        "KKKKKKKKKKKK",
        "............",
    ),
    # Travel: airliner silhouette, nose to the right
    "plane": (
        ".........KK.",
        ".K.KWKWKWKKK",
        "KKKKWKWKWKKK",
        "...KKK...KK.",
        "...KKK......",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
        "............",
    ),
    # Culture: the golden trophy
    "trophy": (
        "..YYYYYYYY..",
        ".YYYYYYYYYY.",
        ".YYWYYYYYYY.",
        ".YYYYYYYYYY.",
        "..YYYYYYYY..",
        "...YYYYYY...",
        "....YYYY....",
        ".....YY.....",
        "...YYYYYY...",
        "..KKKKKKKK..",
        "..KKKKKKKK..",
        "............",
    ),
}

# --------------------------------------------------------------- stories ---
# All items are anchored to Saturday, 21 November 2026 (see design-notes.md).
STORIES = {
    "cop": {
        "tag": "CLIMATE - ANTALYA",
        "head": "COP31 TALKS RUN OVERTIME AS MINISTERS FIGHT OVER FINAL CLIMATE TEXT",
        "body": ("Negotiators in Antalya worked through the night on a deal to phase "
                 "down fossil fuels, with a closing plenary expected on Saturday, "
                 "21 November. Money for poorer nations remained the last sticking "
                 "point as the summit blew past its deadline."),
        "pico": "globe",
    },
    "gta": {
        "tag": "GAMES - LOS ANGELES",
        "head": "GTA VI SHATTERS ENTERTAINMENT RECORDS IN LAUNCH WEEKEND",
        "body": ("Two days after its release on Thursday, 19 November, Rockstar's "
                 "Grand Theft Auto VI passed a reported $1bn in sales, set online "
                 "play records and drew overnight queues worldwide. Analysts called "
                 "it the biggest launch in entertainment history."),
        "pico": "pad",
    },
    "f1": {
        "tag": "SPORT - LAS VEGAS",
        "head": "TITLE RIVALS MEET UNDER THE NEON LIGHTS IN LAS VEGAS GP TONIGHT",
        "body": ("Formula One's new engine era hits the Strip on Saturday night, "
                 "with the title fight neck and neck and Cadillac chasing its best "
                 "result on the street course."),
        "pico": "f1car",
    },
    "ukr": {
        "tag": "WAR IN UKRAINE - KYIV",
        "head": "KYIV BRACES FOR FIFTH WARTIME WINTER AS STRIKES DEEPEN BLACKOUTS",
        "body": ("Russian strikes on the power grid left cities in rolling "
                 "blackouts as temperatures fell. Officials said on Friday that "
                 "talks remain stalled."),
        "pico": "flag",
    },
    "atp": {
        "tag": "TENNIS - TURIN",
        "head": "ALCARAZ AND SINNER HEADLINE SATURDAY SEMIS AT ATP FINALS",
        "body": ("The world's top two were kept apart in the last-four draw in Turin, "
                 "with the champion to be crowned on Sunday. Sinner chases a third "
                 "straight title at home."),
        "pico": "racket",
    },
    "apec": {
        "tag": "TRADE - SHENZHEN",
        "head": "APEC LEADERS CLOSE SHENZHEN SUMMIT WITH PLEDGE ON OPEN TRADE",
        "body": ("Pacific-rim leaders ended their annual meeting in southern China "
                 "with a promise to keep supply chains open despite tariff and chip "
                 "frictions. It is the third APEC hosted by China."),
        "pico": "ship",
    },
    "us": {
        "tag": "US POLITICS - WASHINGTON",
        "head": "HOUSE CONTROL STILL UNDECIDED THREE WEEKS AFTER MIDTERMS",
        "body": ("Recounts and court fights in a handful of districts kept the House "
                 "up for grabs after the 3 November elections, with both parties "
                 "warning of weeks more litigation."),
        "pico": "vote",
    },
    "co2": {
        "tag": "SCIENCE - EXETER",
        "head": "CARBON BUDGET SHOWS EMISSIONS AT NEW HIGH, 1.5C POOL NEARLY SPENT",
        "body": ("Researchers released the annual Global Carbon Budget during the "
                 "COP31 summit: fossil CO2 rose again in 2026 and the 1.5C carbon "
                 "budget is nearly spent."),
        "pico": "chart",
    },
}

BRIEFS = [
    ("plane", "TRAVEL", "Airports brace for a record Thanksgiving rush before "
     "Thursday's holiday; the TSA expects 18m+ passengers."),
    ("trophy", "CULTURE", "GTA VI tops The Game Awards nominations out this "
     "week; the December ceremony follows in Los Angeles."),
]

# ------------------------------------------------------------ PNG encoder --

def write_png(path, w, h, rgb):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    stride = w * 3
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
        f.write(chunk(b"IEND", b""))


# ----------------------------------------------------------------- canvas --

class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.data = bytearray(bytes(bg) * (w * h))

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.data[i:i + 3] = bytes(c)

    def fill(self, x0, y0, x1, y1, c):
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.w - 1, x1), min(self.h - 1, y1)
        if x1 < x0 or y1 < y0:
            return
        row = bytes(c) * (x1 - x0 + 1)
        for y in range(y0, y1 + 1):
            i = (y * self.w + x0) * 3
            self.data[i:i + len(row)] = row

    def hline(self, x0, x1, y, c, thick=1):
        self.fill(x0, y, x1, y + thick - 1, c)

    def vline(self, x, y0, y1, c, thick=1):
        self.fill(x, y0, x + thick - 1, y1, c)


def grain(cv, seed=20261121):
    """Subtle deterministic paper texture."""
    s = seed
    d = cv.data
    for i in range(0, len(d), 3):
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        n = ((s >> 16) & 7) - 3
        if n:
            for k in (0, 1, 2):
                v = d[i + k] + n
                if 0 <= v <= 255:
                    d[i + k] = v


def text_w(s, scale):
    return max(0, len(s) * 6 - 1) * scale


def draw_text(cv, x, y, s, scale, color, bold=0):
    for ch in s:
        g = FONT.get(ch, FONT["?"])
        for r in range(7):
            bits = g[r]
            if not bits:
                continue
            yy = y + r * scale
            for c in range(5):
                if bits & (1 << (4 - c)):
                    xx = x + c * scale
                    cv.fill(xx, yy, xx + scale - 1, yy + scale - 1, color)
        if bold:
            for r in range(7):
                bits = g[r]
                for c in range(5):
                    if bits & (1 << (4 - c)):
                        xx = x + c * scale + bold
                        cv.fill(xx, y + r * scale, xx + scale - 1,
                                y + r * scale + scale - 1, color)
        x += 6 * scale


def wrap(s, scale, maxw):
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, scale, color, maxw, lead, bold=0):
    for line in wrap(s, scale, maxw):
        draw_text(cv, x, y, line, scale, color, bold)
        y += lead
    return y


def draw_kicker(cv, x, y, tag, scale=2):
    draw_text(cv, x, y, tag, scale, RED, bold=scale // 2)
    cv.hline(x, x + text_w(tag, scale) - scale, y + 8 * scale + 1, RED, 2)
    return y + 8 * scale + 1 + 2


def draw_pico(cv, x, y, key, scale):
    art = PICO[key]
    for r, row in enumerate(art):
        for c, ch in enumerate(row):
            col = PICO_PALETTE.get(ch)
            if col:
                cv.fill(x + c * scale, y + r * scale,
                        x + c * scale + scale - 1, y + r * scale + scale - 1, col)
    return len(art) * scale, max(len(r) for r in art) * scale


# ----------------------------------------------------------------- layout --

MARGIN = 40
COLW = 745
GUT = 30
CELLW = 490
CELLG = 24


def masthead(cv):
    x0, x1 = MARGIN, W - MARGIN
    cv.hline(x0, x1, 40, RULE, 5)
    y = 56
    draw_text(cv, x0, y, "LATE FINAL EDITION", 2, GREY)
    right = "WORLD EDITION - PRICE $2.50"
    draw_text(cv, x1 - text_w(right, 2), y, right, 2, GREY)

    title = "THE WORLD DAILY"
    tw = text_w(title, 10)
    draw_text(cv, (W - tw) // 2, 76, title, 10, INK, bold=2)

    cv.hline(x0, x1, 150, RULE, 3)
    cv.hline(x0, x1, 156, RULE, 1)

    y = 164
    draw_text(cv, x0, y, "VOL. CXLII - No. 32,587", 2, GREY)
    motto = "INTELLIGENCE FOR A CHANGING WORLD"
    draw_text(cv, (W - text_w(motto, 2)) // 2, y, motto, 2, GREY)
    draw_text(cv, x1 - text_w("FOUNDED 1884", 2), y, "FOUNDED 1884", 2, GREY)

    date = "Saturday, 21 November 2026"
    dw = text_w(date, 4)
    draw_text(cv, (W - dw) // 2, 182, date, 4, INK, bold=1)

    cv.hline(x0, x1, 216, RULE, 3)
    cv.hline(x0, x1, 222, RULE, 1)


def lead_story(cv, x, y, story, pico_scale=7):
    ph, _ = draw_pico(cv, x + COLW - 12 * pico_scale, y, story["pico"], pico_scale)
    ky = draw_kicker(cv, x, y, story["tag"])
    hy = ky + 10
    hy = draw_para(cv, x, hy, story["head"], 4, INK, COLW - 12 * pico_scale - 24,
                   30, bold=1)
    by = max(hy + 8, y + ph + 12)
    draw_para(cv, x, by, story["body"], 2, INK, COLW, 18)


def grid_story(cv, x, y, story, pico_scale=3):
    draw_pico(cv, x + CELLW - 12 * pico_scale, y, story["pico"], pico_scale)
    ky = draw_kicker(cv, x, y, story["tag"], 2)
    hy = ky + 8
    hy = draw_para(cv, x, hy, story["head"], 2, INK, CELLW - 12 * pico_scale - 8,
                   24, bold=1)
    draw_para(cv, x, hy + 4, story["body"], 2, INK, CELLW, 18)


def briefs(cv, y):
    x = MARGIN
    draw_text(cv, x, y + 6, "IN BRIEF", 2, RED, bold=1)
    yy = y + 26
    for pkey, tag, item in BRIEFS:
        draw_pico(cv, x, yy - 2, pkey, 2)
        tx = x + 32
        draw_text(cv, tx, yy, tag + ":", 2, RED, bold=1)
        lines = wrap(item, 2, W - MARGIN - (tx + text_w(tag + ":", 2) + 10))
        draw_para(cv, tx + text_w(tag + ":", 2) + 10, yy, item, 2, INK,
                  W - MARGIN - (tx + text_w(tag + ":", 2) + 10), 24)
        yy += 24 * len(lines)
    return yy


def footer(cv, y):
    x0, x1 = MARGIN, W - MARGIN
    cv.hline(x0, x1, y, RULE, 3)
    cv.hline(x0, x1, y + 6, RULE, 1)
    line = ("THE WORLD DAILY - PAGE ONE - EVERY ITEM AS REPORTED ON "
            "SATURDAY, 21 NOVEMBER 2026 - LATE FINAL")
    draw_text(cv, (W - text_w(line, 2)) // 2, y + 16, line, 2, GREY)


def render():
    cv = Canvas(W, H, PAPER)
    grain(cv)
    masthead(cv)

    # Lead pair: COP31 (world) and GTA VI (games/culture)
    ly = 236
    lead_story(cv, MARGIN, ly, STORIES["cop"])
    lead_story(cv, MARGIN + COLW + GUT, ly, STORIES["gta"])
    cv.vline(MARGIN + COLW + GUT // 2, ly, 430, RULE, 1)

    # Double rule between leads and the 6-story grid
    y = 470
    cv.hline(MARGIN, W - MARGIN, y, RULE, 2)
    cv.hline(MARGIN, W - MARGIN, y + 6, RULE, 1)

    # Grid: two rows of three
    keys = ["f1", "ukr", "atp", "apec", "us", "co2"]
    gy = y + 22
    for i, key in enumerate(keys):
        row, col = divmod(i, 3)
        gx = MARGIN + col * (CELLW + CELLG)
        grid_story(cv, gx, gy + row * 180, STORIES[key])
    cv.hline(MARGIN, W - MARGIN, gy + 170, GREY, 1)
    for col in (1, 2):
        gx = MARGIN + col * (CELLW + CELLG) - CELLG // 2
        cv.vline(gx, gy, gy + 348, GREY, 1)

    by = briefs(cv, gy + 360)
    footer(cv, by + 10)

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    write_png(path, W, H, cv.data)
    print("wrote", path)


if __name__ == "__main__":
    render()
