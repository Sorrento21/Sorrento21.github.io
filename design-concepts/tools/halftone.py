"""Rebuild an image out of dots and code blocks.

Not characters — a character grid spends a whole cell on one glyph, which is why faces
never survive it. Here each cell gets a dot whose radius follows the ink, plus, in the
solid areas, short horizontal bars that read as blocks of code. Tone comes from three
places at once: dot size, dot alpha, and which colour band the cell falls in.

  python3 halftone.py src.png --width 1600 --cell 6 --out out.png            # tinted bands
  python3 halftone.py src.png --width 1600 --cell 6 --mono --out mask.png    # alpha mask
"""
import argparse, math, subprocess

# cool → warm, walked by cell brightness
BANDS = [(0x36, 0x6E, 0x8A), (0x3F, 0xA9, 0xC8), (0x53, 0xC9, 0xA8),
         (0x7F, 0xE4, 0x9B), (0xC8, 0xF2, 0xD8), (0xEE, 0xF8, 0xF2)]


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height", "-of", "csv=p=0:s=x", path],
                         capture_output=True, text=True, check=True).stdout.strip()
    w, h = out.split("x")[:2]
    return int(w), int(h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--cell", type=int, default=6, help="grid pitch in pixels")
    ap.add_argument("--crop", help="x0,y0,x1,y1 as fractions")
    ap.add_argument("--floor", type=int, default=44, help="source level treated as empty")
    ap.add_argument("--gamma", type=float, default=.85)
    ap.add_argument("--dot", type=float, default=1.06, help="dot radius multiplier")
    ap.add_argument("--blocks", type=float, default=.34, help="share of solid cells drawn as bars")
    ap.add_argument("--block-min", type=float, default=.5, help="ink a cell needs before it can be a bar")
    ap.add_argument("--mono", action="store_true", help="white on transparent, for CSS to tint")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    iw, ih = probe(a.src)
    x0, y0, x1, y1 = (0., 0., 1., 1.)
    if a.crop:
        x0, y0, x1, y1 = [float(v) for v in a.crop.split(",")]
    W = a.width
    H = round(W * (ih * (y1 - y0)) / (iw * (x1 - x0)))
    vf = (f"crop=iw*{x1-x0:.4f}:ih*{y1-y0:.4f}:iw*{x0:.4f}:ih*{y0:.4f},"
          f"scale={W}:{H}:flags=lanczos,format=gray")
    src = subprocess.run(["ffmpeg", "-v", "error", "-i", a.src, "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True, check=True).stdout

    cell = a.cell
    cols, rows = W // cell, H // cell
    span = max(1, 255 - a.floor)

    # ── cell ink ───────────────────────────────────────────────────────────
    ink = [0.0] * (cols * rows)
    for cy in range(rows):
        for cx in range(cols):
            s = 0
            for y in range(cy * cell, (cy + 1) * cell):
                base = y * W + cx * cell
                s += sum(src[base:base + cell])
            v = (s / (cell * cell) - a.floor) / span
            ink[cy * cols + cx] = 0.0 if v <= 0 else min(1.0, v) ** a.gamma

    buf = bytearray(W * H * 4)

    def blend(x, y, r, g, b, cov):
        if cov <= 0 or not (0 <= x < W and 0 <= y < H):
            return
        i = (y * W + x) * 4
        A = buf[i + 3] / 255
        cov = min(1.0, cov)
        na = cov + A * (1 - cov)
        if na <= 0:
            return
        for k, c in enumerate((r, g, b)):
            buf[i + k] = int((c * cov + buf[i + k] * A * (1 - cov)) / na)
        buf[i + 3] = int(na * 255)

    def colour(v):
        if a.mono:
            return (255, 255, 255)
        return BANDS[min(len(BANDS) - 1, int(v * len(BANDS)))]

    # ── code blocks: short bars across runs of solid cells ─────────────────
    taken = bytearray(cols * rows)
    if a.blocks > 0:
        for cy in range(rows):
            cx = 0
            while cx < cols:
                k = cy * cols + cx
                v = ink[k]
                if v >= a.block_min and not taken[k]:
                    # deterministic, but uneven enough to look hand-set
                    h = (cx * 73856093) ^ (cy * 19349663)
                    if (h >> 4 & 255) / 255 < a.blocks:
                        run = 2 + (h >> 12 & 3)
                        run = min(run, cols - cx)
                        while run > 1 and ink[cy * cols + cx + run - 1] < a.block_min:
                            run -= 1
                        if run >= 2:
                            r, g, b = colour(v)
                            alpha = .55 + .45 * v
                            y_top = cy * cell + int(cell * .22)
                            y_bot = cy * cell + int(cell * .78)
                            for y in range(y_top, y_bot):
                                for x in range(cx * cell, (cx + run) * cell - 1):
                                    blend(x, y, r, g, b, alpha)
                            for i in range(run):
                                taken[cy * cols + cx + i] = 1
                            cx += run
                            continue
                cx += 1

    # ── dots everywhere else ───────────────────────────────────────────────
    for cy in range(rows):
        for cx in range(cols):
            k = cy * cols + cx
            v = ink[k]
            if v <= .02 or taken[k]:
                continue
            r, g, b = colour(v)
            rad = cell * .5 * math.sqrt(v) * a.dot
            alpha = .35 + .65 * v
            ox, oy = cx * cell + cell / 2, cy * cell + cell / 2
            lo_x, hi_x = int(ox - rad - 1), int(ox + rad + 2)
            lo_y, hi_y = int(oy - rad - 1), int(oy + rad + 2)
            for y in range(lo_y, hi_y):
                dy = y + .5 - oy
                for x in range(lo_x, hi_x):
                    dx = x + .5 - ox
                    d = math.hypot(dx, dy)
                    cov = 1.0 if d <= rad - .5 else (rad + .5 - d if d <= rad + .5 else 0)
                    if cov > 0:
                        blend(x, y, r, g, b, alpha * cov)

    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba",
                    "-s", f"{W}x{H}", "-i", "-", "-compression_level", "9", a.out],
                   input=bytes(buf), check=True)
    print(f"{W}x{H}, {cols}x{rows} cells, cell {cell}px -> {a.out}")


if __name__ == "__main__":
    main()
