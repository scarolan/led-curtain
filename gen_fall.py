#!/usr/bin/env python3
"""
Hand-drawn 20x20 pixel-art GIFs for a WLED LED curtain -- fall / Thanksgiving set.

Every image is authored at native 20x20 (ASCII pixel maps + tiny procedural
shapes); nothing is downscaled. Drawing helpers live in pixelart.py. The
non-spooky fall scenes from the Halloween set (leaves, maple, fire, coffee,
owl) are reused as-is.

Usage:  python3 gen_fall.py [scene ...]   -> gifs/*.gif + preview_fall.png
"""
import math, random, sys
from pixelart import *
import gen_halloween as hw

SCENES, scene = registry()

# extra palette entries for this set
F = dict(C)
F.update({
    'Q': (225, 105, 20),    # fox / squirrel orange
    'q': (135, 55, 10),     # dark fox
    'T': (205, 160, 85),    # dried husk tan
    'A': (160, 200, 20),    # yellow-green
    'K': (255, 120, 0),     # filling orange
    'D': (85, 85, 110),     # dark slate (crow, geese, plate)
    'h': (120, 58, 10),     # weave shadow brown
    'X': (0, 0, 0),
})

# reuse the fall-flavoured Halloween scenes
for _name in ('leaves', 'maple', 'fire', 'coffee', 'owl'):
    SCENES[_name] = hw.SCENES[_name]

# ================================================================== SCENES

# ---- 1. Cornucopia: fruit tumbles out of the horn one piece at a time -----
HORN = """
....................
....................
..............NNN...
.............NhhNN..
............NNNNhN..
...........NNNN.NN..
..........NNNNN.....
.........NNNNNN.....
........NNNNNNN.....
...NNNNNNNNNNNN.....
..NnnnNNNNNNNNN.....
.NnnnnnNNNNNNN......
.NnnnnnnNNNNN.......
.NnnnnnNNNNN........
..NnnnNNNN..........
...NNNNN............
....................
....................
....................
nnnnnnnnnnnnnnnnnnnn
"""
FRUIT = [  # (sprite, x, y, palette overrides)
    (".PP.\nPPPP\nPPPP\n.PP.\n..P.", 3, 12, {}),                         # grapes
    (".g.\nRRR\nRRR\nRRR", 0, 15, {}),                                   # apple
    (".X.\n.XX\nXXX\nXXX\n.XX", 8, 14, {'X': (200, 225, 0)}),           # pear
    ("yyy\nyyy\nyyy", 4, 16, {}),                                        # orange
    ("..n..\n.OoO.\nOOoOO\nOOoOO\n.OOO.", 12, 14, {}),                   # little pumpkin
    (".g.\nRRR\nRRR\nRRR", 17, 15, {}),                                  # second apple
]
@scene
def cornucopia():
    base = full(HORN, F)
    for y in range(H):                      # basket-weave texture on the horn
        for x in range(W):
            if base[y][x] == F['N'] and (x + y) % 2:
                base[y][x] = F['h']
    for (x, y) in [(1, 11), (1, 12), (1, 13), (2, 10), (2, 14), (3, 9), (3, 15)]:
        base[y][x] = (210, 140, 60)         # lit rim of the opening
    def frame(n, pop=False, dim=1.0):
        f = copy(base)
        for k, (art, x, y, over) in enumerate(FRUIT[:n]):
            pal = dict(F); pal.update(over)
            blit(f, art, x, y - (1 if pop and k == n - 1 else 0), pal)
        if dim < 1:
            f = [[scale(c, dim) for c in row] for row in f]
        return f
    frames, durs = [frame(0)], [700]
    for n in range(1, len(FRUIT) + 1):
        frames += [frame(n, pop=True), frame(n)]
        durs += [110, 420]
    frames += [frame(len(FRUIT))]; durs += [2600]
    for d in (0.6, 0.3):
        frames.append(frame(len(FRUIT), dim=d)); durs.append(90)
    return frames, durs

