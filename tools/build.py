#!/usr/bin/env python3
"""
Build the "Conceitos e análises estatísticas com R e JASP" static ebook site.

Reads the rendered bookdown HTML (staged in tools/src/), extracts the real
chapter content (discarding the gitbook chrome), rewrites asset paths to local
relative paths, keeps R/JASP code blocks with a language class, and emits:

  - content/<file>.html   cleaned chapter fragments (book text, source of truth)
  - content/toc.json      book structure (chapters + section anchors)
  - <file>.html           full static pages (sidebar + reading column + chrome)

The served site is plain HTML/CSS/JS with no runtime build step. This generator
is only needed to regenerate pages from the imported book text.

Author layer lives in content/annotations.json and is injected at runtime.
"""
import json
import re
import shutil
from pathlib import Path
from html import escape
from bs4 import BeautifulSoup, NavigableString

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "src"
CONTENT = ROOT / "content"

AUTHOR = "Luis Anunciação"
AUTHOR_AFFIL = "PUC-Rio"
BOOK_TITLE = "Conceitos e análises estatísticas com R e JASP"
BOOK_DESC = ("Livro-texto de conceitos e análises estatísticas com R e JASP, "
             "com camada de anotações do autor.")
# Base URL used for canonical/OG tags. Relative paths keep the site portable to
# any GitHub Pages subpath; this is only used to build absolute share URLs.
SITE_BASE = "https://anovabr.github.io/mqt-ebook"

# Chapter order and canonical filenames, taken from the source sidebar TOC.
CHAPTERS = [
    "index.html",
    "programas-estatísticos.html",
    "aspectos-gerais.html",
    "estatística-descritiva.html",
    "família-de-distribuições.html",
    "tipos-de-amostragem.html",
    "estatística-inferencial.html",
    "um-exemplo-real-de-pesquisa.html",
    "qui-quadrado.html",
    "fatores-de-risco.html",
    "teste-t.html",
    "anova.html",
    "anova-de-medidas-repetidas.html",
    "modelo-linear-misto.html",
    "correlação.html",
    "regressão-linear-simples.html",
    "regressão-linear-múltipla.html",
    "regressão-logística-binária.html",
    "quarta-capa.html",
    "referencias.html",
]

report = {"chapters": [], "warnings": [], "images_missing": []}


def slug_of(fname):
    return fname[:-5] if fname.endswith(".html") else fname


# Cache of {dir -> {lowercase_name: real_name}} for case-insensitive lookups.
_dir_index = {}


def _case_correct(rel):
    """If a case-insensitive match for `rel` exists on disk, return the correct
    relative path; otherwise None."""
    p = ROOT / rel
    d = p.parent
    key = str(d)
    if key not in _dir_index:
        _dir_index[key] = {}
        if d.exists():
            for f in d.iterdir():
                _dir_index[key][f.name.lower()] = f.name
    real = _dir_index[key].get(p.name.lower())
    if real:
        return str(Path(rel).parent / real)
    return None


