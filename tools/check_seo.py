#!/usr/bin/env python3
"""Guard for the HS Solutions site's SEO. Exit 0 = every check passed.

    python tools/check_seo.py                 # check this repo
    python tools/check_seo.py --root <dir>    # check another tree (used to prove it goes RED)

It reads the facts from tools/seo.py so the two cannot disagree, but it checks the FILES,
never the tool's own output in memory: a page someone hand-edits after the tool ran is
exactly what it exists to catch.
"""
import argparse
import glob
import html
import importlib.util
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("seo", os.path.join(HERE, "seo.py"))
seo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seo)

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=seo.ROOT)
ROOT = ap.parse_args().root

fails = []
passes = 0


def check(ok, msg):
    global passes
    if ok:
        passes += 1
    else:
        fails.append(msg)


def read(rel):
    p = os.path.join(ROOT, rel)
    return open(p, "rb").read().decode("utf-8") if os.path.exists(p) else None


pages = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "*.html")))
check(pages == sorted(seo.PAGES), f"pages on disk {pages} != SEO table {sorted(seo.PAGES)}")
check(not os.path.isdir(os.path.join(ROOT, "services")),
      "services/ exists: every page would be served twice under two URLs")

titles, descs = {}, {}
for f in pages:
    t = read(f)
    url = seo.url_for(f)

    ts = re.findall(r"<title>(.*?)</title>", t, re.S)
    check(len(ts) == 1, f"{f}: {len(ts)} <title> tags")
    ds = re.findall(r'<meta name="description" content="([^"]*)"', t)
    check(len(ds) == 1, f"{f}: {len(ds)} meta descriptions")
    cs = re.findall(r'<link rel="canonical" href="([^"]*)"', t)
    check(cs == [url], f"{f}: canonical {cs} != [{url}]")
    check(re.findall(r'<meta property="og:url" content="([^"]*)"', t) == [url],
          f"{f}: og:url does not match its canonical")
    # Measure what a searcher sees: "&amp;" is one character on screen, five in the file.
    if ts:
        shown = html.unescape(ts[0])
        check(len(shown) <= 65, f"{f}: title is {len(shown)} chars (Google truncates ~60)")
        titles.setdefault(ts[0], []).append(f)
    if ds:
        shown = html.unescape(ds[0])
        check(70 <= len(shown) <= 170, f"{f}: description is {len(shown)} chars")
        descs.setdefault(ds[0], []).append(f)

    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    check(len(lds) == 1, f"{f}: {len(lds)} JSON-LD blocks")
    if lds:
        try:
            graph = json.loads(lds[0])["@graph"]
        except Exception as ex:  # a parse failure must name itself, not crash the guard
            graph = []
            check(False, f"{f}: JSON-LD does not parse ({ex})")
        types = {n.get("@type"): n for n in graph}
        biz = types.get("ProfessionalService", {})
        check(biz.get("telephone") == seo.PHONE_SCHEMA, f"{f}: schema telephone {biz.get('telephone')}")
        check(biz.get("url") == seo.SITE + "/", f"{f}: schema url {biz.get('url')}")
        check(biz.get("name") == seo.NAME, f"{f}: schema name {biz.get('name')}")
        check([a.get("name") for a in biz.get("areaServed", [])] == seo.AREAS,
              f"{f}: areaServed is not exactly {seo.AREAS}")
        check("streetAddress" not in json.dumps(biz),
              f"{f}: a street address appeared -- this is a service-area business")
        # Walk KEYS, never the serialized text: "review responses" is a real service and
        # a substring scan for "review" fails the page for describing it.
        keys = set()
        stack = list(graph)
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                keys.update(node)
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
        for banned in ("aggregateRating", "review", "reviews", "sameAs"):
            check(banned not in keys, f"{f}: schema carries '{banned}', which nothing verifies")
        if f == "index.html":
            check("Service" not in types, "index.html: homepage should not claim a single Service")
        else:
            svc = types.get("Service", {})
            check(svc.get("provider", {}).get("@id") == seo.SITE + "/#business",
                  f"{f}: Service node missing or not tied to the business")
            check(svc.get("url") == url, f"{f}: Service url {svc.get('url')}")

    tel = f'href="tel:{seo.PHONE_TEL}"'
    hdr = re.search(r"<header\b.*?</header>", t, re.S)
    ftr = re.search(r"<footer\b.*?</footer>", t, re.S)
    check(bool(hdr) and tel in hdr.group(0), f"{f}: no tel: link inside <header>")
    check(bool(ftr) and tel in ftr.group(0), f"{f}: no tel: link inside <footer>")
    check(bool(ftr) and all(a in ftr.group(0) for a in seo.AREAS),
          f"{f}: footer does not name every served city")
    check("hssolutions.com" not in t, f"{f}: still links a domain we do not own (hssolutions.com)")
    check("(555)" not in t and "555-" not in t, f"{f}: placeholder phone number")

for title, fs in titles.items():
    check(len(fs) == 1, f"duplicate title on {fs}: {title}")
for d, fs in descs.items():
    check(len(fs) == 1, f"duplicate description on {fs}")

sm = read("sitemap.xml")
check(sm is not None, "sitemap.xml missing")
if sm:
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [u.text for u in ET.fromstring(sm).findall("s:url/s:loc", ns)]
    want = sorted(seo.url_for(f) for f in seo.PAGES)
    check(sorted(locs) == want, f"sitemap locs {sorted(locs)} != pages {want}")
    check(len(locs) == len(set(locs)), "sitemap lists a URL twice")

rb = read("robots.txt")
check(rb is not None and f"Sitemap: {seo.SITE}/sitemap.xml" in rb, "robots.txt missing or no Sitemap line")
check(rb is not None and not re.search(r"(?m)^Disallow:\s*/\s*$", rb), "robots.txt blocks the whole site")

vj = read("vercel.json")
check(vj is not None, "vercel.json missing")
if vj:
    redirects = json.loads(vj).get("redirects", [])
    check(any(r["source"] == "/services/:slug" and r["destination"] == "/:slug" and r.get("permanent")
              for r in redirects), "vercel.json has no permanent /services/:slug redirect")

for m in fails:
    print("FAIL", m)
print(f"{passes} checks passed, {len(fails)} failed")
sys.exit(1 if fails else 0)
