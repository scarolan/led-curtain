#!/usr/bin/env python3
"""
Hand-drawn 20x20 pixel-art GIFs for a WLED LED curtain -- December / winter holiday set.

Every image is authored at native 20x20 (ASCII pixel maps + tiny procedural
shapes); nothing is downscaled. Drawing helpers live in pixelart.py.

Usage:  python3 gen_christmas.py [scene ...]   -> gifs/*.gif + preview_christmas.png
"""
import math, random, sys
from pixelart import *
import gen_halloween as hw

SCENES, scene = registry()

X = dict(C)
X.update({
    'E': (0, 150, 40),      # evergreen
    'e': (0, 80, 20),       # dark evergreen
    'D': (70, 70, 100),     # dark slate (penguin, silhouettes, hat)
    'Q': (210, 125, 50),    # gingerbread
    'U': (255, 130, 140),   # rosy pink
    'b': (120, 170, 255),   # ice blue
    'X': (0, 0, 0),
})
SNOW = (235, 240, 255)

def snowfall(f, i, N, flakes, cols=(SNOW, (170, 190, 230))):
    """Draw drifting snow; `flakes` = list of (x, y0, speed, sway). Loops every N frames."""
    for k, (x, y0, spd, sw) in enumerate(flakes):
        y = (y0 + i * spd) % 24 - 2
        xx = x + round(sw * math.sin(2 * math.pi * i * spd / N + k))
        put(f, xx, y, cols[k % len(cols)])

FLAKES = [(1, 0, 1, 1), (5, 7, 1, 0), (9, 3, 1, 1), (13, 11, 1, 0), (17, 5, 1, 1), (3, 15, 1, 0),
          (11, 19, 1, 1), (15, 1, 1, 0), (7, 13, 1, 1), (19, 9, 1, 0)]

# ================================================================== SCENES

# ---- 1. Christmas tree with twinkling lights ------------------------------
TREE = """
.........Y..........
........YYY.........
.........Y..........
.........E..........
........EEE.........
.......EEEEE........
......EEEEEEE.......
.......EEEEE........
......EEEEEEE.......
.....EEEEEEEEE......
....EEEEEEEEEEE.....
......EEEEEEE.......
.....EEEEEEEEE......
....EEEEEEEEEEE.....
...EEEEEEEEEEEEE....
..EEEEEEEEEEEEEEE...
........NNN.........
........NNN.........
....RRRR...BBBB.....
....RYRR...BWBB.....
"""
@scene
def tree():
    base = full(TREE, X)
    for y in range(H):                      # darker inner needles
        for x in range(W):
            if base[y][x] == X['E'] and (x * 3 + y * 5) % 7 == 0:
                base[y][x] = X['e']
    lights = [(9, 5, 'R'), (8, 7, 'B'), (10, 8, 'Y'), (6, 10, 'P'), (12, 10, 'R'), (9, 11, 'W'),
              (7, 13, 'Y'), (11, 12, 'B'), (5, 14, 'R'), (13, 14, 'P'), (9, 14, 'Y'), (3, 15, 'B'),
              (15, 15, 'R'), (7, 15, 'W'), (11, 15, 'Y')]
    N = 16
    frames = []
    for i in range(N):
        f = copy(base)
        for k, (lx, ly, c) in enumerate(lights):
            ph = (i + k * 5) % N
            put(f, lx, ly, X[c] if ph < 9 else scale(X[c], 0.3))
        star = lerp(X['Y'], X['W'], 0.5 + 0.5 * math.sin(2 * math.pi * i / N))
        for (sx, sy) in [(9, 0), (8, 1), (9, 1), (10, 1), (9, 2)]:
            put(f, sx, sy, star)
        frames.append(f)
    return frames, 150

# ---- 2. Snowfall over a pine wood -----------------------------------------
PINES = """
....e......e........
...eee....eee.....e.
..eeeee..eeeee...eee
...eee....eee...eeee
..eeeee..eeeee.eeeee
.eeeeeee.eeeeeeeeeee
"""
@scene
def snow():
    base = blank()
    blit(base, PINES, 0, 11, X)
    for x in range(W):
        base[17][x] = SNOW; base[18][x] = SNOW if x % 3 else (200, 215, 240); base[19][x] = (200, 215, 240)
    flakes = FLAKES + [(2, 4, 2, 0), (10, 9, 2, 1), (16, 14, 2, 0), (6, 1, 2, 1)]
    N = 24
    frames = []
    for i in range(N):
        f = copy(base)
        snowfall(f, i, N, flakes)
        frames.append(f)
    return frames, 130