def clean_chapter(fname):
    """Return (content_soup_fragment_html, meta, section_tree)."""
    src = (SRC / fname).read_text(encoding="utf-8")
    soup = BeautifulSoup(src, "lxml")

    section = soup.find("section", class_="normal")
    if section is None:
        report["warnings"].append(f"{fname}: no <section class='normal'> found")
        return None
    # The chapter body is the first .section.level1 inside the page section.
    chapter = section.find("div", class_="section")
    if chapter is None:
        # index.html top level may differ; fall back to the whole section.
        chapter = section

    # --- strip pandoc code line-number anchors -------------------------------
    for a in chapter.select('a[aria-hidden="true"]'):
        a.decompose()

    # --- normalise code blocks ----------------------------------------------
    for pre in chapter.find_all("pre"):
        code = pre.find("code")
        classes = " ".join(pre.get("class", []) + (code.get("class", []) if code else []))
        text = (code.get_text() if code else pre.get_text())
        # rebuild a clean <pre><code> so highlight.js can re-highlight
        pre.clear()
        new_code = soup.new_tag("code")
        if "sourceCode" in classes and re.search(r"\br\b", classes):
            new_code["class"] = ["language-r"]
        else:
            new_code["class"] = ["nohighlight"]
        new_code.string = text
        pre.attrs = {}
        pre.append(new_code)

    # --- rewrite image paths to local relative ------------------------------
    for img in chapter.find_all("img"):
        src_attr = img.get("src", "")
        if src_attr.startswith("img/"):
            img["src"] = "assets/" + src_attr
        elif src_attr.startswith("gitbook-demo_files/figure-html/"):
            img["src"] = "assets/figure-html/" + src_attr.split("/")[-1]
        elif src_attr.startswith("assets/") or src_attr.startswith("http"):
            pass
        else:
            report["warnings"].append(f"{fname}: unexpected img src '{src_attr}'")
        # verify the file exists locally; GitHub Pages is case-sensitive, but the
        # source sometimes references .PNG where the file is .png — correct it.
        local = img["src"]
        if local.startswith("assets/") and not (ROOT / local).exists():
            fixed = _case_correct(local)
            if fixed:
                img["src"] = fixed
            else:
                report["images_missing"].append(f"{fname}: {local}")
        img["loading"] = "lazy"
        img.attrs.pop("style", None)  # let CSS handle sizing/centering

    # --- wrap tables for horizontal scroll on mobile ------------------------
    for table in chapter.find_all("table"):
        if table.parent.get("class") and "table-wrap" in table.parent.get("class"):
            continue
        wrap = soup.new_tag("div")
        wrap["class"] = ["table-wrap"]
        table.wrap(wrap)

    # --- collect the section tree (anchors) for the sidebar -----------------
    def sec_info(sec):
        cls = sec.get("class", [])
        level = next((int(c[5:]) for c in cls if c.startswith("level")), None)
        sid = sec.get("id")
        if not sid or level is None:
            return None
        heading = sec.find(["h1", "h2", "h3", "h4", "h5"], recursive=False)
        if heading is None:
            return None
        num_span = heading.find("span", class_="header-section-number")
        number = num_span.get_text(strip=True) if num_span else ""
        title = heading.get_text(" ", strip=True)
        if number:
            title = title.replace(number, "", 1).strip()
        return {"id": sid, "level": level, "number": number, "title": title}

    # The chapter title comes from the chapter root itself (its own <h1>).
    root_info = sec_info(chapter) if chapter.name == "div" else None
    chapter_title = root_info["title"] if root_info else slug_of(fname)
    chapter_id = chapter.get("id", slug_of(fname))

    tree = []
    for sec in chapter.find_all("div", class_="section"):  # descendants only
        info = sec_info(sec)
        if info:
            tree.append(info)

    # --- meta: first real paragraph as description, first image as OG -------
    first_p = ""
    for p in chapter.find_all("p"):
        t = p.get_text(" ", strip=True)
        if len(t) > 40:
            first_p = t
            break
    desc = re.sub(r"\s+", " ", first_p)[:200] if first_p else BOOK_DESC
    og_img = ""
    first_img = chapter.find("img")
    if first_img:
        og_img = first_img.get("src", "")

    frag = chapter.decode()
    meta = {"desc": desc, "og_img": og_img,
            "title": chapter_title, "id": chapter_id}
    return frag, meta, tree


def build():
    book = []
    for i, fname in enumerate(CHAPTERS, start=1):
        result = clean_chapter(fname)
        if result is None:
            continue
        frag, meta, tree = result
        slug = slug_of(fname)
        title = meta["title"]
        # Save cleaned fragment (book text, source of truth)
        (CONTENT / fname).write_text(frag, encoding="utf-8")
        book.append({
            "num": i, "file": fname, "slug": slug, "title": title,
            "desc": meta["desc"], "og_img": meta["og_img"], "sections": tree,
        })
        report["chapters"].append({
            "num": i, "file": fname, "title": title,
            "sections": len(tree),
            "images": frag.count("<img"),
            "code_blocks": frag.count("language-r"),
        })
    (CONTENT / "toc.json").write_text(
        json.dumps(book, ensure_ascii=False, indent=2), encoding="utf-8")

    for idx, ch in enumerate(book):
        prev_ch = book[idx - 1] if idx > 0 else None
        nxt_ch = book[idx + 1] if idx < len(book) - 1 else None
        page = render_page(ch, book, prev_ch, nxt_ch)
        (ROOT / ch["file"]).write_text(page, encoding="utf-8")

    (ROOT / "tools" / "build_data.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Built {len(book)} chapters.")
    print(f"Warnings: {len(report['warnings'])}, "
          f"missing images: {len(report['images_missing'])}")


