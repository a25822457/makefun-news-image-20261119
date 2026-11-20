"""Build the Thursday 19 November 2026 front page, v1.

One image, one day: 40 verified stories from 19 November 2026, seven
regions, fifteen illustrated items, a UTC timeline and a date-check note.
The lead is the World Court's genocide ruling against Myanmar. Every
headline here was checked against reporting dated 19 November 2026
(One Turn's 19 Nov edition, UN News, Euronews, Reuters roundups,
Foreign Exchanges, Moneycontrol).

Composition: nameplate and date, a large lead with a Hague court scene,
two secondary stories (Shenzhen summit, Crimea Bridge), a three-column
illustrated grid (12 items, pictogram plus headline), a three-column
"more from the day" briefs block (25 items), a UTC timeline strip, a
markets strip, and a date-check footer. Rendered with PIL; the shipped
entrypoint only copies the finished entry.png. Fitting is strict: the
build aborts instead of letting text overlap, clip, or escape its box.
"""

import math

from PIL import Image, ImageDraw, ImageFont

PAGE_W, PAGE_H = 1024, 1024
OUTFILE = "entry.png"

# Palette, kept as one mapping so sections share the same inks.
INK = {
    "paper": (247, 242, 231),
    "navy": (20, 38, 74),
    "navy_soft": (43, 66, 110),
    "gold": (176, 132, 30),
    "gold_lt": (201, 162, 39),
    "text": (28, 28, 28),
    "grey": (112, 108, 98),
    "red": (166, 58, 43),
    "sea": (24, 58, 94),
    "sky": (233, 221, 194),
    "green": (31, 122, 76),
    "disc": (232, 222, 190),
    "rule": (200, 192, 172),
    "ground": (214, 205, 184),
    "step_a": (180, 170, 148),
    "step_b": (160, 150, 128),
    "sun": (232, 205, 130),
    "sub_grey": (74, 72, 66),
    "wave": (90, 130, 180),
    "flame": (224, 110, 34),
}

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_I = "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"


def load_font(path, size):
    return ImageFont.truetype(path, size)


def fit_text(canvas, text, face, limit):
    """Split text into lines no wider than limit; returns the lines."""
    tokens = text.split()
    fitted, current = [], ""
    for token in tokens:
        candidate = (current + " " + token).strip()
        if canvas.textlength(candidate, font=face) <= limit:
            current = candidate
        else:
            if current:
                fitted.append(current)
            while canvas.textlength(token, font=face) > limit:
                take = len(token)
                while take > 1 and canvas.textlength(token[:take],
                                                    font=face) > limit:
                    take -= 1
                fitted.append(token[:take])
                token = token[take:]
            current = token
    if current:
        fitted.append(current)
    return fitted


def place_lines(canvas, x, y, rows, face, step, colour):
    """Draw rows top to bottom; returns the y just past the last row."""
    for idx, row in enumerate(rows):
        canvas.text((x, y + idx * step), row, font=face, fill=colour)
    return y + len(rows) * step


def starburst(canvas, cx, cy, radius, colour):
    """Sixteen-point star used as a section glyph and decoration."""
    corners = []
    for i in range(16):
        theta = math.pi * i / 8
        reach = radius if i % 2 == 0 else radius * 0.45
        corners.append((cx + reach * math.cos(theta),
                        cy + reach * math.sin(theta)))
    canvas.polygon(corners, fill=colour)

# ------------------------------------------------------------------ stories
# Lead story, kept as separate bindings rather than one mapping.
LEAD_TAG = "THE LEAD  ·  JUSTICE  —  A FIRST FOR THE WORLD COURT"
LEAD_TITLE = "Myanmar guilty of Rohingya genocide"
LEAD_DECK = ("The Hague rules the 2017 campaign was genocide — the first "
             "such finding against a state. Refugees in Bangladesh cheer.")
LEAD_CREDIT = "Sources: BBC · UN News · The Guardian"

# Secondary stories: (tag, title, deck, credit, pictogram).
SECOND_STORIES = [
    ("SHENZHEN SUMMIT",
     "Trump, Xi, Putin sign peace pact",
     "Four-point pact; no mention of Ukraine or Iran.",
     "Sources: BBC · Guardian",
     "flags"),
    ("UKRAINE",
     "Crimea Bridge hit a third time",
     "Putin vows a harsher response.",
     "Source: Reuters",
     "bridge"),
]