# ---- 3. Santa ----------------------------------------------------------------
SANTA = """
...........WW.......
........RRRWW.......
.......RRRRR........
......RRRRRRR.......
.....RRRRRRRRR......
....RRRRRRRRRRR.....
...WWWWWWWWWWWWW....
...WWWWWWWWWWWWW....
....SSSSSSSSSSS.....
....SSkSSSSSkSS.....
....SUSSSSSSSUS.....
...WWSSSSUSSSSWW....
..WWWWSSSSSSSWWWW...
..WWWWWWWRRWWWWWW...
..WWWWWWWWWWWWWWW...
...WWWWWWWWWWWWW....
....WWWWWWWWWWW.....
.....WWWWWWWWW......
......WWWWWWW.......
.......WWWWW........
"""
@scene
def santa():
    pal = dict(X); pal['S'] = (250, 200, 160)
    base = full(SANTA, pal)
    def frame(eyes='open', pom=0):
        f = copy(base)
        if eyes in ('blink', 'wink'):
            put(f, 6, 9, pal['S'])
            if eyes == 'blink':
                put(f, 12, 9, pal['S'])
        if pom:
            for (x, y) in [(11, 0), (12, 0), (11, 1), (12, 1)]:
                put(f, x, y, (0, 0, 0))
            for (x, y) in [(12, 0), (13, 0), (12, 1), (13, 1)]:
                put(f, x, y, X['W'])
            put(f, 11, 1, X['R'])
        return f
    sched = [(('open', 0), 1500), (('blink', 0), 120), (('open', 1), 700), (('open', 0), 700),
             (('wink', 1), 500), (('open', 0), 1200), (('blink', 0), 120), (('open', 1), 600)]
    return [frame(*a) for a, _ in sched], [d for _, d in sched]

# ---- 4. Gifts: the top box pops open ---------------------------------------
GIFTS = """
....................
....................
....................
.........Y.Y........
........YYYYY.......
......RRRRYRRRR.....
......RRRRYRRRR.....
......YYYYYYYYY.....
......RRRRYRRRR.....
......RRRRYRRRR.....
......RRRRYRRRR.....
....................
.BBBWBBBB.GGGGRGGGG.
.BBBWBBBB.GGGGRGGGG.
.WWWWWWWW.RRRRRRRRR.
.BBBWBBBB.GGGGRGGGG.
.BBBWBBBB.GGGGRGGGG.
.BBBWBBBB.GGGGRGGGG.
.BBBWBBBB.GGGGRGGGG.
....................
"""
@scene
def gifts():
    base = full(GIFTS, X)
    def frame(lift=0, glow=False, spark=()):
        f = copy(base)
        if lift:
            for y in range(3, 8):           # bow + lid rows move up
                for x in range(6, 15):
                    f[y][x] = (0, 0, 0)
            for y in range(3, 8):
                for x in range(6, 15):
                    c = base[y][x]
                    if c != (0, 0, 0):
                        put(f, x, y - lift, c)
            if glow:
                for x in range(7, 14):
                    put(f, x, 8 - lift + 1, X['M'] if x % 2 else X['Y'])
        for (x, y) in spark:
            put(f, x, y, X['W'])
        return f
    sp = [(4, 4), (16, 3), (3, 9), (17, 8), (10, 1)]
    sched = [((0, False, ()), 1200), ((1, True, ()), 120), ((2, True, sp[:2]), 120), ((3, True, sp), 900),
             ((3, True, sp[2:]), 400), ((2, True, ()), 120), ((1, True, ()), 120), ((0, False, ()), 1500),
             ((0, False, sp[1:3]), 300), ((0, False, ()), 400)]
    return [frame(*a) for a, _ in sched], [d for _, d in sched]