def sidebar_html(book, current):
    """Server-render the full chapter/subsection tree for the sidebar."""
    out = ['<ul class="toc-root">']
    for ch in book:
        is_cur = ch["file"] == current["file"]
        cls = "toc-chapter" + (" is-current open" if is_cur else "")
        subs = [s for s in ch["sections"] if s["level"] >= 2]
        has_subs = bool(subs)
        out.append(f'<li class="{cls}" data-file="{escape(ch["file"])}">')
        toggle = ('<button class="toc-toggle" aria-label="Expandir seção" '
                  'aria-expanded="{}"></button>').format("true" if is_cur else "false") if has_subs else ""
        out.append(
            f'{toggle}<a class="toc-link toc-l1" href="{escape(ch["file"])}">'
            f'<span class="toc-num">{escape(str(ch["num"]))}</span>'
            f'<span class="toc-txt">{escape(ch["title"])}</span></a>'
        )
        if has_subs:
            out.append('<ul class="toc-subs">')
            for s in subs:
                href = f'{escape(ch["file"])}#{escape(s["id"])}'
                out.append(
                    f'<li class="toc-sub toc-l{s["level"]}">'
                    f'<a class="toc-link" href="{href}" data-anchor="{escape(s["id"])}">'
                    f'{escape(s["title"])}</a></li>'
                )
            out.append("</ul>")
        out.append("</li>")
    out.append("</ul>")
    return "\n".join(out)


def render_page(ch, book, prev_ch, nxt_ch):
    slug = ch["slug"]
    page_url = f"{SITE_BASE}/{ch['file']}"
    og_img_abs = f"{SITE_BASE}/{ch['og_img']}" if ch["og_img"] else f"{SITE_BASE}/assets/img/capa_r_jasp.PNG"
    full_title = f"{ch['title']} · {BOOK_TITLE}" if ch["num"] > 1 else BOOK_TITLE
    desc = escape(ch["desc"], quote=True)

    prev_link = (
        f'<a class="pnav pnav-prev" href="{escape(prev_ch["file"])}" rel="prev">'
        f'<span class="pnav-dir">← Anterior</span>'
        f'<span class="pnav-title">{escape(prev_ch["title"])}</span></a>'
        if prev_ch else '<span class="pnav pnav-empty"></span>'
    )
    next_link = (
        f'<a class="pnav pnav-next" href="{escape(nxt_ch["file"])}" rel="next">'
        f'<span class="pnav-dir">Próximo →</span>'
        f'<span class="pnav-title">{escape(nxt_ch["title"])}</span></a>'
        if nxt_ch else '<span class="pnav pnav-empty"></span>'
    )

    frag = (CONTENT / ch["file"]).read_text(encoding="utf-8")

    return PAGE_TEMPLATE.format(
        lang="pt-BR",
        title=escape(full_title, quote=True),
        desc=desc,
        author=escape(AUTHOR),
        book_title=escape(BOOK_TITLE),
        chapter_title=escape(ch["title"]),
        page_url=escape(page_url, quote=True),
        og_img=escape(og_img_abs, quote=True),
        og_type="article" if ch["num"] > 1 else "book",
        slug=escape(slug, quote=True),
        chapter_num=ch["num"],
        sidebar=sidebar_html(book, ch),
        content=frag,
        prev_link=prev_link,
        next_link=next_link,
    )


PAGE_TEMPLATE = r"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="{author}">
<link rel="canonical" href="{page_url}">
<meta name="theme-color" content="#faf8f5" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#14110e" media="(prefers-color-scheme: dark)">
<!-- Open Graph -->
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{book_title}">
<meta property="og:title" content="{chapter_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{page_url}">
<meta property="og:image" content="{og_img}">
<meta property="og:locale" content="pt_BR">
<!-- Twitter -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{chapter_title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og_img}">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<!-- KaTeX -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" crossorigin="anonymous">
<!-- highlight.js theme (light/dark handled via CSS below) -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github.min.css">
<link rel="stylesheet" href="assets/css/style.css">
<script>
  // Set theme before paint to avoid a flash of the wrong theme.
  (function () {{
    try {{
      var t = localStorage.getItem('mqt-theme');
      if (!t) t = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', t);
      var fs = localStorage.getItem('mqt-fontsize');
      if (fs) document.documentElement.style.setProperty('--reading-size', fs + 'px');
    }} catch (e) {{}}
  }})();
</script>
</head>
<body data-chapter="{slug}" data-chapter-num="{chapter_num}">
<a class="skip-link" href="#main">Pular para o conteúdo</a>

<header class="topbar">
  <button class="hamburger" id="menuBtn" aria-label="Abrir menu" aria-expanded="false" aria-controls="sidebar">
    <span></span><span></span><span></span>
  </button>
  <a class="topbar-title" href="index.html">{book_title}</a>
  <button class="icon-btn theme-btn js-theme" id="themeTop" aria-label="Alternar tema claro/escuro">
    <svg class="i-sun" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="12" cy="12" r="5" fill="currentColor"/><g stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/></g></svg>
    <svg class="i-moon" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
  </button>
</header>

<div class="progress" id="progress"><div class="progress-bar" id="progressBar"></div></div>

