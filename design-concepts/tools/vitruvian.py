"""Vitruvian character art.

Takes the rendered reference of Jiacheng, and

  1. mirrors one half onto the other, so both hands and both feet are identical
     — the pose is symmetric by definition, and this is what fixes the
     "every foot is at a different angle" problem;
  2. measures the landmarks (head top, fingertips of the T-pose arms, soles of
     the closed feet, fingertips of the raised arms, soles of the spread feet);
  3. re-derives the two figures Leonardo actually drew — the square touching
     head / T-fingertips / closed feet, and the circle centred on the navel
     passing through the raised fingertips and the spread feet;
  4. resamples the whole thing to a character grid and prints it as HTML.

Everything is deterministic: same input, same output, no model in the loop.
"""
import argparse, math, subprocess

RAMP = "@%#*+=-:. "                      # densest → lightest
BOX = {"h": "─", "v": "│", "tl": "┌", "tr": "┐", "bl": "└", "br": "┘"}


def grey(path, w, h, extra=""):
    vf = f"scale={w}:{h}:flags=lanczos{extra},format=gray"
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", vf,
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    return subprocess.run(cmd, capture_output=True, check=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("--cols", type=int, default=190)
    ap.add_argument("--aspect", type=float, default=0.5)
    ap.add_argument("--floor", type=int, default=18, help="ink below this is background")
    ap.add_argument("--gamma", type=float, default=0.85)
    ap.add_argument("--mirror", choices=["left", "right", "none"], default="left")
    ap.add_argument("--crop", help="x0,y0,x1,y1 as fractions — skips auto-detection")
    ap.add_argument("--navel", type=float, default=.605,
                    help="navel height as a fraction of the body height — the circle's radius")
    ap.add_argument("--pad", type=float, default=0.09, help="empty margin added round the crop")
    ap.add_argument("--dehatch", type=float, default=0.0,
                    help="strength of per-row background removal — the reference is drawn\n                          over horizontal hatching, which otherwise reads as solid bands")
    ap.add_argument("--reduce", choices=["mean", "max", "mix"], default="mix",
                    help="how a block of pixels becomes one cell; line art needs max")
    ap.add_argument("--out", required=True)
    ap.add_argument("--landmarks", help="write the hotspot anchors (percentages) here")
    a = ap.parse_args()

    # sample generously, then reduce — keeps the thin wireframe alive
    SW = a.cols * 6
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                            "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", a.photo],
                           capture_output=True, text=True, check=True).stdout.strip()
    iw, ih = (int(v) for v in probe.split("x")[:2])
    SH = round(SW * ih / iw)
    if a.crop:
        x0, y0, x1, y1 = (float(v) for v in a.crop.split(","))
    else:
        x0 = y0 = 0.0; x1 = y1 = 1.0
    # first pass: find the figure's bounding box so we can crop away the empty plate
    PW = 900
    PH = round(PW * ih / iw)
    pre = grey(a.photo, PW, PH)
    ph = [0] * 256
    for v in pre:
        ph[v] += 1
    pbg = ph.index(max(ph))
    if not a.crop:
        hit = lambda x, y: (pre[y * PW + x] - pbg) > 10
        cols_hit = [x for x in range(PW) if sum(1 for y in range(PH) if hit(x, y)) > 2]
        rows_hit = [y for y in range(PH) if sum(1 for x in range(PW) if hit(x, y)) > 2]
        x0, x1 = min(cols_hit) / PW, (max(cols_hit) + 1) / PW
        y0, y1 = min(rows_hit) / PH, (max(rows_hit) + 1) / PH
        mx, my = (x1 - x0) * .04, (y1 - y0) * .04
        x0, x1 = max(0, x0 - mx), min(1, x1 + mx)
        y0, y1 = max(0, y0 - my), min(1, y1 + my)
    SH = round(SW * (ih * (y1 - y0)) / (iw * (x1 - x0)))
    cmd = ["ffmpeg", "-v", "error", "-i", a.photo, "-vf",
           f"crop=iw*{x1-x0:.4f}:ih*{y1-y0:.4f}:iw*{x0:.4f}:ih*{y0:.4f},"
           f"scale={SW}:{SH}:flags=lanczos,format=gray",
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    buf = subprocess.run(cmd, capture_output=True, check=True).stdout
    at = lambda x, y: buf[y * SW + x]

    # background = the most common level; ink = how far above it a pixel sits
    hist = [0] * 256
    for v in buf:
        hist[v] += 1
    bg = hist.index(max(hist))
    ink = bytearray(SW * SH)
    for i, v in enumerate(buf):
        ink[i] = max(0, min(255, (v - bg) * 3))

    # pad the canvas so the circle — which reaches past the square — has room
    if a.pad > 0:
        px_, py_ = int(SW * a.pad), int(SH * a.pad)
        NW, NH = SW + 2 * px_, SH + 2 * py_
        big = bytearray(NW * NH)
        for y in range(SH):
            big[(y + py_) * NW + px_:(y + py_) * NW + px_ + SW] = ink[y * SW:(y + 1) * SW]
        ink, SW, SH = big, NW, NH

    # ── ignore the guide lines that came with the reference ────────────────
    # they are long, perfectly straight and dim; the body is not
    col_hits = [sum(1 for y in range(SH) if ink[y * SW + x] > 30) for x in range(SW)]
    row_hits = [sum(1 for x in range(SW) if ink[y * SW + x] > 30) for y in range(SH)]
    for x in range(SW):
        if col_hits[x] > SH * .55:
            for y in range(SH):
                ink[y * SW + x] = 0
    for y in range(SH):
        if row_hits[y] > SW * .55:
            for x in range(SW):
                ink[y * SW + x] = 0

    # ── strip the horizontal hatching the reference is drawn over ──────────
    if a.dehatch > 0:
        for y in range(SH):
            base = y * SW
            row = sorted(ink[base:base + SW])
            med = row[SW // 2]
            if med:
                cut = int(med * a.dehatch)
                for x in range(SW):
                    ink[base + x] = max(0, ink[base + x] - cut)

    # ── body extents and axis ──────────────────────────────────────────────
    def row_span(y, th=26):
        xs = [x for x in range(SW) if ink[y * SW + x] > th]
        return (min(xs), max(xs)) if xs else None

    spans = [row_span(y) for y in range(SH)]
    ys = [y for y in range(SH) if spans[y]]
    top, bot = min(ys), max(ys)
    axis = round(sum((spans[y][0] + spans[y][1]) / 2 for y in ys) / len(ys))

    # ── mirror for symmetry ────────────────────────────────────────────────
    if a.mirror != "none":
        for y in range(SH):
            for dx in range(0, min(axis, SW - axis)):
                src = axis - dx if a.mirror == "left" else axis + dx
                dst = axis + dx if a.mirror == "left" else axis - dx
                ink[y * SW + dst] = ink[y * SW + src]
        spans = [row_span(y) for y in range(SH)]
        ys = [y for y in range(SH) if spans[y]]
        top, bot = min(ys), max(ys)

    # ── landmarks ──────────────────────────────────────────────────────────
    upper = [y for y in ys if y < (top + bot) / 2]
    lower = [y for y in ys if y > (top + bot) * .62]
    t_row = max(upper, key=lambda y: spans[y][1] - spans[y][0])     # widest → T-pose arms
    t_left, t_right = spans[t_row]
    raised_y = min((y for y in upper if spans[y][1] - spans[y][0] > (t_right - t_left) * .45),
                   default=t_row)
    raised_left = spans[raised_y][0]
    foot_row = max(lower, key=lambda y: spans[y][1] - spans[y][0])  # widest low row → spread feet
    foot_left, foot_right = spans[foot_row]
    # the closed feet are the lowest ink near the axis
    band = int((t_right - t_left) * .06)
    closed_bot = max((y for y in ys
                      if any(ink[y * SW + x] > 26 for x in range(max(0, axis - band), min(SW, axis + band)))),
                     default=bot)

    # ── square: head ↔ closed feet, fingertip ↔ fingertip ──────────────────
    side = max(t_right - t_left, closed_bot - top)
    sq_l, sq_r = axis - side / 2, axis + side / 2
    sq_t, sq_b = top, top + side

    # ── circle: Leonardo's construction ────────────────────────────────────
    # centred on the navel and tangent to the sole line, so its radius is simply
    # the navel's height. Fitting it to the detected fingertips instead sounds
    # better but is not stable: the reference's own circle survives as ink, so
    # the extremal points move with the sampling resolution.
    cy = sq_b - a.navel * side
    r = a.navel * side

    # ── grow the canvas so the circle fits, then re-centre everything ───────
    m = side * .035
    ex = max(0, math.ceil(r + m - axis), math.ceil(axis + r + m - SW))
    ex_t = max(0, math.ceil(r + m - cy))
    ex_b = max(0, math.ceil(cy + r + m - SH))
    if ex or ex_t or ex_b:
        NW, NH = SW + 2 * ex, SH + ex_t + ex_b
        big = bytearray(NW * NH)
        for y in range(SH):
            big[(y + ex_t) * NW + ex:(y + ex_t) * NW + ex + SW] = ink[y * SW:(y + 1) * SW]
        ink, SW, SH = big, NW, NH
        axis += ex; top += ex_t; bot += ex_t; cy += ex_t
        sq_l += ex; sq_r += ex; sq_t += ex_t; sq_b += ex_t
        t_left += ex; t_right += ex; t_row += ex_t
        raised_left += ex; raised_y += ex_t
        foot_left += ex; foot_right += ex; foot_row += ex_t
        closed_bot += ex_t

    # ── resample to the character grid ─────────────────────────────────────
    cols = a.cols
    rows = max(1, round(cols * (SH / SW) * a.aspect))
    cw, ch = SW / cols, SH / rows
    cells = []
    for gy in range(rows):
        line = []
        for gx in range(cols):
            x0, x1 = int(gx * cw), max(int(gx * cw) + 1, int((gx + 1) * cw))
            y0, y1 = int(gy * ch), max(int(gy * ch) + 1, int((gy + 1) * ch))
            n = 0
            s = 0
            m = 0
            for y in range(y0, min(y1, SH)):
                base = y * SW
                for x in range(x0, min(x1, SW)):
                    v = ink[base + x]
                    s += v; n += 1
                    if v > m:
                        m = v
            mean = s / n if n else 0
            line.append(mean if a.reduce == "mean" else m if a.reduce == "max" else (mean + m) / 2)
        cells.append(line)

    peak = max(max(r_) for r_ in cells) or 1
    grid = [[" "] * cols for _ in range(rows)]
    level = [[-1] * cols for _ in range(rows)]
    for gy in range(rows):
        for gx in range(cols):
            v = (cells[gy][gx] / peak) ** a.gamma
            if v * 255 <= a.floor:
                continue
            grid[gy][gx] = RAMP[min(len(RAMP) - 1, int((1 - v) * (len(RAMP) - 1) + .5))]
            level[gy][gx] = min(4, int(v * 5))

    # ── draw the geometry into the same grid ───────────────────────────────
    to_col = lambda x: int(round(x / SW * cols))
    to_row = lambda y: int(round(y / SH * rows))

    def put(gx, gy, ch_, lv):
        if 0 <= gx < cols and 0 <= gy < rows and grid[gy][gx] == " ":
            grid[gy][gx] = ch_; level[gy][gx] = lv

    L, R = to_col(sq_l), to_col(sq_r)
    T, B = to_row(sq_t), to_row(sq_b)
    for gx in range(L + 1, R):
        put(gx, T, BOX["h"], 5); put(gx, B, BOX["h"], 5)
    for gy in range(T + 1, B):
        put(L, gy, BOX["v"], 5); put(R, gy, BOX["v"], 5)
    for gx, gy, k in ((L, T, "tl"), (R, T, "tr"), (L, B, "bl"), (R, B, "br")):
        put(gx, gy, BOX[k], 5)

    steps = int(2 * math.pi * r)
    for i in range(steps * 2):
        th = i * math.pi / steps
        put(to_col(axis + r * math.cos(th)), to_row(cy + r * math.sin(th)), "·", 5)

    # ── emit ───────────────────────────────────────────────────────────────
    out = []
    for gy in range(rows):
        line, i = [], 0
        row = grid[gy]
        while i < cols:
            j = i
            while j < cols and level[gy][j] == level[gy][i]:
                j += 1
            chunk = "".join(row[i:j]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            line.append(chunk if level[gy][i] < 0 else f'<i class="l{level[gy][i]}">{chunk}</i>')
            i = j
        out.append("".join(line))
    open(a.out, "w").write("\n".join(out))

    if a.landmarks:
        import json
        pctx = lambda x: round(x / SW * 100, 2)
        pcty = lambda y: round(y / SH * 100, 2)
        head_h = closed_bot - top
        # wrist sits a little inside the fingertip; the raised hand is the upper arm's end
        t_wrist_l = t_left + (t_right - t_left) * .07
        anchors = {
            "axis": pctx(axis),
            "head_top": pcty(top), "chin": pcty(top + head_h * .13),
            "face": {"x": pctx(axis), "y": pcty(top + head_h * .075)},
            "ear": {"x": pctx(axis + (t_right - t_left) * .028), "y": pcty(top + head_h * .075)},
            "throat": {"x": pctx(axis), "y": pcty(top + head_h * .155)},
            "wrist_left": {"x": pctx(t_wrist_l), "y": pcty(t_row)},
            "hand_raised_right": {"x": pctx(2 * axis - raised_left), "y": pcty(raised_y)},
            "square": {"l": pctx(sq_l), "r": pctx(sq_r), "t": pcty(sq_t), "b": pcty(sq_b)},
            "circle": {"cx": pctx(axis), "cy": pcty(cy), "r_x": round(r / SW * 100, 2)},
            "grid": {"cols": cols, "rows": rows},
        }
        open(a.landmarks, "w").write(json.dumps(anchors, indent=2))
        print("  landmarks ->", a.landmarks)
    print(f"{cols}x{rows} cells -> {a.out}")
    print(f"  axis={axis} top={top} closed_feet={closed_bot} t-arms={t_left}..{t_right}")
    print(f"  square side={side:.0f}  circle centre_y={cy:.0f} r={r:.0f}")


if __name__ == "__main__":
    main()
