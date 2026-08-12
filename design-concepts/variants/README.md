# Body-map figure variants

Each variant is a dot-and-code-block halftone built by `../tools/halftone.py` from a source render
kept beside it. To put one live, copy it to `src/images/bodymap.png`, set the `width`/`height` on
the `<img>` in `src/_includes/partials/bodymap.njk`, and re-measure the five hotspot percentages in
`src/_data/body.json` against the new crop.

## A — ascii_render.c (grey-green, code column on the left)

    python3 ../tools/halftone.py bodymap-a-source.png \
      --width 1960 --cell 5 --blocks 0.30 --gamma 0.78 --floor 40 --dot 1.08 --out a.png
    ffmpeg -i a.png -vf "palettegen=max_colors=32:reserve_transparent=1" pal.png
    ffmpeg -i a.png -i pal.png -lavfi "paletteuse=dither=none" bodymap-a.png

1960 × 1881 · 392 × 376 cells · 57 KB. Source cropped from `../refs/vitruvian-modern.png`
with `crop=765:734:306:14`.

## B — blueprint (teal, code beside the figure) — **live**

    python3 ../tools/halftone.py bodymap-b-source.png \
      --width 1960 --cell 5 --blocks 0.30 --gamma 0.78 --floor 33 --dot 1.08 --out b.png
    ffmpeg -i b.png -vf "palettegen=max_colors=32:reserve_transparent=1" pal.png
    ffmpeg -i b.png -i pal.png -lavfi "paletteuse=dither=none" bodymap-b.png

1960 × 1934 · 392 × 386 cells · 63 KB. Source cropped from `../refs/vitruvian-blueprint.png`
with `crop=742:732:309:16`. Hotspots (percent of the image box):
glasses 50.0/9.8 · earphone 53.4/10.1 · neckband 50.0/17.6 · wrist 15.6/25.1 · phone 89.1/8.1.
A's were: 49.0/9.9 · 52.3/10.2 · 49.0/16.6 · 15.7/24.2 · 90.2/7.1.

## C — matrix CRT (bright green, code inside the body)

    python3 ../tools/halftone.py bodymap-c-source.png \
      --width 1960 --cell 5 --blocks 0.30 --gamma 0.78 --floor 12 --dot 1.08 --out c.png
    ffmpeg -i c.png -vf "palettegen=max_colors=32:reserve_transparent=1" pal.png
    ffmpeg -i c.png -i pal.png -lavfi "paletteuse=dither=none" bodymap-c.png

1960 × 1903 · 392 × 380 cells · 110 KB — heaviest of the three, because the source is dense and
bright almost everywhere, so few cells quantise away. Source cropped from
`../refs/vitruvian-matrix.png` with `crop=762:740:304:18`. `--floor 12`: this render sits on near
black, not on slate. Hotspots: glasses 48.7/9.5 · earphone 53.5/9.9 · neckband 48.7/17.2 ·
wrist 15.0/24.6 · phone 87.4/7.7.
