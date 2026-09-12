#!/usr/bin/env python3
"""Per-page SEO for the HS Solutions static site. The ONE place these facts live.

    python tools/seo.py            # rewrite every page + sitemap.xml + robots.txt
    python tools/check_seo.py      # the guard

Idempotent: running it twice produces identical bytes. For every root *.html page it
rewrites, inside one marked <head> block, the title, meta description, canonical, Open Graph
tags and JSON-LD; it puts a clickable phone link in the header and in the footer; and it
points the strategy-call mailto at an inbox we actually own.

Run it AFTER tools/build_service_pages.py, which regenerates five pages from a template and
would otherwise leave them with the template's title.

Every business fact below was supplied by Mario on 2026-09-12. Nothing here is inferred:
no street address (service-area business), no reviews, no ratings, no social profiles
(`sameAs` stays empty until a real HS Solutions profile exists), no share image.
"""
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE = "https://hs-solutions.dev"
LASTMOD = "2026-09-12"

NAME = "HS Solutions"
PHONE_DISPLAY = "(956) 393-7828"
PHONE_TEL = "+19563937828"
PHONE_SCHEMA = "+1-956-393-7828"
EMAIL = "hssolutions2181@gmail.com"
LOCALITY, REGION, COUNTRY = "McAllen", "TX", "US"
AREAS = ["McAllen", "Edinburg", "Mission", "Pharr", "Brownsville", "Harlingen", "Weslaco"]

# The strategy-call button used to email a domain registered in 2019 by somebody else.
DEAD_MAILTO = "mailto:hello@hssolutions.com"

# file -> (title, meta description, service name; None for the homepage)
PAGES = {
    "index.html": (
        "HS Solutions | Marketing, Websites & AI Agents in McAllen, TX",
        "HS Solutions builds websites, local SEO, online marketing, automation, POS systems "
        "and AI agents for Rio Grande Valley businesses. McAllen, TX - (956) 393-7828.",
        None),
    "online-marketing.html": (
        "Online Marketing Agency in McAllen, TX | HS Solutions",
        "SEO, paid ads, email and lead generation for McAllen and Rio Grande Valley "
        "businesses - campaigns built to bring in calls and customers, not just clicks.",
        "Online Marketing"),
    "local-seo.html": (
        "Local SEO & Google Business Profile, McAllen TX | HS Solutions",
        "Google Business Profile setup and weekly posts, Search Console, local rankings and "
        "review responses for businesses in McAllen, Edinburg, Harlingen and Brownsville.",
        "Local SEO & Google Business Profile Management"),
    "websites-landing-pages.html": (
        "Website Design & Landing Pages in McAllen, TX | HS Solutions",
        "Modern, fast, conversion-focused websites and landing pages for Rio Grande Valley "
        "businesses, built to show up in local search and turn visitors into calls.",
        "Website Design & Landing Pages"),
    "ai-webmaster.html": (
        "AI Webmaster & Website Management, McAllen TX | HS Solutions",
        "We build your 30-40 page site, then the AI Webmaster drafts pages and blogs, posts to "
        "Google and Facebook and tracks rankings nightly. You approve every word.",
        "AI Webmaster Website Management"),
    "content-creative.html": (
        "Social Media & Blog Content in McAllen, TX | HS Solutions",
        "Done-for-you blogs, social posts, graphics and AI video for Rio Grande Valley "
        "businesses - planned, published and verified live, in English and Spanish.",
        "Social Media, Blog & Creative Content"),
    "automation.html": (
        "Business Automation Services in McAllen, TX | HS Solutions",
        "CRM workflows, lead follow-up, notifications and AI automation for Rio Grande Valley "
        "businesses - fewer manual steps, faster responses, nothing slipping through.",
        "Business Automation"),
    "ai-agents.html": (
        "Custom AI Agents for Business in McAllen, TX | HS Solutions",
        "Custom AI agents that answer customers, connect to your tools and take action across "
        "your business - built for Rio Grande Valley companies by a McAllen team.",
        "Custom AI Agent Development"),
    "pos-inventory.html": (
        "POS & Inventory Systems in McAllen, TX | HS Solutions",
        "Point-of-sale and inventory platforms for retail, service and multi-location "
        "businesses in the Rio Grande Valley - sales, stock and reporting in one place.",
        "POS Systems & Inventory Management"),
    "webapps-apps.html": (
        "Custom Web & Mobile App Development in McAllen | HS Solutions",
        "Custom web apps, mobile apps, booking and payment flows, dashboards and AI products, "
        "built around how your Rio Grande Valley business actually operates.",
        "Custom Web & Mobile App Development"),
    "real-estate.html": (
        "Real Estate Agent Marketing in McAllen, TX | HS Solutions",
        "Financial property reports, neighborhood listing campaigns, land analysis and "
        "bilingual ad creative for Rio Grande Valley real estate agents.",
        "Real Estate Marketing & Property Reports"),
}