# ---- 5. Reindeer with a glowing nose ----------------------------------------
REINDEER = """
..N.....N..N.....N..
..NN...N....N...NN..
...N..N......N..N...
...NN.N......N.NN...
....NNN......NNN....
.....N........N.....
.....N..NNNN..N.....
.....NNNNNNNNNN.....
......NNNNNNNN......
......NWkNNkWN......
......NNNNNNNN......
.......NNNNNN.......
.......NNNNNN.......
.......NSSSSN.......
......NSSZZSSN......
......NSSZZSSN......
.......SSSSSS.......
.......SkSSkS.......
....................
....................
"""
@scene
def reindeer():
    N = 16
    frames = []
    for i in range(N):
        t = 0.5 + 0.5 * math.sin(2 * math.pi * i / N)
        pal = dict(X); pal['Z'] = lerp((200, 0, 0), (255, 120, 120), t); pal['S'] = (235, 200, 150)
        f = full(REINDEER, pal)
        if t > 0.55:                                     # glow halo
            halo = lerp((0, 0, 0), (200, 40, 40), (t - 0.55) / 0.45)
            for (x, y) in [(8, 14), (11, 14), (8, 15), (11, 15), (9, 13), (10, 13), (9, 16), (10, 16)]:
                if f[y][x] == pal['S']:
                    f[y][x] = lerp(pal['S'], (255, 120, 120), (t - 0.55) / 0.45 * 0.8)
        if i == 11:
            put(f, 7, 9, X['N']); put(f, 8, 9, X['N']); put(f, 11, 9, X['N']); put(f, 12, 9, X['N'])
        frames.append(f)
    return frames, 120

# ---- 6. Snowman in the snow --------------------------------------------------
SNOWMAN = """
....................
.......DDDDDD.......
.......DDDDDD.......
.......DRRRRD.......
.....DDDDDDDDDD.....
.......WWWWWW.......
......WWkWWkWW......
......WWWOOWWW......
......WkWWWWkW......
.......WkkkkW.......
.....RRRRRRRRRR.....
....RRWWWWWWWWWW....
...NRRWWWWkWWWWWN...
..N.RRWWWWWWWWWW.N..
.N..RRWWWWkWWWWW..N.
....WWWWWWWWWWWW....
...WWWWWWWWWWWWWW...
..WWWWWWWWkWWWWWWW..
..WWWWWWWWWWWWWWWW..
IIIIIIIIIIIIIIIIIIII
"""
@scene
def snowman():
    pal = dict(X); pal['W'] = SNOW; pal['I'] = (200, 215, 240)
    base = full(SNOWMAN, pal)
    N = 24
    frames = []
    for i in range(N):
        f = copy(base)
        if i % 12 >= 6:                                  # scarf tail flutters
            for y in (13, 14):
                f[y][5] = (0, 0, 0); put(f, 3, y, X['R'])
        if i in (9, 21):
            put(f, 8, 6, SNOW); put(f, 11, 6, SNOW)
        snowfall(f, i, N, FLAKES[:7])
        frames.append(f)
    return frames, 150

# ---- 7. Scrolling "MERRY CHRISTMAS" ------------------------------------------
FONT = dict(hw.FONT)
FONT.update({
    'M': ["X...X", "XX.XX", "X.X.X", "X...X", "X...X", "X...X", "X...X"],
    'R': ["XXXX.", "X...X", "X...X", "XXXX.", "X.X..", "X..X.", "X...X"],
    'C': [".XXXX", "X....", "X....", "X....", "X....", "X....", ".XXXX"],
    'T': ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
    'S': [".XXXX", "X....", "X....", ".XXX.", "....X", "....X", "XXXX."],
    'I': ["XXX", ".X.", ".X.", ".X.", ".X.", ".X.", "XXX"],
    '*': ["..X..", "..X..", "XXXXX", ".XXX.", "XXXXX", "..X..", "..X.."],
})
@scene
def merry():
    text = "* MERRY CHRISTMAS *"
    strip = [[] for _ in range(7)]
    for n, ch in enumerate(text):
        g = FONT[ch]
        c = X['Y'] if ch == '*' else (X['R'] if n % 2 else X['G'])
        for r in range(7):
            strip[r] += [c if px == 'X' else None for px in g[r]] + [None]
    width = len(strip[0])
    frames = []
    for off in range(width + W):
        f = blank()
        for r in range(7):
            for x in range(W):
                sx = x + off - W
                if 0 <= sx < width and strip[r][sx]:
                    put(f, x, 6 + r, strip[r][sx])
        snowfall(f, off, 24, FLAKES[:6], cols=((90, 100, 130),))
        frames.append(f)
    return frames, 70