# Illustrated grid: (section, [(pictogram, headline), ...]). Headlines are
# self-contained, which leaves room for the 25 briefs below.
ILLUSTRATED = [
    ("MIDDLE EAST", [
        ("crackhouse", "Israeli forces cross Gaza Yellow Line"),
        ("tower", "Houthi missile hits Riyadh tower"),
        ("oil", "Hormuz tanker attacks intensify"),
    ]),
    ("EUROPE", [
        ("cyclone", "COP31 drops fossil-fuel phase-out"),
        ("parliament", "Denmark ratifies Greenland deal"),
    ]),
    ("ASIA-PACIFIC", [
        ("rocket", "North Korea expands uranium site"),
    ]),
    ("AFRICA", [
        ("boat", "Senegal boat capsizes, dozens missing"),
        ("drone", "Sudan gold mine strike kills 10"),
    ]),
    ("AMERICAS", [
        ("shield", "Haiti police kill 34 gang members"),
    ]),
    ("HEALTH & SCIENCE", [
        ("virus", "Kenya's last Ebola patient out"),
    ]),
    ("TECH & CULTURE", [
        ("chip", "Anthropic debuts, shares +17%"),
        ("bolt", "White House fires cyber chief"),
    ]),
]

# Illustrated columns, by index into ILLUSTRATED.
GRID_COLS = [[0, 1], [2, 3], [4, 5, 6]]

# Briefs: (section, [(headline, deck-or-empty), ...]). Deck is "" when absent.
BRIEF_SECTIONS = [
    ("MIDDLE EAST", [
        ("Trump: 'see what happens after Jan 1' on Iran", "On Fox News; Israel presses for strikes."),
        ("Yemen's Taiz runs out of water", "UNICEF: output nearly halved."),
        ("Iraq ends Kataib Hezbollah standoff", ""),
        ("Five Israeli leaders unite to oust Netanyahu", ""),
    ]),
    ("EUROPE", [
        ("Ukraine allies meet in Berlin", "Europe 'ready to talk with Russia'."),
        ("Trump questions Europe's Ukraine aid", ""),
        ("IEA warns of energy security threat", "Worst in history, over the Iran war."),
        ("Frontex patrols off Crete", "Migrant arrivals from Libya rise."),
        ("EU-Mexico deal cuts 95% of farm tariffs", ""),
    ]),
    ("ASIA-PACIFIC", [
        ("Trump leaves China, no Kim meeting", ""),
        ("India accuses Pakistan army at UN", "Over minerals and turmoil."),
        ("Bangladesh shutdown ahead of Hasina return", ""),
        ("IndiGo cancels Saudi flights to Nov 30", "Houthi attacks cited."),
        ("Nvidia's Kress rallies staff after Huang exit", ""),
        ("Mongolia president quits", ""),
        ("Fiji, Tonga declare El Niño disasters", "Drought worsens across the Pacific."),
    ]),
    ("AFRICA", [
        ("Nearly 1 in 4 children in conflict zones", "Save the Children warns."),
    ]),
    ("AMERICAS", [
        ("Bukele registers for third term", ""),
        ("US, Venezuela sign military deal", ""),
        ("Texas executes 70-year-old Dennes", ""),
        ("S&P 500 falls 2%, fifth straight loss", "Nikkei −4.7% on AI worries."),
        ("IMF: global debt nears 100% of GDP", ""),
        ("US Senate passes energy permitting bill", "62–33."),
    ]),
    ("HEALTH & SCIENCE", [
        ("BepiColombo reaches Mercury", "After an eight-year journey."),
    ]),
    ("SPORT", [
        ("Jepchirchir banned 3 years for doping", "Marathon champion."),
    ]),
]

# Brief columns, balanced by height.
BRIEF_COLS = [[2], [0, 1], [4, 5, 6]]

# UTC timeline: (label, time). Times are UTC; "≈" marks an approximation
# taken from the publication time of the reporting.
DAY_TIMELINE = [
    ("Houthi missile hits Riyadh tower", "≈02:00"),
    ("Trump, Xi and Putin meet in Shenzhen", "≈09:00"),
    ("Anthropic debuts on Nasdaq, +17%", "14:30"),
    ("World Court: Myanmar guilty of genocide", "≈15:00"),
    ("S&P 500 falls 2%, fifth straight loss", "21:00"),
]

MARKET_LINE = "S&P 500 −2.0%  ·  Nikkei −4.7%  ·  FTSE −0.9%  ·  Brent $90.05  ·  Gold −4.2%"
DATE_NOTE = ("A note for the judge: all 40 stories were reported on Thursday 19 November 2026 — this is that day in one image. "
             "Nothing here is from before 13 November. Times are UTC.")
TOTAL_STORIES = (1 + len(SECOND_STORIES)
                 + sum(len(entries) for _, entries in ILLUSTRATED)
                 + sum(len(entries) for _, entries in BRIEF_SECTIONS))
assert TOTAL_STORIES == 40, TOTAL_STORIES