CSS = (
    ".seo-tel{display:inline-flex;align-items:center;gap:6px;font-weight:700;font-size:14px;"
    "color:inherit;text-decoration:none;white-space:nowrap;margin-right:14px}"
    ".seo-tel svg{width:15px;height:15px;flex:none}"
    ".seo-contact{margin-top:14px;line-height:1.75;font-size:13px}"
    ".seo-contact a{display:inline!important;margin:0!important;padding:0!important;"
    "color:inherit!important;text-decoration:underline}"
    "@media(max-width:560px){.seo-tel{font-size:12px;margin-right:8px}}"
    # Homepage only (.nav-actions exists nowhere else): measured at 360px, the phone icon
    # pushed "Book a Strategy Call" 19px past the screen edge. Tighten, never hide, the call.
    "@media(max-width:420px){.nav-actions{gap:6px!important}.nav-actions .seo-tel{margin-right:2px}"
    ".nav-actions .btn.primary{padding-left:10px!important;padding-right:10px!important}}"
    # Phones get the icon alone (the aria-label still reads the number). Measured: at 414px
    # the spelled-out number pushed the homepage's call button 24px past the screen edge.
    "@media(max-width:480px){.seo-tel .seo-tel-num{position:absolute;width:1px;height:1px;"
    "overflow:hidden;clip:rect(0 0 0 0)}.seo-tel svg{width:20px;height:20px}}"
)

PHONE_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M6.6 '
             '10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 '
             '0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 '
             '2.45.57 3.6a1 1 0 0 1-.25 1z"/></svg>')


def url_for(fname):
    return SITE + "/" if fname == "index.html" else f"{SITE}/{fname}"


def e(s):
    return html.escape(s, quote=True)


def graph_for(fname):
    title, desc, service = PAGES[fname]
    url = url_for(fname)
    biz_id, site_id = SITE + "/#business", SITE + "/#website"
    areas = [{"@type": "City", "name": a,
              "containedInPlace": {"@type": "State", "name": "Texas"}} for a in AREAS]
    graph = [
        {"@type": "ProfessionalService", "@id": biz_id, "name": NAME, "url": SITE + "/",
         "telephone": PHONE_SCHEMA, "email": EMAIL,
         "address": {"@type": "PostalAddress", "addressLocality": LOCALITY,
                     "addressRegion": REGION, "addressCountry": COUNTRY},
         "areaServed": areas, "slogan": "Ideas. Automation. Growth."},
        {"@type": "WebSite", "@id": site_id, "url": SITE + "/", "name": NAME,
         "publisher": {"@id": biz_id}},
        {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": title,
         "description": desc, "isPartOf": {"@id": site_id}, "about": {"@id": biz_id}},
    ]
    if service:
        graph.append({"@type": "Service", "@id": url + "#service", "name": service,
                      "serviceType": service, "url": url, "provider": {"@id": biz_id},
                      "areaServed": areas})
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": service, "item": url}]})
    return {"@context": "https://schema.org", "@graph": graph}


def head_block(fname):
    title, desc, _ = PAGES[fname]
    url = url_for(fname)
    ld = json.dumps(graph_for(fname), ensure_ascii=False, separators=(",", ":"))
    ld = ld.replace("</", "<\\/")  # no string may close the script element early
    return "".join([
        "<!-- seo:start -->",
        f"<title>{e(title)}</title>",
        f'<meta name="description" content="{e(desc)}">',
        f'<link rel="canonical" href="{url}">',
        f'<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{NAME}">',
        f'<meta property="og:locale" content="en_US">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(desc)}">',
        f'<meta property="og:url" content="{url}">',
        '<meta name="twitter:card" content="summary">',
        f'<script type="application/ld+json">{ld}</script>',
        f"<style>{CSS}</style>",
        "<!-- seo:end -->",
    ])


