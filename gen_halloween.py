#!/usr/bin/env python3
"""
Hand-drawn 20x20 pixel-art GIFs for a WLED LED curtain -- Halloween / fall set.

Every image is authored at native 20x20: ASCII pixel maps plus a few tiny
procedural shapes (circles, a web, doom-fire). Nothing is downscaled.
Drawing helpers and the palette live in pixelart.py.

Usage:  python3 gen_halloween.py          -> gifs/*.gif + preview_halloween.png
"""
import math, random, sys
from pixelart import *

SCENES, scene = registry()

# ================================================================== SCENES

# ---- 1. Jack-o'-lantern with candle flicker --------------------------------
PUMPKIN = """
.........nn.........
.........ng.........
........gGG.........
......oOOOgOOOo.....
....oOOOOOoOOOOOo...
...oOOOoOOoOOoOOOo..
..oOOOoEOOoOOEoOOOo.
.oOOOoEEEOoOEEEoOOOo
.oOOOEEEEEoEEEEEOOOo
.oOOoOOOOEEOOOOoOOOo
.oOOoOOOEEEEOOOoOOOo
.oOOoOOOOOoOOOOoOOOo
.oOOEOOOOOoOOOOOEOOo
.oOOEEOEEEEEEEOEEOOo
..oOOEEEEOEEOEEEEOo.
..oOOOEEEEEEEEEEOOo.
...oOOOOoOOoOOOOOo..
....oOOOOoOOOOOOo...
......oOOOoOOOo.....
........oooo........
"""
@scene
def pumpkin():
    glow = [(255, 228, 70), (255, 190, 0), (255, 160, 0), (235, 115, 0)]
    seq = [1, 1, 0, 1, 2, 1, 0, 1, 1, 3, 2, 1, 0, 1, 1, 2]
    frames = []
    for s in seq:
        pal = dict(C); pal['E'] = glow[s]
        frames.append(full(PUMPKIN, pal))
    return frames, 110

