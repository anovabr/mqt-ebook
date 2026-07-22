#!/usr/bin/env python3
"""Structural verification of the built site against a running local server."""
import json
import re
import sys
import urllib.request
from urllib.parse import urljoin, quote

BASE = "http://localhost:8971/"
CHAPTERS = json.load(open("content/toc.json", encoding="utf-8"))

ok = 0
fail = []
warn = []


def get(path):
    url = urljoin(BASE, quote(path))
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read()


def head_ok(path):
    try:
        s, _ = get(path)
        return s == 200
    except Exception:
        return False


REQUIRED_MARKERS = {
    "sidebar": r'id="sidebar"',
    "toc tree": r'class="toc-root"',
    "toc toggle/collapse": r'class="toc-toggle"',
    "progress bar": r'id="progressBar"',
    "floating action bar": r'id="fab"',
    "back-to-top": r'id="toTop"',
    "font-decrease": r'id="fontDec"',
    "font-increase": r'id="fontInc"',
    "theme toggle (fab)": r'id="themeFab"',
    "theme toggle (top)": r'id="themeTop"',
    "share button": r'id="shareBtn"',
    "share fallback menu": r'id="shareMenu"',
    "share whatsapp": r'data-net="whatsapp"',
    "share twitter": r'data-net="twitter"',
    "share linkedin": r'data-net="linkedin"',
    "share email": r'data-net="email"',
    "share copy-link": r'data-net="copy"',
    "share scope book": r'data-scope="book"',
    "hamburger": r'id="menuBtn"',
    "KaTeX css": r'katex@0\.16',
    "KaTeX autorender": r'auto-render',
    "highlight.js": r'highlight\.min\.js',
    "app.js": r'assets/js/app\.js',
    "style.css": r'assets/css/style\.css',
    "og:title": r'property="og:title"',
    "twitter:card": r'name="twitter:card"',
    "canonical": r'rel="canonical"',
    "theme pre-paint": r"mqt-theme",
}

CHROME_LEAKS = [
    r'class="book-summary"', r'navigation-prev', r'navigation-next',
    r'gitbook-demo_files', r'<a href="[^"]*#cb\d+-\d+"',
]

print("== Per-chapter checks ==")
all_assets = set()
all_links = set()
for ch in CHAPTERS:
    f = ch["file"]
    try:
        status, body = get(f)
    except Exception as e:
        fail.append(f"{f}: fetch error {e}")
        continue
    if status != 200:
        fail.append(f"{f}: HTTP {status}")
        continue
    html = body.decode("utf-8", "replace")
    missing = [name for name, pat in REQUIRED_MARKERS.items() if not re.search(pat, html)]
    if missing:
        fail.append(f"{f}: missing markers: {', '.join(missing)}")
    else:
        ok += 1
    for pat in CHROME_LEAKS:
        if re.search(pat, html):
            fail.append(f"{f}: chrome leak matched /{pat}/")
    # leading-slash absolute paths are forbidden (breaks subpath hosting)
    for m in re.finditer(r'(?:src|href)="(/[^/][^"]*)"', html):
        fail.append(f"{f}: absolute path '{m.group(1)}'")
    # collect assets + internal links
    for m in re.finditer(r'(?:src|href)="([^"#:]+\.(?:png|jpe?g|gif|svg|css|js|json))"', html, re.I):
        all_assets.add(m.group(1))
    for m in re.finditer(r'href="([^":#]+\.html)(#[^"]*)?"', html):
        all_links.add(m.group(1))
    # content signals
    n_imgs = len(re.findall(r"<img", html))
    has_math = bool(re.search(r"\\\(|\\\[|math inline|math display", html))
    n_code = len(re.findall(r'code class="language-r"', html))
    exp = next(c for c in json.load(open("tools/build_data.json"))["chapters"] if c["file"] == f)
    if exp["images"] and n_imgs < exp["images"]:
        warn.append(f"{f}: fewer <img> ({n_imgs}) than expected ({exp['images']})")
    if exp["code_blocks"] and not n_code:
        fail.append(f"{f}: expected R code blocks but found none")
    print(f"  {f:42} imgs={n_imgs:<3} code={n_code:<3} math={'Y' if has_math else 'n'} "
          f"{'OK' if not missing else 'MISSING'}")

print("\n== Asset resolution (%d unique) ==" % len(all_assets))
bad_assets = [a for a in sorted(all_assets) if not head_ok(a)]
for a in bad_assets:
    fail.append(f"asset 404: {a}")
print(f"  {len(all_assets) - len(bad_assets)}/{len(all_assets)} assets return 200")

print("\n== Internal link resolution (%d unique) ==" % len(all_links))
known = {c["file"] for c in CHAPTERS}
for l in sorted(all_links):
    if l not in known and not head_ok(l):
        fail.append(f"dead internal link: {l}")
print(f"  all internal .html links point to known chapters: "
      f"{all(l in known for l in all_links)}")

print("\n== annotations.json ==")
try:
    s, b = get("content/annotations.json")
    data = json.loads(b)
    print(f"  loaded OK, chapters keyed: "
          f"{[k for k in data if not k.startswith('_')]}")
except Exception as e:
    fail.append(f"annotations.json: {e}")

print("\n== SUMMARY ==")
print(f"  chapters fully OK: {ok}/{len(CHAPTERS)}")
print(f"  warnings: {len(warn)}")
for w in warn:
    print("   ! " + w)
print(f"  failures: {len(fail)}")
for x in fail:
    print("   ✗ " + x)
sys.exit(1 if fail else 0)