# ---- 2. Pumpkin patch under the stars with a firefly ----------------------
BIG_PUMPKIN = """
.....nn.....
....OoOoO...
..OOoOoOoOO.
.OOoOOoOOoOO
.OOoOOoOOoOO
.OOoOOoOOoOO
.OOoOOoOOoOO
.OOoOOoOOoOO
..OOoOoOoOO.
...OOoOoOO..
....OOOOO...
"""
SMALL_PUMPKIN = """
...n...
.yoyoy.
yyoyoyy
yyoyoyy
.yoyoy.
..yyy..
"""
@scene
def pumpkins():
    base = blank()
    for x in range(W):
        base[17][x] = F['g'] if x % 3 else F['G']
        base[18][x] = F['n']; base[19][x] = F['n']
    blit(base, BIG_PUMPKIN, 0, 6, F)
    blit(base, SMALL_PUMPKIN, 13, 11, F)
    for (x, y) in [(7, 5), (8, 4), (9, 4), (10, 5), (11, 6), (12, 7), (13, 8), (14, 9), (15, 10)]:
        put(base, x, y, F['g'])
    for (x, y) in [(8, 3), (9, 3), (14, 8), (14, 7)]:
        put(base, x, y, F['G'])
    stars = [(1, 0), (4, 2), (12, 1), (17, 3), (19, 0), (15, 5), (2, 4)]
    N = 24
    frames = []
    for i in range(N):
        f = copy(base)
        for k, (sx, sy) in enumerate(stars):
            ph = (i + k * 7) % N
            put(f, sx, sy, F['W'] if ph < 3 else ((120, 120, 90) if ph < 12 else (0, 0, 0)))
        fx = 15 + round(3.2 * math.sin(2 * math.pi * i / N))
        fy = 3 + round(2.2 * math.cos(2 * math.pi * i / N))
        if i % 6 < 4:
            put(f, fx, fy, F['L'])
        frames.append(f)
    return frames, 140

