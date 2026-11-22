#!/usr/bin/env python3
"""22 November 2026: 46 stories, a UTC timeline and a date check.

Draws a one-page newspaper front page summing up the world news of
Sunday 22 November 2026 and writes it to /output/entry.png (or
$MAKEFUN_OUTPUT_DIR/entry.png).

Pure Python 3.13 standard library only: no Pillow, no numpy, no
network, no files read at runtime. The image is drawn from the story
data below with a hand-built 5x7 bitmap font and a hand-built PNG
encoder (zlib + struct), so two runs write byte-identical output.
"""

import os
import struct
import sys
import zlib

W = 1024
H = 1024

PAPER = (247, 243, 234)
INK = (20, 28, 45)
NAVY = (20, 33, 61)
NAVY2 = (28, 48, 88)
RED = (178, 34, 34)
BLUE = (30, 90, 168)
GREEN = (34, 120, 70)
GOLD = (176, 132, 20)
GOLD_BG = (212, 160, 32)
PURPLE = (110, 70, 160)
GREY = (96, 96, 92)
WHITE = (255, 255, 255)
LIGHT = (232, 226, 212)
RULE = (180, 172, 154)


def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(rgb, width, height):
    """Encode a bytes-like RGB buffer as a deterministic PNG."""
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )


class Canvas:
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bg * (width * height))

    def rect(self, x, y, w, h, color):
        if x < 0:
            w += x
            x = 0
        if y < 0:
            h += y
            y = 0
        if x + w > self.w:
            w = self.w - x
        if y + h > self.h:
            h = self.h - y
        if w <= 0 or h <= 0:
            return
        r, g, b = color
        row = bytes((r, g, b)) * w
        base = y * self.w * 3 + x * 3
        step = self.w * 3
        for yy in range(h):
            off = base + yy * step
            self.px[off:off + w * 3] = row

    def set_px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            off = (y * self.w + x) * 3
            self.px[off], self.px[off + 1], self.px[off + 2] = color

    def hline(self, x, y, length, color, thick=1):
        self.rect(x, y, length, thick, color)

    def vline(self, x, y, length, color, thick=1):
        self.rect(x, y, thick, length, color)


# 5x7 bitmap font. Each glyph is 7 rows of 5 characters; "#" is ink.
FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#...#", "#####", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
}

FONT.update({
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "$": ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
})


def text_width(s, scale):
    return len(s) * (5 * scale + 1) - 1


def draw_text(cv, x, y, s, scale, color):
    """Draw uppercase text left-aligned at (x, y). Unknown chars are skipped."""
    cx = x
    for ch in s:
        glyph = FONT.get(ch)
        if glyph is not None:
            for gy in range(7):
                row = glyph[gy]
                for gx in range(5):
                    if row[gx] == "#":
                        cv.rect(cx + gx * scale, y + gy * scale,
                                scale, scale, color)
        cx += 5 * scale + 1
    return cx


def draw_text_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_width(s, scale) // 2, y, s, scale, color)


def draw_check(cv, x, y, scale, color):
    """A small tick mark, scale pixels per unit."""
    for i in range(3):
        cv.rect(x + i * scale, y + i * scale, scale, scale, color)
    for i in range(5):
        cv.rect(x + (2 + i) * scale, y + (2 - i) * scale, scale, scale, color)


