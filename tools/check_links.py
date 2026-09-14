#!/usr/bin/env python3
"""Guard: every link goes somewhere, every image is ours and described. Exit 0 = clean.

    python tools/check_links.py                  # index.html
    python tools/check_links.py --file <path>    # another copy (used to prove it goes RED)
    python tools/check_links.py --all            # every page in the repo (report, service pages included)
"""
import argparse
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ap = argparse.ArgumentParser()
ap.add_argument("--file")
ap.add_argument("--all", action="store_true")
a = ap.parse_args()
files = sorted(glob.glob(os.path.join(ROOT, "*.html"))) if a.all else [a.file or os.path.join(ROOT, "index.html")]

fails = []
passes = 0


def check(ok, msg):
    global passes
    if ok:
        passes += 1
    else:
        fails.append(msg)


for path in files:
    f = os.path.basename(path)
    base = os.path.dirname(path)
    raw = open(path, encoding="utf-8").read()
    if re.search(r'<base\s+href="/"', raw):
        base = ROOT  # a copy served from a subfolder with <base href="/"> resolves against the site root
    body = re.sub(r"<script\b.*?</script>", " ", raw, flags=re.S | re.I)
    ids = set(re.findall(r'\bid="([^"]+)"', body))

    for tag in re.findall(r"<a\b[^>]*>", body):
        m = re.search(r'\bhref="([^"]*)"', tag)
        check(bool(m) and m.group(1).strip() not in ("", "#"), f"{f}: <a> with no destination: {tag[:80]}")
        if not m:
            continue
        href = m.group(1)
        if href.startswith("#") and len(href) > 1:
            check(href[1:] in ids, f"{f}: {href} points at an id that does not exist")
        elif href.startswith(("mailto:", "tel:", "http://", "https://")):
            check(True, "")
        elif href:
            target = href.split("#")[0].split("?")[0]
            tpath = os.path.join(base, target)
            check(os.path.exists(tpath), f"{f}: link to missing file {href}")
            # A link to another page's section must land on it. The old service pages linked
            # index.html#about and #cases, which never existed, and this check could not see it.
            if "#" in href and os.path.exists(tpath) and tpath.endswith(".html"):
                frag = href.split("#", 1)[1]
                tbody = re.sub(r"<script\b.*?</script>", " ", open(tpath, encoding="utf-8").read(), flags=re.S | re.I)
                check(frag in set(re.findall(r'\bid="([^"]+)"', tbody)),
                      f"{f}: {href} points at an id that does not exist on {target}")

    for tag in re.findall(r"<img\b[^>]*>", body):
        src = re.search(r'\bsrc="([^"]*)"', tag)
        alt = re.search(r'\balt="([^"]*)"', tag)
        decorative = 'aria-hidden="true"' in tag
        check(bool(alt) and (alt.group(1).strip() or decorative), f"{f}: image without alt text: {tag[:90]}")
        if src:
            s = src.group(1)
            check(not s.startswith(("http://", "https://", "//")), f"{f}: hotlinked image {s[:70]}")
            if not s.startswith(("http", "//", "data:")):
                check(os.path.exists(os.path.join(base, s.split("?")[0])), f"{f}: image file missing {s}")
    for u in re.findall(r"url\(\s*['\"]?([^'\")]+)", body):
        check(not u.startswith(("http://", "https://", "//")), f"{f}: hotlinked CSS image {u[:70]}")
        if not u.startswith(("http", "//", "data:")):
            check(os.path.exists(os.path.join(base, u)), f"{f}: CSS image file missing {u}")

    for label in ("Privacy Policy", "Terms of Service", "Login"):
        # a label that looks like a link but goes nowhere
        m = re.search(r"<(span|a)(?![^>]*href)[^>]*>[^<]*" + re.escape(label), body)
        check(not m, f"{f}: '{label}' shown as if it were a link, with no page behind it")

for m in fails:
    print("FAIL", m)
print(f"{passes} checks passed, {len(fails)} failed ({len(files)} file(s))")
sys.exit(1 if fails else 0)