# ---- 2. Ghost bobbing among purple sparkles --------------------------------
GHOST = """
....IIII....
..IIIIIIII..
.IIIIIIIIII.
.IIIIIIIIII.
III..III..II
III..III..II
IIIIIIIIIIII
IIIIIIIIIIII
IIII....IIII
IIII....IIII
IIIIIIIIIIII
IIIIIIIIIIII
IIIIIIIIIIII
"""
GHOST_TAIL = ["I.III.III.II", "II.III.III.I"]
@scene
def ghost():
    stars = [(1, 2), (17, 1), (2, 16), (18, 12), (16, 18), (1, 9), (18, 5)]
    N = 16
    frames = []
    for i in range(N):
        f = blank()
        for k, (sx, sy) in enumerate(stars):
            ph = (i + k * 3) % N
            c = C['P'] if ph < 7 else (C['W'] if ph < 9 else C['p'])
            put(f, sx, sy, c)
        y = 3 + round(2 * math.sin(2 * math.pi * i / N))
        blit(f, GHOST, 4, y)
        blit(f, GHOST_TAIL[(i // 2) % 2], 4, y + 13)
        frames.append(f)
    return frames, 110

# ---- 3. Bat flapping across a full moon ------------------------------------
BAT = ["""
X......X.X......X
XX.....XXX.....XX
XXXX...RXR...XXXX
.XXXXXXXXXXXXXXX.
...XXXXXXXXXXX...
.....XX.X.XX.....
.......XXX.......
""", """
.......X.X.......
.......XXX.......
XXXX..XRXRX..XXXX
XXXXXXXXXXXXXXXXX
.XXX.XXXXXXX.XXX.
..X...XXXXX...X..
.......XXX.......
""", """
.......X.X.......
.......XXX.......
...XXXXRXRXXXX...
.XXXXXXXXXXXXXXX.
XXX.XXXXXXXXX.XXX
X....XX.X.XX....X
.......XXX.......
"""]
@scene
def bat():
    base = blank()
    for s in [(0, 1), (2, 18), (18, 0), (19, 17), (1, 12), (18, 7), (10, 0), (0, 19)]:
        put(base, s[0], s[1], C['w'])
    disc(base, 9.5, 9.5, 8.6, C['M'])
    for (x, y) in [(6, 5), (7, 5), (13, 12), (12, 13), (13, 13), (8, 15), (4, 10)]:
        put(base, x, y, (225, 165, 30))
    pal = dict(C); pal['X'] = (0, 0, 0)
    seq = [0, 1, 2, 1]
    offs = [(1, 6), (1, 7), (2, 8), (2, 7), (2, 6), (1, 6), (1, 7), (1, 8)]
    frames = []
    for i in range(8):
        f = copy(base)
        ox, oy = offs[i]
        blit(f, BAT[seq[i % 4]], ox, oy, pal)
        frames.append(f)
    return frames, 130

# ---- 4. Spider dropping on a thread beside its web -------------------------
SPIDER = ["""
.d.www.d.
d.wwwww.d
d.wwwww.d
.wwwwwww.
d..www..d
.d.RwR.d.
.d.....d.
""", """
d..www..d
.dwwwwwd.
d.wwwww.d
.wwwwwww.
.d.www.d.
d..RwR..d
d.......d
"""]
@scene
def spider():
    base = blank()
    web = (80, 80, 105)
    cx, cy = 19.0, 0.0
    for deg in (92, 115, 135, 158, 180):
        a = math.radians(deg)
        for r in range(0, 11):
            put(base, round(cx + r * math.cos(a)), round(cy + r * math.sin(a)), web)
    for rad in (3.5, 6.5, 9.5):
        for deg in range(90, 181, 2):
            a = math.radians(deg)
            put(base, round(cx + rad * math.cos(a)), round(cy + rad * math.sin(a)), web)
    thread = (95, 95, 120)
    ys = list(range(-7, 11)) + [10, 11, 10, 10, 11, 10] + list(range(10, -8, -1))
    frames = []
    for i, y in enumerate(ys):
        f = copy(base)
        for ty in range(0, max(0, y)):
            put(f, 7, ty, thread)
        blit(f, SPIDER[i % 2], 3, y)
        frames.append(f)
    return frames, 90

# ---- 5. Skull with pulsing red eyes ----------------------------------------
SKULL = """
....................
....................
......WWWWWWWW......
....WWWWWWWWWWWW....
...WWWWWWWWWWWWWW...
..WWWWWWWWWWWWWWWW..
..WWWWWWWWWWWWWWWW..
.WWWWWWWWWWWWWWWWWW.
.WW.....WWWW.....WW.
.WW.EE..WWWW..EE.WW.
.WW.EE..WWWW..EE.WW.
.WWW...WWWWWW...WWW.
..WWWWWWW..WWWWWWW..
..WWWWWWW..WWWWWWW..
...WWWWWWWWWWWWWW...
....WWWWWWWWWWWW....
....W.WW.WW.WW.W....
....W.WW.WW.WW.W....
....................
....................
"""
@scene
def skull():
    N = 16
    frames = []
    for i in range(N):
        t = 0.5 - 0.5 * math.cos(2 * math.pi * i / N)
        pal = dict(C); pal['E'] = lerp((70, 0, 0), (255, 40, 30), t)
        frames.append(full(SKULL, pal))
    return frames, 90

# ---- 6. Witch hat under twinkling stars ------------------------------------
HAT = """
....................
..........P.........
.........PP.........
.........PPP........
........PPPP........
........PPPPP.......
.......PPPPPP.......
.......PPPPPPP......
......PPPPPPPP......
......PPPPPPPPp.....
.....PPPPPPPPPp.....
.....PPPPPPPPPPp....
....OOOOOOOOOOOO....
....OOOOOYYOOOOO....
....OOOOOYYOOOOO....
.PPPPPPPPPPPPPPPPPP.
PPPPPPPPPPPPPPPPPPPP
.pPPPPPPPPPPPPPPPPp.
....................
....................
"""
@scene
def witchhat():
    base = full(HAT)
    stars = [(2, 2), (16, 3), (3, 8), (17, 8), (1, 12), (18, 12), (6, 4), (14, 1), (9, 19), (3, 19), (16, 19)]
    N = 12
    frames = []
    for i in range(N):
        f = copy(base)
        for k, (sx, sy) in enumerate(stars):
            ph = (i + k * 5) % N
            c = C['Y'] if ph < 2 else (C['W'] if ph < 4 else ((90, 80, 40) if ph < 8 else (0, 0, 0)))
            put(f, sx, sy, c)
        frames.append(f)
    return frames, 120

# ---- 7. Falling autumn leaves ---------------------------------------------
LEAF = ["""
.X.
XXX
.X.
""", """
XX
XX
"""]
@scene
def leaves():
    rnd = random.Random(7)
    cols = [C['R'], C['O'], C['Y'], (200, 40, 0), (255, 150, 0), C['N'], (255, 60, 0)]
    N = 24
    leaves_ = []
    for k in range(8):
        leaves_.append(dict(x=rnd.randint(0, 17), y0=rnd.randint(0, 23), spd=rnd.choice([1, 1, 2]),
                            col=cols[k % len(cols)], ph=rnd.random() * 2 * math.pi, sw=rnd.choice([1, 2])))
    pile = [[rnd.choice(cols) if rnd.random() < 0.9 else (0, 0, 0) for _ in range(W)] for _ in range(2)]
    frames = []
    for i in range(N):
        f = blank()
        for x in range(W):
            f[19][x] = pile[1][x]
            if pile[0][x] != (0, 0, 0) and x % 3 != 1:
                f[18][x] = pile[0][x]
        for k, Lf in enumerate(leaves_):
            y = (Lf['y0'] + i * Lf['spd']) % 24 - 4
            x = Lf['x'] + round(Lf['sw'] * math.sin(2 * math.pi * i * Lf['spd'] / N + Lf['ph']))
            blit(f, LEAF[(i // 2 + k) % 2], x, y, {'X': Lf['col']})
        frames.append(f)
    return frames, 110

# ---- 8. Bonfire (doom-fire algorithm) --------------------------------------
@scene
def fire():
    rnd = random.Random(3)
    MAXH, FH = 24, 18
    stops = [(0, (0, 0, 0)), (4, (90, 0, 0)), (9, (220, 20, 0)), (14, (255, 100, 0)),
             (19, (255, 190, 0)), (24, (255, 255, 170))]
    def heat2col(h):
        for (a, ca), (b, cb) in zip(stops, stops[1:]):
            if a <= h <= b:
                return lerp(ca, cb, (h - a) / (b - a))
        return stops[-1][1]
    heat = [[0] * W for _ in range(FH)]
    for x in range(W):
        heat[FH - 1][x] = MAXH
    def step():
        for y in range(1, FH):
            for x in range(W):
                src = heat[y][x]
                dx = x - rnd.randint(0, 2) + 1
                dec = rnd.choice([0, 1, 1, 2, 2, 3])
                if 0 <= dx < W:
                    heat[y - 1][dx] = max(0, src - dec)
    for _ in range(40):
        step()
    grabs = []
    for _ in range(48):
        step(); grabs.append([row[:] for row in heat])
    N = 40
    frames = []
    for i in range(N):
        g = grabs[i + 8]
        if i >= 32:                       # cross-fade the tail into the head for a seamless loop
            t = (i - 31) / 9
            g2 = grabs[i - 32]
            g = [[g[y][x] * (1 - t) + g2[y][x] * t for x in range(W)] for y in range(FH)]
        f = blank()
        for y in range(FH):
            for x in range(W):
                f[y][x] = heat2col(g[y][x])
        blit(f, "..NNNNNNNNNNNNNNNN..\n.nnNNnnNNnnNNnnNNnn.", 0, 18)
        frames.append(f)
    return frames, 70

# ---- 9. Black cat silhouette on a harvest moon -----------------------------
CAT = """
.X.......X...
.XX.....XX...
.XXX...XXX...
.XXXXXXXXX...
.XEEXXXEEX...
.XXXXXXXXX...
..XXXXXXX....
...XXXXX.....
..XXXXXXX..X.
.XXXXXXXXX.XX
.XXXXXXXXX..X
.XXXXXXXXX..X
.XXXXXXXXXXXX
.XX.XXX.XX...
"""
@scene
def cat():
    base = blank()
    disc(base, 9.5, 9.5, 9.7, (255, 110, 0))
    for (x, y) in [(3, 5), (4, 5), (15, 14), (16, 15), (2, 12), (17, 6)]:
        put(base, x, y, (215, 80, 0))
    def frame(eyes):
        f = copy(base)
        pal = {'X': (0, 0, 0), 'E': (255, 230, 0) if eyes else (0, 0, 0)}
        blit(f, CAT, 3, 4, pal)
        return f
    sched = [(True, 1800), (False, 120), (True, 260), (False, 120), (True, 2600), (False, 140)]
    frames = [frame(e) for e, _ in sched]
    return frames, [d for _, d in sched]

# ---- 10. Spooky eyes blinking in the dark ----------------------------------
@scene
def eyes():
    spots = [(0, 1, 'Y'), (10, 2, 'G'), (3, 7, 'R'), (10, 10, 'O'), (1, 13, 'L'), (9, 16, 'P')]
    EYE = [".XX.", "XkkX", ".XX."]
    N = 64
    frames = []
    for i in range(N):
        f = blank()
        for k, (x, y, cc) in enumerate(spots):
            start = (k * 11) % N
            t = (i - start) % N
            L = 34
            if t >= L:
                continue
            br = (t + 1) / 4 if t < 3 else ((L - t) / 4 if t > L - 4 else 1.0)
            col = scale(C[cc], br)
            for ex in (x, x + 6):
                if t in (13, 14, 25):                                   # blink
                    for dx in range(4):
                        put(f, ex + dx, y + 1, scale(col, 0.45))
                else:
                    for dy, row in enumerate(EYE):
                        for dx, ch in enumerate(row):
                            if ch == 'X':
                                put(f, ex + dx, y + dy, col)
                            elif ch == 'k':
                                put(f, ex + dx, y + dy, scale(col, 0.12))
        frames.append(f)
    return frames, 100

# ---- 11. Frankenstein's monster --------------------------------------------
FRANK_TOP = """
....................
..dddddddddddddddd..
.dddddddddddddddddd.
.dddddddddddddddddd.
.ddGdGGGdGGGdGGGdGd.
.GGGGGGGGGGGGGGGGGG.
wwGGrRrRrGGGGGGGGGww
wwGGGGGGGGGGGGGGGGww
"""
FRANK_EYES = {
    'mid':   [".GGWWWWGGGGGGWWWWGG.", ".GGWkkWGGGGGGWkkWGG."],
    'left':  [".GGWWWWGGGGGGWWWWGG.", ".GGkkWWGGGGGGkkWWGG."],
    'right': [".GGWWWWGGGGGGWWWWGG.", ".GGWWkkGGGGGGWWkkGG."],
    'blink': [".GGGGGGGGGGGGGGGGGG.", ".GGddddGGGGGGddddGG."],
}
FRANK_BOT = """
.GGGGGGGGGGGGGGGGGG.
.GGGGGGGGggGGGGGGGG.
.GGGGGGGGggGGGGGGGG.
.GGGGGGGGGGGGGGGGGG.
..GGGGdGGdGGGdGGGG..
..GGddddddddddddGG..
..GGGGdGGdGGGdGGGG..
...GGGGGGGGGGGGGG...
....GGGGGGGGGGGG....
....................
"""
@scene
def frank():
    def frame(eyes, spark=False):
        art = FRANK_TOP.strip('\n') + '\n' + '\n'.join(FRANK_EYES[eyes]) + '\n' + FRANK_BOT.strip('\n')
        f = full(art)
        if spark:
            for (x, y, c) in [(0, 4, C['Y']), (1, 5, C['W']), (0, 8, C['W']), (19, 4, C['W']),
                              (18, 5, C['Y']), (19, 8, C['Y']), (1, 3, (255, 240, 120)), (18, 3, (255, 240, 120))]:
                put(f, x, y, c)
        return f
    sched = [('mid', 1500), ('left', 600), ('mid', 700), ('blink', 120), ('mid', 1200),
             ('mid+', 80), ('blink', 80), ('mid+', 80), ('mid', 700), ('right', 600), ('mid', 900), ('blink', 120)]
    frames = [frame(e.rstrip('+'), spark=e.endswith('+')) for e, _ in sched]
    return frames, [d for _, d in sched]

# ---- 12. Scrolling "HAPPY HALLOWEEN" with pumpkin O's ----------------------
FONT = {
    'H': ["X...X", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    'A': [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    'P': ["XXXX.", "X...X", "X...X", "XXXX.", "X....", "X....", "X...."],
    'Y': ["X...X", "X...X", ".X.X.", "..X..", "..X..", "..X..", "..X.."],
    'L': ["X....", "X....", "X....", "X....", "X....", "X....", "XXXXX"],
    'W': ["X...X", "X...X", "X...X", "X.X.X", "X.X.X", "XX.XX", "X...X"],
    'E': ["XXXXX", "X....", "X....", "XXXX.", "X....", "X....", "XXXXX"],
    'N': ["X...X", "XX..X", "X.X.X", "X..XX", "X...X", "X...X", "X...X"],
    'B': ["XXXX.", "X...X", "X...X", "XXXX.", "X...X", "X...X", "XXXX."],
    '!': ["..X..", "..X..", "..X..", "..X..", "..X..", ".....", "..X.."],
    'O': ["..g..", ".OOO.", "OOOOO", "O.O.O", "OOOOO", "O...O", ".OOO."],   # tiny jack-o'-lantern
    ' ': ["...", "...", "...", "...", "...", "...", "..."],
}
@scene
def happy():
    text = "HAPPY HALLOWEEN"
    strip = [[] for _ in range(7)]
    for ch in text:
        g = FONT[ch]
        for r in range(7):
            strip[r] += list(g[r]) + ['.']
    width = len(strip[0])
    pal = {'X': (190, 70, 255), 'O': C['O'], 'g': C['G']}
    frames = []
    for off in range(width + W):
        f = blank()
        for r in range(7):
            for x in range(W):
                sx = x + off - W
                if 0 <= sx < width and strip[r][sx] != '.':
                    put(f, x, 6 + r, pal[strip[r][sx]])
        frames.append(f)
    return frames, 70

# ---- 13. Maple leaf turning colour -----------------------------------------
MAPLE = """
.......X.......
......XXX......
.X....XvX....X.
.XX..XXvXX..XX.
.XXX.XXvXX.XXX.
..XvXXXvXXXvX..
...XXvXvXvXX...
XXXXXXXvXXXXXXX
.XXXXXXvXXXXXX.
..XXXXXvXXXXX..
...XXXXvXXXX...
....XXXvXXX....
.....XX.XX.....
.......n.......
.......n.......
.......n.......
"""
@scene
def maple():
    keys = [(30, 200, 30), (255, 200, 0), (255, 110, 0), (230, 20, 0), (130, 50, 10)]
    seq = []
    for a, b in zip(keys, keys[1:]):
        seq += [a] * 5 + [lerp(a, b, t / 5) for t in range(1, 5)]
    seq += [keys[-1]] * 5
    seq += [scale(keys[-1], 1 - t / 5) for t in range(1, 5)] + [(0, 0, 0)] * 2
    seq += [scale(keys[0], t / 5) for t in range(1, 5)]
    frames = []
    for c in seq:
        f = blank()
        pal = {'X': c, 'v': scale(c, 0.5), 'n': scale(C['N'], max(0.25, sum(c) / 600))}
        blit(f, MAPLE, 2, 2, pal)
        frames.append(f)
    return frames, 120

# ---- 14. Candy corn trio bouncing -----------------------------------------
CORN = """
..WW..
..WW..
.OOOO.
.OOOO.
YYYYYY
YYYYYY
.YYYY.
"""
@scene
def candy():
    N = 18
    frames = []
    for i in range(N):
        f = blank()
        for k in range(3):
            ph = (i + k * 6) % N
            b = abs(math.sin(math.pi * ph / N))
            y = 11 - round(6 * b)
            blit(f, CORN, 7 * k, y)
        for x in range(W):
            f[19][x] = (60, 0, 110) if x % 2 == 0 else (85, 0, 140)
        frames.append(f)
    return frames, 90

# ---- 15. Haunted house with lightning -------------------------------------
HOUSE = """
..MM................
.MMMM.....p.........
.MMMM....ppp........
..MM....ppppp.......
........ppppp.......
........pEEpp.......
........ppppp.......
.....pppppppppppp...
....pppppppppppppp..
...pppppppppppppppp.
...pppppppppppppppp.
...ppEEppppEEppEEpp.
...ppEEppppEEppEEpp.
...pppppppppppppppp.
...pppppppppppppppp.
...ppEEppOOppppEEpp.
...ppEEppOOppppEEpp.
...ppppppOOpppppppp.
gggggggggggggggggggg
gggggggggggggggggggg
"""
@scene
def house():
    rnd = random.Random(5)
    bolt = [(17, 0), (16, 1), (16, 2), (15, 3), (16, 4), (15, 5), (14, 6)]
    def frame(flash=False, dark=()):
        pal = dict(C)
        pal['E'] = (255, 190, 0) if not flash else (255, 230, 120)
        pal['O'] = (255, 90, 0)
        if flash:
            pal['.'] = (150, 150, 230); pal['g'] = (40, 60, 110); pal['M'] = (255, 240, 200)
        f = full(HOUSE, pal)
        for (x, y) in dark:
            put(f, x, y, pal['p'])
        if flash:
            for (x, y) in bolt:
                put(f, x, y, C['W'])
        return f
    windows = [[(9, 5), (10, 5)], [(5, 11), (6, 11), (5, 12), (6, 12)], [(11, 11), (12, 11), (11, 12), (12, 12)],
               [(15, 11), (16, 11), (15, 12), (16, 12)], [(5, 15), (6, 15), (5, 16), (6, 16)],
               [(15, 15), (16, 15), (15, 16), (16, 16)]]
    frames, durs = [], []
    for i in range(14):
        dark = windows[rnd.randrange(len(windows))] if rnd.random() < 0.35 else []
        frames.append(frame(dark=dark)); durs.append(220)
    frames += [frame(flash=True), frame(), frame(flash=True), frame()]
    durs += [70, 60, 90, 300]
    for i in range(6):
        dark = windows[rnd.randrange(len(windows))] if rnd.random() < 0.35 else []
        frames.append(frame(dark=dark)); durs.append(220)
    return frames, durs

# ---- 16. Owl on a branch ---------------------------------------------------
OWL_TOP = """
....................
.....N.......N......
.....NN.....NN......
.....NNNNNNNNN......
....NNNNNNNNNNN.....
"""
OWL_EYES = {
    'mid':   ["....NEEENNNEEEN.....", "....NEkENNNEkEN.....", "....NEEENONEEEN....."],
    'left':  ["....NEEENNNEEEN.....", "....NkEENNNkEEN.....", "....NEEENONEEEN....."],
    'right': ["....NEEENNNEEEN.....", "....NEEkNNNEEkN.....", "....NEEENONEEEN....."],
    'blink': ["....NNNNNNNNNNN.....", "....NnnnNNNnnnN.....", "....NNNNNONNNNN....."],
}
OWL_BOT = """
....NNNNNOONNNN.....
....NNNNNNNNNNN.....
...NNSNSNSNSNSNN....
...NNNSNSNSNSNNN....
...NNSNSNSNSNSNN....
...NNNSNSNSNSNNN....
....NNNNNNNNNNN.....
.....NNNNNNNNN......
..R...O.O.O.O...O...
.nnnnnnnnnnnnnnnnnn.
..nnnnnnnnnnnnnnnn..
....................
"""
@scene
def owl():
    def frame(eyes):
        art = OWL_TOP.strip('\n') + '\n' + '\n'.join(OWL_EYES[eyes]) + '\n' + OWL_BOT.strip('\n')
        pal = dict(C); pal['E'] = (255, 215, 0); pal['n'] = (105, 50, 10)
        return full(art, pal)
    sched = [('mid', 1500), ('left', 600), ('mid', 500), ('blink', 120), ('mid', 2000),
             ('right', 600), ('mid', 400), ('blink', 120), ('mid', 200), ('blink', 120)]
    return [frame(e) for e, _ in sched], [d for _, d in sched]


# ---- 17. Steaming mug of coffee / tea ---------------------------------------
MUG = """
....................
....................
....................
....................
....................
....................
....................
....................
...nNNNNNNNNNNNn....
...XXXXXXXXXXXXXXXX.
...XXXXXXXXXXXXX..X.
...XSSSSSSSSSSSX..X.
...XSSSSSSSSSSSX..X.
...XXXXXXXXXXXXX..X.
...XXXXXXXXXXXXXXXX.
...XXXXXXXXXXXXX....
....XXXXXXXXXXX.....
.....XXXXXXXXX......
..wwwwwwwwwwwwwwww..
....wwwwwwwwww......
"""
@scene
def coffee():
    pal = dict(C); pal['X'] = (0, 165, 175); pal['N'] = (120, 60, 20); pal['n'] = (70, 32, 8)
    base = full(MUG, pal)
    # a little maple leaf on the cream band
    for (x, y) in [(8, 11), (9, 11), (10, 11), (9, 12), (9, 10)]:
        put(base, x, y, (220, 50, 20))
    N = 12
    frames = []
    for i in range(N):
        f = copy(base)
        for k, cx in enumerate((6, 9, 12)):
            for y in range(1, 8):
                if (y + i + k) % 4 == 0:
                    continue                                   # gaps that travel upward
                x = cx + round(1.1 * math.sin((y + i * 0.9) / 1.6 + k * 2.1))
                b = 0.2 + 0.8 * (y / 7)                        # fades as it rises
                put(f, x, y, scale((210, 210, 235), b))
        frames.append(f)
    return frames, 130

# ---- 18. Tombstone with a ghost peeking from behind -----------------------
STONE = """
....................
....................
....................
.......wwwwwww......
.....wwwwwwwwwww....
....wwwwwwwwwwwww...
...wwwwwwwwwwwwwww..
...wwwwwwwwwwwwwww..
...wwwwwwwwwwwwwww..
...wwwwwwwwwwwwwww..
...wwwwwwwwwwwwwww..
...wwwwwwwwwwwwwww..
...wwwwwwwwwwwwwww..
...wwwwwwwwwwwwwww..
...wwdwwwwwwwwwwww..
...wwwdwwwwwwwwwww..
...wwwwwwwwwwwwwww..
GgGGgGGGgGGGGgGGGGgG
gggggggggggggggggggg
nnnnnnnnnnnnnnnnnnnn
"""
RIP = {'R': ["XX.", "X.X", "XX.", "X.X", "X.X"],
       'I': ["XXX", ".X.", ".X.", ".X.", "XXX"],
       'P': ["XX.", "X.X", "XX.", "X..", "X.."]}
MINI_GHOST = """
.III.
IIIII
IkIkI
IIIII
I.I.I
"""
@scene
def tombstone():
    stone = full(STONE)
    for k, ch in enumerate('RIP'):
        blit(stone, '\n'.join(RIP[ch]), 5 + k * 4, 8, {'X': (0, 0, 0)})
    stars = [(1, 1), (17, 2), (3, 4), (19, 6), (0, 9), (18, 12), (16, 0)]
    N = 32
    ghost_y = [9] * 10 + [3, 2, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 2, 3] + [9] * 6
    frames = []
    for i in range(N):
        f = blank()
        for k, (sx, sy) in enumerate(stars):
            ph = (i + k * 5) % N
            put(f, sx, sy, C['W'] if ph < 3 else ((110, 110, 130) if ph < 12 else (0, 0, 0)))
        # moon
        for (x, y) in [(15, 0), (16, 0), (14, 1), (15, 1), (16, 1), (17, 1), (15, 2), (16, 2)]:
            put(f, x, y, C['M'])
        blit(f, MINI_GHOST, 8, ghost_y[i], {'I': C['I'], 'k': (0, 0, 0)})
        for y in range(H):
            for x in range(W):
                if stone[y][x] != (0, 0, 0) or y >= 3 and 7 <= x <= 13 and y <= 16:
                    f[y][x] = stone[y][x]
        frames.append(f)
    return frames, 120

# ---- 19. Bubbling cauldron over a fire -------------------------------------
CAULDRON = """
....................
....................
....................
....................
..wwwwwwwwwwwwwwww..
.wGGGGGGGGGGGGGGGGw.
.wwwwwwwwwwwwwwwwww.
..XXXXXXXXXXXXXXXX..
.XXhXXXXXXXXXXXXXXX.
.XXhXXXXXXXXXXXXXXX.
.XXhXXXXXXXXXXXXXXX.
.XXXhXXXXXXXXXXXXXX.
..XXXXXXXXXXXXXXXX..
...XXXXXXXXXXXXXX...
....XX........XX....
....XX........XX....
....................
....................
..nnNNNNNNNNNNNNnn..
.nnnNNNNNNNNNNNNnnn.
"""
@scene
def cauldron():
    rnd = random.Random(9)
    pal = dict(C); pal['X'] = (95, 95, 125); pal['h'] = (150, 150, 185); pal['w'] = (165, 165, 195)
    base = full(CAULDRON, pal)
    N = 16
    frames = []
    fire_cols = [(255, 200, 0), (255, 120, 0), (255, 60, 0), (200, 30, 0)]
    bubbles = [(5, 0), (9, 2), (13, 1), (7, 4)]        # x, phase
    for i in range(N):
        f = copy(base)
        # surface froth
        for x in range(2, 18):
            if rnd.random() < 0.3:
                put(f, x, 5, C['L'])
        # rising bubbles pop at the top
        for (bx, ph) in bubbles:
            t = (i + ph) % 8
            if t < 5:
                put(f, bx + (t % 2), 4 - t, C['L'] if t < 4 else C['G'])
            elif t == 5:
                for (dx, dy) in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    put(f, bx + dx, 0 + dy, scale(C['L'], 0.6))
        # fire under the pot, between the legs
        for y in (14, 15, 16, 17):
            span = {14: (7, 12), 15: (6, 13), 16: (5, 14), 17: (4, 15)}[y]
            for x in range(span[0], span[1] + 1):
                centre = 1 - abs(x - 9.5) / (span[1] - span[0]) * 1.6
                p = centre * (0.9 if y >= 16 else 0.65)
                if rnd.random() < p:
                    heat = rnd.random() * 0.5 + (0.5 if y >= 16 else 0.1)
                    put(f, x, y, fire_cols[min(3, int((1 - heat) * 4))])
        frames.append(f)
    return frames, 110

# ---- 20. The Eye of Sauron -------------------------------------------------
@scene
def sauron():
    """Lidless eye wreathed in flame: fiery lens-shaped iris, black slit pupil
    that slowly scans left and right, flames licking off the top and bottom.
    Flicker comes from a periodic noise table so the loop is seamless."""
    rnd = random.Random(1_111)
    N, K = 48, 8                               # frames, noise keyframes
    tbl = [[[rnd.random() for _ in range(K)] for _ in range(H)] for _ in range(W)]
    def noise(x, y, t):                        # smooth, periodic in t over N frames
        u = (t / N) * K
        i, fr = int(u) % K, u - int(u)
        fr = fr * fr * (3 - 2 * fr)
        a, b = tbl[x % W][y % H][i], tbl[x % W][y % H][(i + 1) % K]
        return a + (b - a) * fr
    stops = [(0, (0, 0, 0)), (3, (70, 0, 0)), (7, (180, 10, 0)), (11, (255, 60, 0)),
             (15, (255, 130, 0)), (19, (255, 200, 20)), (24, (255, 250, 190))]
    def heat2col(h):
        h = max(0, min(24, h))
        for (a, ca), (b, cb) in zip(stops, stops[1:]):
            if a <= h <= b:
                return lerp(ca, cb, (h - a) / (b - a))
        return stops[-1][1]
    CX, CY, A, HC = 9.5, 10.0, 9.5, 3.8         # lens centre, half-width, half-height
    R = (A * A + HC * HC) / (2 * HC)            # radius of the two arcs forming the lens
    def half_h(x):                              # true lens (vesica) profile: pointed tips
        u = min(A, abs(x - CX))
        return max(0.0, math.sqrt(R * R - u * u) - (R - HC))
    frames = []
    for t in range(N):
        f = blank()
        px = CX + round(2.2 * math.sin(2 * math.pi * t / N))  # pupil scans in whole-pixel steps
        ph = half_h(px) - 1.3
        for x in range(W):
            hh = half_h(x)
            if hh < 0.5:
                continue
            top, bot = int(round(CY - hh)), int(round(CY + hh))
            for y in range(top, bot + 1):
                dx = (x + 0.5 - px - 0.5) / (A * 0.95)
                dy = (y - CY) / max(hh, 0.6)
                d = min(1.0, math.sqrt(dx * dx + dy * dy))
                flick = (noise(x, y, t) - 0.5) * 5
                heat = 23 - 17 * d + flick
                if y in (top, bot) or x in (int(CX - A + 0.5), int(CX + A - 0.5)):
                    heat = min(heat, 8 + flick)              # dark rim
                f[y][x] = heat2col(round(heat))
            # pupil: tapered black slit
            for y in range(top, bot + 1):
                dy = abs(y - CY)
                if dy > ph:
                    continue
                w_here = 0.98                                # clean 2-px slit
                if abs(x - px) < w_here:                     # px is n.5 -> two columns
                    f[y][x] = (0, 0, 0)
                elif abs(x - px) < w_here + 1.0:
                    f[y][x] = heat2col(round(23 + (noise(x, y, t) - 0.5) * 3))   # hot ring
            # flames licking above and below the lid
            for side, edge in ((-1, top), (1, bot)):
                fh = (0.6 + noise(x + 7 * side, 0, t)) * 2.9 * (hh / HC) ** 1.4
                for k in range(1, 5):
                    if k <= fh:
                        y = edge + side * k
                        heat = 13 - 2.8 * k + (noise(x, y, t) - 0.5) * 4
                        if 0 <= y < H:
                            f[y][x] = heat2col(round(heat))
        frames.append(f)
    return frames, 80

# ================================================================== main
if __name__ == '__main__':
    run(SCENES, 'preview_halloween.png', sys.argv[1:])
