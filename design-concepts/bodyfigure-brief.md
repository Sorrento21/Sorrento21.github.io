# Brief — full-body figure for the gallery body map (v2, Vitruvian pose)

What the image is for: the Gallery page opens with a figure of Jiacheng; five sensing sites
(glasses · earphone · neckband · wrist · phone hand) are clickable hotspots laid over it, and each
one reveals the papers that put a device there. So the picture has two jobs at once — **look like
him** and **behave like a diagram**.

Two changes from v1: the pose now follows **Vitruvian Man**, and the rendering must be **one single
drawing language from face to feet** — no photoreal face on a wireframe body.

---

## 1 · The prompt (paste this, attach the two reference photos)

> A stylised full-body technical study of the man in the attached reference photos — East Asian man
> in his twenties, round thin wire-frame glasses, dark hair with a swept fringe, wearing a black
> turtleneck under a dark jacket and dark trousers.
>
> **Pose — after Leonardo's Vitruvian Man:** standing upright and facing the viewer dead on,
> perfectly symmetrical, arms extended straight out to both sides at shoulder height so the arm span
> equals the body height, palms open and facing forward, fingers together and extended, legs
> straight with feet together and flat, head level, looking straight at the viewer, calm neutral
> expression. Anatomically proportioned, canonical proportions, no foreshortening.
>
> **Rendering — one consistent language everywhere:** the whole figure is drawn as a holographic
> scan in fine contour lines that follow the anatomy, with faint even horizontal scan lines across
> the entire body. The face is built from the **same** contour lines as the hands, arms and feet —
> denser there only because a face has more features, never a different technique. No painterly or
> photographic shading on the face, no smooth rendered skin, no soft airbrush anywhere. Line weight
> is uniform head to feet. The features must still be recognisably his: the glasses, the fringe, the
> shape of the jaw.
>
> **Palette:** near-monochrome. Cool graphite-grey line work with a single accent, mint green
> (#5BE49B), used only in thin edge highlights. No other hues, no glow bloom, no gradient that
> depends on the background colour.
>
> **Framing:** the complete figure, fingertips and feet included, centred, square composition, with
> generous empty margin on all four sides — nothing touching or crossing the frame edge. Camera at
> chest height, orthographic feel, no perspective distortion.
>
> **Background:** fully transparent (alpha). If transparency is impossible, flat solid near-black
> #0A0D10 — no vignette, gradient, floor, shadow, circle, square, grid or props of any kind.
>
> **Lighting:** flat and even from the front so the left and right halves read identically. No side
> light, no cast shadow, no one-sided rim light.
>
> Style keywords: technical illustration, anatomical plate, engineering diagram, holographic scan,
> precise, restrained.

**Negative / avoid:** text, letters, numbers, watermarks, logos; the Vitruvian circle and square
(they are drawn separately in code); a second pair of arms or legs; extra fingers; tilted, walking
or three-quarter pose; arms lowered or bent; hands closed, in pockets, or touching the body; hats,
masks, headphones, watches, phones or any wearable device (those are drawn separately); background,
floor, furniture, particles, sparks; neon glow; photorealistic skin; cropped fingertips, feet or
head.

If the tool refuses to work from a photo of a real person, drop the word "portrait" and ask for a
**stylised, non-photorealistic illustration inspired by the reference**, keeping the same features.

---

## 2 · Technical spec (this is what makes it work as a map)

| | |
|---|---|
| Aspect ratio | **1 : 1 square** (arm span ≈ height, so a portrait crop would waste space). 1536 × 1536 px, or 1400 × 1400 |
| Format | **PNG with alpha.** Transparent background strongly preferred |
| Margins | ≥ 10 % empty on every side — callout labels and leader lines live there |
| Head | top of hair ≈ 8 % from the top, chin ≈ 22 % |
| Arm line | horizontal, at ≈ 30 % of the height, both arms at exactly the same height |
| Wrists | at ≈ 18 % and ≈ 82 % of the width — clear of the frame edge |
| Feet | soles at ≈ 92 % of the height |
| Symmetry | body centre line at 50 % of the width, ± 2 % |
| Colour | must read on both a near-black and a warm-white page — no white halo, no dark matte |

Why these numbers: the hotspots are positioned in percentages of the image. A symmetrical
Vitruvian pose is ideal for this — the outstretched arms put the two wrists far from the torso, so
the wrist and phone markers can never collide, which was the weak point of the arms-down pose.

---

## 3 · What to send back

One PNG. Two would be better:

1. **`bodyfigure-dark.png`** — tuned to sit on the dark theme.
2. **`bodyfigure-light.png`** — same figure, line work dark enough to read on the warm-white theme.

If only one is possible, send the transparent version and I will derive the second by inverting and
re-tinting it.

## 4 · What I do with it

Drop it in `src/images/`, place it behind the existing hotspot layer, re-measure the five marker
positions against the real image, and draw on top in SVG:

- the **Vitruvian circle and square** — as line work I can animate (a slow sweep, or drawing itself
  in on load) and recolour per theme, which a baked-in raster could not do;
- the **device glyphs** (glasses frame, earbud, neckband, watch, phone) — so devices stay editable
  from `src/_data/body.json` and stay crisp at any size.

That keeps the human underneath your actual likeness, and everything that has to change over time
in code.