<div class="layout">
  <aside class="sidebar" id="sidebar" aria-label="Sumário do livro">
    <div class="sidebar-head">
      <a href="index.html" class="brand">
        <span class="brand-title">{book_title}</span>
        <span class="brand-author">{author} · PUC-Rio</span>
      </a>
      <div class="side-controls" role="group" aria-label="Preferências de leitura">
        <button class="side-ctl js-theme" aria-label="Alternar tema claro/escuro" title="Tema">
          <svg class="i-sun" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="12" cy="12" r="5" fill="currentColor"/><g stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/></g></svg>
          <svg class="i-moon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
        </button>
        <button class="side-ctl js-font-dec" aria-label="Diminuir fonte" title="Diminuir fonte">A−</button>
        <button class="side-ctl js-font-inc" aria-label="Aumentar fonte" title="Aumentar fonte">A+</button>
        <button class="side-ctl js-share" aria-label="Compartilhar" title="Compartilhar" aria-haspopup="true" aria-expanded="false">
          <svg viewBox="0 0 24 24" width="17" height="17" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M18 8a3 3 0 1 0-2.8-4M6 15a3 3 0 1 0 0-.1M18 22a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg>
        </button>
      </div>
    </div>
    <nav class="toc" aria-label="Sumário">
      {sidebar}
    </nav>
  </aside>
  <div class="scrim" id="scrim" hidden></div>

  <main class="reading" id="main">
    <article class="chapter" id="chapter">
      {content}
    </article>

    <nav class="chapter-nav" aria-label="Navegação entre capítulos">
      {prev_link}
      {next_link}
    </nav>

    <footer class="site-footer">
      <p>{book_title} — camada de anotações por {author} (PUC-Rio).</p>
      <p class="muted">Site estático gerado a partir do livro original em bookdown.</p>
    </footer>
  </main>
</div>

<!-- Scroll-aware floating action bar -->
<div class="fab" id="fab" aria-hidden="false">
  <button class="fab-btn" id="toTop" aria-label="Voltar ao topo" title="Voltar ao topo">
    <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M12 19V5M5 12l7-7 7 7"/></svg>
  </button>
  <button class="fab-btn js-font-dec" id="fontDec" aria-label="Diminuir fonte" title="Diminuir fonte">A−</button>
  <button class="fab-btn js-font-inc" id="fontInc" aria-label="Aumentar fonte" title="Aumentar fonte">A+</button>
  <button class="fab-btn js-theme" id="themeFab" aria-label="Alternar tema" title="Tema claro/escuro">
    <svg class="i-sun" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="12" cy="12" r="5" fill="currentColor"/><g stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/></g></svg>
    <svg class="i-moon" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="currentColor" d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>
  </button>
  <button class="fab-btn js-share" id="shareBtn" aria-label="Compartilhar" title="Compartilhar" aria-haspopup="true" aria-expanded="false">
    <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M18 8a3 3 0 1 0-2.8-4M6 15a3 3 0 1 0 0-.1M18 22a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM8.6 13.5l6.8 4M15.4 6.5l-6.8 4"/></svg>
  </button>
</div>

<!-- Desktop share fallback menu -->
<div class="share-menu" id="shareMenu" role="menu" hidden>
  <div class="share-menu-head">Compartilhar</div>
  <div class="share-scope" role="group" aria-label="Nível de compartilhamento">
    <button class="scope-btn is-active" data-scope="chapter">Este capítulo</button>
    <button class="scope-btn" data-scope="book">O livro</button>
  </div>
  <button class="share-item" data-net="copy" role="menuitem"><span class="share-ico">🔗</span> Copiar link</button>
  <a class="share-item" data-net="whatsapp" role="menuitem" target="_blank" rel="noopener"><span class="share-ico">🟢</span> WhatsApp</a>
  <a class="share-item" data-net="twitter" role="menuitem" target="_blank" rel="noopener"><span class="share-ico">✖</span> X / Twitter</a>
  <a class="share-item" data-net="linkedin" role="menuitem" target="_blank" rel="noopener"><span class="share-ico">in</span> LinkedIn</a>
  <a class="share-item" data-net="email" role="menuitem"><span class="share-ico">✉</span> E-mail</a>
</div>

<div class="toast" id="toast" role="status" aria-live="polite"></div>

<script>window.MQT_SITE_BASE = {site_base!r};</script>
<!-- highlight.js -->
<script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>
<script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/languages/r.min.js"></script>
<!-- KaTeX auto-render -->
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" crossorigin="anonymous"></script>
<script src="assets/js/app.js" defer></script>
</body>
</html>
"""
PAGE_TEMPLATE = PAGE_TEMPLATE.replace("{site_base!r}", "'" + SITE_BASE + "'")


if __name__ == "__main__":
    build()
