"""Turn an image into a 1-bit stipple — the texture the reference renders are made of.

The look people read as "ASCII art" in those renders is not characters at all: it is a
halftone at full resolution. Characters cost you resolution (one glyph per cell); a dither
keeps every pixel and only throws away tone, which is why a face survives it.

  python3 dither.py photo.jpg --width 1400 --mode fs   --out out.png
  python3 dither.py photo.jpg --width 1400 --mode bayer --out out.png
"""
import argparse, subprocess

BAYER8 = [[0,32,8,40,2,34,10,42],[48,16,56,24,50,18,58,26],[12,44,4,36,14,46,6,38],
          [60,28,52,20,62,30,54,22],[3,35,11,43,1,33,9,41],[51,19,59,27,49,17,57,25],
          [15,47,7,39,13,45,5,37],[63,31,55,23,61,29,53,21]]


def probe(path):
    out = subprocess.run(["ffprobe","-v","error","-select_streams","v:0","-show_entries",
                          "stream=width,height","-of","csv=p=0:s=x",path],
                         capture_output=True, text=True, check=True).stdout.strip()
    w, h = out.split("x")[:2]
    return int(w), int(h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--width", type=int, default=1200)
    ap.add_argument("--mode", choices=["fs", "bayer"], default="fs")
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--contrast", type=float, default=1.0)
    ap.add_argument("--crop", help="x0,y0,x1,y1 as fractions")
    ap.add_argument("--floor", type=int, default=0,
                    help="source levels at or below this are held blank — keeps the background clean")
    ap.add_argument("--alpha", action="store_true",
                    help="write white-on-transparent, so CSS can tint it per theme")
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
    buf = bytearray(subprocess.run(["ffmpeg","-v","error","-i",a.src,"-vf",vf,
                                    "-f","rawvideo","-pix_fmt","gray","-"],
                                   capture_output=True, check=True).stdout)

    # tone curve first — a dither has no midtones to fix afterwards
    lut = [min(255, max(0, int((((v / 255) ** a.gamma) - .5) * a.contrast * 255 + 128)))
           for v in range(256)]
    px = [lut[v] for v in buf]

    keep = [v > a.floor for v in buf] if a.floor else None

    if a.mode == "bayer":
        for y in range(H):
            row = y * W
            for x in range(W):
                t = (BAYER8[y & 7][x & 7] + .5) * 4
                px[row + x] = 255 if px[row + x] > t else 0
    else:                                    # Floyd–Steinberg
        for y in range(H):
            row = y * W
            for x in range(W):
                i = row + x
                old = px[i]
                new = 255 if old > 127 else 0
                px[i] = new
                err = old - new
                if x + 1 < W:            px[i + 1]     += err * 7 // 16
                if y + 1 < H:
                    if x:                px[i + W - 1] += err * 3 // 16
                    px[i + W]                          += err * 5 // 16
                    if x + 1 < W:        px[i + W + 1] += err * 1 // 16

    bits = [min(255, max(0, px[i])) for i in range(W * H)]
    if keep:
        bits = [b if keep[i] else 0 for i, b in enumerate(bits)]

    if a.alpha:                      # white glyphs, alpha = the bit → CSS tints it
        raw = bytes(b for v in bits for b in (255, 255, 255, v))
        fmt, pix = "rgba", "rgba"
    else:
        raw, fmt, pix = bytes(bits), "gray", "gray"
    subprocess.run(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt",pix,
                    "-s",f"{W}x{H}","-i","-","-vf",f"format={fmt}","-compression_level","9",a.out],
                   input=raw, check=True)
    print(f"{W}x{H} -> {a.out}")


if __name__ == "__main__":
    main()