# ---- 8. Candy cane with barber-pole stripes ----------------------------------
CANE = """
........XXXXX.......
.......XXXXXXX......
......XXX...XXX.....
......XX.....XX.....
......XX.....XX.....
.............XX.....
.............XX.....
.............XX.....
.............XX.....
.............XX.....
.............XX.....
.............XX.....
.............XX.....
.............XX.....
.............XX.....
.............XX.....
.............XX.....
.............XX.....
.............XX.....
.............XX.....
"""
@scene
def candycane():
    rows = rows_of(CANE)
    N = 6
    frames = []
    for i in range(N):
        f = blank()
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch == 'X':
                    f[y][x] = X['R'] if ((x + y + i) // 3) % 2 else SNOW
        for (x, y) in [(2, 16), (3, 15), (4, 16), (3, 17), (4, 17), (5, 17), (2, 18), (4, 18)]:   # holly
            put(f, x, y, X['E'])
        for (x, y) in [(3, 16), (4, 15)]:
            put(f, x, y, X['R'])
        frames.append(f)
    return frames, 150

# ---- 9. Cardinal on a snowy branch -------------------------------------------
CARDINAL = """
....................
....................
....................
....................
.........R..........
........RRR.........
.......RRRRR........
......RRRRRRR.......
......RkRRRRR.......
.....OkkRRRRRR......
......RRRRRRRRR.....
......RRRRRRRRRR....
.......RRRRRRRRRR...
........RRRRR..RRR..
.........RRR....RR..
..........n.n.......
WWWWWWWWWWWWWWWWWWWW
NNNNNNNNNNNNNNNNNNNN
nnnnnnnnnnnnnnnnnnnn
....................
"""
@scene
def cardinal():
    pal = dict(X); pal['W'] = SNOW; pal['R'] = (230, 20, 20)
    base = full(CARDINAL, pal)
    put(base, 7, 8, X['W'])                              # eye ring
    N = 24
    frames = []
    for i in range(N):
        f = copy(base)
        if i % 8 == 5:                                   # tail flick
            for (x, y) in [(15, 13), (16, 13), (17, 13), (16, 14), (17, 14)]:
                f[y][x] = (0, 0, 0)
            for (x, y) in [(15, 12), (16, 12), (17, 12), (16, 11), (17, 11)]:
                put(f, x, y, pal['R'])
        if i == 14:
            put(f, 7, 8, pal['R'])
        snowfall(f, i, N, FLAKES[:6])
        frames.append(f)
    return frames, 140

# ---- 10. Jingle bells swinging ----------------------------------------------
BELL = """
..YYY..
.YYYYY.
.YYYYY.
.YYYYY.
YYYYYYY
YYYYYYY
.YYYYY.
...y...
"""
@scene
def bells():
    N = 16
    frames = []
    for i in range(N):
        f = blank()
        for (x, y) in [(8, 0), (9, 0), (10, 0), (11, 0), (7, 1), (8, 1), (11, 1), (12, 1), (9, 2), (10, 2), (8, 3), (11, 3)]:
            put(f, x, y, X['R'])
        for k, bx in enumerate((2, 11)):
            s = math.sin(2 * math.pi * i / N + k * math.pi)
            pal = dict(X); pal['Y'] = (255, 200, 0) if (k + i // 4) % 2 else (255, 215, 60); pal['y'] = X['n']
            dx = round(2 * s)
            for r, row in enumerate(rows_of(BELL)):       # shear: bottom rows swing furthest
                ox = round(dx * r / 7)
                for c, ch in enumerate(row):
                    if ch != '.':
                        put(f, bx + c + ox, 9 + r, pal[ch])
            for y in range(3, 9):                        # ribbon from the bow to the bell
                put(f, round(9.5 + (bx + 3 - 9.5) * (y - 2) / 7), y, X['R'])
        if i % 8 == 0:
            for (x, y) in [(0, 10), (19, 10), (1, 8), (18, 8)]:
                put(f, x, y, X['W'])
        frames.append(f)
    return frames, 120

# ---- 11. Gingerbread man dancing --------------------------------------------
GINGER = ["""
.......QQQQQQ.......
......QQQQQQQQ......
.....QQkQQQQkQQ.....
.....QQQQQQQQQQ.....
.....QQWQQQQWQQ.....
......QQWWWWQQ......
.......QQQQQQ.......
..QQQQQQQQQQQQQQQQ..
.QWQQQQQQRQQQQQQQWQ.
.QQQ..QQQQQQQQ..QQQ.
......QQQGQQQQ......
......QQQQQQQQ......
......QQQRQQQQ......
......QQQQQQQQ......
.....QQQQQQQQQQ.....
....QQQQ....QQQQ....
....QWQQ....QQWQ....
...QQQQQ....QQQQQ...
....................
....................
""", """
..QQ...........QQ...
.QWQ...QQQQQQ...QWQ.
.QQQ..QQQQQQQQ..QQQ.
..QQ.QQkQQQQkQQ.QQ..
..QQ.QQQQQQQQQQ.QQ..
..QQ.QQWQQQQWQQ.QQ..
..QQ..QQWWWWQQ..QQ..
..QQQ..QQQQQQ..QQQ..
...QQQQQQQQQQQQQQ...
.....QQQQQQQRQQ.....
......QQQGQQQQ......
......QQQQQQQQ......
......QQQRQQQQ......
......QQQQQQQQ......
.....QQQQQQQQQQ.....
....QQQQ....QQQQ....
...QQWQQ....QQWQQ...
..QQQQQ......QQQQQ..
....................
....................
"""]
@scene
def gingerbread():
    pal = dict(X); pal['W'] = SNOW
    a, b = full(GINGER[0], pal), full(GINGER[1], pal)
    sched = [(a, 500), (b, 500), (a, 500), (b, 500), (a, 250), (b, 250), (a, 250), (b, 250)]
    return [f for f, _ in sched], [d for _, d in sched]

# ---- 12. Northern lights over a pine wood ----------------------------------
@scene
def aurora():
    rnd = random.Random(42)
    N = 40
    stars = [(rnd.randrange(W), rnd.randrange(0, 13)) for _ in range(9)]
    ramps = [[(0, 0, 0), (0, 45, 25), (0, 95, 50), (0, 150, 75), (30, 210, 110), (140, 245, 190)],     # green
             [(0, 0, 0), (0, 40, 45), (0, 85, 95), (10, 135, 150), (60, 195, 210), (170, 240, 245)],   # teal
             [(0, 0, 0), (28, 0, 50), (65, 0, 110), (115, 15, 175), (165, 60, 225), (215, 150, 255)]]  # purple
    frames = []
    for i in range(N):
        f = blank()
        t = 2 * math.pi * i / N
        for k, (sx, sy) in enumerate(stars):
            if (i + k * 4) % N < N - 6:
                put(f, sx, sy, (120, 120, 150))
        for x in range(W):
            bottom = 10.5 + 1.8 * math.sin(x / 4.5 + t) + 0.8 * math.sin(x / 2.2 - 2 * t)
            height = 6.5 + 2.5 * math.sin(x / 3.5 - t)
            bright = 0.65 + 0.35 * math.sin(x / 2.0 + 3 * t)
            hue = 0.5 + 0.5 * math.sin(x / 6.0 - t)                 # 0 green .. 1 purple
            ramp = ramps[min(2, int(hue * 3))]
            for y in range(0, 14):
                u = (y - (bottom - height)) / height               # 0 at the top, 1 at the bright lower edge
                if u < 0 or u > 1:
                    continue
                v = (u ** 1.6) * bright * (1 - max(0.0, (y - bottom + 1.0)))
                lvl = min(5, int(v * 6.5))
                if lvl > 0:
                    f[y][x] = ramp[lvl]
        blit(f, PINES, 0, 14, X)
        frames.append(f)
    return frames, 120

# ---- 13. Wreath with twinkling lights ---------------------------------------
@scene
def wreath():
    rnd = random.Random(12)
    CX, CY = 9.5, 9.0
    base = blank()
    for y in range(H):
        for x in range(W):
            r = math.hypot(x - CX, y - CY)
            if 5.0 <= r <= 8.6:
                base[y][x] = X['E'] if rnd.random() < 0.65 else X['e']
    for (x, y) in [(8, 16), (9, 16), (10, 16), (11, 16), (7, 17), (8, 17), (11, 17), (12, 17), (9, 15), (10, 15),
                   (8, 18), (12, 18), (7, 19), (13, 19)]:
        put(base, x, y, X['R'])
    berries = [(5, 3), (13, 2), (16, 7), (3, 11), (15, 13), (6, 15), (2, 6), (17, 11), (10, 1), (9, 17)]
    lights = [(9, 1), (14, 4), (17, 9), (14, 14), (4, 14), (2, 9), (4, 4), (12, 16), (6, 2), (16, 6)]
    N = 16
    frames = []
    for i in range(N):
        f = copy(base)
        for (x, y) in berries:
            put(f, x, y, X['R'])
        for k, (x, y) in enumerate(lights):
            ph = (i + k * 3) % N
            put(f, x, y, X['W'] if ph < 4 else (X['Y'] if ph < 9 else (90, 70, 0)))
        frames.append(f)
    return frames, 150

# ---- 14. Santa's sleigh crossing the moon -----------------------------------
SLEIGH = """
XX.X.....XX.X.........XX
.XXX......XXX.........XX
..XXXXXXX..XXXXXXXXXXXXX
..X....X...X....X..XXXXX
...................XX...XX
"""
@scene
def sleigh():
    base = blank()
    disc(base, 9.5, 9.5, 8.6, X['M'])
    for (x, y) in [(6, 5), (7, 5), (13, 12), (12, 13), (13, 13), (8, 15), (4, 10), (14, 6)]:
        put(base, x, y, (225, 165, 30))
    for s in [(0, 1), (2, 18), (18, 0), (19, 17), (1, 12), (18, 7), (10, 0), (0, 19)]:
        put(base, s[0], s[1], X['w'])
    rows = rows_of(SLEIGH)
    N = 46
    frames = []
    for i in range(N):
        f = copy(base)
        x0 = 21 - i
        y0 = 7 + round(1.2 * math.sin(2 * math.pi * i / 10))
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch != 'X':
                    continue
                x, y = x0 + dx, y0 + dy
                if 0 <= x < W and 0 <= y < H:
                    f[y][x] = (0, 0, 0) if base[y][x] != (0, 0, 0) else (50, 50, 75)
        put(f, x0, y0 + 1, X['R'])                       # lead reindeer's nose
        frames.append(f)
    return frames, 130

# ---- 15. Penguin in a Santa hat ---------------------------------------------
PENGUIN = """
....................
........RRRR........
.......RRRRRW.......
......WWWWWWW.......
......DDDDDDDD......
.....DDWWDDWWDD.....
.....DDWkDDWkDD.....
.....DDDDOODDDD.....
......DDDOODDD......
.....DDWWWWWWDD.....
....DDDWWWWWWDDD....
...DDDDWWWWWWDDDD...
..DDDDDWWWWWWDDDDD..
..DD.DDWWWWWWDD.DD..
.....DDWWWWWWDD.....
.....DDDWWWWDDD.....
......DDDDDDDD......
.......OOO.OOO......
......OOOO.OOOO.....
IIIIIIIIIIIIIIIIIIII
"""
@scene
def penguin():
    pal = dict(X); pal['W'] = SNOW; pal['I'] = (190, 210, 240)
    base = full(PENGUIN, pal)
    def frame(dx=0, lean=0, blink=False):
        f = blank()
        for y in range(H):
            for x in range(W):
                c = base[y][x]
                if c == (0, 0, 0) or y == 19:
                    continue
                put(f, x + dx + (lean if y < 9 else 0), y, c)
        for x in range(W):
            f[19][x] = pal['I']
        if blink:
            put(f, 8 + dx + lean, 6, pal['W']); put(f, 12 + dx + lean, 6, pal['W'])
        return f
    sched = [((0, 0), 400), ((-1, -1), 400), ((0, 0), 400), ((1, 1), 400), ((0, 0), 400), ((-1, -1), 400),
             ((0, 0, True), 120), ((0, 0), 900), ((1, 1), 400), ((0, 0), 400)]
    return [frame(*a) for a, _ in sched], [d for _, d in sched]

# ---- 16. Hot cocoa with marshmallows ----------------------------------------
COCOA = """
....................
....................
....................
....................
....................
....................
....................
....................
...nNNNNNNNNNNNn....
...RRRRRRRRRRRRRRRR.
...RRRRRRRRRRRRR..R.
...RRRWRRRWRRRRR..R.
...RRWWWRWWWRRRR..R.
...RRRWRRRWRRRRR..R.
...RRRRRRRRRRRRRRRR.
...RRRRRRRRRRRRR....
....RRRRRRRRRRR.....
.....RRRRRRRRR......
..wwwwwwwwwwwwwwww..
....wwwwwwwwww......
"""
@scene
def cocoa():
    pal = dict(X); pal['N'] = (120, 60, 20); pal['n'] = (70, 32, 8); pal['R'] = (220, 20, 30); pal['W'] = SNOW
    base = full(COCOA, pal)
    for (x, y) in [(5, 8), (6, 8), (9, 8), (10, 8), (13, 8)]:        # marshmallows floating on top
        put(base, x, y, SNOW)
    for (x, y) in [(12, 7), (12, 6), (12, 5), (12, 4), (13, 4)]:     # candy cane handle
        put(base, x, y, X['R'] if (y // 1) % 2 else SNOW)
    N = 12
    frames = []
    for i in range(N):
        f = copy(base)
        for k, cx in enumerate((6, 9)):
            for y in range(1, 8):
                if (y + i + k) % 4 == 0:
                    continue
                x = cx + round(1.1 * math.sin((y + i * 0.9) / 1.6 + k * 2.1))
                b = 0.2 + 0.8 * (y / 7)
                if f[y][x] == (0, 0, 0):
                    put(f, x, y, scale((210, 210, 235), b))
        frames.append(f)
    return frames, 130

# ---- 17. Ornaments swinging from a bough ------------------------------------
BAUBLE = """
..y..
.yyy.
.XXX.
XXWXX
XXXXX
.XXX.
"""
@scene
def ornaments():
    base = blank()
    for x in range(W):
        base[0][x] = X['E'] if x % 2 else X['e']
        if x % 3 == 0:
            base[1][x] = X['e']
    N = 20
    frames = []
    baubles = [(3, 9, X['R'], 0.0), (9, 12, X['B'], 2.1), (15, 8, X['P'], 4.2)]
    for i in range(N):
        f = copy(base)
        for (bx, by, col, ph) in baubles:
            dx = round(1.6 * math.sin(2 * math.pi * i / N + ph))
            for y in range(1, by):
                put(f, round(bx + dx * (y / by)), y, (150, 150, 170))
            pal = dict(X); pal['X'] = col; pal['y'] = X['M']; pal['W'] = X['W']
            blit(f, BAUBLE, bx + dx - 2, by, pal)
        frames.append(f)
    return frames, 110

# ---- 18. Fireplace with stockings -------------------------------------------
HEARTH = """
....................
.RGEGEGEGEGEGEGEGER.
nnnnnnnnnnnnnnnnnnnn
.WW..NnNnNnNnN..WW..
.RR..nNnNnNnNn..GG..
.RR..NnN.....N..GG..
.RRR.nNn.....n..GGG.
..RR.NnN.....N..GG..
.....nNn.....n......
.....NnN.....N......
.....nNn.....n......
.....NnN.....N......
.....nNn.....n......
.....NnN.....N......
.....nNn.....n......
.....NnNnNnNnN......
.....nNnNnNnNn......
..wwwwwwwwwwwwwww...
....................
....................
"""
@scene
def fireplace():
    rnd = random.Random(5)
    pal = dict(X); pal['N'] = (170, 70, 40); pal['n'] = (110, 40, 25); pal['W'] = SNOW
    base = full(HEARTH, pal)
    FW, FH, MAXH = 5, 12, 20                             # firebox cols 8-12, rows 3-14
    stops = [(0, (0, 0, 0)), (4, (90, 0, 0)), (8, (220, 20, 0)), (13, (255, 100, 0)), (17, (255, 190, 0)), (20, (255, 255, 170))]
    def heat2col(h):
        h = max(0, min(MAXH, h))
        for (a, ca), (b, cb) in zip(stops, stops[1:]):
            if a <= h <= b:
                return lerp(ca, cb, (h - a) / (b - a))
        return stops[-1][1]
    heat = [[0] * FW for _ in range(FH)]
    for x in range(FW):
        heat[FH - 1][x] = MAXH
    def step():
        for y in range(1, FH):
            for x in range(FW):
                dx = x - rnd.randint(0, 2) + 1
                dec = rnd.choice([0, 1, 2, 2, 3, 4])
                if 0 <= dx < FW:
                    heat[y - 1][dx] = max(0, heat[y][x] - dec)
    for _ in range(30):
        step()
    N = 24
    frames = []
    for i in range(N):
        step()
        f = copy(base)
        for y in range(FH):
            for x in range(FW):
                f[3 + y][8 + x] = heat2col(round(heat[y][x]))
        blit(f, "nNNn.\n.nNNn", 8, 13, pal)                   # logs
        put(f, 1, 1, X['Y'] if i % 6 < 3 else X['R']); put(f, 18, 1, X['R'] if i % 6 < 3 else X['Y'])
        frames.append(f)
    return frames, 90

# ---- 19. Snowflake crystallising --------------------------------------------
@scene
def snowflake():
    CX = CY = 9.5
    def frame(L, bright=1.0):
        f = blank()
        for k in range(6):
            a = math.radians(k * 60)
            for r in range(0, int(L * 10)):
                rr = r / 10
                x, y = CX + rr * math.cos(a), CY + rr * math.sin(a)
                put(f, round(x), round(y), scale(X['b'] if rr < 3 else SNOW, bright))
                for br in (3.5, 6.5):                         # side branches
                    if rr >= br and rr - br < 2.6 and L > br:
                        for s in (-1, 1):
                            bl = min(rr - br, L - br)
                            ba = a + s * math.radians(60)
                            put(f, round(x - (rr - br) * math.cos(a) + bl * math.cos(ba)),
                                round(y - (rr - br) * math.sin(a) + bl * math.sin(ba)), scale(SNOW, bright * 0.8))
        put(f, 9, 9, X['W']); put(f, 10, 10, X['W']); put(f, 9, 10, X['W']); put(f, 10, 9, X['W'])
        return f
    frames, durs = [], []
    for L in [1, 2, 3, 4, 5, 6, 7, 8, 9.4]:
        frames.append(frame(L)); durs.append(110)
    for i in range(8):
        frames.append(frame(9.4, 0.75 + 0.25 * math.sin(math.pi * i / 4))); durs.append(220)
    for b in (0.6, 0.3):
        frames.append(frame(9.4, b)); durs.append(110)
    return frames, durs

# ---- 20. Baby in the manger under the star --------------------------------
MANGER = """
.........Y..........
........YYY.........
......YYYYYYY.......
........YYY.........
.........Y..........
....................
....................
....................
....................
....................
....................
.....SSSS.WWWWWWW...
....SSnSnSWWWWWWWW..
....SSSSSSWWWWWWWW..
.....SSSS.WWWWWWW...
...yyyyyyyyyyyyyyy..
..NNNNNNNNNNNNNNNNN.
...NnNNnNNnNNnNNnN..
....NNNNNNNNNNNNN...
...N.............N..
"""
@scene
def manger():
    pal = dict(X); pal['S'] = (250, 205, 165); pal['W'] = SNOW; pal['y'] = (230, 180, 40); pal['n'] = (120, 70, 30)
    base = full(MANGER, pal)
    N = 24
    frames = []
    for i in range(N):
        f = copy(base)
        t = 0.5 + 0.5 * math.sin(2 * math.pi * i / N)
        star = lerp(X['Y'], X['W'], t)
        for (x, y) in [(9, 0), (8, 1), (9, 1), (10, 1), (6, 2), (7, 2), (8, 2), (9, 2), (10, 2), (11, 2), (12, 2),
                       (8, 3), (9, 3), (10, 3), (9, 4)]:
            put(f, x, y, star)
        for y in range(5, 11):                           # beam of light down to the manger
            put(f, 9, y, scale((255, 230, 120), 0.12 + 0.18 * t * (10 - y) / 5))
        for k, (sx, sy) in enumerate([(2, 2), (17, 1), (1, 7), (18, 6), (4, 5), (15, 8)]):
            ph = (i + k * 4) % N
            put(f, sx, sy, (150, 150, 180) if ph < 6 else (0, 0, 0))
        frames.append(f)
    return frames, 150

# ---- 21. Fireworks -----------------------------------------------------------
@scene
def fireworks():
    rnd = random.Random(99)
    N = 48
    bursts = [(0, 5, 6, X['R']), (10, 14, 5, X['Y']), (20, 9, 8, X['B']), (30, 15, 12, X['P']), (38, 4, 12, X['G'])]
    sparks = {b: [(rnd.random() * 2 * math.pi, rnd.choice([0.5, 1.0, 1.0])) for _ in range(26)] for b in range(len(bursts))}
    frames = []
    for i in range(N):
        f = blank()
        for b, (t0, bx, by, col) in enumerate(bursts):
            t = (i - t0) % N
            if t < 5:                                      # rocket climbing
                y = 19 - round((19 - by) * t / 5)
                put(f, bx, y, X['W']); put(f, bx, y + 1, (140, 140, 80)); put(f, bx, y + 2, (70, 70, 40))
            elif t < 15:
                age = t - 5
                r = 0.8 + age * 0.75
                fade = max(0.0, 1 - age / 10)
                if age == 0:
                    disc(f, bx, by, 1.5, X['W'])
                for (a, sp) in sparks[b]:
                    c = X['W'] if age < 2 else lerp((0, 0, 0), col, fade)
                    put(f, round(bx + r * sp * math.cos(a)), round(by + r * sp * math.sin(a) + age * age * 0.04), c)
        frames.append(f)
    return frames, 90

# ================================================================== main
if __name__ == '__main__':
    run(SCENES, 'preview_christmas.png', sys.argv[1:])