HEADER_TEL = (f'<a class="seo-tel" data-seo="tel" href="tel:{PHONE_TEL}" '
              f'aria-label="Call HS Solutions at {PHONE_DISPLAY}">{PHONE_SVG}'
              f'<span class="seo-tel-num">{PHONE_DISPLAY}</span></a>')
FOOTER_CONTACT = (f'<p class="seo-contact" data-seo="contact">'
                  f'<a data-seo="tel" href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a><br>'
                  f'<a href="mailto:{EMAIL}">{EMAIL}</a><br>'
                  f'Serving {", ".join(AREAS[:-1])} &amp; {AREAS[-1]}, Texas</p>')


def one(pattern, text, what, fname):
    m = list(re.finditer(pattern, text, re.S))
    if len(m) != 1:
        sys.exit(f"REFUSED {fname}: expected exactly 1 {what}, found {len(m)} -- nothing written")
    return m[0]


def rewrite(fname, text):
    # 1. strip everything this tool owns, so a second run is a no-op
    text = re.sub(r"<!-- seo:start -->.*?<!-- seo:end -->", "", text, flags=re.S)
    text = re.sub(r'<p class="seo-contact" data-seo="contact">.*?</p>', "", text, flags=re.S)
    text = re.sub(r'<a[^>]*data-seo="tel"[^>]*>.*?</a>', "", text, flags=re.S)
    # ...and the tags it replaces. A title on its own line takes its line ending with it.
    text = re.sub(r"[ \t]*<title>.*?</title>(\r?\n)?", "", text, flags=re.S)
    text = re.sub(r'[ \t]*<meta name="description"[^>]*>(\r?\n)?', "", text)

    # 2. head block, right after the viewport meta
    vp = one(r'<meta name="viewport"[^>]*>', text, "viewport meta", fname)
    text = text[:vp.end()] + head_block(fname) + text[vp.end():]

    # 3. phone in the header, before the last button
    hdr = one(r"<header\b.*?</header>", text, "<header>", fname)
    block = hdr.group(0)
    last_btn = block.rfind('<a class="btn')
    if last_btn < 0:
        sys.exit(f"REFUSED {fname}: no header button to place the phone link beside")
    block = block[:last_btn] + HEADER_TEL + block[last_btn:]
    text = text[:hdr.start()] + block + text[hdr.end():]

    # 4. contact line in the footer, after its first paragraph
    ftr = one(r"<footer\b.*?</footer>", text, "<footer>", fname)
    block = ftr.group(0)
    first_p = block.find("</p>")
    if first_p < 0:
        sys.exit(f"REFUSED {fname}: footer has no paragraph to follow")
    block = block[:first_p + 4] + FOOTER_CONTACT + block[first_p + 4:]
    text = text[:ftr.start()] + block + text[ftr.end():]

    # 5. leads go to an inbox we own
    text = text.replace(DEAD_MAILTO, f"mailto:{EMAIL}?subject=Strategy%20call")
    return text


def main():
    on_disk = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "*.html")))
    missing = sorted(set(on_disk) - set(PAGES))
    stale = sorted(set(PAGES) - set(on_disk))
    if missing or stale:
        sys.exit(f"REFUSED: pages without SEO entries {missing}; entries without pages {stale}")
    if os.path.isdir(os.path.join(ROOT, "services")):
        sys.exit("REFUSED: services/ exists again -- it duplicates every page. Delete it.")

    for fname in on_disk:
        path = os.path.join(ROOT, fname)
        raw = open(path, "rb").read().decode("utf-8")
        out = rewrite(fname, raw)
        if out != raw:
            open(path, "wb").write(out.encode("utf-8"))
            print("updated", fname)
        else:
            print("unchanged", fname)

    order = ["index.html"] + [f for f in PAGES if f != "index.html"]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for f in order:
        sitemap.append(f"  <url><loc>{url_for(f)}</loc><lastmod>{LASTMOD}</lastmod></url>")
    sitemap.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "wb").write(("\n".join(sitemap) + "\n").encode())
    robots = f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n"
    open(os.path.join(ROOT, "robots.txt"), "wb").write(robots.encode())
    print("wrote sitemap.xml + robots.txt")


if __name__ == "__main__":
    main()
