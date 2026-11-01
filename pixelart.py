"""
Shared drawing helpers for the 20x20 LED-curtain pixel-art generators.

Everything is authored at native 20x20: ASCII pixel maps plus tiny procedural
shapes. Palette is small and saturated so every pixel reads on LEDs
(black = LED off).
"""
import math, os, subprocess
from PIL import Image

W = H = 20
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "gifs")
os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------------------------ palette
C = {
    '.': (0, 0, 0),         # off
    'O': (255, 90, 0),      # pumpkin orange
    'o': (150, 38, 0),      # dark orange (ribs / outline)
    'Y': (255, 200, 0),     # yellow
    'y': (255, 140, 10),    # amber
    'M': (255, 205, 70),    # moon gold
    'G': (20, 210, 20),     # green
    'g': (10, 95, 10),      # dark green
    'L': (150, 255, 0),     # lime
    'W': (255, 255, 255),   # white
    'I': (205, 225, 255),   # ice white (ghost)
    'w': (140, 140, 160),   # gray
    'd': (60, 60, 80),      # dark gray
    'P': (160, 20, 240),    # purple
    'p': (85, 0, 140),      # dark purple
    'R': (255, 0, 0),       # red
    'r': (130, 0, 0),       # dark red
    'B': (40, 100, 255),    # blue
    'N': (150, 75, 15),     # brown
    'n': (95, 45, 10),      # dark brown
    'S': (240, 190, 120),   # beige
    'k': (0, 0, 0),         # black that is explicitly painted (pupils)
}

# ------------------------------------------------------------------ helpers
def blank(color=(0, 0, 0)):
    return [[color] * W for _ in range(H)]

def copy(f):
    return [row[:] for row in f]

def put(f, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        f[y][x] = c

def rows_of(art):
    return art.strip('\n').split('\n')

def blit(f, art, x0=0, y0=0, pal=None, skip='.'):
    """Paint an ASCII sprite onto frame f. Chars equal to `skip` are transparent."""
    pal = pal or C
    for dy, row in enumerate(rows_of(art)):
        for dx, ch in enumerate(row):
            if ch == skip:
                continue
            put(f, x0 + dx, y0 + dy, pal[ch])

def full(art, pal=None):
    """A complete 20x20 ASCII frame ('.' painted black)."""
    rows = rows_of(art)
    assert len(rows) == H and all(len(r) == W for r in rows), \
        f"bad frame geometry: {[len(r) for r in rows]} rows={len(rows)}"
    f = blank()
    blit(f, art, 0, 0, pal, skip=None)
    return f

def disc(f, cx, cy, r, c):
    for y in range(H):
        for x in range(W):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                f[y][x] = c

def scale(c, k):
    return tuple(max(0, min(255, int(round(v * k)))) for v in c)

def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))

def save_gif(name, frames, durations):
    """Write a full-frame, global-palette GIF (safest for WLED's decoder).

    Each frame is written as its own single-image GIF, then gifsicle stitches
    them: no sub-rectangle frames, no transparency, one shared colour table.
    """
    import tempfile, shutil
    if isinstance(durations, (int, float)):
        durations = [int(durations)] * len(frames)
    colors = sorted({px for f in frames for row in f for px in row},
                    key=lambda c: (c != (0, 0, 0), c))      # black first
    assert len(colors) <= 256, f"{name}: {len(colors)} colours"
    idx = {c: i for i, c in enumerate(colors)}
    pal = bytearray()
    for c in colors:
        pal += bytes(c)
    tmp = tempfile.mkdtemp()
    args = ['gifsicle', '--loopcount=forever', '--no-interlace', '--no-warnings']
    for i, (f, d) in enumerate(zip(frames, durations)):
        im = Image.frombytes('P', (W, H), bytes(idx[px] for row in f for px in row))
        im.putpalette(bytes(pal))
        p = os.path.join(tmp, f'{i:04d}.gif')
        im.save(p, interlace=False)
        args += [f'-d{max(2, round(d / 10))}', p]
    path = os.path.join(OUT, name)
    subprocess.run(args + ['-o', path], check=True)
    shutil.rmtree(tmp)
    return path

def registry():
    """Return (scenes_dict, decorator). Decorated functions return (frames, durations_ms)."""
    scenes = {}
    def scene(fn):
        scenes[fn.__name__] = fn
        return fn
    return scenes, scene

# ------------------------------------------------------------------ output
def preview_sheet(results, path):
    """Contact sheet: 4 evenly spaced frames per scene, 8x zoom with 1px grid."""
    Z, GAP = 8, 1
    cell = W * (Z + GAP) + GAP
    cols = 4
    rows = len(results)
    sheet = Image.new('RGB', (cols * (cell + 6) + 6, rows * (cell + 6) + 6), (30, 30, 30))
    for r, (name, (frames, _)) in enumerate(results):
        picks = [frames[int(k * (len(frames) - 1) / 3)] for k in range(4)] if len(frames) > 1 else frames * 4
        for c, fr in enumerate(picks):
            tile = Image.new('RGB', (cell, cell), (18, 18, 18))
            px = tile.load()
            for y in range(H):
                for x in range(W):
                    col = fr[y][x]
                    for dy in range(Z):
                        for dx in range(Z):
                            px[GAP + x * (Z + GAP) + dx, GAP + y * (Z + GAP) + dy] = col
            sheet.paste(tile, (6 + c * (cell + 6), 6 + r * (cell + 6)))
    sheet.save(path)

def run(scenes, preview_name, only=()):
    """Render every scene (or just `only`) to gifs/ and write a contact sheet."""
    results = []
    for name, fn in scenes.items():
        if only and name not in only:
            continue
        frames, durs = fn()
        path = save_gif(name + '.gif', frames, durs)
        results.append((name, (frames, durs)))
        print(f"{name:10s} {len(frames):4d} frames  {os.path.getsize(path):6d} bytes")
    preview_sheet(results, os.path.join(HERE, preview_name))
    print(f"preview -> {preview_name}")
