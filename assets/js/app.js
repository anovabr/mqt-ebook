/* =========================================================================
   Conceitos e análises estatísticas com R e JASP — client behaviour.
   Vanilla JS, no dependencies (beyond KaTeX + highlight.js loaded from CDN).
   ========================================================================= */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement, body = doc.body;
  var reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };

  var CHAPTER = body.getAttribute("data-chapter");
  var SITE_BASE = (window.MQT_SITE_BASE || "").replace(/\/$/, "");

  /* ---- Toast ----------------------------------------------------------- */
  var toastEl = $("#toast"), toastTimer;
  function toast(msg) {
    if (!toastEl) return;
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toastEl.classList.remove("show"); }, 2200);
  }

  /* ---- Theme ----------------------------------------------------------- */
  function setTheme(t) {
    root.setAttribute("data-theme", t);
    try { localStorage.setItem("mqt-theme", t); } catch (e) {}
  }
  function toggleTheme() {
    setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
  }
  $$(".js-theme").forEach(function (b) { b.addEventListener("click", toggleTheme); });
  // React to OS theme changes only when the user hasn't chosen explicitly.
  try {
    matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function (e) {
      if (!localStorage.getItem("mqt-theme")) setTheme(e.matches ? "dark" : "light");
    });
  } catch (e) {}

  /* ---- Font size ------------------------------------------------------- */
  var MIN = 16, MAX = 24, STEP = 1;
  function currentSize() {
    var v = getComputedStyle(root).getPropertyValue("--reading-size");
    return parseInt(v, 10) || 19;
  }
  function setSize(px) {
    px = Math.max(MIN, Math.min(MAX, px));
    root.style.setProperty("--reading-size", px + "px");
    try { localStorage.setItem("mqt-fontsize", px); } catch (e) {}
  }
  $$(".js-font-inc").forEach(function (b) { b.addEventListener("click", function () { setSize(currentSize() + STEP); }); });
  $$(".js-font-dec").forEach(function (b) { b.addEventListener("click", function () { setSize(currentSize() - STEP); }); });

  /* ---- Sidebar drawer -------------------------------------------------- */
  var menuBtn = $("#menuBtn"), sidebar = $("#sidebar"), scrim = $("#scrim");
  function openNav() { body.classList.add("nav-open"); if (menuBtn) menuBtn.setAttribute("aria-expanded", "true"); if (scrim) scrim.hidden = false; }
  function closeNav() { body.classList.remove("nav-open"); if (menuBtn) menuBtn.setAttribute("aria-expanded", "false"); }
  if (menuBtn) menuBtn.addEventListener("click", function () {
    body.classList.contains("nav-open") ? closeNav() : openNav();
  });
  if (scrim) scrim.addEventListener("click", closeNav);
  doc.addEventListener("keydown", function (e) { if (e.key === "Escape") { closeNav(); closeShare(); } });
  // Close drawer after navigating to an in-page anchor on mobile.
  if (sidebar) sidebar.addEventListener("click", function (e) {
    var a = e.target.closest("a.toc-link");
    if (a && innerWidth < 1024 && a.getAttribute("href").indexOf("#") === 0) closeNav();
  });

  /* ---- TOC collapse ---------------------------------------------------- */
  $$(".toc-toggle").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var li = btn.closest(".toc-chapter");
      var open = li.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });

  /* ---- Progress bar ---------------------------------------------------- */
  var bar = $("#progressBar");
  function updateProgress() {
    var h = doc.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    var p = max > 0 ? (h.scrollTop || body.scrollTop) / max : 0;
    if (bar) bar.style.width = (p * 100).toFixed(2) + "%";
  }

  /* ---- Floating action bar (scroll-aware) ------------------------------ */
  var fab = $("#fab"), lastY = 0, SHOW_AFTER = 320;
  function updateFab() {
    var y = window.pageYOffset || doc.documentElement.scrollTop;
    if (fab) {
      // Hidden at the top of a chapter; slides up once the reader scrolls down.
      if (y > SHOW_AFTER) fab.classList.add("show");
      else fab.classList.remove("show");
    }
    lastY = y;
  }

  var ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    (reduceMotion ? runScroll : requestAnimationFrame)(function () {
      updateProgress(); updateFab(); updateScrollSpy(); ticking = false;
    });
  }
  function runScroll(fn) { fn(); }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", function () { updateProgress(); updateFab(); });

  var toTop = $("#toTop");
  if (toTop) toTop.addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
  });

  /* ---- Scroll spy: highlight active section in the sidebar ------------- */
  var sections = $$("#chapter .section[id]");
  var tocLinks = {};
  $$('.toc-sub a[data-anchor]').forEach(function (a) { tocLinks[a.getAttribute("data-anchor")] = a; });
  var activeId = null;
  function updateScrollSpy() {
    if (!sections.length) return;
    var pos = (window.pageYOffset || doc.documentElement.scrollTop) + 120;
    var cur = null;
    for (var i = 0; i < sections.length; i++) {
      if (sections[i].offsetTop <= pos) cur = sections[i];
    }
    var id = cur ? cur.id : null;
    if (id === activeId) return;
    if (activeId && tocLinks[activeId]) tocLinks[activeId].classList.remove("active");
    activeId = id;
    if (id && tocLinks[id]) {
      tocLinks[id].classList.add("active");
      // keep the active item visible within the sidebar viewport
      if (innerWidth >= 1024) tocLinks[id].scrollIntoView({ block: "nearest" });
    }
  }

  /* ---- Section anchor links (deep-link + copy) ------------------------- */
  $$("#chapter .section[id]").forEach(function (sec) {
    var h = sec.querySelector(":scope > h1, :scope > h2, :scope > h3, :scope > h4");
    if (!h) return;
    var a = doc.createElement("a");
    a.className = "anchor-link";
    a.href = "#" + sec.id;
    a.setAttribute("aria-label", "Copiar link para esta seção");
    a.title = "Copiar link para esta seção";
    a.textContent = "#";
    a.addEventListener("click", function (e) {
      e.preventDefault();
      var url = absoluteUrl(CHAPTER_FILE() + "#" + sec.id);
      history.replaceState(null, "", "#" + sec.id);
      copyText(url).then(function () { toast("Link da seção copiado"); });
    });
    h.appendChild(a);
  });

  /* ---- Sharing --------------------------------------------------------- */
  function CHAPTER_FILE() {
    var f = location.pathname.split("/").pop();
    return f && f.length ? f : "index.html";
  }
  function absoluteUrl(rel) {
    if (SITE_BASE) return SITE_BASE + "/" + rel.replace(/^\.?\//, "");
    return new URL(rel, location.href).href;
  }
  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) return navigator.clipboard.writeText(text);
    return new Promise(function (res) {
      var ta = doc.createElement("textarea"); ta.value = text;
      ta.style.position = "fixed"; ta.style.opacity = "0"; doc.body.appendChild(ta);
      ta.select(); try { doc.execCommand("copy"); } catch (e) {}
      doc.body.removeChild(ta); res();
    });
  }

  var shareBtns = $$(".js-share"), shareMenu = $("#shareMenu");
  function setShareAria(v) { shareBtns.forEach(function (b) { b.setAttribute("aria-expanded", v); }); }
  var shareScope = "chapter";
  var pageTitle = doc.title.replace(/ · .*/, "");
  var bookTitle = "Conceitos e análises estatísticas com R e JASP";

  function shareTargets() {
    if (shareScope === "book") {
      return { url: absoluteUrl("index.html"), title: bookTitle, text: bookTitle };
    }
    return { url: absoluteUrl(CHAPTER_FILE()), title: pageTitle,
             text: pageTitle + " — " + bookTitle };
  }
  function nativeShare(t) {
    if (navigator.share) {
      navigator.share({ title: t.title, text: t.text, url: t.url }).catch(function () {});
      return true;
    }
    return false;
  }
  function openShare() {
    if (!shareMenu) return;
    updateShareLinks();
    shareMenu.hidden = false;
    setShareAria("true");
  }
  function closeShare() {
    if (shareMenu && !shareMenu.hidden) { shareMenu.hidden = true; setShareAria("false"); }
  }
  function updateShareLinks() {
    var t = shareTargets();
    var u = encodeURIComponent(t.url), txt = encodeURIComponent(t.text);
    var map = {
      whatsapp: "https://api.whatsapp.com/send?text=" + txt + "%20" + u,
      twitter: "https://twitter.com/intent/tweet?text=" + txt + "&url=" + u,
      linkedin: "https://www.linkedin.com/sharing/share-offsite/?url=" + u,
      email: "mailto:?subject=" + encodeURIComponent(t.title) + "&body=" + txt + "%0A%0A" + u
    };
    $$(".share-item[data-net]", shareMenu).forEach(function (el) {
      var net = el.getAttribute("data-net");
      if (map[net]) el.setAttribute("href", map[net]);
    });
  }
  shareBtns.forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var t = shareTargets();
      // Prefer the native share sheet (mobile); fall back to the desktop menu.
      if (nativeShare(t)) return;
      shareMenu && shareMenu.hidden ? openShare() : closeShare();
    });
  });
  if (shareMenu) {
    $$(".scope-btn", shareMenu).forEach(function (b) {
      b.addEventListener("click", function () {
        $$(".scope-btn", shareMenu).forEach(function (x) { x.classList.remove("is-active"); });
        b.classList.add("is-active");
        shareScope = b.getAttribute("data-scope");
        updateShareLinks();
      });
    });
    var copyItem = $('.share-item[data-net="copy"]', shareMenu);
    if (copyItem) copyItem.addEventListener("click", function () {
      copyText(shareTargets().url).then(function () { toast("Link copiado"); closeShare(); });
    });
    doc.addEventListener("click", function (e) {
      if (shareMenu.hidden) return;
      if (shareMenu.contains(e.target)) return;
      if (e.target.closest && e.target.closest(".js-share")) return;
      closeShare();
    });
  }

  /* ---- Author annotation layer ---------------------------------------- */
  // Injects author notes/asides/examples from content/annotations.json without
  // touching the imported book text. Keyed by chapter slug + section anchor.
  function injectAnnotations(data) {
    if (!data) return;
    var chap = data[CHAPTER];
    if (!chap) return;
    Object.keys(chap).forEach(function (key) {
      var entry = chap[key];
      if (key === "_chapter") return injectChapterSpace(entry);
      var sec = doc.getElementById(key);
      if (!sec) return;
      var heading = sec.querySelector(":scope > h1, :scope > h2, :scope > h3, :scope > h4");
      if (entry.note) {
        var note = block("author-note", "✎ Nota do autor", entry.note);
        heading ? heading.insertAdjacentElement("afterend", note) : sec.prepend(note);
      }
      if (entry.aside) {
        var aside = block("author-aside", "Comentário", entry.aside);
        heading ? heading.insertAdjacentElement("afterend", aside) : sec.prepend(aside);
      }
    });
  }
  function injectChapterSpace(entry) {
    if (!entry) return;
    var art = $("#chapter");
    var box = doc.createElement("section");
    box.className = "author-examples";
    var html = '<div class="al-head">' + (entry.title || "Exemplos e análises do autor") + "</div>";
    if (entry.subtitle) html += '<div class="al-sub">' + entry.subtitle + "</div>";
    html += entry.body || "";
    box.innerHTML = html;
    art.appendChild(box);
    if (window.hljs) $$("pre code", box).forEach(function (c) { window.hljs.highlightElement(c); });
    renderMathIn(box);
  }
  function block(cls, head, html) {
    var d = doc.createElement("div");
    d.className = cls;
    d.innerHTML = '<div class="al-head">' + head + "</div>" + html;
    return d;
  }
  function loadAnnotations() {
    fetch("content/annotations.json", { cache: "no-cache" })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(injectAnnotations)
      .catch(function () { /* annotations are optional */ });
  }

  /* ---- Code highlighting + math --------------------------------------- */
  function highlightCode() {
    if (!window.hljs) return;
    $$("#chapter pre code.language-r").forEach(function (c) { window.hljs.highlightElement(c); });
  }
  function renderMathIn(el) {
    if (!window.renderMathInElement) return;
    // Only the delimiters the source actually uses. NB: no "$" delimiter — this
    // is a Portuguese text where "R$" (currency) would otherwise be parsed as math.
    window.renderMathInElement(el, {
      delimiters: [
        { left: "\\[", right: "\\]", display: true },
        { left: "\\(", right: "\\)", display: false }
      ],
      throwOnError: false, ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"]
    });
  }
  function renderMath() { renderMathIn($("#chapter")); }

  /* ---- Init ------------------------------------------------------------ */
  function ready(fn) {
    if (doc.readyState !== "loading") fn();
    else doc.addEventListener("DOMContentLoaded", fn);
  }
  ready(function () {
    highlightCode();
    updateProgress(); updateFab(); updateScrollSpy();
    loadAnnotations();
    // KaTeX auto-render is deferred; run once it is available.
    if (window.renderMathInElement) renderMath();
    else window.addEventListener("load", renderMath);
  });
})();
