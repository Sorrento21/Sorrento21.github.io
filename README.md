# Jiacheng Liu — Personal Website

Static site built with [Eleventy (11ty)](https://www.11ty.dev/). Live at
**https://sorrento21.github.io**.

The guiding idea: **content lives in data files, layout lives in templates.**
You add a paper, project, or news item by editing one JSON file — never by
copying HTML. There is exactly one copy of the header, footer, and each card
style, so nothing can fall out of sync.

## The theme

The site is styled as **one terminal window**: every section is the output of a
command (`whoami --verbose`, `open publications/ --preview`, `tail updates.log`).
Two rules keep that from becoming a gimmick:

- **Two palettes, one theme.** Night is the dark terminal; day is warm paper with
  the same four signal colours darkened until they read on light. The button in
  the title bar switches them. A visitor's first load follows their OS setting;
  once they press the button their choice is remembered (`localStorage.theme`)
  and the OS is ignored from then on. To force one palette for everyone, drop
  the `<script>` in `base.njk`'s `<head>` and hard-code
  `data-theme="light"` (or `"dark"`) on `<html>`.
- **Figures lead.** Publications are a two-pane browser — a list on the left, a
  large figure preview on the right that cross-fades as you move through it with
  the mouse, <kbd>↑</kbd>/<kbd>↓</kbd> or <kbd>j</kbd>/<kbd>k</kbd>. Clicking any
  figure opens it full size.
- **Mono is for the shell, not for prose.** Command lines, keys and metadata are
  JetBrains Mono; paragraphs are Inter, so long text stays readable.

Everything degrades: with JavaScript off nothing is hidden, the preview pane is
server-rendered with the first entry already in it, and every image is a plain
link to itself. Fonts are self-hosted in `src/styles/fonts/` — no third-party CDN
at runtime (also the reason the site loads normally in mainland China).

## Pages

Four top-level pages, plus one generated page per paper and per project:

```
/index.html  /publications.html  /gallery.html  /contact.html
/papers/<slug>.html      ← one per entry in research.json      (title, authors, figure, abstract, links)
/projects/<slug>.html    ← one per entry in other_projects.json
```

The home page runs in this order: **who I am → updates → research question →
publications → projects → gallery**. There is no projects *index* page: the
thumbnail grid on the home page is that index (`#projects`), and each tile links
to the project's own page.

`/publications.html` is the formal list — grouped by year, newest first, each
entry tagged the way a CV does it (`[C.1]` conference, `[J.1]` journal,
`[W.1]` workshop/demo, `[P.1]` preprint; numbered per kind, oldest first, so a
tag never changes when a new paper lands). Titles link to the paper page.

Clicking a paper anywhere on the site opens its page — never a bare enlarged
image. The figure on that page is still clickable if you want it full size.
Gallery artwork is the exception: it has no page, so it opens in the lightbox.

**All internal links are root-relative** (`/images/…`, `/papers/…`), because the
detail pages live one directory down. Keep it that way when adding markup.

## Project layout

```
website/
├── src/
│   ├── _data/                 ← THE CONTENT. Edit these to add/remove items.
│   │   ├── site.json          ·  name, nav bar, social links, footer
│   │   ├── updates.json       ·  "Updates" news feed on the home page
│   │   ├── research.json      ·  THE PAPERS — home page, Publications page, /papers/*
│   │   ├── other_projects.json·  design/course projects — home page grid + /projects/*
│   │   └── gallery.json        ·  the Gallery page (paintings, cocktails)
│   ├── _includes/
│   │   ├── layouts/base.njk    ·  the terminal window shell (<head>, title bar, footer, lightbox)
│   │   └── partials/
│   │       ├── header.njk      ·  title bar + nav (one copy for the whole site)
│   │       └── macros.njk      ·  cmd() prompt lines, pubBrowser(), tile(), logLine()
│   ├── index.njk               ·  home page   → /index.html
│   ├── publications.njk        ·  → /publications.html  (grouped by year)
│   ├── paper.njk               ·  → /papers/<slug>.html   (one per research.json entry)
│   ├── project.njk             ·  → /projects/<slug>.html (one per other_projects.json entry)
│   ├── gallery.njk             ·  → /gallery.html
│   ├── contact.njk             ·  → /contact.html
│   ├── images/  docs/  styles/  js/   ← static assets, copied through untouched
├── .eleventy.js                ·  build config
├── package.json
└── .github/workflows/deploy.yml·  auto-build + publish on every push
```

`_site/` (the built site) and `node_modules/` are generated — never edit them,
they are git-ignored.

## Preview locally

Node lives in a dedicated conda env called `website`.

```bash
conda activate website
npm start          # serves http://localhost:8080 with live reload
```

Edit any `.json` or `.njk` file and the browser refreshes automatically.
(First time only: run `npm install` to fetch Eleventy.)

## Deploy

Just commit and push to the default branch:

```bash
git add -A && git commit -m "Add new paper" && git push
```

A GitHub Action builds the site and publishes it. No manual build needed.

> **One-time setup** (only if Pages isn't already on "Actions"): in the
> `Sorrento21.github.io` repo → **Settings → Pages → Build and deployment →
> Source → "GitHub Actions"**.

---

## How to add content

### Add a paper

`src/_data/research.json` is the **single source of truth for papers** — the
home page, the Publications page and the generated
`/papers/<slug>.html` all read from it. Copy a block and edit:

```json
{
  "slug": "my-paper",                       ← becomes /papers/my-paper.html
  "title": "My New Paper Title",
  "image": "images/research/my_paper.gif",  ← .png, .jpg or .gif all work
  "alt": "one line describing the figure",
  "authors": "<u>Jiacheng Liu</u>, Coauthor One",   ← <u>…</u> marks you; * marks co-first
  "venue": "CHI 2027",
  "status": "Under review",                 ← "Published" turns the badge green
  "year": "2027",                           ← the venue's year: it groups the list
  "type": "C",                              ← C conference · J journal · W workshop/demo · P preprint
  "abstract": "Paste the paper's real abstract here.",
  "keywords": ["Wearables", "Sensing"],
  "links": [
    { "label": "Paper", "url": "docs/my_paper.pdf" },
    { "label": "DOI",   "url": "https://doi.org/..." }
  ]
}
```

Drop the figure in `src/images/research/` and any PDF in `src/docs/`.
`abstract` may be `""` — the page then says the work is still in preparation
instead of showing an empty section.

The Publications page groups and numbers everything itself from `year` and
`type` — there is no second file to keep in sync.

### Use a GIF or a video as the figure

Point `image` at a `.gif` and it plays by itself. To convert a screen recording
(much smaller than exporting a GIF from most tools):

```bash
ffmpeg -i clip.mov -vf "fps=15,scale=760:-1:flags=lanczos,palettegen=max_colors=128:stats_mode=diff" pal.png
ffmpeg -i clip.mov -i pal.png -lavfi "fps=15,scale=760:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle" src/images/research/my_paper.gif
```

The 4.4-second PPG clip lands at ~285 KB this way.

### Add a news update

Edit `src/_data/updates.json` — newest first:

```json
{ "date": "2026-08-01", "html": "🎉 <strong>Something exciting</strong> happened." }
```

### Add a project or a Gallery item

`src/_data/other_projects.json` needs a `slug` (→ `/projects/<slug>.html`),
`title`, `image`, `context` ("2024, Coursework of …"), `role`, and a
`description` for the project page. An empty `description` renders a
"write-up coming soon" line rather than an empty page.

`src/_data/gallery.json` is unchanged: rows of images; each row keeps the number
of columns you author it with.

### Put a device on the body map

The Gallery page opens with an interactive figure: every device my papers put on
the body is a hotspot, and clicking one lists the papers behind it. It is driven
by `src/_data/body.json`:

```json
{
  "id": "wrist",
  "label": "Smartwatch / wristband",
  "sensing": "PPG at the wrist",
  "x": 154, "y": 262,          ← coordinates in the figure's 420 × 520 viewBox
  "labelSide": "left",         ← which edge the callout label hangs off
  "papers": ["ppg-as-a-bridge", "reliable-ppg-authentication"]
}
```

A paper can appear on several devices and a device can carry several papers.
To draw a new device, add a `<g class="dev" data-glyph="<id>">` to the SVG in
`src/_includes/partials/bodymap.njk` at the same coordinates. Hotspots are real
buttons laid over the drawing, so the map is keyboard-navigable; with JS off
every device panel is simply listed.

### Change the nav bar, socials, or footer

Edit `src/_data/site.json`. One edit updates every page.

---

## Notes

- **Design source** (`gallery.psd`) lives in `../design-src/`, kept out of the
  published site.
- The whole theme lives in `src/styles/site.css` (plus `fonts.css` and the four
  self-hosted `.woff2` files). Behaviour lives in `src/js/site.js` — about 210
  lines: theme switch, mobile nav, scroll reveal, the typed first command, the
  figure lightbox, and the publication browser.
- **Adding colours:** both palettes are declared as custom properties at the top
  of `site.css` (`:root` and `:root[data-theme="light"]`). Every rule underneath
  is written against those tokens — if you find yourself typing a literal colour
  further down the file, add a token instead, or the light theme will break.
- `design-concepts/` holds the ten redesign prototypes this theme was chosen
  from, plus `archive/` for the earlier round. Eleventy only builds `src/`, so
  none of it is published; delete the folder whenever you like.
- **Venue colour is derived from `status`**: anything containing "submit",
  "review", "in prep" or "ready to" renders pink (in review); everything else is
  green (out). Since papers now live in one file, the home page and the
  Publications page can no longer disagree about the same paper.
- **Abstracts are the papers' own**, transcribed from the PDFs in
  `~/Documents/Personal/docs/Publications/`. If a paper changes, update both.
