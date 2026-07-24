# Jiacheng Liu — Personal Website

Static site built with [Eleventy (11ty)](https://www.11ty.dev/). Live at
**https://sorrento21.github.io**.

The guiding idea: **content lives in data files, layout lives in templates.**
You add a paper, project, or news item by editing one JSON file — never by
copying HTML. There is exactly one copy of the header, footer, and each card
style, so nothing can fall out of sync.

## Project layout

```
website/
├── src/
│   ├── _data/                 ← THE CONTENT. Edit these to add/remove items.
│   │   ├── site.json          ·  name, nav bar, social links, footer
│   │   ├── updates.json       ·  "Updates" news feed on the home page
│   │   ├── research.json      ·  research projects (home page + Projects page)
│   │   ├── other_projects.json·  "Other Projects" on the Projects page
│   │   ├── publications.json  ·  the Publications page, grouped
│   │   └── gallery.json        ·  the Gallery page (paintings, cocktails)
│   ├── _includes/
│   │   ├── layouts/base.njk    ·  the shared page shell (<head>, header, footer)
│   │   └── partials/
│   │       ├── header.njk      ·  nav bar (one copy for the whole site)
│   │       └── macros.njk      ·  the card renderers (project / publication / gallery)
│   ├── index.njk               ·  home page   → /index.html
│   ├── projects.njk            ·  → /projects.html
│   ├── publications.njk        ·  → /publications.html
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

### Add a research project

Edit `src/_data/research.json`. Copy an existing block and change the fields.
`meta` lines render in the order you list them; `text` may contain inline HTML
(`<u>…</u>` to underline yourself, `<b>…</b>` to bold). `links` may be empty.

```json
{
  "image": "images/research/my_project.png",
  "alt": "my project",
  "title": "My New Paper Title",
  "meta": [
    { "cls": "author", "text": "<u>Jiacheng Liu</u>, Coauthor One, Coauthor Two" },
    { "cls": "state",  "text": "2026, CHI'26" }
  ],
  "links": [
    { "label": "Paper", "url": "docs/my_paper.pdf" },
    { "label": "DOI",   "url": "https://doi.org/..." }
  ]
}
```

Drop the image in `src/images/research/` and the PDF in `src/docs/`. Done —
it appears on both the home page and the Projects page.

### Add a publication

Edit `src/_data/publications.json`. It is a list of groups
(`"SELECTED PAPERS"`, `"DEMO AND WORKSHOP"`, …); add an item to a group's
`items`, or add a whole new group. `image` may be `""` for no thumbnail.
`links` render joined by `|`.

### Add a news update

Edit `src/_data/updates.json` — newest first:

```json
{ "date": "2026-08-01", "html": "🎉 <strong>Something exciting</strong> happened." }
```

### Add an "Other Project" or a Gallery item

Same pattern in `src/_data/other_projects.json` / `src/_data/gallery.json`.
For gallery, `variant` is `"main_project"` (large, 2-up) or `"project"`
(small, 3-up).

### Change the nav bar, socials, or footer

Edit `src/_data/site.json`. One edit updates every page.

---

## Notes

- **Design source** (`gallery.psd`) lives in `../design-src/`, kept out of the
  published site.
- The theme (colours, fonts, spacing) is unchanged from the original site and
  lives entirely in `src/styles/`.
