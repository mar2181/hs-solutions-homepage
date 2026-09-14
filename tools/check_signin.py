#!/usr/bin/env python3
"""Guard for /sign-in -- the fallback page for the shared login database.

A person who lands on /sign-in may carry a LIVE sign-in token in the address
bar. This checks the page can never keep it, show it, or send it anywhere:

  - it strips the address bar in <head>, before the body renders
  - it touches no storage and no network API, and writes no HTML from the URL
  - it loads nothing from any other host
  - vercel.json serves it with a CSP that blocks every request, no-referrer,
    no-store and noindex, and the clean /sign-in path is rewritten to it
  - it stays out of the sitemap

Every rule is proven able to fail against a planted bad page first.
Run: python tools/check_signin.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "sign-in", "index.html")

failures = []
passes = 0


def check(ok, msg):
    global passes
    if ok:
        passes += 1
    else:
        failures.append(msg)
        print("FAIL", msg)


FORBIDDEN = [
    "localStorage", "sessionStorage", "document.cookie", "indexedDB",
    "fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "EventSource",
    "innerHTML", "outerHTML", "insertAdjacentHTML", "document.write",
    "postMessage", "window.open(",
]


def strip_comments(html):
    """The page explains its own rules in comments ("no localStorage..."), so a
    scan that reads comments accuses the explanation. Remove them first."""
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    return re.sub(r"/\*.*?\*/", "", html, flags=re.S)


def problems(html):
    out = []
    html = strip_comments(html)
    for word in FORBIDDEN:
        if word in html:
            out.append(f"uses {word}")
    for attr in re.findall(r'(?:src|href)\s*=\s*"([^"]*)"', html):
        if re.match(r"^(https?:)?//", attr):
            out.append(f"loads or links another host: {attr}")
    if re.search(r"@import|url\(|<link[^>]+stylesheet", html):
        out.append("pulls in an external stylesheet or resource")
    head = html.split("<body", 1)[0]
    if "history.replaceState" not in head:
        out.append("does not strip the address bar in <head>")
    if not re.search(r'<meta name="robots" content="noindex', html):
        out.append("missing noindex meta")
    if '<meta name="referrer" content="no-referrer"' not in html:
        out.append("missing no-referrer meta")
    # the only URL value allowed on screen is the pattern-checked error code
    if re.search(r"textContent\s*=\s*[^;]*\bp\.", html):
        out.append("writes a raw URL value onto the page")
    return out


# 1. controls: each rule can fire
good = ('<head><meta name="robots" content="noindex, nofollow">'
        '<meta name="referrer" content="no-referrer">'
        '<script>history.replaceState(null,"",location.pathname)</script></head><body></body>')
check(problems(good) == [], "control: a minimal correct page passes")
for bad, why in [
    (good.replace("</head>", "<script>localStorage.setItem('t',1)</script></head>"), "storage"),
    (good.replace("</head>", "<script>fetch('/x')</script></head>"), "network"),
    (good.replace("</head>", '<script src="https://cdn.example.com/a.js"></script></head>'), "external script"),
    (good.replace("</head>", '<link rel="stylesheet" href="/a.css"></head>'), "stylesheet"),
    (good.replace("history.replaceState(null,\"\",location.pathname)", ""), "no strip in head"),
    (good.replace('content="noindex, nofollow"', 'content="index"'), "indexable"),
    (good + "<script>el.textContent = p.error_description;</script>", "raw URL value on screen"),
    (good.replace("</head>", "<script>x.innerHTML='a'</script></head>"), "innerHTML"),
]:
    check(problems(bad) != [], f"control: a page with {why} is flagged")

# 2. the real page
check(os.path.isfile(PAGE), "sign-in/index.html exists")
html = open(PAGE, encoding="utf-8").read()
for p in problems(html):
    check(False, f"sign-in page {p}")

# 3. vercel.json serves it safely
cfg = json.load(open(os.path.join(ROOT, "vercel.json"), encoding="utf-8"))
rw = [r for r in cfg.get("rewrites", []) if r.get("source") == "/sign-in"]
check(len(rw) == 1 and rw[0].get("destination") == "/sign-in/index.html",
      "/sign-in is rewritten (not redirected) to the page, so the query string survives")
hdrs = [h for h in cfg.get("headers", []) if h.get("source", "").startswith("/sign-in")]
check(len(hdrs) == 1, "exactly one header block for /sign-in")
got = {h["key"].lower(): h["value"] for h in (hdrs[0]["headers"] if hdrs else [])}
csp = got.get("content-security-policy", "")
check("default-src 'none'" in csp, "CSP blocks every request by default")
check(not re.search(r"https?:|\*|'self'", csp), "CSP allows no host at all")
check("frame-ancestors 'none'" in csp, "CSP forbids framing")
check(got.get("referrer-policy") == "no-referrer", "Referrer-Policy is no-referrer")
check(got.get("cache-control") == "no-store", "Cache-Control is no-store")
check("noindex" in got.get("x-robots-tag", ""), "X-Robots-Tag is noindex")
redir = [r for r in cfg.get("redirects", []) if r.get("source", "").startswith("/sign-in")]
check(redir == [], "no redirect on /sign-in (a redirect would move the address and can drop the query)")

# 4. never advertised
check("sign-in" not in open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read(),
      "sign-in is not in the sitemap")

print(f"\n{passes} passed, {len(failures)} failed")
sys.exit(1 if failures else 0)
