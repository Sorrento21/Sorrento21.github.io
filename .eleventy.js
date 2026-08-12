/**
 * Eleventy config.
 *
 * The filters below exist so the templates can stay dumb: the two content
 * shapes in src/_data (research/other_projects carry `meta` lines; publications
 * carry `authors`/`conference`) are normalised here instead of in every template.
 */

// Text of the first `meta` line carrying a given class, e.g. "author".
const metaLine = (item, cls) =>
  ((item && item.meta) || []).reduce((found, m) => found || (m.cls === cls ? m.text : ""), "");

module.exports = function (eleventyConfig) {
  // Static assets: copied through untouched. Object form maps a project-root-relative
  // source to an output-relative destination, so src/images -> _site/images, etc.
  // This keeps every published URL identical to the old site.
  eleventyConfig.addPassthroughCopy({ "src/images": "images" });
  eleventyConfig.addPassthroughCopy({ "src/docs": "docs" });
  eleventyConfig.addPassthroughCopy({ "src/styles": "styles" });
  eleventyConfig.addPassthroughCopy({ "src/js": "js" });

  // Rebuild the site when CSS/JS change during `npm start`.
  eleventyConfig.addWatchTarget("src/styles/");
  eleventyConfig.addWatchTarget("src/js/");

  /* ——— content filters ——— */

  // Author list of an entry, whichever shape it uses. May contain <u> markup.
  eleventyConfig.addFilter("authors", (item) => item.authors || metaLine(item, "author"));

  // Venue / status line of an entry, whichever shape it uses. Papers carry
  // `venue` + `status`; projects carry a "state" meta line.
  eleventyConfig.addFilter("venue", (item) => {
    if (item.venue) return item.status ? `${item.venue} · ${item.status}` : item.venue;
    return item.conference || metaLine(item, "state");
  });

  // Resolve a list of slugs to the papers themselves (the body map stores slugs).
  eleventyConfig.addFilter("bySlug", (items, slugs) =>
    (slugs || []).map((s) => (items || []).find((i) => i.slug === s)).filter(Boolean)
  );

  // Publication-list numbering, in the convention academic CVs use: a letter for
  // the kind of venue and a running number per kind, oldest first — so a paper's
  // tag never changes when a newer one is added. C conference · J journal ·
  // W workshop/demo · P preprint.
  eleventyConfig.addFilter("withTags", (papers) => {
    const counts = {};
    const tags = new Map();
    [...(papers || [])]
      .sort((a, b) => String(a.year).localeCompare(String(b.year)))
      .forEach((p) => {
        const t = p.type || "C";
        counts[t] = (counts[t] || 0) + 1;
        tags.set(p.slug, t + "." + counts[t]);
      });
    return (papers || []).map((p) => Object.assign({}, p, { tag: tags.get(p.slug) }));
  });

  // Group papers by year, newest year first.
  eleventyConfig.addFilter("byYear", (papers) => {
    const groups = new Map();
    (papers || []).forEach((p) => {
      const y = String(p.year || "");
      if (!groups.has(y)) groups.set(y, []);
      groups.get(y).push(p);
    });
    return [...groups.entries()]
      .sort((a, b) => b[0].localeCompare(a[0]))
      .map(([year, items]) => ({ year, items }));
  });

  // Short venue label for the list gutter. Prefers the parenthesised short name
  // when there is one that looks like a venue — "Proceedings of the … (IEEE VR'24)"
  // -> "IEEE VR'24" — but not a bare status like "(Submitted)".
  eleventyConfig.addFilter("shortVenue", (v) => {
    const full = String(v || "").split(" · ")[0];
    const paren = full.match(/\(([^)]+)\)/);
    if (paren && /\d/.test(paren[1])) return paren[1].trim();
    let t = full.replace(/^\s*\d{4},\s*/, "").replace(/ready to submit to\s*/i, "");
    const head = t.match(/^[^,(]+/);
    const s = (head ? head[0] : t).trim();
    return s.length > 24 ? s.slice(0, 23).trim() + "…" : s || "unpublished";
  });

  // Colour tone for a venue: pink while it is in review / in preparation,
  // green once it is out.
  eleventyConfig.addFilter("venueTone", (v) =>
    /submit|review|in prep|ready to/i.test(String(v || "")) ? "c-p" : "c-g"
  );

  // First four-digit year found in a string ("" if none).
  eleventyConfig.addFilter("year", (v) => (String(v || "").match(/\b(19|20)\d{2}\b/) || [""])[0]);

  // A "*" in the author list marks co-first authorship.
  eleventyConfig.addFilter("isCoFirst", (a) => String(a || "").includes("*"));

  // Level tag for an updates.log line, inferred from the entry text.
  eleventyConfig.addFilter("logKind", (html) => {
    const t = String(html || "");
    if (/🏆|🏵|award/i.test(t)) return "award";
    if (/📩|submit/i.test(t)) return "submit";
    return "news";
  });

  // Root-relative URL. Detail pages live in subdirectories (/papers/…), so every
  // internal link has to start at the site root; external ones pass through.
  eleventyConfig.addFilter("link", (u) =>
    /^(https?:|mailto:|tel:|#|\/)/.test(String(u || "")) ? u : "/" + String(u || "")
  );

  // Same, for a whole list of {label, url} pairs (used when the list is handed
  // to the browser as JSON).
  eleventyConfig.addFilter("absLinks", (links) =>
    (links || []).map((l) => ({
      label: l.label,
      url: /^(https?:|mailto:|tel:|#|\/)/.test(String(l.url || "")) ? l.url : "/" + String(l.url || ""),
    }))
  );

  // Zero-padded index for the list gutters.
  eleventyConfig.addFilter("pad", (n) => String(n).padStart(2, "0"));

  // Flatten gallery.json down to its image items, for the homepage teaser.
  eleventyConfig.addFilter("galleryImages", (blocks, n) => {
    const out = [];
    (blocks || []).forEach((b) => {
      if (b.type === "gallery") (b.rows || []).forEach((r) => (r.items || []).forEach((i) => out.push(i)));
    });
    return n ? out.slice(0, n) : out;
  });

  eleventyConfig.addFilter("stripTags", (s) => String(s || "").replace(/<[^>]*>/g, ""));

  return {
    dir: {
      input: "src",
      includes: "_includes",
      data: "_data",
      output: "_site",
    },
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
  };
};
