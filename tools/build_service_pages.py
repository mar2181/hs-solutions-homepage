#!/usr/bin/env python3
"""Builds the 10 service pages in the homepage's own design system. Run from anywhere.

    python tools/build_service_pages.py     # writes the 10 pages + the homepage quote form
    python tools/seo.py                     # then: titles, canonicals, JSON-LD, phone links
    python tools/check_seo.py && python tools/check_proof.py --all && python tools/check_links.py --all
    node tools/check_lead.mjs

Why it is built this way:
  - The CSS is COPIED OUT OF index.html at build time, never retyped. The old service pages were
    a different template with a different logo, so the site read as two companies. One source of
    styling means a homepage tweak reaches every page on the next build.
  - Every image is a real screenshot already in assets/ (proof_sources.json names who may appear).
    Nothing is hotlinked: the old pages pulled 60+ Unsplash photos, 6 of which now 404.
  - No testimonials, star ratings, percentages or "3x" claims. The old pages carried invented
    five-star reviews under real-sounding names; tools/check_proof.py --all now refuses them.
  - The quote form is ONE fragment, written into every page and into the homepage between
    <!-- quote:start --> and <!-- quote:end -->, posting to api/lead.js.
"""
import html
import os
import re
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHONE_TEL = "+19563937828"
PHONE_DISPLAY = "(956) 393-7828"

# Must match api/lead.js SERVICES exactly; check_lead.mjs compares them.
SERVICE_CHOICES = [
    "Not sure yet", "Website or landing page", "Local SEO and Google Business Profile",
    "Online marketing and ads", "Content and creative", "AI agent", "AI Webmaster",
    "Automation", "Web or mobile app", "POS and inventory", "Real estate marketing",
]

e = html.escape


def webp_size(rel):
    b = open(os.path.join(ROOT, rel), "rb").read(40)
    kind = b[12:16]
    if kind == b"VP8X":
        return 1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little")
    if kind == b"VP8 ":
        return struct.unpack("<H", b[26:28])[0] & 0x3FFF, struct.unpack("<H", b[28:30])[0] & 0x3FFF
    if kind == b"VP8L":
        v = int.from_bytes(b[21:25], "little")
        return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
    sys.exit(f"REFUSED: {rel} is not a webp this script can measure")


def img(rel, alt, lazy=True, priority=False):
    w, h = webp_size(rel)
    extra = ' fetchpriority="high"' if priority else (' loading="lazy"' if lazy else "")
    return f'<img src="{rel}" alt="{e(alt)}" width="{w}" height="{h}"{extra}>'


def homepage_css():
    src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    blocks = [b for b in re.findall(r"<style>(.*?)</style>", src, re.S) if "ONE system" in b]
    if len(blocks) != 1:
        sys.exit(f"REFUSED: expected exactly one homepage design-system <style>, found {len(blocks)}")
    return blocks[0].strip("\n")


EXTRA_CSS = """
/* service pages + the quote form (added by tools/build_service_pages.py) */
.svc-hero{padding-block:clamp(36px,4.5vw,64px) clamp(56px,7vw,96px)}
.svc-hero-grid{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,6fr);gap:clamp(32px,4vw,64px);align-items:center}
.crumb{font-size:12px;color:var(--muted);margin:0 0 18px}
.crumb a:hover{text-decoration:underline;text-underline-offset:3px}
.svc-copy h1{font-size:clamp(40px,4.6vw,68px)}
.svc-copy .sub{font-size:20px;line-height:1.5;color:var(--muted);margin-top:20px;max-width:36ch}
.svc-shot{margin:0}
.svc-shot .frame{display:block;border:1px solid var(--line);border-radius:var(--r2);overflow:hidden;background:var(--white)}
.svc-shot .frame img{width:100%;height:auto}
.svc-shot.square .frame{max-width:520px;margin-left:auto}
.included{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 clamp(24px,4vw,64px);border-top:1px solid var(--line)}
.included .svc:hover b{text-decoration:none}
.band .shot img{display:block}
/* the quote form's styles live in index.html's design system, copied in above */
@media (max-width:1080px){.svc-hero-grid{grid-template-columns:1fr}.svc-shot.square .frame{margin-left:0}}
@media (max-width:720px){
  .svc-hero{padding-block:12px 40px}
  .svc-hero-grid{display:flex;flex-direction:column;gap:12px}
  .svc-shot{order:-1;height:calc(50svh - 30px);min-height:260px;display:flex;flex-direction:column}
  .svc-shot .frame{flex:1 1 0;min-height:0}
  .svc-shot .frame img{height:100%;object-fit:cover;object-position:top}
  .svc-shot.square .frame{max-width:none}
  .svc-shot .caption{margin-top:8px}
  .svc-copy{background:var(--white);border:1px solid var(--line);border-radius:var(--r2);padding:18px 20px}
  .svc-copy .crumb{display:none}
  .svc-copy h1{font-size:34px}
  .svc-copy .sub{font-size:16px;margin-top:10px;line-height:1.45}
  .included{grid-template-columns:1fr}
}
"""

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 32 32%22%3E%3Crect x=%223%22 y=%223%22 width=%2226%22 height=%2226%22 rx=%226%22 fill=%22%23fbfaf6%22 stroke=%22%23121212%22 stroke-width=%225%22/%3E%3Crect x=%2211%22 y=%222%22 width=%228%22 height=%2228%22 fill=%22%23ffd82f%22/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<title>HS Solutions</title>
<style>
"""

PHONE_SVG = ('<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 '
             '6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 '
             '4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.6a1 1 0 0 1-.25 1z"/></svg>')

HEADER = """<header class="nav">
  <div class="wrap nav-inner">
    <a class="logo" href="index.html" aria-label="HS Solutions home"><span class="logo-mark" aria-hidden="true"></span>HS Solutions</a>
    <nav class="nav-links" aria-label="Main">
      <a href="index.html#work">Work</a><a href="index.html#services">Services</a><a href="index.html#petbuddy">Pet Buddy</a><a href="#faq">FAQ</a>
    </nav>
    <div class="nav-actions"><a class="btn dark" href="#quote">Get a quote</a></div>
  </div>