# ---- 3. Pumpkin pie, eaten slice by slice ---------------------------------
@scene
def pie():
    CX = CY = 9.5
    rnd = random.Random(2)
    crumbs = {(rnd.randrange(W), rnd.randrange(W)) for _ in range(28)}
    def frame(eaten):
        f = blank()
        for y in range(H):
            for x in range(W):
                dx, dy = x - CX, y - CY
                r = math.hypot(dx, dy)
                if r > 9.9:
                    continue
                f[y][x] = (50, 50, 70)                                   # plate
                if r > 9.1:
                    continue
                ang = (math.degrees(math.atan2(dx, -dy)) + 360) % 360    # 0 = top, clockwise
                slot = int(ang // 45)
                if slot < eaten:
                    if r < 8.5 and (x, y) in crumbs:
                        f[y][x] = F['N']                                  # crumbs
                    continue
                edge = min(ang % 45, 45 - ang % 45) * math.pi / 180 * r
                if edge < 0.5 and r > 1.2:
                    f[y][x] = (30, 30, 40)                               # cut line
                elif r > 6.8:
                    f[y][x] = F['N'] if int(ang // 12) % 2 else (200, 115, 40)   # crimped crust
                else:
                    f[y][x] = F['K']
        for s in range(eaten, 8):                                        # whipped cream per slice
            a = math.radians(s * 45 + 22.5)
            put(f, round(CX + 4.3 * math.sin(a)), round(CY - 4.3 * math.cos(a)), F['W'])
        return f
    frames = [frame(0)] + [frame(n) for n in range(1, 9)]
    durs = [1800] + [650] * 7 + [1100]
    return frames, durs

# ---- 4. Squirrel nibbling an acorn ----------------------------------------
SQUIRREL = """
....................
..............QQQ...
.............QQQQQ..
............QQQqQQ..
....Q.Q.....QQqqQQ..
...QQQQQ....QQqqQQ..
..QQkQQQQ...QQQqQQ..
..QQQQQQQQ..QQQQQQ..
..QQQQQQQQQ.QQQQQQ..
...QQSSSQQQQQQQQQQ..
..nnSSSSSQQQQQQQQ...
..NNSSSSSSQQQQQQ....
...QSSSSSSQQQQQ.....
...QSSSSSSQQQQQ.....
...QQSSSSQQQQQQ.....
...QQQQQQQQQQQQ.....
...QQQQQQQQQQQQ.....
..QQQQ....QQQQ......
..qqqq....qqqq......
nnnnnnnnnnnnnnnnnnnn
"""
@scene
def squirrel():
    base = full(SQUIRREL, F)
    def frame(tail_up=False, nibble=False, blink=False):
        f = blank()
        for y in range(H):
            for x in range(W):
                c = base[y][x]
                if c == (0, 0, 0):
                    continue
                ty = y
                if x >= 12 and y <= 8 and tail_up:
                    ty = y - 1
                if x <= 10 and 4 <= y <= 8 and nibble:
                    ty = y + 1
                put(f, x, ty, c)
        if blink:
            put(f, 4, 6 + (1 if nibble else 0), F['Q'])
        return f
    sched = [((False, False, False), 500), ((True, False, False), 500), ((False, False, False), 500),
             ((True, True, False), 150), ((False, False, False), 150), ((True, True, False), 150),
             ((False, False, False), 150), ((True, True, False), 150), ((False, False, True), 120),
             ((True, False, False), 600), ((False, False, False), 900), ((True, False, True), 120)]
    return [frame(*a) for a, _ in sched], [d for _, d in sched]

# ---- 5. Indian corn with twinkling kernels --------------------------------
CORN = """
.........KK.........
........KKKK........
.......KKKKKK.......
.......KKKKKK.......
......KKKKKKKK......
......KKKKKKKK......
......KKKKKKKK......
......KKKKKKKK......
......KKKKKKKK......
......KKKKKKKK......
.....TKKKKKKKKT.....
....TTKKKKKKKKTT....
...TT.TKKKKKKT.TT...
..TT..TTKKKKTT..TT..
.TT..TT.KKKK.TT..TT.
TT..TT..TKKT..TT..TT
....TT...TT...TT....
...TT.........TT....
...T...........T....
....................
"""
@scene
def corn():
    rnd = random.Random(11)
    kcols = [(210, 30, 20), (255, 200, 0), (115, 50, 20), (255, 120, 0), (110, 20, 130), (245, 205, 130)]
    rows = rows_of(CORN)
    kern = {(x, y): rnd.choice(kcols) for y, row in enumerate(rows) for x, ch in enumerate(row) if ch == 'K'}
    pal = dict(F); pal['T'] = F['T']
    base = full(CORN, pal)
    for y in range(H):                      # lighter husk highlights
        for x in range(W):
            if base[y][x] == F['T'] and (x + y) % 3 == 0:
                base[y][x] = F['S']
    N = 16
    frames = []
    for i in range(N):
        f = copy(base)
        for (x, y), c in kern.items():
            ph = (x * 5 + y * 3 + i) % N
            f[y][x] = lerp(c, (255, 255, 255), 0.45) if ph < 2 else c
        frames.append(f)
    return frames, 130

# ---- 6. Apple tree dropping apples ----------------------------------------
CANOPY = """
......XXXXXXXX......
....XXXXXXXXXXXX....
...XXXXXXXXXXXXXX...
..XXXXXXXXXXXXXXXX..
..XXXXXXXXXXXXXXXX..
.XXXXXXXXXXXXXXXXXX.
.XXXXXXXXXXXXXXXXXX.
.XXXXXXXXXXXXXXXXXX.
..XXXXXXXXXXXXXXXX..
..XXXXXXXXXXXXXXXX..
...XXXXXXXXXXXXXX...
.....XXXXXXXXXX.....
"""
TRUNK = """
........nnnn........
........NNNN........
........NNNN........
........NNNN........
.......NNNNNN.......
"""
def canopy_cells():
    return [(x, y) for y, row in enumerate(rows_of(CANOPY)) for x, ch in enumerate(row) if ch == 'X']

def ground(f):
    for x in range(W):
        f[17][x] = F['G'] if x % 4 == 1 else F['g']
        f[18][x] = F['g']
        f[19][x] = F['n']

@scene
def apples():
    rnd = random.Random(4)
    greens = [(20, 170, 20), (30, 200, 30), (70, 190, 20), (15, 140, 15)]
    base = blank()
    ground(base)
    for (x, y) in canopy_cells():
        base[y][x] = rnd.choice(greens)
    blit(base, TRUNK, 0, 12, F)
    apples_ = [(4, 5), (9, 3), (14, 6), (7, 9), (12, 9), (16, 3), (3, 8), (10, 7)]
    fall_order = [3, 6, 1]                 # which apples let go, in order
    N = 36
    drops = []                             # (frame, apple index) when each starts falling
    for k, idx in enumerate(fall_order):
        drops.append((4 + k * 9, idx))
    frames = []
    for i in range(N):
        f = copy(base)
        for k, (ax, ay) in enumerate(apples_):
            y = ay
            for (t0, idx) in drops:
                if idx == k and i >= t0:
                    t = i - t0
                    path = [ay + 1, ay + 3, ay + 6, 16, 15, 16]
                    y = min(16, path[t]) if t < len(path) else 16
                    if y > 16: y = 16
            put(f, ax, y, F['R'])
        frames.append(f)
    return frames, 140

# ---- 7. Sunflower with a visiting bee -------------------------------------
@scene
def sunflower():
    CX, CY = 9.5, 7.5
    def frame(rot, bee):
        f = blank()
        for y in range(H):
            for x in range(W):
                dx, dy = x - CX, y - CY
                r = math.hypot(dx, dy)
                if r > 7.6:
                    continue
                if r <= 3.6:
                    f[y][x] = F['n'] if (x + y) % 2 else (70, 35, 8)
                    continue
                ang = math.degrees(math.atan2(dy, dx)) + rot
                edge = min(ang % 30, 30 - ang % 30) * math.pi / 180 * r
                if edge < 0.45:
                    continue
                f[y][x] = F['Y'] if r < 6.6 else (235, 165, 0)
        for y in range(15, 20):
            f[y][9] = F['g']; f[y][10] = F['G'] if y % 2 else F['g']
        for (x, y) in [(6, 17), (7, 17), (8, 16), (12, 18), (13, 18), (11, 17)]:
            put(f, x, y, F['G'])
        if bee is not None:
            a = 2 * math.pi * bee
            bx, by = round(CX + 9 * math.cos(a)), round(CY + 0.5 + 6.5 * math.sin(a))
            put(f, bx, by, F['Y']); put(f, bx + (1 if math.cos(a) < 0 else -1), by, F['D'])
        return f
    N = 24
    return [frame(4 * math.sin(2 * math.pi * i / N), i / N) for i in range(N)], 130

# ---- 8. Wheat swaying in front of a harvest sun ---------------------------
@scene
def wheat():
    stalks = [(1, 5, 0.0), (4, 8, 1.2), (8, 4, 2.4), (11, 7, 0.6), (15, 6, 1.8), (18, 9, 3.0)]
    N = 24
    frames = []
    for i in range(N):
        f = blank()
        disc(f, 13.5, 6.5, 5.6, (255, 120, 20))
        disc(f, 13.5, 6.5, 3.2, (255, 160, 40))
        for (bx, top, ph) in stalks:
            for y in range(top, 20):
                bend = ((19 - y) / (19 - top)) ** 2
                xo = round(1.6 * math.sin(2 * math.pi * i / N + ph) * bend)
                x = bx + xo
                j = y - top
                if j < 6:
                    put(f, x, y, F['M'])
                    put(f, x + (1 if j % 2 else -1), y, (205, 150, 30))
                    if j == 0:
                        put(f, x, y - 1, (205, 150, 30))
                else:
                    put(f, x, y, (200, 130, 20))
        frames.append(f)
    return frames, 110

# ---- 9. Scarecrow and a bold crow -----------------------------------------
SCARECROW = """
....................
......yyyyyyyy......
......ynnnnnny......
....yyyyyyyyyyyy....
.......SSSSSS.......
.......SkSSkS.......
.......SSSSSS.......
.......SSkkSS.......
........SSSS........
.YBBBBBBBBBBBBBBBBY.
.YBBBBBBBBBBBBBBBBY.
Y....BBBBBBBBBB....Y
.....BBBBRBBBBB.....
.....BBBBRRBBBB.....
.....nnnnnnnnnn.....
.....NNNN..NNNN.....
.....NNNN..NNNN.....
.....NNNN..NNNN.....
....YYYYY..YYYYY....
y.y.y.y.y.y.y.y.y.y.
"""
CROW = ["D.D\n.D.", ".D.\nD.D"]
@scene
def scarecrow():
    base = full(SCARECROW, F)
    for x in range(W):                      # patch of blue plaid
        for y in range(9, 14):
            if base[y][x] == F['B'] and (x + y) % 2:
                base[y][x] = (25, 70, 190)
    path = [(19, 0), (17, 1), (15, 1), (13, 2), (11, 3), (9, 4), (7, 5), (5, 6), (3, 7), (1, 7)]
    frames, durs = [], []
    for k, (x, y) in enumerate(path):
        f = copy(base); blit(f, CROW[k % 2], x, y, F); frames.append(f); durs.append(150)
    sit = copy(base); blit(sit, "D.D\n.D.", 0, 7, F); put(sit, 1, 7, F['D']); put(sit, 1, 8, F['D'])
    frames += [sit, frame_blink(sit)]; durs += [1800, 120]
    frames += [sit]; durs += [900]
    for k, (x, y) in enumerate(reversed(path)):
        f = copy(base); blit(f, CROW[k % 2], x, y, F); frames.append(f); durs.append(130)
    frames.append(copy(base)); durs.append(1500)
    return frames, durs

def frame_blink(f):
    g = copy(f)
    for (x, y) in [(8, 5), (11, 5)]:
        put(g, x, y, F['S'])
    return g

# ---- 10. Autumn tree turning colour and shedding --------------------------
BRANCHES = """
........n..n........
.....n...nn...n.....
......n..nn..n......
.......n.nn.n.......
........nnnn........
.........nn.........
.........nn.........
"""
@scene
def tree():
    rnd = random.Random(21)
    cells = canopy_cells()
    th = {c: rnd.random() for c in cells}
    keys = [(25, 180, 25), (255, 200, 0), (255, 110, 0), (225, 20, 0), (125, 45, 10)]
    N = 64
    frames = []
    pile = {}
    for i in range(N):
        T = i / (N - 1)
        f = blank()
        ground(f)
        blit(f, BRANCHES, 0, 5, F)
        blit(f, TRUNK, 0, 12, F)
        for (x, y) in cells:
            p = round(max(0.0, T * 7.0 - th[(x, y)] * 2.8) * 4) / 4      # quantised: few colours
            if p >= 4.6:
                if (x, y) not in pile:
                    pile[(x, y)] = (rnd.randrange(W), rnd.choice(keys[1:4]))
                continue
            if p >= 4.0:
                col = scale(keys[4], 0.55)
            else:
                k = int(p)
                col = lerp(keys[k], keys[k + 1], p - k)
            f[y][x] = col
        for (px, c) in pile.values():
            if f[16][px] == (0, 0, 0):
                f[16][px] = c
        frames.append(f)
    hold = frames[-1]
    frames += [hold] * 6
    frames += [[[lerp(c, (0, 0, 0), 0.5) for c in row] for row in hold], frames[0]]
    return frames, 120

# ---- 11. Scrolling "HAPPY THANKSGIVING" in fall colours -------------------
FONT = dict(hw.FONT)
FONT.update({
    'T': ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
    'K': ["X...X", "X..X.", "X.X..", "XX...", "X.X..", "X..X.", "X...X"],
    'S': [".XXXX", "X....", "X....", ".XXX.", "....X", "....X", "XXXX."],
    'G': [".XXX.", "X...X", "X....", "X.XXX", "X...X", "X...X", ".XXX."],
    'I': ["XXX", ".X.", ".X.", ".X.", ".X.", ".X.", "XXX"],
    'V': ["X...X", "X...X", "X...X", "X...X", "X...X", ".X.X.", "..X.."],
    '*': [".....", "..X..", ".XXX.", "XXXXX", ".XXX.", "..X..", "....."],   # leaf bullet
})
@scene
def thanks():
    text = "* HAPPY THANKSGIVING *"
    cols = [F['Y'], F['O'], (235, 30, 0), (210, 110, 30)]
    strip = [[] for _ in range(7)]
    for n, ch in enumerate(text):
        g = FONT[ch]
        c = F['G'] if ch == '*' else cols[n % len(cols)]
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
        frames.append(f)
    return frames, 70

# ---- 12. Geese migrating across the harvest moon --------------------------
GOOSE = ["D.D\n.D.", ".D.\nD.D"]
@scene
def geese():
    base = blank()
    disc(base, 10, 9, 7.6, F['M'])
    for (x, y) in [(7, 6), (8, 6), (12, 11), (13, 12), (9, 13), (14, 7)]:
        put(base, x, y, (225, 170, 40))
    stars = [(1, 1), (18, 2), (2, 16), (17, 17), (0, 9), (19, 12), (5, 19)]
    N = 34
    frames = []
    for i in range(N):
        f = copy(base)
        for k, (sx, sy) in enumerate(stars):
            ph = (i + k * 5) % N
            put(f, sx, sy, F['W'] if ph < 3 else ((110, 110, 130) if ph < 14 else (0, 0, 0)))
        lx = 21 - i
        for k in range(3):
            for s in (-1, 1):
                if k == 0 and s == 1:
                    continue
                x, y = lx + 4 * k, 9 + s * 2 * k
                blit(f, GOOSE[(i // 2 + k) % 2], x, y, F)
        frames.append(f)
    return frames, 150

# ---- 13. Football sailing through the uprights ----------------------------
BALL = ["..NNN..\n.NWWWN.\n..NNN..", "...NN..\n..NWN..\n.NWN...\n.NN....", "..NN...\n..NWN..\n...NWN.\n....NN."]
@scene
def football():
    base = blank()
    for x in range(W):
        base[16][x] = F['G']; base[17][x] = F['g']; base[18][x] = F['G'] if x % 5 else F['W']; base[19][x] = F['g']
    for y in range(13, 16):
        put(base, 17, y, F['Y'])
    for x in range(15, 20):
        put(base, x, 12, F['Y'])
    for y in range(4, 12):
        put(base, 15, y, F['Y']); put(base, 19, y, F['Y'])
    N = 26
    frames = []
    for i in range(N):
        f = copy(base)
        t = i / (N - 1)
        x = round(-6 + 28 * t)
        y = round(14 - 11 * math.sin(math.pi * t))
        pal = dict(F); pal['N'] = (165, 75, 20)
        blit(f, BALL[(i // 2) % 3], x - 3, y - 1, pal)
        if 14 <= x <= 20:
            for yy in range(4, 12):
                put(f, 15, yy, F['W']); put(f, 19, yy, F['W'])
        frames.append(f)
    frames.append(copy(base))
    return frames, [110] * N + [600]

# ---- 14. Fox sitting in the leaves ----------------------------------------
FOX = """
....................
....................
....................
...Q.....Q..........
...QQ...QQ..........
...QdQ.QdQ..........
...QQQQQQQ..........
...QkQQQkQ..........
...QQQQQQQ..........
....WQdQW...........
.....WWW............
.....QQQQQQ.........
....QQWWQQQQQ.......
....QWWWWQQQQQQ.....
....QWWWWQQQQQQQ....
....QQWWQQQQQQQQQ...
....QQQQQQQQQQQQQQ..
....QQ.QQ...QQQQQQQ.
....dd.dd....QQQQWW.
....................
"""
@scene
def fox():
    rnd = random.Random(8)
    base = full(FOX, F)
    cols = [F['O'], F['Y'], (200, 40, 0), (255, 150, 0), F['N']]
    for x in range(W):
        base[19][x] = rnd.choice(cols) if rnd.random() < 0.85 else (0, 0, 0)
    TAIL_UP = "......QQ\nQQQQQWW.\n.QQQQ...\n"
    def frame(wag=False, blink=False, ear=False):
        f = copy(base)
        if wag:                              # lift the tail: rows 17-18 right of the body
            for y in (17, 18):
                for x in range(12, W):
                    f[y][x] = (0, 0, 0)
            blit(f, TAIL_UP, 12, 15, F)
        if blink:
            put(f, 4, 7, F['Q']); put(f, 8, 7, F['Q'])
        if ear:
            put(f, 9, 3, (0, 0, 0)); put(f, 10, 4, F['Q'])
        return f
    sched = [((False, False, False), 900), ((True, False, False), 350), ((False, False, False), 350),
             ((True, False, False), 350), ((False, True, False), 120), ((False, False, False), 1200),
             ((False, False, True), 180), ((False, False, False), 160), ((False, False, True), 180),
             ((False, False, False), 700), ((True, False, False), 350), ((False, True, False), 120)]
    return [frame(*a) for a, _ in sched], [d for _, d in sched]

# ---- 15. Toadstools with a passing snail ----------------------------------
MUSHROOMS = """
....................
....................
....RRRRRRR.........
..RRRRWRRRRRR.......
.RRWRRRRRRWRRR......
.RRRRRRRWRRRRR......
.RRRRWRRRRRRWR......
.....SSSS...........
.....SSSS....RRRRR..
.....SSSS...RRWRRRR.
.....SSSS...RRRRRWR.
.....SSSS.....SSS...
.....SSSS.....SSS...
.....SSSS.....SSS...
....SSSSSS....SSS...
gGggGgggGggGgggGggGg
nnnnnnnnnnnnnnnnnnnn
....................
....................
....................
"""
SNAIL = ["""
.....S.S
.NNN..S.
NNyNN.S.
NyyNNSS.
NNNNSSS.
SSSSSSS.
""", """
.....S..
.NNN..SS
NNyNN.S.
NyyNNSS.
NNNNSSS.
SSSSSSS.
"""]
@scene
def mushrooms():
    pal = dict(F); pal['S'] = (235, 200, 140)
    base = full(MUSHROOMS, pal)
    N = 56
    frames = []
    for i in range(N):
        f = copy(base)
        x = -8 + i // 2
        blit(f, SNAIL[(i // 3) % 2], x, 9, pal)
        frames.append(f)
    return frames, 180

# ================================================================== main
if __name__ == '__main__':
    run(SCENES, 'preview_fall.png', sys.argv[1:])