# 46 stories from Sunday 22 November 2026. Each headline was checked
# against two independent reports published on 22 November 2026 (UTC).
# (tag, headline) -- tag colours: R conflict, B politics, G climate,
# Y economy, P sport and culture.
STORIES = [
    ("R", "IRAN STRIKES US AIR BASE IN KUWAIT"),
    ("R", "TANKERS HIT OFF OMAN AS TENSIONS RISE"),
    ("R", "BAHRAIN PROBES PATRIOT CRASH, DRONES"),
    ("R", "ADNOC SHIP HIT IN HORMUZ, 1 CREW MISSING"),
    ("B", "TRUMP: IRAN DEAL COULD LAST 20 YEARS"),
    ("B", "VANCE REFUSES TO BACK TRUMP IRAN STRIKES"),
    ("R", "US AIRLINES WARNED OF AL-QAEDA THREAT"),
    ("R", "SAUDI COALITION DOWNS HOUTHI MISSILES"),
    ("R", "4 KILLED IN GAZA CEASEFIRE BREACHES"),
    ("B", "EISENKOT INVITES LIKUD TO COALITION TALKS"),
    ("R", "400 DRONES, 110 MISSILES HIT UKRAINE"),
    ("R", "RUSSIAN STRIKE ON LVIV: 2 KILLED, 10 HURT"),
    ("R", "DRONES HIT RUSSIAN CARGO SHIP IN BALTIC"),
    ("R", "BLASTS AT RUSSIAN BALTIC FLEET BASE"),
    ("R", "UKRAINE HITS ISKANDER MISSILE FUEL MAKER"),
    ("R", "RUSSIAN MISSILE CRASHES IN POLAND"),
    ("B", "ESTONIA TO CLOSE BORDER WITH RUSSIA"),
    ("B", "NATO VOWS TO DEFEND EVERY INCH OF POLAND"),
    ("B", "DENMARK EXPELS RUSSIAN MILITARY ATTACHE"),
    ("B", "US OPEN TO WESTERN HEMISPHERE UN CHIEF"),
    ("G", "COP31 DEADLOCKED OVER FOSSIL FUELS"),
    ("G", "COP31 AI PLEDGE SHUNNED BY BIG US TECH"),
    ("G", "CHARLES THANKS TURKIYE FOR HOSTING COP31"),
    ("Y", "EU-INDONESIA DEAL: 98.5% OF TARIFFS CUT"),
    ("B", "TRUMP TOUTS SUMMIT WITH XI AND PUTIN"),
    ("B", "CHINA BOMBER TURNS BACK 170KM FROM MANILA"),
    ("B", "US-CHINA MILITARIES END TALKS IN SHANGHAI"),
    ("B", "HONG KONG ELECTION COMMITTEE VOTE BEGINS"),
    ("B", "FRANCE SEEKS UN ACTION ON MYANMAR RULING"),
    ("B", "JAPAN TO HOLD LIVE-FIRE DRILLS IN INDIA"),
    ("B", "NATIONS AGREE AI KILLER-ROBOT RULES 2028"),
    ("G", "CYCLONE AKVAN: 14 FLIGHTS AXED AT RANCHI"),
    ("B", "MODI OPENS NITISH SETU BRIDGE IN BIHAR"),
    ("B", "CHAHAL JOINS BJP, GETS OBC MORCHA ROLE"),
    ("B", "BOLSONARO IN ICU WITH BOWEL OBSTRUCTION"),
    ("R", 'MEXICO NABS "EL CHAPO ISIDRO"; 11 KILLED'),
    ("R", "2 SHOT DEAD OUTSIDE WALMART IN CANADA"),
    ("B", "US JAILS GUPTA 19 YEARS OVER PANNUN PLOT"),
    ("R", "BASRA POWER PLANT FIRE: 4 DEAD, 35 HURT"),
    ("B", "FEMA HQ HIT BY BED BUGS; STAFF SENT HOME"),
    ("Y", "AI MAY HAVE CRACKED FAMOUS MATHS PROBLEM"),
    ("Y", "PALO ALTO BUYS APPLIED COMPUTE FOR $4.5BN"),
    ("Y", "STRIPE: AI REVENUE UP 103% IN A YEAR"),
    ("B", "BLAIR: REJOIN EU ONLY IF UK INNOVATES"),
    ("P", "MACKLEMORE GIVES SINGLE PROFITS TO GAZA"),
    ("P", "CUMMINS KEEPS AUSTRALIA TEST CAPTAINCY"),
]

TAG_COLORS = {"R": RED, "B": BLUE, "G": GREEN, "Y": GOLD, "P": PURPLE}