</header>
"""

FOOTER = """<footer>
  <div class="wrap">
    <div class="foot">
      <div>
        <a class="logo" href="index.html"><span class="logo-mark" aria-hidden="true"></span>HS Solutions</a>
      </div>
      <nav aria-label="Services"><h4>Services</h4><a href="websites-landing-pages.html">Websites and landing pages</a><a href="local-seo.html">Local SEO</a><a href="online-marketing.html">Online marketing</a><a href="content-creative.html">Content and creative</a><a href="automation.html">Automation</a><a href="webapps-apps.html">Webapps and apps</a><a href="pos-inventory.html">POS and inventory</a><a href="real-estate.html">Real estate reports</a><a href="ai-agents.html">AI agents</a><a href="ai-webmaster.html">AI Webmaster</a></nav>
      <nav aria-label="HS Solutions"><h4>HS Solutions</h4><a href="index.html">Home</a><a href="index.html#work">Work</a><a href="index.html#petbuddy">Pet Buddy</a><a href="index.html#process">Process</a><a href="#quote">Get a quote</a></nav>
    </div>
    <p class="copyright">&copy; 2026 HS Solutions, McAllen, Texas.</p>
  </div>
</footer>
"""

DOCK = f"""<nav class="dock" aria-label="Quick">
  <a href="index.html"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 11 12 4l9 7"/><path d="M5 10v10h14V10"/></svg>Home</a>
  <a href="index.html#services"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h10"/></svg>Services</a>
  <a href="tel:{PHONE_TEL}">{PHONE_SVG}Call</a>
  <a href="#quote"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 6h16v12H4z"/><path d="m4 7 8 6 8-6"/></svg>Quote</a>
</nav>
"""


def quote_form(page, preselect):
    if preselect not in SERVICE_CHOICES:
        sys.exit(f"REFUSED {page}: '{preselect}' is not a service api/lead.js accepts")
    opts = "".join(f'<option{" selected" if s == preselect else ""}>{e(s)}</option>' for s in SERVICE_CHOICES)
    return (
        f'<form class="quote-form" action="/api/lead" method="post" data-lead>'
        f'<input type="hidden" name="page" value="{page}"><input type="hidden" name="t" value="">'
        '<div class="hp" aria-hidden="true"><label>Leave this empty<input name="website" tabindex="-1" autocomplete="off"></label></div>'
        '<div class="qf-row"><label>Name<input name="name" required maxlength="80" autocomplete="name"></label>'
        '<label>Business<input name="business" maxlength="120" autocomplete="organization"></label></div>'
        '<div class="qf-row"><label>Phone<input name="phone" type="tel" maxlength="30" autocomplete="tel"></label>'
        '<label>Email<input name="email" type="email" maxlength="120" autocomplete="email"></label></div>'
        f'<label>What do you need?<select name="service">{opts}</select></label>'
        '<label>Tell us a little<textarea name="message" rows="4" maxlength="2000"></textarea></label>'
        '<button class="btn primary" type="submit">Send</button>'
        '<p class="qf-status" role="status" aria-live="polite"></p>'
        f'<p id="quote-sent" class="qf-flag">Thanks. Your message reached us, and we\'ll reply by phone or email.</p>'
        f'<p id="quote-failed" class="qf-flag">That didn\'t send. Please call {PHONE_DISPLAY}.</p>'
        '<p class="qf-note">Add a phone or an email. We reply to you directly and never share your details.</p>'
        '</form>'
    )


def page_html(fname, p):
    hero_img = img(p["hero"][0], p["hero"][1], lazy=False, priority=True)
    shot_cls = "svc-shot square" if p["hero"][0].endswith("vera.webp") else "svc-shot"
    included = "".join(f'<div class="svc"><b>{e(a)}</b><span>{e(b)}</span></div>' for a, b in p["included"])

    bands = []
    for i, band in enumerate(p["bands"]):
        title, text, rel, alt, caption = band
        if rel.endswith("-full.webp"):
            visual = (f'<div class="scroll-shot" style="background-image:url({rel})" role="img" '
                      f'aria-label="{e(alt)}"></div>')
        else:
            visual = f'<div class="shot">{img(rel, alt)}</div>'
        bands.append(
            f'<div class="band{" flip" if i % 2 else ""}"><div class="band-copy"><h3>{e(title)}</h3>'
            f'<p class="muted">{e(text)}</p></div><div>{visual}<p class="caption">{e(caption)}</p></div></div>')

    steps = "".join(f'<div class="step"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for a, b in p["steps"])
    faqs = "".join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in p["faqs"])

    body = f"""<main id="top">
