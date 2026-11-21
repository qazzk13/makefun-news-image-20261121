#!/usr/bin/env python3
"""THE WORLD IN A DAY - Saturday 21 November 2026.

Draws a 960x960 newspaper-front-page PNG summing up the world's news of
Saturday 21 November 2026. Pure Python 3 standard library, no network,
fully deterministic: two runs produce byte-identical output.

Stories were verified against sources read on 21 November 2026:
AP, Reuters, UN News, Bloomberg, Al Jazeera, WSJ.
"""

import os
import struct
import zlib

W, H = 960, 960

# ---------------------------------------------------------------- palette
PAPER = (246, 242, 233)
INK = (26, 30, 40)
NAVY = (20, 34, 64)
NAVY2 = (34, 52, 92)
GOLD = (198, 148, 52)
RED = (172, 40, 34)
TEAL = (36, 116, 116)
GREEN = (88, 132, 58)
CARD = (255, 255, 255)
BORDER = (206, 200, 186)
MUTED = (104, 99, 88)
BLUE = (44, 88, 148)
AMBER = (172, 112, 30)

# ------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, "1" = ink. Text is rendered uppercase.
F = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "X": ["10001", "01010", "00100", "00100", "00100", "01010", "10001"],
    "Y": ["10001", "01010", "00100", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10001", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    ":": ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ";": ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    "-": ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    "$": ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    "%": ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    "+": ["00000", "00100", "00100", "01110", "00100", "00100", "00000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    "(": ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ")": ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "?": ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "*": ["00000", "10101", "01110", "10101", "00000", "00000", "00000"],
}

# ------------------------------------------------------------- canvas
PX = bytearray(W * H * 3)


def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PX[i] = c[0]
        PX[i + 1] = c[1]
        PX[i + 2] = c[2]


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            put(xx, yy, c)


def frame(x, y, w, h, c, t=2):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


def text_w(s, s_):
    return len(s) * 6 * s_ - s_


def draw_text(x, y, s, s_, c):
    s = s.upper()
    cx = x
    for ch in s:
        g = F.get(ch, F[" "])
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == "1":
                    rect(cx + col * s_, y + r * s_, s_, s_, c)
        cx += 6 * s_
    return cx


def draw_centered(y, s, s_, c, cx=W // 2):
    draw_text(cx - text_w(s, s_) // 2, y, s, s_, c)


def wrap(s, s_, maxw):
    words = s.upper().split()
    lines = []
    cur = ""
    for wd in words:
        t = wd if not cur else cur + " " + wd
        if text_w(t, s_) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------- layout
def card(x, y, w, h, kicker, kc, headline, hs, body, bs, source):
    rect(x, y, w, h, CARD)
    frame(x, y, w, h, BORDER, 2)
    rect(x, y, w, 6, kc)
    draw_text(x + 18, y + 14, kicker, 2, kc)
    cy = y + 38
    for ln in wrap(headline, hs, w - 36):
        draw_text(x + 18, cy, ln, hs, INK)
        cy += 8 * hs + 2
    cy += 4
    for ln in wrap(body, bs, w - 36):
        draw_text(x + 18, cy, ln, bs, MUTED)
        cy += 8 * bs + 2
    draw_text(x + 18, y + h - 24, source, 2, kc)


def main():
    rect(0, 0, W, H, PAPER)

    # masthead
    rect(0, 0, W, 148, NAVY)
    rect(0, 148, W, 6, GOLD)
    draw_centered(18, "THE WORLD IN A DAY", 8, (255, 255, 255))
    draw_centered(86, "SATURDAY 21 NOVEMBER 2026", 3, GOLD)
    draw_text(28, 120, "ONE IMAGE. THE WHOLE PLANET.", 2, (200, 208, 226))
    r = "EST. 2026 * VOL. 1 NO. 6"
    draw_text(W - 28 - text_w(r, 2), 120, r, 2, (200, 208, 226))

    # headline story
    hx, hy, hw, hh = 28, 168, 904, 270
    rect(hx, hy, hw, hh, NAVY2)
    frame(hx, hy, hw, hh, GOLD, 3)
    draw_text(hx + 24, hy + 18, "UKRAINE / POLAND", 3, GOLD)
    draw_text(hx + 24, hy + 52, "MISSILES CROSS NATO BORDER", 5, (255, 255, 255))
    body = (
        "Russia fired 400+ drones and 110 missiles at Ukraine overnight; "
        "at least 8 died in Kyiv. Two missiles and a suspected drone "
        "fell inside Poland - a suspected provocation, Warsaw says; "
        "NATO: a serious violation of allied airspace."
    )
    cy = hy + 108
    for ln in wrap(body, 3, hw - 48):
        draw_text(hx + 24, cy, ln, 3, (216, 222, 236))
        cy += 27
    draw_text(hx + 24, hy + hh - 28, "SOURCES: AP / REUTERS", 2, GOLD)

    # story grid: two columns
    gx, gy = 28, 452
    cw, chh, gap = 444, 196, 12
    card(gx, gy, cw, chh, "CLIMATE", TEAL,
         "COP31 TALKS RUN LONG, FOSSIL WORDS CUT", 3,
         "Negotiators in Antalya blew past the deadline and extended the "
         "summit a day after the draft cut every mention of "
         "fossil fuels.", 2, "UN NEWS / REUTERS")
    card(gx + cw + gap, gy, cw, chh, "MARKETS", RED,
         "AI SELL-OFF TIPS WALL ST INTO CORRECTION", 3,
         "The S+P fell 3.7% to 6,910.42 and the Dow shed 950 points; the "
         "Nasdaq lost 5.3%, negative for the year. Nvidia "
         "dropped 14%.", 2, "REUTERS / WSJ / AP")
    gy2 = gy + chh + gap
    card(gx, gy2, cw, chh, "GAZA", AMBER,
         "STRIKE KILLS 6 AS WINTER RAINS CLOSE IN", 3,
         "An Israeli airstrike killed six people in Gaza as winter rain "
         "deepened the humanitarian crisis for displaced families.", 2, "AL JAZEERA / UN NEWS")
    card(gx + cw + gap, gy2, cw, chh, "CRYPTO", BLUE,
         "BITCOIN AT $57,716, LOWEST SINCE 2024", 3,
         "Bitcoin slid to its lowest level since September 2024, wiping "
         "out every gain made since the US election a year ago.",
         2, "BLOOMBERG")

    # bottom strip: sixth story + footer
    by = gy2 + chh + gap
    rect(28, by, 904, 58, CARD)
    frame(28, by, 904, 58, BORDER, 2)
    rect(28, by, 6, 58, GREEN)
    draw_text(48, by + 10, "DENMARK EXPELS RUSSIAN DIPLOMATS", 3, GREEN)
    draw_text(48, by + 38,
              "COPENHAGEN: THE ENVOYS PLOTTED TO KILL A UKRAINIAN RAPPER (AL JAZEERA)",
              2, MUTED)
    draw_centered(936,
                  "DRAWN IN CODE * PURE PYTHON * NO PHOTOS * SOURCES AS MARKED",
                  2, MUTED)

    # write PNG
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += PX[yy * W * 3:(yy + 1) * W * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(png)
    print("wrote", path, len(png), "bytes")


if __name__ == "__main__":
    main()