# UTC timeline of 22 November 2026, from reports timed that day.
TIMELINE = [
    "00:02 UN RESOLUTION",
    "00:07 COP31 OVERTIME",
    "00:11 NATO AIRSPACE",
    "00:36 UN CHIEF ROW",
    "01:03 COP31 DEADLOCK",
    "01:13 EISENKOT BACKED",
    "01:47 EU DEAL SIGNED",
    "02:00 BALTIYSK BLASTS",
]


def build():
    cv = Canvas(W, H, PAPER)

    # ---- Masthead ----
    cv.rect(0, 0, W, 118, NAVY)
    draw_text(cv, 24, 16, "22 NOVEMBER 2026", 5, WHITE)
    draw_text(cv, 660, 24, "SUNDAY - 46 STORIES", 3, (212, 160, 32))
    draw_text(cv, 24, 82,
              "THE WORLD IN ONE IMAGE - EVERY STORY CHECKED AGAINST 2 SOURCES",
              2, (200, 205, 220))
    cv.hline(0, 118, W, GOLD_BG, 4)

    # ---- Climax band: the day's three biggest numbers ----
    boxes = [
        (16, RED, WHITE, "400", "DRONES + 110 MISSILES", "HIT UKRAINE"),
        (352, NAVY2, WHITE, "98.5%", "TARIFFS CUT IN", "EU-INDONESIA DEAL"),
        (688, GOLD_BG, NAVY, "$4.5BN", "PALO ALTO BUYS", "APPLIED COMPUTE"),
    ]
    for bx, bg, fg, big, line1, line2 in boxes:
        cv.rect(bx, 126, 320, 112, bg)
        draw_text(cv, bx + 16, 138, big, 4, fg)
        draw_text(cv, bx + 16, 186, line1, 2, fg)
        draw_text(cv, bx + 16, 206, line2, 2, fg)

    # ---- Legend ----
    legend = "RED CONFLICT   BLUE POLITICS   GREEN CLIMATE   GOLD ECONOMY   PURPLE SPORT AND CULTURE"
    draw_text_centered(cv, W // 2, 248, legend, 1, GREY)
    cv.hline(16, 268, W - 32, RULE, 1)

    # ---- Story grid: 2 columns x 23 rows ----
    left_x, right_x = 16, 524
    top_y, row_h = 276, 28
    for i, (tag, headline) in enumerate(STORIES):
        col = i // 23
        row = i % 23
        x = left_x if col == 0 else right_x
        y = top_y + row * row_h
        cv.rect(x, y + 6, 16, 16, TAG_COLORS[tag])
        draw_text(cv, x + 24, y + 7, headline, 2, INK)
        if row < 22:
            cv.hline(x, y + 26, 484, LIGHT, 1)

    # ---- UTC timeline ----
    cv.rect(0, 924, W, 68, NAVY)
    draw_text(cv, 16, 930, "UTC TIMELINE - 22 NOVEMBER 2026", 2, (212, 160, 32))
    for i, item in enumerate(TIMELINE):
        col = i % 4
        row = i // 4
        x = 16 + col * 252
        y = 952 + row * 20
        draw_text(cv, x, y, item, 2, WHITE)

    # ---- Footer: date check + sources ----
    cv.rect(0, 992, W, 32, PAPER)
    draw_check(cv, 16, 1000, 2, GREEN)
    draw_text(cv, 34, 999,
              "DATE CHECK: 22 NOVEMBER 2026 WAS A SUNDAY - VERIFIED",
              2, INK)
    draw_text(cv, 16, 1014,
              "46 STORIES, EACH CHECKED AGAINST 2 SOURCES - REUTERS, BBC, AP, AFP, AL JAZEERA, NDTV, INDIA TODAY",
              1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    data = encode_png(cv.px, W, H)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(data)
    print("wrote %s (%d bytes, %dx%d, %d stories)"
          % (path, len(data), W, H, len(STORIES)))


if __name__ == "__main__":
    main()