<section class="svc-hero">
  <div class="wrap svc-hero-grid">
    <div class="svc-copy">
      <p class="crumb"><a href="index.html">Home</a> / <a href="index.html#services">Services</a> / {e(p["crumb"])}</p>
      <p class="eyebrow">{e(p["eyebrow"])}</p>
      <h1>{e(p["h1"])}</h1>
      <p class="sub">{e(p["sub"])}</p>
      <div class="hero-ctas"><a class="btn primary" href="#quote">Get a quote</a><a class="btn" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a></div>
    </div>
    <figure class="{shot_cls}"><span class="frame">{hero_img}</span><figcaption class="caption">{e(p["hero"][2])}</figcaption></figure>
  </div>
</section>

<section id="included" style="padding-top:0">
  <div class="wrap">
    <div class="head"><div><p class="eyebrow">What's included</p><h2>{e(p["inc_h2"])}</h2></div><p class="muted">{e(p["inc_p"])}</p></div>
    <div class="included">{included}</div>
  </div>
</section>

<section id="work" style="padding-top:0">
  <div class="wrap">
    <div class="head"><div><p class="eyebrow">Real work</p><h2>{e(p["work_h2"])}</h2></div></div>
    {"".join(bands)}
  </div>
</section>

<section id="process" style="padding-top:0">
  <div class="wrap">
    <div class="head"><div><p class="eyebrow">Process</p><h2>How it runs.</h2></div></div>
    <div class="steps">{steps}</div>
  </div>
</section>

<section id="faq" style="padding-top:0">
  <div class="wrap faq">
    <div class="head"><div><p class="eyebrow">FAQ</p><h2>Quick answers.</h2></div></div>
    {faqs}
  </div>
</section>

<section id="quote" style="padding-top:0">
  <div class="wrap">
    <div class="cta dark">
      <div class="cta-copy">
        <p class="eyebrow">Get a quote</p>
        <h2>{e(p["cta_h2"])}</h2>
        <p class="muted">{e(p["cta_p"])}</p>
        <div class="cta-actions"><a class="btn" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a></div>
      </div>
      <div class="cta-form"><!-- quote:start -->{quote_form(fname, p["service"])}<!-- quote:end --></div>
    </div>
  </div>
