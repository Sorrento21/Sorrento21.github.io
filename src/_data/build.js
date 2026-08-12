// A build stamp for the asset URLs. Static hosts serve CSS and JS with long
// heuristic caching, so without this a deploy can leave people on the old files.
module.exports = () => ({ time: Date.now().toString(36) });
