# Local SEO plan: getting hs-solutions.dev to rank in McAllen

Written 2026-09-14. The goal is the local results for searches like "web design McAllen",
"SEO company McAllen" and "marketing agency McAllen TX". Every step below is either done,
or names who has to do it. Nothing here asks for fake reviews, invented stats or a fake address.

## Where we stand (measured, not assumed)

| | state |
|---|---|
| Site on hs-solutions.dev | live, 11 pages, every page has its own title, description, canonical and business schema |
| Sitemap + robots.txt | live, and guarded by `tools/check_seo.py` |
| Quote form | live, delivers to hssolutions2181@gmail.com (proven with a real send) |
| **Google Search Console** | **NOT set up.** hs-solutions.dev is not a property. Google cannot tell us what we rank for, and nothing has been submitted |
| **Google Business Profile** | **none exists.** A different "HS SOLUTIONS" is listed in Reynosa, MX and will compete on brand searches |
| Reviews | none |
| Analytics | none |
| Links from other sites | none measured |

## Why the order below

For a local service business, the map pack (the three businesses under the map) is decided mostly
by the Google Business Profile: its category, how close it is to the searcher, and its reviews.
The website supports the profile; it cannot replace it. So the profile and reviews come first,
and page work comes after.

## Step 1: Search Console (Mario, 5 minutes, then Claude)

1. search.google.com/search-console, signed in as **marioelizondo81@gmail.com** (the account every
   automated pull uses).
2. Add property, choose **Domain**, type `hs-solutions.dev`.
3. Google shows a TXT record. Send it to Claude.
4. Claude adds it to the Vercel DNS for hs-solutions.dev, Mario presses Verify, and Claude submits
   the sitemap through the API and pings Bing through IndexNow.

Why Mario: the stored Google login can read and write Search Console but does not carry the
site-verification permission, so the first step has to happen in the browser.

## Step 2: Google Business Profile (Mario)

- Create it as a **service-area business** with **no street address shown** (we do not publish one,
  and a virtual office address is a suspension risk).
- Primary category: **Website designer**. Secondary: **Internet marketing service**,
  **Marketing agency**, **Software company**.
- Service areas: McAllen, Edinburg, Mission, Pharr, Weslaco, Harlingen, Brownsville.
- Name exactly **HS Solutions**, phone **(956) 393-7828**, website **https://hs-solutions.dev/**.
  Name, phone and website must match the site character for character.
- Add real photos: the screenshots in `assets/work/` and `assets/product/` are ours and honest.
- Verification is usually a video of the business or a postcard; do it the day it is offered.

## Step 3: Reviews from real clients (Mario)

We have real clients who can speak to real work: The Sugar Shack, Island Candy, Island Arcade,
SPI Fun Rentals, Custom Designs TX, Juan Elizondo, RGV Reef, Ironfield Peptides.
Ask each owner once, personally, with the review link from the profile. No incentives, no
writing it for them. Five honest reviews is a real advantage in this market.

## Step 4: Citations (Claude can draft, Mario submits)

Same name, phone and website everywhere: Bing Places (imports from Google once the profile exists),
Apple Business Connect, Yelp, BBB, the McAllen Chamber of Commerce directory, Clutch, UpCity,
Facebook page "About" section. Inconsistent listings hurt; missing ones are just lost signal.

## Step 5: Links from the sites we built (needs each client's OK)

Eight live client sites are ours to run. A small "Website by HS Solutions" credit in each footer,
linking to hs-solutions.dev, is normal practice and is the fastest set of real local links we can
get. It changes client sites, so each owner says yes first.

## Step 6: Content (Claude)

After Search Console shows what people actually search, add pages that answer those questions:
a guide to Google Business Profile for Valley businesses, what a small-business website should
include, and case-study pages for the client sites. Not city pages copied seven times; Google
treats those as doorway pages.

## Done this round (2026-09-14)

- Homepage recoloured to ink, yellow and off-white, per Mario.
- The scrolling website frame now shows the Ironfield Peptides storefront.
- A homepage FAQ answer names the Valley cities we serve, in plain language.