</section>
</main>
"""
    return (HEAD + homepage_css() + "\n" + EXTRA_CSS.strip("\n") + "\n</style>\n</head>\n<body>\n"
            + HEADER + "\n" + body + "\n" + FOOTER + "\n" + DOCK
            + '<script src="assets/site.js" defer></script>\n</body>\n</html>\n')


RANKINGS = "assets/product/mc-rankings.webp"
RANKINGS_ALT = ("Mission Control rankings table: six client businesses, keywords tracked, how many sit in "
                "Google's top three, and which moved up or down")

PAGES = {
    "websites-landing-pages.html": dict(
        service="Website or landing page", crumb="Websites",
        eyebrow="Website design, McAllen TX",
        h1="Websites built to get the call.",
        sub="Fast, mobile-first websites and landing pages for Rio Grande Valley businesses, in English and Spanish when your customers need it.",
        hero=("assets/work/sugar-shack-top.webp", "The Sugar Shack website home page", "the-sugar-shack.com, a candy store on South Padre Island"),
        inc_h2="Everything a site needs to earn its keep.",
        inc_p="Built from scratch for your business, not a theme with your logo dropped in.",
        included=[("Custom design", "Laid out around what you sell"), ("Mobile first", "Tested on real phones before launch"),
                  ("Local SEO foundations", "Titles, schema, sitemap and speed"), ("English and Spanish", "When your market is bilingual"),
                  ("Landing pages for ads", "One page, one offer, one action"), ("Quote and booking forms", "Leads land in your inbox"),
                  ("Hosting and updates", "We keep it running and current"), ("You own it", "The site and the content are yours")],
        work_h2="Sites we built, live today.",
        bands=[("A homepage that sells a place", "Island Candy's site puts the shop, the menu and the way to find it in front of a visitor on the first screen. Hover the frame to scroll the whole homepage.",
                "assets/work/island-candy-full.webp", "The full Island Candy homepage", "island-candy.com"),
               ("A directory people actually use", "ClearCross Progreso compares dental and pharmacy prices across the border, with pages for every clinic and procedure.",
                "assets/work/clearcross-top.webp", "ClearCross Progreso website, comparing dental and pharmacy prices in Nuevo Progreso", "clearcrossprogreso.com")],
        steps=[("Talk", "What you sell, who buys it, and what the site has to do."), ("Design", "You see the real layout early, on your phone."),
               ("Build", "We write, build and test it on phones and desktops."), ("Launch and run", "It goes live and we keep it updated.")],
        faqs=[("How long does a website take?", "It depends on the number of pages and how much has to be written. You get a timeline on the first call, before anything starts."),
              ("How much does it cost?", "Every site is scoped on a short call, and you get a real number before any work begins."),
              ("Can I update it myself?", "We make changes for you. With the AI Webmaster you can also ask for new pages and posts in plain language and approve them."),
              ("Do you build in Spanish?", "Yes. We build bilingual sites when your customers search in both languages."),
              ("Who owns the website?", "You do: the site, the content and the domain.")],
        cta_h2="Tell us about the site you need.",
        cta_p="Send a few lines and we'll come back with what we'd build first and what it would take."),

    "local-seo.html": dict(
        service="Local SEO and Google Business Profile", crumb="Local SEO",
        eyebrow="Local SEO, McAllen TX",
        h1="Show up when the Valley searches.",
        sub="Google Business Profile, Search Console and local rankings, set up and looked after for businesses from Mission to Brownsville.",
        hero=(RANKINGS, RANKINGS_ALT, "Mission Control, the software we track client rankings in. Real numbers, client names hidden."),
        inc_h2="The places customers look first.",
        inc_p="Most local customers decide from the map and the first few results. We work on both.",
        included=[("Google Business Profile", "Setup, verification and upkeep"), ("Weekly profile posts", "Published and checked live"),
                  ("Search Console", "Setup, sitemap and indexing checks"), ("Local keyword tracking", "Where you rank, measured regularly"),
                  ("Review responses", "Answered in the customer's language"), ("City and service pages", "Pages written for the searches you want"),
                  ("Competitor checks", "Who outranks you, and why"), ("Plain-English reports", "What moved and what we did")],
        work_h2="Tracked, not guessed.",
        bands=[("Rankings you can see", "We track client keywords and watch who moves into Google's top three. You see the same numbers we do.",
                RANKINGS, RANKINGS_ALT, "Mission Control rankings view. Client names hidden."),
               ("A profile that stays current", "Custom Designs TX, a McAllen lighting and security company, gets its site, Google profile and posts kept up to date.",
                "assets/work/custom-designs.webp", "The Custom Designs TX website home page", "customdesignstx.com")],
        steps=[("Audit", "Your profile, your site and who ranks above you."), ("Fix", "Claim, verify and correct what is wrong or missing."),
               ("Publish", "Posts, pages and review replies go out regularly."), ("Track", "Rankings are measured and reported in plain English.")],
        faqs=[("Do I need both a website and a Google Business Profile?", "Yes. The profile puts you on the map; the website is what Google ranks and what you control. We look after both."),
              ("How long until I rank higher?", "Profile fixes and posts show up right away. Rankings build over weeks and months, and we show you the data either way."),
              ("Can you guarantee a top spot?", "No. Nobody controls Google's results. We control the work, and we show you what it did."),
              ("Do you work in Spanish?", "Yes. We post and reply in English and Spanish."),
              ("What if I have more than one location?", "Each location gets its own profile, and each one is kept up.")],
        cta_h2="Find out where you stand.",
        cta_p="Tell us your business and city, and we'll look at your profile and rankings before we talk."),

    "online-marketing.html": dict(
        service="Online marketing and ads", crumb="Online marketing",
        eyebrow="Online marketing, McAllen TX",
        h1="Marketing that brings in calls, not just clicks.",
        sub="Google and Facebook ads, landing pages and follow-up for Rio Grande Valley businesses, with every call and form counted.",
        hero=("assets/work/juan-elizondo-moment.webp", "Juan Elizondo's real estate website, its hero with a home search", "juanjoseelizondo.com, a McAllen real estate agent's site"),
        inc_h2="Every part of the campaign, in one place.",
        inc_p="The ad, the page it lands on and the follow-up are built together, so nothing leaks between them.",
        included=[("Google Ads", "Search campaigns for buyers ready to call"), ("Facebook and Instagram ads", "Local audiences, real creative"),
                  ("A landing page per offer", "Built to turn the click into a lead"), ("Call and form tracking", "Every lead counted"),
                  ("Email follow-up", "So a lead doesn't go cold"), ("Bilingual creative", "English and Spanish ads"),
                  ("Monthly reporting", "What the money did, in plain English"), ("Budget advice", "Where to spend and where to stop")],
        work_h2="Built for businesses we still run.",
        bands=[("Ads that point somewhere good", "Juan Elizondo's ads send buyers to a site built for them, in English and Spanish, instead of a generic listing page.",
                "assets/work/juan-elizondo-moment.webp", "Juan Elizondo's real estate website hero", "juanjoseelizondo.com"),
               ("Search and ads, measured together", "Paid campaigns and local rankings are tracked side by side, so you can see what is earning the calls.",
                RANKINGS, RANKINGS_ALT, "Mission Control rankings view. Client names hidden.")],
        steps=[("Talk", "What a customer is worth to you and who you want."), ("Build", "Ads, landing page and tracking set up together."),
               ("Launch", "Campaigns go live with a clear budget."), ("Report", "Every month: what it cost, what it brought in, what changes.")],
        faqs=[("Is ad spend included in your fee?", "No. Ad spend is paid to Google or Meta directly, so you always see exactly what went to the platform."),
              ("Can you guarantee results?", "No. Anyone who guarantees sales is guessing. We track every call and form and show you what the money did."),
              ("How soon will I see leads?", "Paid ads can bring activity within days of launch. Search rankings take longer."),
              ("Do you run ads in Spanish?", "Yes. Many Valley campaigns work best in both languages."),
              ("How much does it cost?", "It depends on the channels and budget. You get a real number on the first call.")],
        cta_h2="Tell us what a new customer is worth.",
        cta_p="Send a few lines about your business and we'll tell you where we'd spend first."),

    "content-creative.html": dict(
        service="Content and creative", crumb="Content",
        eyebrow="Content and creative, McAllen TX",
        h1="Content that keeps your business visible.",
        sub="Blog posts, Google and Facebook posts, images and short video for Rio Grande Valley businesses, planned and published for you.",
        hero=("assets/work/sugar-shack-top.webp", "The Sugar Shack website home page", "the-sugar-shack.com"),
        inc_h2="A month of content, handled.",
        inc_p="Written, designed and published, and you approve it before anything goes out.",
        included=[("Blog posts", "Written for the searches you want"), ("Google Business posts", "Published and checked live"),
                  ("Facebook posts", "Planned on a calendar you can see"), ("Custom images", "Made for each post"),
                  ("Short video and reels", "Without a studio day"), ("English and Spanish", "Both, when it matters"),
                  ("Your approval first", "Nothing posts without your yes"), ("Monthly plan", "Topics tied to what you sell")],
        work_h2="Content running on real sites.",
        bands=[("A candy store with a story", "The Sugar Shack's site carries long-form posts with their own images, published on a schedule. Hover the frame to scroll the page.",
                "assets/work/sugar-shack-full.webp", "The full Sugar Shack homepage", "the-sugar-shack.com"),
               ("A brand built on content", "Wild Society, a supplement brand, runs its site and blog through a content engine we built.",
                "assets/work/wild-society-top.webp", "Wild Society supplement brand website", "wild-society-landing.vercel.app")],
        steps=[("Plan", "Topics and a calendar built around what you sell."), ("Create", "Copy, images and video made for each post."),
               ("Approve", "You review everything before it publishes."), ("Publish", "Posts go live and we check that they did.")],
        faqs=[("Who writes it?", "We plan and produce it. You review every piece before it publishes."),
              ("Do you post it for me?", "Yes, to Google Business and Facebook, and we check each post is actually live."),
              ("Can you use my voice in videos?", "Only with your written approval. It is your voice and your likeness, never used without your say-so."),
              ("Do you work in Spanish?", "Yes. Content and posting run in both languages."),
              ("How much does it cost?", "It depends on how much you want each month. You get a real number on the first call.")],
        cta_h2="Stop letting your marketing go quiet.",
        cta_p="Tell us what you sell and we'll sketch the first month of content."),

    "ai-agents.html": dict(
        service="AI agent", crumb="AI agents",
        eyebrow="AI agents, McAllen TX",
        h1="AI agents that answer, book and follow up.",
        sub="Custom AI agents that talk to your customers in English or Spanish, work from your own information, and hand the lead to a person.",
        hero=("assets/product/petbuddy-site.webp", "The Pet Buddy Concierge website: give your website a voice, eyes and tools", "petbuddyconcierge.com, our own product"),
        inc_h2="Agents built around your business.",
        inc_p="Each agent works from your own services, prices and policies, and knows when to hand off to you.",
        included=[("Website voice concierge", "Answers visitors out loud, day or night"), ("English and Spanish", "It follows the customer's language"),
                  ("Lead capture", "Name, number and need, sent to you"), ("Appointment booking", "Straight onto your calendar"),
                  ("Your own information", "Answers from your material, not guesses"), ("Tool connections", "CRM, email, calendar and more"),
                  ("Support agents", "Repeat questions handled"), ("Research and reports", "Internal agents for your team")],
        work_h2="Agents working on real sites.",
        bands=[("Pet Buddy, our own concierge", "A character that lives on a website, talks with visitors, shows them around the page and passes you the lead.",
                "assets/product/vera.webp", "Vera, one of the Pet Buddy concierge characters", "Vera, a Pet Buddy concierge character"),
               ("A Spanish-speaking guide for buyers", "Naves McAllen's site walks Mexican buyers through industrial parks in Spanish, with a live concierge on the page.",
                "assets/work/naves-top.webp", "Naves McAllen industrial real estate website, in Spanish", "naves.juanjoseelizondo.com")],
        steps=[("Talk", "Which questions eat your day, and where leads get lost."), ("Build", "An agent trained on your own information."),
               ("Test", "We try to break it before a customer can."), ("Launch and tune", "It goes live and we keep improving it.")],
        faqs=[("Will it make things up?", "It answers from your own information, and we test it on questions it should refuse or pass to you."),
              ("Does it replace my staff?", "It takes the repeat questions and the after-hours contacts. People handle the rest."),
              ("Does it speak Spanish?", "Yes. It follows the language the customer uses."),
              ("Can it connect to my tools?", "Yes: calendars, email, CRMs and your own systems."),
              ("How much does it cost?", "It depends on what the agent needs to do and connect to. You get a real number on the first call.")],
        cta_h2="Tell us what your agent should handle.",
        cta_p="Describe the questions and tasks that take up your day, and we'll tell you what an agent could take off your plate."),

    "ai-webmaster.html": dict(
        service="AI Webmaster", crumb="AI Webmaster",
        eyebrow="AI Webmaster, McAllen TX",
        h1="A website that keeps itself current.",
        sub="We build your site, then the AI Webmaster drafts pages and blog posts, posts to Google and Facebook, and tracks your rankings. You approve every word.",
        hero=("assets/work/custom-designs.webp", "The Custom Designs TX website home page", "customdesignstx.com, run with the AI Webmaster"),
        inc_h2="A marketing assistant that works from your site.",
        inc_p="Ask for what you need in plain language, the way you would ask an employee.",
        included=[("A full site build", "30 to 40 pages built for your business"), ("Pages and posts on request", "Drafted and queued for you"),
                  ("Google and Facebook posts", "Published and checked live"), ("Ranking checks", "See what is working"),
                  ("Owner dashboard", "Drafts, approvals and rankings in one place"), ("Your approval first", "Nothing publishes without your yes"),
                  ("Strategy ideas", "Suggested next pages and posts"), ("You own it", "The site and the content are yours")],
        work_h2="Running on client sites today.",
        bands=[("A client site it keeps current", "Custom Designs TX gets blog posts drafted by the Webmaster, approved by the owner, then published and checked.",
                "assets/work/custom-designs.webp", "The Custom Designs TX website home page", "customdesignstx.com"),
               ("Rankings in the same place", "The rankings view shows which keywords moved, so the next page gets written for the right search.",
                RANKINGS, RANKINGS_ALT, "Mission Control rankings view. Client names hidden.")],
        steps=[("We build", "Your site, built for your business and your market."), ("It drafts", "Pages, posts and profile updates, queued for you."),
               ("You approve", "Nothing goes live without your yes."), ("It tracks", "Rankings show what is working.")],
        faqs=[("Is it really automatic?", "It writes and queues. You approve. Nothing publishes without your yes."),
              ("Do I need to know how to blog?", "No. Ask for what you want in plain language."),
              ("Who owns the site?", "You do: the code and the content."),
              ("What if I don't like a draft?", "Ask for changes. It rewrites until you approve."),
              ("How much does it cost?", "It depends on the size of the site and how much it publishes. You get a real number on the first call.")],
        cta_h2="Put your website to work.",
        cta_p="Tell us about your business and we'll show you what the Webmaster would do first."),

    "automation.html": dict(
        service="Automation", crumb="Automation",
        eyebrow="Business automation, McAllen TX",
        h1="Automate the busywork.",
        sub="Lead follow-up, CRM workflows, reminders and reports for Rio Grande Valley businesses, built around how you already work.",
        hero=("assets/product/pos-sell.webp", "HS POS Pro point-of-sale screen with product photos, categories and the current order total", "HS POS Pro, our point-of-sale app. Store name hidden."),
        inc_h2="The repetitive work, handled.",
        inc_p="We start with the task that eats the most hours and automate that first.",
        included=[("Lead follow-up", "Text and email within minutes"), ("CRM workflows", "Contacts and pipeline kept current"),
                  ("Appointment reminders", "Fewer no-shows"), ("Notifications", "The right person told at the right time"),
                  ("Internal tasks", "Created automatically from events"), ("Reports", "Delivered without anyone building them"),
                  ("AI assistants", "Sort and qualify incoming requests"), ("Your existing tools", "Gmail, calendars, sheets, CRMs")],
        work_h2="Automation we run every day.",
        bands=[("Sales and stock that update themselves", "In HS POS Pro a sale updates inventory on its own, so nobody re-counts the shelf to know what is left.",
                "assets/product/pos-sell.webp", "HS POS Pro point-of-sale screen", "HS POS Pro, running in a real store. Store name hidden."),
               ("Rankings checked without anyone checking", "Client rankings are collected on a schedule and land in one view, with no one copying numbers by hand.",
                RANKINGS, RANKINGS_ALT, "Mission Control rankings view. Client names hidden.")],
        steps=[("Map", "Walk through the task as it happens today."), ("Design", "Decide what the system does and what a person still does."),
               ("Build", "Connect your tools and test it with real cases."), ("Run", "It goes live and we watch for anything that slips.")],
        faqs=[("How much does automation cost?", "It depends on the number of workflows and tools involved. We scope it around your real process."),
              ("What tools can you connect?", "Most CRMs, calendars, email, text messaging, payment tools, spreadsheets and databases."),
              ("Do I need technical experience?", "No. We build it and make it simple for your team to use."),
              ("How long does setup take?", "A single workflow can be quick. Larger multi-tool projects need more planning and testing."),
              ("What happens when something breaks?", "We watch the systems we build and fix what fails.")],
        cta_h2="Tell us what takes too long.",
        cta_p="Describe the task your team repeats every day, and we'll tell you how we'd automate it."),

    "webapps-apps.html": dict(
        service="Web or mobile app", crumb="Webapps and apps",
        eyebrow="Custom software, McAllen TX",
        h1="Software built around how you work.",
        sub="Custom web apps, mobile apps, dashboards and AI tools for Rio Grande Valley businesses, not a template with your logo on it.",
        hero=("assets/work/clearcross-top.webp", "ClearCross Progreso website, comparing dental and pharmacy prices in Nuevo Progreso", "clearcrossprogreso.com, a price-comparison web app"),
        inc_h2="From a single tool to a full platform.",
        inc_p="Built on your real workflow and connected to the tools you already use.",
        included=[("Custom web apps", "Portals, calculators, workflows"), ("Mobile apps", "For customers or your team"),
                  ("Dashboards", "Sales, stock, leads in one screen"), ("Booking and payments", "Checkout and scheduling flows"),
                  ("AI features", "Search, drafting and assistants"), ("Integrations", "CRM, email, calendars, databases"),
                  ("Ongoing support", "Fixes and improvements after launch"), ("You own it", "Your software, your data")],
        work_h2="Software already running.",
        bands=[("A point of sale for a real store", "HS POS Pro handles checkout, product photos and stock in one app, built for how a local store sells.",
                "assets/product/pos-sell.webp", "HS POS Pro point-of-sale screen with product photos, categories and the current order total", "HS POS Pro, our point-of-sale app. Store name hidden."),
               ("A land report buyers can follow", "Land Analysis RGV compares two commercial lots side by side, in Spanish and English, for a real McAllen agent.",
                "assets/work/land-analysis.webp", "A bilingual market analysis comparing two commercial lots in western Hidalgo County", "Land Analysis RGV, our product")],
        steps=[("Discover", "Your workflow, your tools and the real bottleneck."), ("Design", "Screens shaped around how you actually operate."),
               ("Build", "Development, integrations and real data."), ("Launch and improve", "Live, supported and improved as you grow.")],
        faqs=[("How long does a custom app take?", "It depends on the size of the build. You get a timeline on the first call, before anything starts."),
              ("Do I own it?", "Yes. Your software and your data are yours."),
              ("Can it connect to my current tools?", "Yes: CRMs, email, calendars, payments and databases."),
              ("Do you support it after launch?", "Yes. Ongoing support and improvements are part of the work."),
              ("How much does it cost?", "Every build is scoped on a call, and you get a real number before any work begins.")],
        cta_h2="Describe the app you've been thinking about.",
        cta_p="A few lines is enough. We'll tell you how we'd build it and what it would take."),

    "pos-inventory.html": dict(
        service="POS and inventory", crumb="POS and inventory",
        eyebrow="POS and inventory, McAllen TX",
        h1="Sales and stock in one place.",
        sub="Point-of-sale and inventory systems for Rio Grande Valley stores and service businesses, built around how you sell.",
        hero=("assets/product/pos-sell.webp", "HS POS Pro point-of-sale screen with product photos, categories and the current order total", "HS POS Pro, running in a real store. Store name hidden."),
        inc_h2="What a store needs from its register.",
        inc_p="Checkout, stock and reports that agree with each other, without a spreadsheet on the side.",
        included=[("Fast checkout", "Product photos and categories"), ("Live inventory", "Stock updates with every sale"),
                  ("Products and variants", "Sizes, colors, prices, SKUs"), ("Barcodes", "Scan to sell and to count"),
                  ("Low-stock alerts", "Know before you run out"), ("Sales reports", "What sold, when and for how much"),
                  ("Staff roles", "Who can do what"), ("More than one location", "Stock and sales kept in sync")],
        work_h2="Running in a real store.",
        bands=[("HS POS Pro", "Our own point-of-sale and inventory app, in daily use at a real retail store. The store's name is hidden in this screenshot.",
                "assets/product/pos-sell.webp", "HS POS Pro point-of-sale screen", "HS POS Pro. Store name hidden.")],
        steps=[("Walk the store", "How you sell, count and reorder today."), ("Set up", "Products, prices and stock loaded in."),
               ("Train", "Your team learns it on real sales."), ("Support", "We stay on call and keep improving it.")],
        faqs=[("Can it work for more than one location?", "Yes. Inventory, users and reports can be managed centrally."),
              ("Can I bring my current products over?", "Yes. We load your existing products, prices and stock."),
              ("Do you offer training and support?", "Yes. We train your team and stay on call after launch."),
              ("Can it connect to my other tools?", "Yes: accounting, online store and payment tools."),
              ("How much does it cost?", "It depends on features, locations and hardware. We scope it around your store.")],
        cta_h2="Tell us how your store sells.",
        cta_p="What you sell, how many locations, and what your current register gets wrong."),

    "real-estate.html": dict(
        service="Real estate marketing", crumb="Real estate",
        eyebrow="Real estate marketing, McAllen TX",
        h1="The sharpest materials in the room.",
        sub="Property reports, listing sites and bilingual campaigns for Rio Grande Valley real estate agents, built with a working McAllen agent.",
        hero=("assets/work/land-analysis.webp", "A bilingual market analysis comparing two commercial lots in western Hidalgo County", "Land Analysis RGV, prepared for Juan Elizondo"),
        inc_h2="What an agent needs to win the listing.",
        inc_p="Real figures from real sources, dated and checkable, in English and Spanish.",
        included=[("Property reports", "Pricing and market context, dated"), ("Land analysis", "Parcels compared side by side"),
                  ("Listing websites", "A page for every property"), ("Neighborhood campaigns", "Marketing street by street"),
                  ("MLS listing rewrites", "Clearer, better-organized listings"), ("Spanish ad creative", "For bilingual buyers"),
                  ("Investor calculators", "Answers for cross-border buyers"), ("AI concierge", "A guide on your listing site")],
        work_h2="Built with a real agent.",
        bands=[("A home search that feels local", "Juan Elizondo's site gives buyers a home search and a clear way to reach him, in English and Spanish.",
                "assets/work/juan-elizondo-moment.webp", "Juan Elizondo's real estate website, its hero with a home search", "juanjoseelizondo.com"),
               ("Industrial parks, in Spanish", "Naves McAllen presents industrial property to Mexican companies, with a Spanish-speaking concierge on the page.",
                "assets/work/naves-top.webp", "Naves McAllen industrial real estate website, in Spanish", "naves.juanjoseelizondo.com")],
        steps=[("Research", "The market, the comparables and the property's story."), ("Package", "A report the seller keeps, clear and dated."),
               ("Market", "Listing site and campaigns in English and Spanish."), ("Win the listing", "Walk in as the best-prepared agent.")],
        faqs=[("Who is this for?", "Agents, brokers and teams who want better materials without a marketing department."),
              ("Where do the report figures come from?", "Real sources, dated and checkable. We never invent comparables."),
              ("Do the materials work in Spanish?", "Yes. Reports, sites and ads are bilingual when the market is."),
              ("Do you need MLS access from me?", "We work with the listing data you have and improve what is there."),
              ("How much does it cost?", "It depends on what you need per listing or per month. You get a real number on the first call.")],
        cta_h2="Win the next listing.",
        cta_p="Tell us about your market and your next listing, and we'll show you what we'd build."),
}


def main():
    on_disk = sorted(f for f in os.listdir(ROOT) if f.endswith(".html") and f != "index.html")
    if sorted(PAGES) != on_disk:
        sys.exit(f"REFUSED: builder pages {sorted(PAGES)} != service pages on disk {on_disk}")
    for fname, p in PAGES.items():
        for rel in [p["hero"][0]] + [b[2] for b in p["bands"]]:
            if not os.path.exists(os.path.join(ROOT, rel)):
                sys.exit(f"REFUSED {fname}: image {rel} does not exist")
        out = page_html(fname, p)
        open(os.path.join(ROOT, fname), "wb").write(out.encode("utf-8"))
        print("wrote", fname)

    idx_path = os.path.join(ROOT, "index.html")
    idx = open(idx_path, encoding="utf-8").read()
    marker = re.compile(r"<!-- quote:start -->.*?<!-- quote:end -->", re.S)
    if len(marker.findall(idx)) != 1:
        sys.exit("REFUSED: index.html must contain exactly one <!-- quote:start --><!-- quote:end --> block")
    new = marker.sub(lambda m: "<!-- quote:start -->" + quote_form("index.html", "Not sure yet") + "<!-- quote:end -->", idx)
    if new.count('<script src="assets/site.js" defer></script>') != 1:
        sys.exit("REFUSED: index.html must load assets/site.js exactly once")
    if new != idx:
        open(idx_path, "wb").write(new.encode("utf-8"))
        print("updated index.html quote form")
    print("done -- now run: python tools/seo.py")


if __name__ == "__main__":
    main()
