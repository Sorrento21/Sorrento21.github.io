"""Turn a photo into character art.

ffmpeg does the decoding and resampling (raw 8-bit grey), so this stays dependency-free.
Character cells are about twice as tall as they are wide, so the row count is halved.

  python3 asciify.py photo.jpg --cols 150 --invert --gamma 1.1 --out out.json
"""
import argparse, json, subprocess, sys

# darkest → lightest. A long ramp gives smooth tone; the site renders it in one colour.
RAMP = "@%#*+=-:. "
RAMP_DENSE = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "


def grey(path, cols, rows):
    cmd = ["ffmpeg", "-v", "error", "-i", path,
           "-vf", f"scale={cols}:{rows}:flags=lanczos,format=gray",
           "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    return subprocess.run(cmd, capture_output=True, check=True).stdout


def size(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                          "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", path],
                         capture_output=True, text=True, check=True).stdout.strip()
    w, h = out.split("x")[:2]
    return int(w), int(h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("--cols", type=int, default=140)
    ap.add_argument("--aspect", type=float, default=0.5, help="cell height ÷ width")
    ap.add_argument("--invert", action="store_true", help="use when the subject is darker than the background")
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--floor", type=int, default=0, help="grey level below which a cell is left blank")
    ap.add_argument("--dense", action="store_true")
    ap.add_argument("--levels", type=int, default=5, help="brightness classes for colouring")
    ap.add_argument("--out", default="-")
    a = ap.parse_args()

    w, h = size(a.photo)
    rows = max(1, round(a.cols * h / w * a.aspect))
    buf = grey(a.photo, a.cols, rows)
    if len(buf) < a.cols * rows:
        sys.exit("ffmpeg returned less data than expected")

    ramp = RAMP_DENSE if a.dense else RAMP
    n = len(ramp) - 1

    lines, classes = [], []
    for y in range(rows):
        row = buf[y * a.cols:(y + 1) * a.cols]
        chars, cls = [], []
        for v in row:
            t = v / 255
            if a.invert:
                t = 1 - t
            t = t ** a.gamma
            ink = 1 - t                      # 1 = densest glyph, 0 = empty
            if ink * 255 <= a.floor:
                chars.append(" "); cls.append(-1); continue
            chars.append(ramp[min(n, int(ink * n + .5))])
            cls.append(min(a.levels - 1, int(ink * a.levels)))
        lines.append("".join(chars))
        classes.append(cls)

    # emit HTML, run-length grouping the brightness classes so the DOM stays small
    html = []
    for line, cls in zip(lines, classes):
        out, i = [], 0
        while i < len(line):
            j = i
            while j < len(line) and cls[j] == cls[i]:
                j += 1
            chunk = (line[i:j].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            out.append(chunk if cls[i] < 0 else f'<i class="l{cls[i]}">{chunk}</i>')
            i = j
        html.append("".join(out))
    body = "\n".join(html)
    if a.out == "-":
        print("\n".join(lines))
    else:
        open(a.out, "w").write(body)
        print(f"{a.cols}x{rows} cells -> {a.out}")


if __name__ == "__main__":
    main()
