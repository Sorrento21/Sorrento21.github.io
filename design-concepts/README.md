# Design concepts — personal site redesign

Ten self-contained homepage prototypes, built with the real content from
`src/_data/*.json` and the real images from `src/images/`. Nothing here is wired into
the Eleventy build: `.eleventy.js` only processes `src/`, so this folder is never copied
into `_site/` and the live site is untouched.

## How to look at them

**Double-click `preview.command` in Finder.** It starts a local server from `website/`,
opens the chooser, and keeps running until you press Ctrl-C in its Terminal window.

Equivalent by hand:

```bash
cd website
python3 -m http.server 8899        # or: npx serve .
open http://localhost:8899/design-concepts/index.html
```

A server is required: the concepts pull images from `../src/images/`, and the chooser's
thumbnails are live iframes. If the links or previews go dead, the server has stopped —
start it again.

## The ten

Round two. Five directions were kept and reworked against three notes: **images lead**,
**add motion and interaction**, **strong key visual without hurting usability**.

| File | Name | One line |
|------|------|----------|
| `02-aurora-dark.html` | Aurora Dark | Parallax hero collage; papers as full-bleed image cards on a 12-col grid |
| `04-bento.html` | Bento | Tile wall where half the tiles are pictures; auto light/dark |
| `07-kinetic-type.html` | Kinetic Type | Giant type + scrolling image band; papers unfold their figure inline |
| `09-soft-gradient.html` | Soft Gradient | Pastel mesh, floating photo stack, 3D-tilting paper cards |
| `10-terminal.html` | Terminal | Terminal window with a two-pane file browser and live figure preview |
| `11-cinematic.html` | Cinematic | Full-viewport hero, each paper a screen-height parallax band |
| `12-filmstrip.html` | Filmstrip | Papers as a draggable horizontal strip of large cards |
| `13-media-wall.html` | Media Wall | Masonry of papers + projects + paintings, filterable, lightbox with prev/next |
| `14-spotlight.html` | Spotlight | Canvas sensor field reacting to the cursor; spotlight follows the pointer on cards |
| `15-card-deck.html` | Card Deck | Papers as a throwable stack of cards, one big figure at a time |

`archive/` holds the five from round one that were not picked (01 Editorial Grid,
03 Warm Serif, 05 Signal Lab, 06 Sticky Split, 08 Color Block). Nothing was deleted;
their image paths were rewritten so they still render from the subfolder.

## Using GIFs and video

Every media slot is styled for both `<img>` and `<video>` — the CSS targets
`.m img, .m video` (or equivalent) with `object-fit`, so swapping in a motion asset needs
no new styling:

```html
<!-- animated GIF: just change the file -->
<img src="images/research/bridge.gif" alt="">

<!-- better: a muted looping mp4/webm is ~10x smaller than the same GIF -->
<video src="images/research/bridge.mp4" autoplay muted loop playsinline poster="images/research/bridge.png"></video>
```

The `GIF` badge on the first paper in several concepts is a placeholder marking where a
teaser animation would go — remove it until a real one exists.

## Notes before porting a winner

- **Fonts come from Google Fonts** for prototyping speed. Before shipping, self-host the
  chosen families in `src/styles/fonts/` — the live site should not depend on a
  third-party CDN (privacy, and it is blocked in mainland China).
- **Placeholder copy.** Several concepts rewrite the hero line ("Sensing the body,
  quietly", "I build sensing systems small enough to forget you are wearing them",
  "Making sensing gentle enough to live with") to show the voice each direction implies.
  Keep or discard per taste.
- **Made-up facts to verify or drop.** Bento (04) and Soft Gradient (09) invent a "Now"
  card and counters (5 papers / 2 co-first / 6 design projects / 2 awards 2025); the
  accordion in 07 and the deck in 15 add one-sentence plain-language summaries of each
  paper that I wrote — check them for accuracy before they go public.
- **Figures get cropped.** Concepts 02, 04, 11, 12, 14 and 15 crop paper figures to 16:9
  or wider. Multi-panel figures survive this badly; a purpose-made teaser image per paper
  (one clear device/result shot) would improve every one of these designs more than any
  CSS change.
- **JavaScript.** Each concept carries 20–60 lines: scroll reveal, lightbox, and one
  signature interaction (parallax, accordion, drag rail, keyboard browsing, canvas field,
  card deck). All of it degrades to a readable static page if the script is removed, and
  every animation is wrapped in `prefers-reduced-motion` where it matters.
- **Only the homepage is designed.** Projects / Publications / Gallery / Contact need the
  same treatment; each concept's section patterns are meant to carry over.
- **Porting cost.** The markup already matches the existing Nunjucks data shape, so
  porting is mostly: replace `src/styles/site.css`, adjust `base.njk` + `header.njk`,
  rewrite the three macros in `partials/macros.njk`, and add one small `js/` file. The
  JSON data files do not change — except that image-led layouts want an extra optional
  `teaser` (image or video) field per entry.
