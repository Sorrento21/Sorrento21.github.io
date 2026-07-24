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