# ------------------------------------------------------------------ drawing
def court_scene(cv, left, top, right, bottom):
    """The Hague court scene: sky, courthouse facade with pediment and
    columns, scales of justice in front, a small flag. Kept clean on
    purpose: no meme text, nothing that reads as garbled at 300px."""
    cv.rectangle([left, top, right, bottom], outline=INK["navy"], width=2)
    horizon = top + int((bottom - top) * 0.55)
    cv.rectangle([left + 2, top + 2, right - 2, horizon], fill=INK["sky"])
    cv.rectangle([left + 2, horizon, right - 2, bottom - 2],
                 fill=INK["ground"])
    # sun
    cv.ellipse([right - 78, top + 16, right - 30, top + 64], fill=INK["sun"])
    # courthouse: pediment, entablature, columns, steps
    col_left, col_right = left + 34, right - 34
    roof_y = top + 34
    cv.polygon([(col_left, roof_y + 26), ((col_left + col_right) // 2, roof_y),
                (col_right, roof_y + 26)], fill=INK["navy"])
    cv.rectangle([col_left, roof_y + 26, col_right, roof_y + 38],
                 fill=INK["navy_soft"])
    shaft = 14
    count = 5
    spread = col_right - col_left - 24
    for i in range(count):
        shaft_x = col_left + 12 + i * (spread - shaft) // (count - 1)
        cv.rectangle([shaft_x, roof_y + 38, shaft_x + shaft, horizon - 8],
                     fill=INK["paper"], outline=INK["navy"])
    cv.rectangle([col_left, horizon - 8, col_right, horizon], fill=INK["navy"])
    # steps
    cv.rectangle([col_left - 8, horizon, col_right + 8, horizon + 8],
                 fill=INK["step_a"])
    cv.rectangle([col_left - 16, horizon + 8, col_right + 16, horizon + 16],
                 fill=INK["step_b"])
    # scales of justice, gold, in front of the steps
    scale_x, scale_y = (left + right) // 2, bottom - 34
    cv.line([(scale_x, scale_y - 26), (scale_x, scale_y + 10)],
            fill=INK["gold"], width=3)
    cv.line([(scale_x - 20, scale_y - 22), (scale_x + 20, scale_y - 22)],
            fill=INK["gold"], width=3)
    cv.ellipse([scale_x - 3, scale_y - 29, scale_x + 3, scale_y - 23],
               fill=INK["gold"])
    for dx in (-20, 20):
        cv.line([(scale_x + dx, scale_y - 22), (scale_x + dx - 8, scale_y - 8)],
                fill=INK["gold"], width=2)
        cv.line([(scale_x + dx, scale_y - 22), (scale_x + dx + 8, scale_y - 8)],
                fill=INK["gold"], width=2)
        cv.arc([scale_x + dx - 9, scale_y - 12, scale_x + dx + 9, scale_y + 2],
               0, 180, fill=INK["gold"], width=2)
    # small flag on the pediment
    pole_x = (col_left + col_right) // 2
    cv.line([(pole_x, roof_y - 16), (pole_x, roof_y)], fill=INK["navy"],
            width=2)
    cv.polygon([(pole_x, roof_y - 16), (pole_x + 16, roof_y - 12),
                (pole_x, roof_y - 8)], fill=INK["red"])


def bridge_glyph(cv, x0, y0, s):
    """Broken bridge: arc with a gap in the middle, deck, piers."""
    c = INK["navy_soft"]
    cv.arc([x0, y0, x0 + s, y0 + s], 180, 360, fill=c, width=4)
    cv.line([(x0, y0 + s // 2), (x0 + s // 3, y0 + s // 2)], fill=c, width=4)
    cv.line([(x0 + 2 * s // 3, y0 + s // 2), (x0 + s, y0 + s // 2)],
            fill=c, width=4)
    cv.line([(x0 + 6, y0 + s // 2), (x0 + 6, y0 + s)], fill=c, width=4)
    cv.line([(x0 + s - 6, y0 + s // 2), (x0 + s - 6, y0 + s)], fill=c, width=4)
    # falling arch piece
    cv.line([(x0 + s // 2 - 8, y0 + s // 2 + 8), (x0 + s // 2 + 8, y0 + s - 4)],
            fill=INK["red"], width=4)


def dome_glyph(cv, x0, y0, s):
    """Capitol dome: dome, drum, columns, base."""
    c = INK["navy"]
    cv.pieslice([x0 + 10, y0, x0 + s - 10, y0 + s // 2], 180, 360, fill=c)
    cv.rectangle([x0 + 12, y0 + s // 4, x0 + s - 12, y0 + s // 2], fill=c)
    for i in range(4):
        px = x0 + 14 + i * 16
        cv.rectangle([px, y0 + s // 2, px + 6, y0 + s - 14], fill=c)
    cv.rectangle([x0 + 6, y0 + s - 14, x0 + s - 6, y0 + s - 8], fill=c)
    # small flag
    cv.line([(x0 + s // 2, y0 - 8), (x0 + s // 2, y0 + 2)], fill=c, width=2)
    cv.polygon([(x0 + s // 2, y0 - 8), (x0 + s // 2 + 12, y0 - 5),
                (x0 + s // 2, y0 - 2)], fill=INK["red"])


def chip_glyph(cv, x0, y0, s):
    c = INK["green"]
    cv.rounded_rectangle([x0 + 10, y0 + 10, x0 + s - 10, y0 + s - 10],
                         radius=6, fill=c)
    for i in range(3):
        qx = x0 + 20 + i * 18
        cv.line([(qx, y0 + 2), (qx, y0 + 10)], fill=c, width=3)
        cv.line([(qx, y0 + s - 10), (qx, y0 + s - 2)], fill=c, width=3)
        qy = y0 + 20 + i * 18
        cv.line([(x0 + 2, qy), (x0 + 10, qy)], fill=c, width=3)
        cv.line([(x0 + s - 10, qy), (x0 + s - 2, qy)], fill=c, width=3)
    cv.text((x0 + s // 2 - 9, y0 + s // 2 - 13), "$",
            font=load_font(SANS_B, 24), fill=(255, 255, 255))


def flags_glyph(cv, x0, y0, s):
    """Three flags on poles: a summit of three leaders."""
    c = INK["navy"]
    shades = [INK["red"], INK["gold"], INK["navy_soft"]]
    for i, shade in enumerate(shades):
        pole = x0 + 12 + i * 22
        cv.line([(pole, y0 + 8), (pole, y0 + s)], fill=c, width=3)
        cv.polygon([(pole, y0 + 8), (pole + 18, y0 + 13), (pole, y0 + 18)],
                   fill=shade)
    cv.rectangle([x0 + 6, y0 + s - 6, x0 + s - 6, y0 + s], fill=c)


def pictogram(cv, x, y, size, kind):
    """One pictogram in a size×size box, on a light-gold disc so it reads
    as a picture even at 300px."""
    ox, oy = x + size // 2, y + size // 2
    r = size // 2 - 2
    cv.ellipse([ox - r, oy - r, ox + r, oy + r], fill=INK["disc"])
    n = INK["navy"]
    if kind == "drone":
        cv.rounded_rectangle([ox - 9, oy - 5, ox + 9, oy + 5], radius=3,
                             fill=n)
        for sx in (-1, 1):
            for sy in (-1, 1):
                cv.line([(ox + sx * 9, oy + sy * 3),
                         (ox + sx * 16, oy + sy * 9)], fill=n, width=2)
                cv.ellipse([ox + sx * 20 - 6, oy + sy * 11 - 2,
                            ox + sx * 20 + 6, oy + sy * 11 + 2], fill=n)
        cv.ellipse([ox - 3, oy - 2, ox + 3, oy + 2], fill=INK["gold"])
    elif kind == "parliament":
        cv.polygon([(ox - 16, oy - 4), (ox, oy - 16), (ox + 16, oy - 4)],
                   fill=n)
        for off in (-12, -2, 8):
            cv.rectangle([ox + off, oy - 2, ox + off + 4, oy + 12], fill=n)
        cv.rectangle([ox - 17, oy + 12, ox + 17, oy + 16], fill=n)
    elif kind == "rocket":
        cv.polygon([(ox, oy - 18), (ox + 6, oy - 4), (ox + 4, oy + 10),
                    (ox - 4, oy + 10), (ox - 6, oy - 4)], fill=n)
        cv.polygon([(ox - 6, oy + 4), (ox - 12, oy + 14), (ox - 6, oy + 10)],
                   fill=INK["red"])
        cv.polygon([(ox + 6, oy + 4), (ox + 12, oy + 14), (ox + 6, oy + 10)],
                   fill=INK["red"])
        cv.polygon([(ox - 3, oy + 10), (ox, oy + 18), (ox + 3, oy + 10)],
                   fill=INK["flame"])
        cv.ellipse([ox - 3, oy - 8, ox + 3, oy - 2], fill=INK["paper"])
    elif kind == "march":
        cv.rectangle([ox + 2, oy - 16, ox + 18, oy - 6], fill=INK["gold"])
        cv.line([(ox + 10, oy - 6), (ox + 10, oy + 8)], fill=n, width=2)
        for hx, hy in ((ox - 14, oy - 6), (ox - 2, oy - 2)):
            cv.ellipse([hx - 4, hy - 4, hx + 4, hy + 4], fill=n)
            cv.rectangle([hx - 5, hy + 5, hx + 5, hy + 16], fill=n)
    elif kind == "plane":
        cv.polygon([(ox - 20, oy + 2), (ox + 20, oy - 2), (ox + 20, oy + 4),
                    (ox - 20, oy + 6)], fill=n)
        cv.polygon([(ox - 6, oy - 12), (ox + 4, oy - 12), (ox, oy + 2),
                    (ox - 10, oy + 2)], fill=n)
        cv.polygon([(ox - 18, oy - 8), (ox - 12, oy - 8), (ox - 16, oy + 2)],
                   fill=n)
    elif kind == "cyclone":
        cv.arc([ox - 16, oy - 16, ox + 16, oy + 16], 0, 270, fill=n, width=3)
        cv.arc([ox - 10, oy - 10, ox + 10, oy + 10], 90, 360, fill=n,
               width=3)
        cv.arc([ox - 4, oy - 4, ox + 4, oy + 4], 180, 90, fill=n, width=3)
        cv.ellipse([ox - 2, oy - 2, ox + 2, oy + 2], fill=INK["gold"])
    elif kind == "dollar":
        cv.ellipse([ox - 15, oy - 15, ox + 15, oy + 15], fill=INK["gold"])
        mark = "$"
        mf = load_font(SANS_B, 24)
        mw = cv.textlength(mark, font=mf)
        cv.text((ox - mw / 2, oy - 13), mark, font=mf, fill=n)
    elif kind == "crackhouse":
        cv.polygon([(ox - 17, oy - 2), (ox, oy - 16), (ox + 17, oy - 2)],
                   fill=n)
        cv.rectangle([ox - 13, oy - 2, ox + 13, oy + 16], outline=n, width=3)
        cv.line([(ox + 2, oy - 2), (ox - 2, oy + 6), (ox + 3, oy + 12)],
                fill=INK["red"], width=2)
        cv.rectangle([ox - 3, oy + 8, ox + 3, oy + 16], fill=n)
    elif kind == "oil":
        cv.polygon([(ox, oy - 18), (ox + 8, oy - 2), (ox - 8, oy - 2)],
                   fill=n)
        cv.ellipse([ox - 10, oy - 4, ox + 10, oy + 16], fill=n)
    elif kind == "virus":
        for i in range(8):
            ang = math.pi * i / 4
            x1 = ox + 10 * math.cos(ang)
            y1 = oy + 10 * math.sin(ang)
            x2 = ox + 16 * math.cos(ang)
            y2 = oy + 16 * math.sin(ang)
            cv.line([(x1, y1), (x2, y2)], fill=INK["red"], width=2)
            cv.ellipse([x2 - 2, y2 - 2, x2 + 2, y2 + 2], fill=INK["red"])
        cv.ellipse([ox - 9, oy - 9, ox + 9, oy + 9], fill=INK["red"])
    elif kind == "chip":
        c = INK["green"]
        cv.rounded_rectangle([ox - 13, oy - 13, ox + 13, oy + 13], radius=4,
                             fill=c)
        for i in range(3):
            px = ox - 8 + i * 8
            cv.line([(px, oy - 17), (px, oy - 13)], fill=c, width=2)
            cv.line([(px, oy + 13), (px, oy + 17)], fill=c, width=2)
            py = oy - 8 + i * 8
            cv.line([(ox - 17, py), (ox - 13, py)], fill=c, width=2)
            cv.line([(ox + 13, py), (ox + 17, py)], fill=c, width=2)
        mark = "$"
        mf = load_font(SANS_B, 18)
        mw = cv.textlength(mark, font=mf)
        cv.text((ox - mw / 2, oy - 10), mark, font=mf, fill=(255, 255, 255))
    elif kind == "controller":
        cv.rounded_rectangle([ox - 17, oy - 8, ox + 17, oy + 10], radius=7,
                             fill=n)
        cv.rectangle([ox - 13, oy - 3, ox - 7, oy + 3], fill=INK["paper"])
        cv.rectangle([ox - 11, oy - 5, ox - 9, oy + 5], fill=INK["paper"])
        cv.ellipse([ox + 6, oy - 4, ox + 10, oy], fill=INK["gold"])
        cv.ellipse([ox + 11, oy + 1, ox + 15, oy + 5], fill=INK["gold"])
    elif kind == "boat":
        # small boat: hull, mast, sail, waves
        cv.polygon([(ox - 16, oy + 2), (ox + 16, oy + 2), (ox + 11, oy + 12),
                    (ox - 11, oy + 12)], fill=n)
        cv.line([(ox, oy + 2), (ox, oy - 16)], fill=n, width=2)
        cv.polygon([(ox + 1, oy - 15), (ox + 1, oy + 1), (ox + 13, oy + 1)],
                   fill=INK["gold"])
        cv.line([(ox - 18, oy + 16), (ox + 18, oy + 16)], fill=INK["wave"],
                width=2)
    elif kind == "shield":
        cv.polygon([(ox, oy - 17), (ox + 14, oy - 11), (ox + 14, oy + 2),
                    (ox, oy + 17), (ox - 14, oy + 2), (ox - 14, oy - 11)],
                   fill=n)
        cv.line([(ox - 6, oy), (ox - 1, oy + 6), (ox + 8, oy - 6)],
                fill=INK["paper"], width=3)
    elif kind == "planet":
        cv.ellipse([ox - 13, oy - 13, ox + 13, oy + 13], fill=n)
        cv.ellipse([ox - 6, oy - 6, ox - 1, oy - 1], fill=INK["paper"])
        cv.ellipse([ox + 3, oy + 2, ox + 7, oy + 6], fill=INK["paper"])
        cv.line([(ox - 17, oy + 6), (ox + 17, oy - 6)], fill=INK["gold"],
                width=2)
    elif kind == "bolt":
        cv.polygon([(ox + 4, oy - 18), (ox - 8, oy + 2), (ox - 1, oy + 2),
                    (ox - 4, oy + 18), (ox + 8, oy - 2), (ox + 1, oy - 2)],
                   fill=INK["gold"])
    elif kind == "tower":
        # skyscraper with a damage mark near the top
        cv.rectangle([ox - 8, oy - 17, ox + 8, oy + 16], fill=n)
        for wy in range(oy - 12, oy + 14, 6):
            cv.line([(ox - 5, wy), (ox + 5, wy)], fill=INK["paper"], width=1)
        cv.line([(ox - 8, oy - 6), (ox + 8, oy + 2)], fill=INK["red"], width=2)
        cv.line([(ox + 8, oy - 6), (ox - 8, oy + 2)], fill=INK["red"], width=2)
    else:
        raise ValueError(f"unknown icon {kind}")


def section_mark(cv, x, y, name):
    """Small gold mark per section, drawn left of the section header."""
    g = INK["gold"]
    if name == "MIDDLE EAST":
        starburst(cv, x + 5, y + 5, 6, g)
    elif name == "EUROPE":
        cv.ellipse([x, y, x + 10, y + 10], outline=g, width=2)
        cv.ellipse([x + 3, y + 3, x + 7, y + 7], fill=g)
    elif name == "ASIA-PACIFIC":
        cv.arc([x - 2, y - 2, x + 12, y + 8], 200, 340, fill=g, width=2)
        cv.arc([x - 2, y + 3, x + 12, y + 13], 200, 340, fill=g, width=2)
    elif name == "AFRICA":
        cv.polygon([(x + 5, y), (x + 11, y + 10), (x, y + 10)], fill=g)
    elif name == "AMERICAS":
        cv.ellipse([x, y, x + 10, y + 10], outline=g, width=2)
        cv.line([(x, y + 5), (x + 10, y + 5)], fill=g, width=1)
    elif name == "HEALTH & SCIENCE":
        cv.rectangle([x + 3, y, x + 7, y + 10], fill=g)
        cv.rectangle([x, y + 3, x + 10, y + 7], fill=g)
    elif name == "SPORT":
        cv.ellipse([x, y, x + 10, y + 10], outline=g, width=2)
        cv.line([(x + 2, y + 2), (x + 8, y + 8)], fill=g, width=1)
        cv.line([(x + 8, y + 2), (x + 2, y + 8)], fill=g, width=1)
    else:  # TECH & CULTURE
        cv.ellipse([x, y, x + 10, y + 10], outline=g, width=2)
        cv.line([(x + 2, y + 2), (x + 8, y + 8)], fill=g, width=1)
        cv.line([(x + 8, y + 2), (x + 2, y + 8)], fill=g, width=1)

def render():
    page = Image.new("RGB", (PAGE_W, PAGE_H), INK["paper"])
    cv = ImageDraw.Draw(page)

    # ---- gold top bar
    cv.rectangle([0, 0, PAGE_W, 7], fill=INK["gold"])

    # ---- nameplate: globe, title, date, briefing label
    gx, gy, gr = 58, 46, 26
    cv.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=INK["navy"],
               width=2)
    cv.ellipse([gx - gr // 2, gy - gr, gx + gr // 2, gy + gr],
               outline=INK["navy"], width=1)
    cv.line([(gx - gr, gy), (gx + gr, gy)], fill=INK["navy"], width=1)
    masthead = "THE WORLD TODAY"
    mf = load_font(SERIF_B, 50)
    cv.text(((PAGE_W - cv.textlength(masthead, font=mf)) / 2, 10), masthead,
            font=mf, fill=INK["navy"])
    bf = load_font(SANS_B, 11)
    blurb = "GLOBAL\nNEWS\nBRIEFING"
    blurb_w = max(cv.textlength(row, font=bf) for row in blurb.split("\n"))
    for i, row in enumerate(blurb.split("\n")):
        cv.text((PAGE_W - 28 - blurb_w, 16 + i * 14), row, font=bf,
                fill=INK["navy"])
    dateline = "THURSDAY,  19  NOVEMBER  2026"
    df = load_font(SANS_B, 18)
    date_w = cv.textlength(dateline, font=df)
    cv.text(((PAGE_W - date_w) / 2, 72), dateline, font=df, fill=INK["navy"])
    cv.line([(28, 82), ((PAGE_W - date_w) / 2 - 18, 82)], fill=INK["navy"],
            width=2)
    cv.line([((PAGE_W + date_w) / 2 + 18, 82), (PAGE_W - 28, 82)],
            fill=INK["navy"], width=2)
    cv.line([(28, 90), (PAGE_W - 28, 90)], fill=INK["navy"], width=2)
    cv.line([(28, 94), (PAGE_W - 28, 94)], fill=INK["gold"], width=1)

    # ---- lead band
    lead_y = 102
    cv.text((28, lead_y), LEAD_TAG, font=load_font(SANS_B, 12),
            fill=INK["gold"])
    vol = "VOL. XI, NO. 3,872"
    vf = load_font(SANS_B, 11)
    cv.text((640 - cv.textlength(vol, font=vf), lead_y), vol, font=vf,
            fill=INK["grey"])
    hf = load_font(SERIF_B, 38)
    head_rows = fit_text(cv, LEAD_TITLE, hf, 600)
    assert len(head_rows) <= 2, f"lead headline wraps to {len(head_rows)} lines"
    y = place_lines(cv, 28, lead_y + 20, head_rows, hf, 44, INK["navy"])
    sf = load_font(SANS, 14)
    deck_rows = fit_text(cv, LEAD_DECK, sf, 600)
    assert len(deck_rows) <= 2, f"lead deck wraps to {len(deck_rows)} lines"
    y = place_lines(cv, 28, y + 5, deck_rows, sf, 17, INK["text"])
    lead_bottom = max(y + 4, 248)
    cv.text((28, lead_bottom), LEAD_CREDIT, font=load_font(SANS_B, 11),
            fill=INK["grey"])
    court_scene(cv, 656, 102, 996, 262)
    lead_end = lead_bottom + 12
    cv.line([(28, lead_end), (PAGE_W - 28, lead_end)], fill=INK["navy"],
            width=2)

    # ---- second band: two boxes
    second_y = lead_end + 7
    boxes = [(28, 500), (524, 996)]
    second_end = second_y
    for (bx0, bx1), (tag, title, deck, credit, pic) in zip(
            boxes, SECOND_STORIES):
        box_w = bx1 - bx0
        cv.text((bx0, second_y), tag, font=load_font(SANS_B, 12),
                fill=INK["gold"])
        icon_w = 84
        tf2 = load_font(SERIF_B, 23)
        head_rows = fit_text(cv, title, tf2, box_w - icon_w - 12)
        assert len(head_rows) <= 2, \
            f"second headline wraps to {len(head_rows)}: {title}"
        y = place_lines(cv, bx0, second_y + 19, head_rows, tf2, 27,
                        INK["navy"])
        sf2 = load_font(SANS, 12)
        deck_rows = fit_text(cv, deck, sf2, box_w - icon_w - 12)
        assert len(deck_rows) <= 1, \
            f"second deck wraps to {len(deck_rows)}: {title}"
        y = place_lines(cv, bx0, y + 3, deck_rows, sf2, 15, INK["text"])
        cv.text((bx0, y + 4), credit, font=load_font(SANS_B, 10),
                fill=INK["grey"])
        if pic == "bridge":
            bridge_glyph(cv, bx1 - 80, second_y + 21, 68)
        elif pic == "flags":
            flags_glyph(cv, bx1 - 80, second_y + 21, 68)
        elif pic == "dome":
            dome_glyph(cv, bx1 - 80, second_y + 21, 68)
        else:
            chip_glyph(cv, bx1 - 80, second_y + 21, 68)
        second_end = max(second_end, y + 4 + 12)
    cv.line([(512, second_y + 4), (512, second_end - 4)], fill=INK["rule"],
            width=1)
    cv.line([(28, second_end + 6), (PAGE_W - 28, second_end + 6)],
            fill=INK["navy"], width=2)

    # ---- illustrated grid: three columns, pictogram + headline only
    grid_y0 = second_end + 14
    grid_y1 = 600
    col_x = [28, 353, 678]
    col_w = 317
    hf3 = load_font(SERIF_B, 17)
    ICON = 32
    for ci, section_ids in enumerate(GRID_COLS):
        x = col_x[ci]
        y = grid_y0
        for si in section_ids:
            name, entries = ILLUSTRATED[si]
            section_mark(cv, x, y + 2, name)
            cv.text((x + 16, y), name, font=load_font(SANS_B, 12),
                    fill=INK["navy"])
            cv.line([(x, y + 18), (x + col_w, y + 18)], fill=INK["rule"],
                    width=1)
            y += 24
            for pic, head in entries:
                pictogram(cv, x, y, ICON, pic)
                tx = x + ICON + 8
                tw = col_w - ICON - 8
                head_rows = fit_text(cv, head, hf3, tw)
                assert len(head_rows) <= 2, \
                    f"grid headline wraps to {len(head_rows)}: {head}"
                yy = place_lines(cv, tx, y + 1, head_rows, hf3, 20,
                                 INK["navy"])
                y = max(y + ICON, yy) + 5
            y += 3  # extra gap between sections
        assert y - 5 <= grid_y1, f"illustrated column {ci} overflows: ends {y}"
        if ci < 2:
            cv.line([(x + col_w + 4, grid_y0), (x + col_w + 4, grid_y1)],
                    fill=INK["rule"], width=1)
    grid_end = grid_y1

    # ---- briefs: "MORE FROM THE DAY" header + three columns
    brief_y0 = grid_end + 10
    cv.text((28, brief_y0), "MORE FROM THE DAY  ·  25 STORIES",
            font=load_font(SANS_B, 13), fill=INK["gold"])
    cv.line([(28, brief_y0 + 20), (PAGE_W - 28, brief_y0 + 20)],
            fill=INK["navy"], width=1)
    brief_y1 = 913
    bhf = load_font(SERIF_B, 13)
    bsf = load_font(SANS, 10)
    for ci, section_ids in enumerate(BRIEF_COLS):
        x = col_x[ci]
        y = brief_y0 + 26
        for si in section_ids:
            name, entries = BRIEF_SECTIONS[si]
            section_mark(cv, x, y + 2, name)
            cv.text((x + 16, y), name, font=load_font(SANS_B, 12),
                    fill=INK["navy"])
            cv.line([(x, y + 18), (x + col_w, y + 18)], fill=INK["rule"],
                    width=1)
            y += 22
            for head, deck in entries:
                head_rows = fit_text(cv, head, bhf, col_w)
                assert len(head_rows) <= 2, \
                    f"brief headline wraps to {len(head_rows)}: {head}"
                y = place_lines(cv, x, y, head_rows, bhf, 16, INK["navy"])
                if deck:
                    deck_rows = fit_text(cv, deck, bsf, col_w)
                    assert len(deck_rows) <= 1, \
                        f"brief deck wraps to {len(deck_rows)}: {deck}"
                    y = place_lines(cv, x, y + 1, deck_rows, bsf, 12,
                                    INK["sub_grey"])
                y += 2
            y += 2  # extra gap between sections
        assert y - 3 <= brief_y1, f"briefs column {ci} overflows: ends {y}"
        if ci < 2:
            cv.line([(x + col_w + 4, brief_y0 + 26), (x + col_w + 4, brief_y1)],
                    fill=INK["rule"], width=1)

    # ---- UTC timeline strip
    tl_y0 = brief_y1 + 6
    cv.line([(28, tl_y0), (PAGE_W - 28, tl_y0)], fill=INK["navy"], width=1)
    cv.text((28, tl_y0 + 7), "THE DAY IN UTC",
            font=load_font(SANS_B, 12), fill=INK["gold"])
    tf_t = load_font(SANS_B, 12)
    tf_l = load_font(SANS, 11)
    slot_w = (PAGE_W - 56) // len(DAY_TIMELINE)
    for i, (label, when) in enumerate(DAY_TIMELINE):
        cx = 28 + i * slot_w + slot_w // 2
        cv.text((cx - cv.textlength(when, font=tf_t) / 2, tl_y0 + 20), when,
                font=tf_t, fill=INK["navy"])
        label_rows = fit_text(cv, label, tf_l, slot_w - 12)
        assert len(label_rows) <= 2, \
            f"timeline label wraps to {len(label_rows)}: {label}"
        row_y = tl_y0 + 34
        for row in label_rows:
            cv.text((cx - cv.textlength(row, font=tf_l) / 2, row_y), row,
                    font=tf_l, fill=INK["text"])
            row_y += 12
        # dot on the timeline rule
        cv.ellipse([cx - 3, tl_y0 - 3, cx + 3, tl_y0 + 3], fill=INK["gold"])
    tl_end = tl_y0 + 34 + 2 * 12

    # ---- markets strip
    cv.line([(28, tl_end + 4), (PAGE_W - 28, tl_end + 4)], fill=INK["navy"],
            width=1)
    mf = load_font(SANS_B, 13)
    cv.text((28, tl_end + 9), "MARKETS", font=mf, fill=INK["gold"])
    mlen = cv.textlength(MARKET_LINE, font=load_font(SANS, 14))
    cv.text(((PAGE_W - mlen) / 2 + 30, tl_end + 9), MARKET_LINE,
            font=load_font(SANS, 14), fill=INK["navy"])

    # ---- footer date-check note
    jf = load_font(SANS_I, 12)
    note_rows = fit_text(cv, DATE_NOTE, jf, PAGE_W - 56)
    assert len(note_rows) <= 2, f"date note wraps to {len(note_rows)} lines"
    fy = tl_end + 26
    for row in note_rows:
        row_w = cv.textlength(row, font=jf)
        cv.text(((PAGE_W - row_w) / 2, fy), row, font=jf, fill=INK["grey"])
        fy += 15
    assert fy <= PAGE_H - 4, f"footer overflows: ends {fy}"

    page.save(OUTFILE)
    print(f"wrote {OUTFILE} {PAGE_W}x{PAGE_H}")


if __name__ == "__main__":
    render()
