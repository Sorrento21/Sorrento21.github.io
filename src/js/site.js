/* ===========================================================================
   Site behaviour. Everything here is progressive: with JS disabled the page is
   still a complete, readable document — the preview pane shows the first
   figure, tiles are ordinary links to the image, and the nav is a plain list.
   =========================================================================== */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Marks that scripting is on. The reveal animation is gated on this class, so
  // with JS off (or if this file fails to load) nothing is ever hidden.
  document.documentElement.classList.add("js");

  /* ——— colour theme ———
     <head> already applied the theme; here we only label the button and handle
     clicks. An explicit choice is remembered; until one is made the page keeps
     following the OS setting live. */
  var root = document.documentElement;
  var themeBtn = document.querySelector(".theme-toggle");
  var themeMeta = document.querySelector('meta[name="theme-color"]');
  var systemLight = window.matchMedia("(prefers-color-scheme: light)");

  function paintTheme(theme) {
    root.setAttribute("data-theme", theme);
    if (themeMeta) themeMeta.setAttribute("content", theme === "light" ? "#EFEDE6" : "#0A0D10");
    if (themeBtn) {
      // The button offers the *other* theme, so it reads as an action.
      var next = theme === "light" ? "dark" : "light";
      themeBtn.querySelector(".glyph").textContent = theme === "light" ? "☾" : "☀";
      themeBtn.querySelector(".tt-label").textContent = next;
      themeBtn.setAttribute("title", "Switch to the " + next + " theme");
      themeBtn.setAttribute("aria-label", "Switch to the " + next + " theme");
    }
  }
  paintTheme(root.getAttribute("data-theme") || "dark");

  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
      paintTheme(next);
      try { localStorage.setItem("theme", next); } catch (e) {}
    });
  }
  // Follow the OS while the visitor has not picked a side.
  systemLight.addEventListener("change", function (e) {
    var stored = null;
    try { stored = localStorage.getItem("theme"); } catch (err) {}
    if (!stored) paintTheme(e.matches ? "light" : "dark");
  });

  /* ——— mobile nav ——— */
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ——— reveal blocks as they scroll in ——— */
  var reveals = Array.prototype.slice.call(document.querySelectorAll("[data-rv]"));
  function show(el) { el.classList.add("in"); }
  function onScreen(el) {
    var r = el.getBoundingClientRect();
    return r.top < window.innerHeight * 0.95 && r.bottom > 0;
  }

  if (reduceMotion || !("IntersectionObserver" in window)) {
    reveals.forEach(show);
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { show(e.target); io.unobserve(e.target); }
      });
    }, { threshold: 0.08 });

    // Anything already on screen is shown outright — an observer callback that
    // never arrives (background tab, odd browser) must not leave the page blank.
    reveals.forEach(function (el) { if (onScreen(el)) show(el); else io.observe(el); });

    // Images can change the layout after first paint; re-check once they are in.
    window.addEventListener("load", function () {
      reveals.forEach(function (el) { if (onScreen(el)) show(el); });
    });
  }

  /* ——— the typed first command ——— */
  var typed = document.querySelector("[data-typed]");
  if (typed) {
    var text = typed.getAttribute("data-typed");
    if (reduceMotion) {
      typed.textContent = text;
    } else {
      var i = 0;
      (function tick() {
        if (i <= text.length) { typed.textContent = text.slice(0, i++); setTimeout(tick, 55); }
      })();
    }
  }

  /* ——— lightbox ——— */
  var lb = document.getElementById("lb");
  var lbImg = lb && lb.querySelector("img");
  var lbCap = lb && lb.querySelector("figcaption");
  var lastFocus = null;

  function openLightbox(src, caption, origin) {
    if (!lb || !src) return;
    lastFocus = origin || document.activeElement;
    lbImg.src = src;
    lbImg.alt = caption || "";
    lbCap.textContent = caption || "";
    lb.hidden = false;
    // next frame, so the transition has a starting state to animate from
    requestAnimationFrame(function () { lb.classList.add("on"); });
    var close = lb.querySelector(".x");
    if (close) close.focus();
  }
  function closeLightbox() {
    if (!lb || lb.hidden) return;
    lb.classList.remove("on");
    setTimeout(function () { lb.hidden = true; lbImg.removeAttribute("src"); }, 260);
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }
  if (lb) {
    lb.addEventListener("click", function (e) {
      if (e.target.tagName !== "IMG") closeLightbox();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeLightbox();
    });
  }

  // Any element carrying data-full opens in the lightbox instead of navigating.
  document.addEventListener("click", function (e) {
    if (e.target.closest("[data-stop]")) return;      // real links inside a tile
    var el = e.target.closest("[data-full]");
    if (!el) return;
    e.preventDefault();
    openLightbox(el.getAttribute("data-full"), el.getAttribute("data-cap"), el);
  });

  /* ——— body map: markers on the figure and the menu bar pick a sensing site ———
     Hovering previews, clicking pins the choice (same grammar as the publication
     browser). Every control carries data-dev, so the menu and the body stay in
     step. Without JS every panel is simply shown in order. */
  Array.prototype.forEach.call(document.querySelectorAll("[data-bodymap]"), function (map) {
    var controls = Array.prototype.slice.call(map.querySelectorAll("[data-dev]"));
    var panels = Array.prototype.slice.call(map.querySelectorAll("[data-panel]"));
    var banks = Array.prototype.slice.call(map.querySelectorAll("[data-bank]"));
    var siteOut = map.querySelector("[data-site]");
    if (!controls.length) return;

    var pinned = null;

    function show(id) {
      map.setAttribute("data-active", id);
      panels.forEach(function (p) { p.hidden = p.getAttribute("data-panel") !== id; });
      banks.forEach(function (b) { b.classList.toggle("on", b.getAttribute("data-bank") === id); });
      controls.forEach(function (c) {
        c.setAttribute("aria-pressed", c.getAttribute("data-dev") === (pinned || id) ? "true" : "false");
      });
      var panel = map.querySelector('[data-panel="' + id + '"]');
      var label = panel && panel.querySelector(".dp-row .v");
      if (siteOut && label) siteOut.textContent = label.textContent;
    }

    controls.forEach(function (el) {
      var id = el.getAttribute("data-dev");
      el.addEventListener("mouseenter", function () { show(id); });
      el.addEventListener("focus", function () { show(id); });
      el.addEventListener("mouseleave", function () { if (pinned) show(pinned); });
      el.addEventListener("click", function () {
        pinned = pinned === id ? null : id;
        show(pinned || id);
      });
    });
    map.addEventListener("mouseleave", function () { if (pinned) show(pinned); });

    show(controls[0].getAttribute("data-dev"));
    bootSequence(map);
  });

  /* ——— the gallery's power-on self test ———
     Plays when you arrive from a click on the gallery link — the flag is set by
     the delegated handler below, so a reload does not replay it. Any click or
     key skips it, and it is skipped outright when motion is reduced. */
  function bootSequence(map) {
    var boot = map.querySelector("[data-boot]");
    var out = boot && boot.querySelector("[data-boot-log]");
    if (!boot || !out) return;

    var armed = sessionStorage.getItem("bodymap-boot") === "1";
    try { sessionStorage.removeItem("bodymap-boot"); } catch (e) {}
    if (!armed || reduceMotion) return;

    var sites = Array.prototype.slice.call(map.querySelectorAll(".bios-tab")).map(function (t) {
      return t.textContent.trim().toLowerCase();
    });
    var pubs = map.querySelectorAll(".devpaper").length;
    var lines = [
      "<b>BODYMAP BIOS (TM) v1.03</b>",
      "COPYRIGHT (C) JIACHENG LIU 2026",
      "",
      "Detecting sensing sites ......... <i>" + sites.length + " found</i>"
    ];
    sites.forEach(function (s) {
      lines.push("  " + (s + " .....................").slice(0, 22) + " <i>OK</i>");
    });
    lines.push("");
    lines.push("Loading figure .................. <i>1960x1934</i>");
    lines.push("Mapping publications ............ <i>" + pubs + " linked</i>");
    lines.push("");
    lines.push("<u>READY.</u> press any key to continue _");

    boot.hidden = false;
    var i = 0, timer = null;
    function step() {
      out.innerHTML = lines.slice(0, ++i).join("\n");
      if (i < lines.length) timer = setTimeout(step, lines[i] === "" ? 40 : 85);
      else timer = setTimeout(done, 420);
    }
    function done() {
      clearTimeout(timer);
      boot.classList.add("out");
      setTimeout(function () { boot.hidden = true; }, 340);
      document.removeEventListener("keydown", done);
    }
    boot.addEventListener("click", done);
    document.addEventListener("keydown", done);
    step();
  }

  // Arm the self test whenever the gallery is opened from a link on the site.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href$="/gallery.html"], a[href="gallery.html"]');
    if (!a) return;
    try { sessionStorage.setItem("bodymap-boot", "1"); } catch (err) {}
  });

  /* ——— publication browser: list + cross-fading figure preview ——— */
  Array.prototype.forEach.call(document.querySelectorAll("[data-browser]"), function (browser) {
    var rows = Array.prototype.slice.call(browser.querySelectorAll(".prow"));
    if (!rows.length) return;

    var stage = browser.querySelector("[data-stage]");
    var imgs = stage.querySelectorAll("img");
    var nofig = stage.querySelector(".nofig");
    var expand = stage.querySelector(".expand");
    var elTitle = browser.querySelector("[data-pv-title]");
    var elAuthors = browser.querySelector("[data-pv-authors]");
    var elVenue = browser.querySelector("[data-pv-venue]");
    var elLinks = browser.querySelector("[data-pv-links]");
    var list = browser.querySelector(".plist");
    var slot = 0, current = 0;

    function select(index, scrollIntoView) {
      current = (index + rows.length) % rows.length;
      var row = rows[current];

      rows.forEach(function (r) {
        r.classList.remove("sel");
        r.setAttribute("aria-selected", "false");
      });
      row.classList.add("sel");
      row.setAttribute("aria-selected", "true");
      if (scrollIntoView && row.scrollIntoView) {
        row.scrollIntoView({ block: "nearest", behavior: reduceMotion ? "auto" : "smooth" });
      }

      var src = row.getAttribute("data-img");
      if (src) {
        var next = imgs[slot ^ 1], prev = imgs[slot];
        next.src = src;
        next.alt = row.getAttribute("data-title") || "";
        next.classList.remove("on");
        requestAnimationFrame(function () {
          next.classList.add("on");
          prev.classList.remove("on");
        });
        slot ^= 1;
        stage.classList.remove("empty");
        if (nofig) nofig.hidden = true;
        if (expand) {
          expand.hidden = false;
          expand.setAttribute("data-full", src);
          expand.setAttribute("data-cap", row.getAttribute("data-title") || "");
        }
      } else {
        imgs[0].classList.remove("on");
        imgs[1].classList.remove("on");
        stage.classList.add("empty");
        if (nofig) nofig.hidden = false;
        if (expand) expand.hidden = true;
      }

      elTitle.textContent = row.getAttribute("data-title") || "";
      elAuthors.innerHTML = row.getAttribute("data-au") || "";
      elVenue.textContent = row.getAttribute("data-venue") || "";
      elVenue.className = "vtag " + (row.getAttribute("data-tone") || "");

      var links = [];
      try { links = JSON.parse(row.getAttribute("data-links") || "[]") || []; } catch (err) { links = []; }
      elLinks.innerHTML = links
        .filter(function (l) { return l && l.url; })
        .map(function (l) {
          return '<a href="' + l.url + '" target="_blank" rel="noopener">' + l.label + "</a>";
        })
        .join(" · ");
    }

    // Hovering previews; clicking follows the row's link to the paper page.
    rows.forEach(function (row, index) {
      row.addEventListener("mouseenter", function () { select(index); });
      row.addEventListener("focus", function () { select(index); });
    });

    // ↑ ↓ / j k move the selection while the list has focus.
    list.addEventListener("keydown", function (e) {
      if (e.key === "ArrowDown" || e.key === "j") { select(current + 1, true); e.preventDefault(); }
      if (e.key === "ArrowUp" || e.key === "k") { select(current - 1, true); e.preventDefault(); }
      if (e.key === "Enter") { rows[current].click(); }
    });

    select(0);
  });
})();
