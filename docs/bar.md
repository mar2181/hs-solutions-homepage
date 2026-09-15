# The bar: HS Solutions homepage

Phase 3 of the design loop. **Nothing was built for this document.** Four pages were measured
off the live DOM on 2026-09-12 in real Chrome at 1920x945, after a full-page scroll so lazy media
existed: `design-teardown/scripts/measure.js` plus a picture and word probe. Screenshots were read
by eye afterwards. Every line below can be checked by looking at the page, and is written as a
ratio or a count wherever possible.

## What was measured

| | **ours (live)** | Instrument | Linear | Stripe |
|---|---|---|---|---|
| what it is | local agency | top digital agency | product tool | product platform |
| screens tall, desktop | 7.7 | 8.7 | 10.6 | 16.1 |
| **screens tall, phone (390px)** | **22.7** | 10.4 | 7.0 | 24.4 |
| **words per screen** | **222** | 48 | 142 | 147 |
| pictures | 17 | 18 | 10 | 28 |
| **picture area, in viewports** | **1.01** | 2.52 | 5.03 | 6.02 |
| tallest picture vs one screen | 0.82 | 0.96 | 1.27 | 1.03 |
| full-bleed pictures | 0 | 0 | 2 | 0 |
| screens with no picture | 3 of 8 | 4 of 9 | 4 of 11 | 2 of 17 |
| **distinct type sizes** | **22** (smallest 7px) | 11 | 14 | 17 |
| **distinct text colours** | **25** | 5 | 17 | 33 |
| **distinct surfaces** | **23** | 4 | 32 | 38 |
| **distinct radii** | **21** | 5 | 16 | 11 |
| font families | 1 | 3 (one serif voice) | 2 | 2 |
| accent uses, first screen | 6 | 0 | 0 | unmeasurable |

Unreliable readings, kept out of the bar:
- Stripe's accent count is 254, because its gradient artwork counts as coloured elements.
- The probe reads Stripe's body size as 32px, which is actually its hero paragraph.
- Instrument's H1 is an SVG logo, so no H1 size exists to compare.

## What the numbers say

1. **We are the wordiest page and the least pictured.** At 222 words a screen we carry 4.6x
   Instrument's density, yet have **2.5x less picture than Instrument and 5x less than Linear**.
   A site that sells websites shows almost none.
2. **The sprawl is material, not type.** 25 text colours, 23 surfaces and 21 radii against
   Instrument's 5, 4 and 5. Every card invents its own box.
3. **The phone page is 22.7 screens**, more than twice Instrument's and three times Linear's.
   Most local prospects will see it on a phone.
4. **None of the references earns its authority with claims.** Instrument shows client work tiles
   with a name and one tag. Stripe shows client wordmarks under the CTA. Linear shows the real
   product. We show six statistics and three testimonials nobody gave.

## The mechanisms (the craft critic judges exactly these)

1. **Picture area ≥ 2.5 viewports on desktop**, and at least one real work or product image is
   **≥ 1.0 screen tall**. Every image of work is a real screenshot or a real product frame.
   Generated scenes are **≤ 25% of total picture area**.
2. **≤ 140 words per screen** on desktop, and **≤ 35 words above the fold** (headline, sub-line
   and buttons combined).
3. **One accent.** Brand yellow appears as a fill **at most twice in the first screen**, never
   as body text on a light ground.
   ⛔ **REVISED 2026-09-14 by Mario** ("it looks a little too white... it needs that black and
   yellow and an off-white look"): the page now alternates ink, yellow and off-white bands
   (ink nav + hero, yellow proof strip, ink services, yellow Pet Buddy, ink footer). Yellow may
   be TEXT on ink (13:1) and a highlighter FILL behind a heading word on paper. The part that
   survives is the safety half: **yellow is never text on a light ground.**
4. **≤ 10 distinct type sizes, none under 12px**, all from one ratio. Display type does the
   hierarchy; grey text does not.
5. **Material restraint: ≤ 6 text colours, ≤ 5 surfaces, ≤ 4 radii.**
6. **The phone page is ≤ 12 screens tall**, using the house mobile shell (slim header, inset
   hero, copy card, dock).
7. **Every claim is verifiable.**
   - A client name appears only if `work_sites.json` marks it `tier: client`.
   - Concept and spec builds carry a "concept" label or stay off the homepage.
   - No count, percentage, star rating or quote appears unless it maps to a sourced entry.

## Steal list (no reference supplies more than two decisions)

| Decision | From | Not also taken |
|---|---|---|
| Work shown as large equal tiles: screenshot, name, one tag, nothing else | Instrument | its black canvas, its serif |
| Material restraint (4 surfaces, 5 radii) | Instrument | its layout |
| The real product shown as a frame at least one screen tall | Linear | its dark palette |
| Tight type scale | Linear | its gradients-on-black |
| Real client names as a quiet proof strip directly under the hero CTA | Stripe | its purple, its gradient art |

**Colour stays ours:** warm off-white paper, ink, one yellow.

> **This looks like none of them because it is the only one where every picture is a working
> site we built for a real Rio Grande Valley business, laid out on warm paper with one yellow,
> instead of on black or a gradient.**

## Image list

| Slot | Source | Honesty label |
|---|---|---|
| Hero | Real screenshots of three client sites composited in device frames (Sugar Shack, Custom Designs TX, Juan Elizondo) from `hs-solutions-landing/assets/work/` | none needed: real work |
| Proof strip | Client names set as type (the `tier: client` entries). No invented logos | none needed |
| Work grid (6 to 8) | sugar-shack, custom-designs, juan-elizondo, spi-fun-rentals, rgv-reef (**re-captured today from rgvreef.org**; the old file came from the deleted site), clearcross, island-candy, naves | client names shown |
| Websites band | Real full-page screenshot (`*_full.jpg`) shown scrolling in a frame | real |
| Local SEO band | Real Mission Control rankings screenshot (`site_mc.jpg`) | "our own system" |
| AI agents / Pet Buddy band | Real Vera avatar and product frames (`assets/vera/`, `petbuddy_poster.jpg`); inspect each file before use | real product |
| POS and inventory band | New capture of hs-pos-pro (live) | "our product" |
| Real estate reports band | Land Analysis RGV screenshot (`tier: build`) | "our product" |
| Closing CTA backdrop | ONE Higgsfield-generated Rio Grande Valley scene at dusk: no text, no people, no storefront implied to be a client | atmosphere only |

Nothing hotlinked. Every file is served from this repo with alt text.
⛔ `work_sites.json` holds a demo password. It must never be copied into this site.

## How the panel is proven able to fail

Before any verdict counts, the craft, system and brief critics get a deliberately broken build:
- one type size throughout
- yellow used nine times in the first screen
- the "500+ businesses" strip restored
- stock photos back in the work grid

We record which critic caught each break. A critic that passes it gets rewritten.
