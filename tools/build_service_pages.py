#!/usr/bin/env python3
# Builds the 5 new service pages (root + services/ mirror) from the redesigned
# online-marketing.html template. Run from the repo root.
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

TPL = open('online-marketing.html', 'rb').read().decode('utf-8')
lines = TPL.split('\r\n')
# lines[0..17] = doctype..header (CSS + nav)   lines[18..36] = sections  lines[37] = footer+close
PREFIX = lines[:18]          # through </header>
FOOTER_LINE = lines[37]      # footer + </body></html>, no trailing newline

SERVICES_ROOT = ('<div><h4>Services</h4>'
    '<a href="websites-landing-pages.html">Websites & Landing Pages</a>'
    '<a href="pos-inventory.html">POS Systems</a>'
    '<a href="automation.html">Automation</a>'
    '<a href="ai-agents.html">AI Agents</a>'
    '<a href="online-marketing.html">Online Marketing</a>'
    '<a href="local-seo.html">Local SEO & Visibility</a>'
    '<a href="real-estate.html">Real Estate Intelligence</a>'
    '<a href="content-creative.html">Content & Creative</a>'
    '<a href="webapps-apps.html">Webapps & Apps</a>'
    '<a href="ai-webmaster.html">AI Webmaster</a></div>')
SERVICES_MIRROR = SERVICES_ROOT.replace('href="', 'href="../')

def hero(p):
    dms = ''.join(f'<div class="dm"><small>{s}</small><strong>{v}</strong></div>' for s, v in p['dms'])
    checks = ''.join(f'<span>{c}</span>' for c in p['checks'])
    return ('<section class="hero"><div class="wrap hero-grid"><div>'
        f'<div class="eyebrow">{p["eyebrow"]}</div>'
        f'<h1>{p["h1"]}</h1><p class="lead">{p["lead"]}</p>'
        f'<div class="checks">{checks}</div>'
        '<div class="actions"><a class="btn y" href="index.html#contact">Get a Free Strategy Call →</a>'
        '<a class="btn d" href="#results">◉ See Our Results</a></div></div>'
        '<div class="hero-visual">'
        f'<img class="hero-photo" src="{p["photo"]}" alt="{p["photo_alt"]}">'
        f'<div class="note">{p["note"]}</div>'
        '<div class="socials"><div class="soc">G</div><div class="soc">f</div><div class="soc">◎</div><div class="soc">▶</div></div>'
        '<div class="dashboard">'
        f'<div class="dash-title">{p["dash_title"]}</div>'
        '<div class="dashbars"><i></i><i></i><i></i><i></i><i></i><i></i></div>'
        f'<div class="dashmetrics">{dms}</div></div>'
        f'<div class="phone"><img src="{p["phone"]}" alt="{p["phone_alt"]}"></div>'
        '</div></div></section>')

def pills_section(p):
    pills = ''.join(f'<div class="pill"><b>{i}</b>{t}</div>' for i, t in p['pills'])
    return ('<section><div class="wrap split"><div>'
        f'<div class="eyebrow" style="color:#111">{p["eyebrow2"]}</div>'
        f'<h2 style="font-size:34px;margin:8px 0">{p["h2"]}</h2>'
        f'<p style="color:var(--mut);line-height:1.6;font-size:13px">{p["intro"]}</p></div>'
        f'<div class="service-pills">{pills}</div></div></section>')

def cards_section(p):
    cards = ''.join(
        f'<article class="service-card"><img src="{c[0]}" alt="{c[1]}"><div class="c">'
        f'<h3>{c[1]}</h3><p>{c[2]}</p><a class="learn" href="index.html#contact">Learn More →</a>'
        '</div></article>' for c in p['cards'])
    return ('<section class="dark"><div class="wrap"><div class="section-head"><div>'
        f'<div class="eyebrow">{p["eyebrow3"]}</div><h2>{p["h2b"]}</h2></div>'
        f'<a class="learn" href="index.html#services">View All Services →</a></div>'
        f'<div class="cards6">{cards}</div></div></section>')

def features_section(p):
    feats = ''.join(
        f'<div class="feature"><div class="ic">{f[0]}</div><h3>{f[1]}</h3><p>{f[2]}</p></div>'
        for f in p['features'])
    return ('<section><div class="wrap split"><div>'
        f'<div class="eyebrow" style="color:#111">{p["eyebrow4"]}</div>'
        f'<h2 style="font-size:32px;margin:8px 0">{p["h2c"]}</h2>'
        f'<p style="font-size:12px;color:var(--mut)">{p["sub"]}</p>'
        f'<div class="features" style="margin-top:24px">{feats}</div></div>'
        f'<img style="border-radius:12px;max-height:330px;object-fit:cover" src="{p["side_img"]}" alt="{p["side_alt"]}">'
        '</div></section>')

def steps_section(p):
    steps = ''.join(
        f'<div class="step"><div class="n">{i + 1}</div><h3>{s[0]}</h3>'
        f'<p style="color:#bcc6cc">{s[1]}</p></div>' + ('<div class="arrow">→</div>' if i < 3 else '')
        for i, s in enumerate(p['steps']))
    return ('<section class="dark"><div class="wrap"><div class="section-head"><div>'
        f'<div class="eyebrow">Our process</div><h2>{p["h2d"]}</h2></div>'
        '<a class="learn" href="index.html#contact">Get Started Today →</a></div>'
        f'<div class="steps">{steps}</div></div></section>')

def results_section(p):
    cases = ''.join(
        f'<div class="case"><img src="{c[0]}"><div class="cc"><strong>{c[1]}</strong>'
        f'<h3>{c[2]}</h3><p>{c[3]}</p></div></div>' for c in p['cases'])
    return ('<section id="results"><div class="wrap"><div class="section-head"><div>'
        f'<div class="eyebrow" style="color:#111">{p["eyebrow5"]}</div><h2>{p["h2e"]}</h2></div>'
        '<a class="learn" style="color:#111" href="index.html#contact">View More Case Studies →</a></div>'
        f'<div class="casegrid">{cases}</div></div></section>')

def results_band(p):
    quotes = ''.join(
        '<div class="quote"><div class="qtop">'
        f'<div class="avatar" style="display:grid;place-items:center;background:var(--y);color:#111;font-weight:900;font-size:20px">{q[0][0]}</div>'
        f'<div><b>{q[0]}</b></div></div>'
        f'<p>{q[1]}</p><div class="who">{q[2]}</div></div>' for q in p['quotes'])
    return ('<section class="dark"><div class="wrap"><div class="section-head"><div>'
        f'<div class="eyebrow">Client results</div><h2>{p["h2f"]}</h2></div>'
        '<span class="learn">More Results →</span></div>'
        f'<div class="testimonials">{quotes}</div></div></section>')

def faq_section(p):
    faqs = ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in p['faqs'])
    return ('<section><div class="wrap faq"><div>'
        '<div class="eyebrow" style="color:#111">Frequently asked questions</div>'
        f'<h2>{p["h2g"]}</h2></div><div class="faq-list">{faqs}</div></div></section>')

def cta_section(p):
    return ('<section class="cta"><div class="wrap cta-grid"><div>'
        f'<div class="eyebrow" style="color:#111">{p["cta_eyebrow"]}</div>'
        f'<h2>{p["cta_h2"]}</h2><p>{p["cta_p"]}</p></div>'
        '<a class="btn d" href="index.html#contact">▣ Book a Free Strategy Call →</a></div></section>')

PAGES = {
 'local-seo.html': dict(
  title='Local SEO & Visibility | HS Solutions',
  eyebrow='Local SEO & Visibility',
  h1='Get Found Where Your Customers Are <span class="accent">Looking.</span>',
  lead='We build, manage and monitor the places your customers actually look — Google Business Profile, Google Search Console, local rankings and reviews — so you show up first when it matters.',
  checks=['Claim & verify your GBP','Weekly GBP posts, verified live','GSC setup & monitoring','Nightly rank tracking','Review responses','Bilingual English & Spanish'],
  photo='https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?auto=format&fit=crop&w=900&q=85', photo_alt='Map with location pins',
  note='Top 3<br>On Google ↗',
  dash_title='Ranked.<br>Found.<br>Chosen.',
  dms=[('Keywords tracked','60'),('Top-3 rankings','28'),('Posts verified','100%')],
  phone='https://images.unsplash.com/photo-1563013544-824ae1b704d3?auto=format&fit=crop&w=500&q=80', phone_alt='Search on a phone',
  eyebrow2='Full local search coverage',
  h2='Everything That Puts You on the Map.',
  intro='From claiming your profile to answering reviews and tracking rankings, we run the full local presence — posted, monitored and verified, not just scheduled and hoped for.',
  pills=[('📍','GBP Setup & Claim'),('📌','GBP Posts & Upkeep'),('🔎','GSC Setup & Monitoring'),('📈','Local Keyword Rankings'),('💬','Review Responses'),('✍️','Local Content'),('🌐','Bilingual ES/EN'),('🕵️','Competitor Tracking')],
  eyebrow3='What we manage', h2b='Your Local Presence, End to End.',
  cards=[
   ('https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?auto=format&fit=crop&w=600&q=80','Google Business Profile','Setup, claim, optimize and maintain the profile that drives local calls and visits.'),
   ('https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=600&q=80','Google Search Console','Setup, monitoring, indexing checks and performance insights for your site.'),
   ('https://images.unsplash.com/photo-1543286386-713bdd548da4?auto=format&fit=crop&w=600&q=80','Local Rankings','Nightly keyword tracking so you always know exactly where you stand.'),
   ('https://images.unsplash.com/photo-1563986768494-4dee2763ff3f?auto=format&fit=crop&w=600&q=80','GBP Posting','Regular posts, published and verified live — never scheduled and hoped for.'),
   ('https://images.unsplash.com/photo-1568992687947-868a62a9f521?auto=format&fit=crop&w=600&q=80','Review Responses','Every review answered professionally, in the right language.'),
   ('https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=600&q=80','Local Content','Service pages and content built to rank in your city.')],
  eyebrow4='Why choose HS Solutions', h2c='Local SEO Done Right.', sub='Measured, bilingual and verified — built for RGV businesses that live on local customers.',
  features=[('📍','Verified, Not Assumed','Every GBP post is confirmed live before we call it done.'),
            ('🌐','Bilingual by Default','English and Spanish, because the market is.'),
            ('📈','Nightly Tracking','Rankings measured every night, with a verification gate.'),
            ('🤝','One Team','Marketing, content and Google profiles working together.')],
  side_img='https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1000&q=85', side_alt='local search dashboard',
  h2d='Simple. Tracked. Verified.',
  steps=[('Claim & Fix','We claim your profiles and fix what is wrong or missing.'),
         ('Optimize','Profiles, categories, photos and content tuned for local search.'),
         ('Publish & Track','Posts go live weekly and rankings are tracked nightly.'),
         ('Rank & Convert','More visibility, more calls, more customers through the door.')],
  eyebrow5='Real results', h2e='Businesses That Rank Where It Counts.',
  cases=[
   ('https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=500&q=80','28','Top-3 Google Rankings','The Sugar Shack • 60 keywords tracked'),
   ('https://images.unsplash.com/photo-1573052905904-34ad8c27f0cc?auto=format&fit=crop&w=500&q=80','100%','Posts Verified Live','GBP • every post confirmed on the profile'),
   ('https://images.unsplash.com/photo-1556761175-b413da4baf72?auto=format&fit=crop&w=500&q=80','+243%','More Leads','Local service business • website + GBP')],
  h2f='Real Businesses. Real Rankings.',
  quotes=[('The Sugar Shack','60 keywords tracked, 28 in Google’s top 3 — and climbing.','South Padre Island, TX'),
          ('Custom Designs TX','Google profile built, maintained and posting every week — verified live.','McAllen, TX'),
          ('Island Candy','Reviews answered and the local profile kept current, hands-off for the owner.','South Padre Island, TX')],
  h2g='Got Questions?<br>We Have Answers.',
  faqs=[
   ('Do I need both a website and a Google Business Profile?','Yes. The profile gets you found in local searches and on Maps; the website is what Google ranks and what you control. We build and maintain both, together.'),
   ('How fast do GBP posts go live?','Immediately after publishing — and we verify each one live on the profile before we call it done.'),
   ('Do you work in Spanish?','Yes. We post and respond in both languages, which matters in RGV markets.'),
   ('How do you track rankings?','Nightly keyword tracking with a verification gate — if a check fails, we never pretend it passed.'),
   ('What if I have multiple locations?','Each location gets its own Google Business Profile, and each one is maintained and posted to.'),
   ('How long until I rank higher?','Honestly, rankings build over weeks and months. Profile visibility and posts are immediate; rankings follow. We show you the data either way.')],
  cta_eyebrow='Ready to get found?', cta_h2='Be the Business They Find First.', cta_p='Schedule a free strategy call and we will look at your current rankings, profile and reviews together.',
 ),
 'real-estate.html': dict(
  title='Real Estate Intelligence | HS Solutions',
  eyebrow='Real Estate Intelligence',
  h1='Win More Listings With <span class="accent">Real Estate Intelligence.</span>',
  lead='Financial property reports, hyperlocal neighborhood campaigns and the tools that make agents look like the sharpest person in the room.',
  checks=['Financial property reports','Neighborhood selling campaigns','Land analysis & HBU','MLS listing optimization','E-2 & FIRPTA calculators','Bilingual ad creative'],
  photo='https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=900&q=85', photo_alt='House with a sold sign',
  note='Listings<br>Won ↗',
  dash_title='Know the<br>Market. Win the<br>Listing.',
  dms=[('Property reports','On demand'),('Campaigns','Hyperlocal'),('Language','ES + EN')],
  phone='https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=500&q=80', phone_alt='Listing on a phone',
  eyebrow2='Built for agents',
  h2='Everything an Agent Needs to Win the Neighborhood.',
  intro='Reports, campaigns and tools built with a real RGV agent — so the materials are what a seller actually wants to see, in both languages.',
  pills=[('📊','Financial Property Reports'),('📍','Neighborhood Selling Marketing'),('🗺️','Land Analysis & HBU'),('📝','MLS Listing Optimization'),('🛂','E-2 & FIRPTA Tools'),('🖥️','Listing Websites'),('🎯','Spanish Ad Creative'),('🔍','Market Research')],
  eyebrow3='What we build', h2b='Tools That Turn Research Into Listings.',
  cards=[
   ('https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=600&q=80','Financial Property Reports','Property, market and neighborhood reports that turn numbers into a decision.'),
   ('https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=600&q=80','Neighborhood Selling Campaigns','Hyperlocal marketing built to win listings street by street.'),
   ('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=600&q=80','Land Analysis & HBU','Parcel comparison and highest-and-best-use analysis buyers understand.'),
   ('https://images.unsplash.com/photo-1554907984-15263bfd63bd?auto=format&fit=crop&w=600&q=80','MLS Listing Optimization','Listings rewritten to rank and convert.'),
   ('https://images.unsplash.com/photo-1553729459-efe14ef6055d?auto=format&fit=crop&w=600&q=80','E-2 & FIRPTA Tools','Calculators and guidance for investor and cross-border buyers.'),
   ('https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=600&q=80','Listing Websites','Modern property and landing sites, with a live AI concierge.')],
  eyebrow4='Why agents choose us', h2c='The Sharpest Materials in the Room.', sub='Real figures, dated and checkable — never invented comps or invented markets.',
  features=[('🏠','Built for Agents','Tools built with an RGV agent, not for a generic industry.'),
            ('📊','Reports, Not Buzzwords','Real figures from real sources, dated and checkable.'),
            ('🌐','Spanish First','The market is bilingual; the materials are too.'),
            ('🎯','Hyperlocal Campaigns','Neighborhood-level marketing that wins the listing.')],
  side_img='https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=85', side_alt='modern home',
  h2d='Research to Signature.',
  steps=[('Research','Market, comparables and the story behind the property.'),
         ('Package','A report the seller keeps — clear, dated and checkable.'),
         ('Market','Hyperlocal campaigns in English and Spanish.'),
         ('Win the Listing','Show up as the best-prepared agent in the room.')],
  eyebrow5='Real results', h2e='Live Work for Real Agents.',
  cases=[
   ('https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=500&q=80','2','Languages, One Campaign','Juan Elizondo • RE/MAX Elite'),
   ('https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=500&q=80','Live','AI Concierge on Listings','Naves McAllen • Spanish-speaking buyers'),
   ('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=500&q=80','HBU','Land Analysis Tool','Land Analysis RGV • comparisons buyers trust')],
  h2f='Built With a Real Agent, for Agents.',
  quotes=[('Juan Elizondo — RE/MAX Elite','Warehouse and homes sites live, with a Spanish-speaking AI concierge guiding buyers.','McAllen, TX'),
          ('Naves McAllen','Bilingual industrial listing site built for Mexican buyers crossing the border.','Live site'),
          ('Land Analysis RGV','Property comparison and highest-and-best-use tool, live today.','Live tool')],
  h2g='Got Questions?<br>We Have Answers.',
  faqs=[
   ('Who is this for?','Real estate agents, brokers and teams that want better materials — reports, campaigns and tools — without a marketing department.'),
   ('What is in a financial property report?','Real figures from real sources, dated and checkable: pricing, comparable sales and market context. No invented comps.'),
   ('Do the materials work in Spanish?','Yes. Reports, campaigns and ads are bilingual by default — the RGV market is.'),
   ('Do you need MLS access from me?','We work with the listing data you have. The listing optimizer improves what is there.'),
   ('Can you market a specific neighborhood?','That is the specialty — hyperlocal campaigns built to win listings street by street.'),
   ('What do the E-2 and FIRPTA tools do?','Calculators for investor-visa buyers and foreign sellers, so you can answer the question on the spot.')],
  cta_eyebrow='Ready to win more listings?', cta_h2='Win the Next Listing.', cta_p='Schedule a free strategy call and see the reports and campaigns in action.',
 ),
 'content-creative.html': dict(
  title='Content & Creative | HS Solutions',
  eyebrow='Content & Creative',
  h1='Content & Creative That <span class="accent">Brings Customers.</span>',
  lead='Done-for-you blogs, social content, graphics and AI video — planned, published and verified, so your marketing never stalls.',
  checks=['SEO blogs that rank','Social content, published for you','Custom imagery per post','AI video & reels','Founder voice clones','Verified live, every time'],
  photo='https://images.unsplash.com/photo-1522542550221-31fd19575a2d?auto=format&fit=crop&w=900&q=85', photo_alt='Creative workspace',
  note='Content<br>That Ships ↗',
  dash_title='Planned.<br>Published.<br>Verified.',
  dms=[('Images per post','4'),('Posts verified','100%'),('Languages','EN + ES')],
  phone='https://images.unsplash.com/photo-1515003197210-e0cd71810b5f?auto=format&fit=crop&w=500&q=80', phone_alt='Video content on a phone',
  eyebrow2='Done-for-you content',
  h2='Everything You Publish, Handled.',
  intro='A month of content planned, written, posted and verified live on Facebook and Google Business — with imagery, video and voice where it counts.',
  pills=[('✍️','SEO Blogs'),('👥','Social Media Content'),('🎨','Graphics & Branding'),('🎬','AI Video'),('🗣️','Founder Voice Clones'),('📱','Reels & Shorts'),('📅','Content Strategy'),('📤','Monthly Publishing')],
  eyebrow3='What we create', h2b='Content Built for the Platform It Lives On.',
  cards=[
   ('https://images.unsplash.com/photo-1492724441997-5dc865305da7?auto=format&fit=crop&w=600&q=80','SEO Blogs','Long-form content that educates, ranks and converts — with custom imagery.'),
   ('https://images.unsplash.com/photo-1611162617474-5b21e879e113?auto=format&fit=crop&w=600&q=80','Social Media Content','Strategy, creation, publishing and ongoing management.'),
   ('https://images.unsplash.com/photo-1626785774573-4b799315345d?auto=format&fit=crop&w=600&q=80','Graphics & Branding','Social assets and brand content built for the platform they live on.'),
   ('https://images.unsplash.com/photo-1492619375914-88005aa9e8fb?auto=format&fit=crop&w=600&q=80','AI Video','Cinematic clips, ads and reels produced at volume.'),
   ('https://images.unsplash.com/photo-1590602847861-f357a9332bbc?auto=format&fit=crop&w=600&q=80','Founder Voice Clones','Your voice, lip-synced, for spokesperson videos at scale.'),
   ('https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=600&q=80','Content Strategy','A month of content planned, written and posted — on a calendar you can see.')],
  eyebrow4='Why choose HS Solutions', h2c='Published, Not Just Planned.', sub='Agencies plan. We publish — and we verify every post is actually live.',
  features=[('✅','Published, Not Planned','Content that actually goes live, verified on the platform.'),
            ('🎬','Video at Volume','Reels and commercials without a studio.'),
            ('🎨','Custom Imagery','Every post gets its own images — no stock clip art.'),
            ('📅','A Calendar You Can See','What is coming, what posted, what performed.')],
  side_img='https://images.unsplash.com/photo-1611162617474-5b21e879e113?auto=format&fit=crop&w=1000&q=85', side_alt='social media on a phone',
  h2d='From Idea to Posted.',
  steps=[('Plan','Strategy, topics and a calendar you can see.'),
         ('Create','Copy, imagery, video and voice where it counts.'),
         ('Publish','Posts go live on Facebook and Google Business.'),
         ('Measure','We verify every post and track what performs.')],
  eyebrow5='Real results', h2e='Content That Is Actually Live.',
  cases=[
   ('https://images.unsplash.com/photo-1455390582262-044cdead277a?auto=format&fit=crop&w=500&q=80','4','Images Per Blog Post','Custom imagery with every article'),
   ('https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=500&q=80','100%','Posts Verified Live','Facebook + GBP, every time'),
   ('https://images.unsplash.com/photo-1536240478700-b869070f9279?auto=format&fit=crop&w=500&q=80','Voice','Founder Clones','Wild Society Nutrition • spokesperson videos')],
  h2f='Real Brands. Real Content.',
  quotes=[('Wild Society Nutrition','Founder voice clone and a magazine-grade blog engine, live.','DTC brand'),
          ('The Sugar Shack','Cinematic blog posts with custom imagery, published on schedule.','South Padre Island, TX'),
          ('Juan Elizondo — RE/MAX Elite','Bilingual ad creative in English and Spanish.','McAllen, TX')],
  h2g='Got Questions?<br>We Have Answers.',
  faqs=[
   ('Who writes the content?','Our team plans and produces it; you review before anything publishes.'),
   ('Do you post it for me?','Yes — to Facebook and Google Business, and we verify every post is live before we call it done.'),
   ('Can you use my voice in videos?','With your approval, we clone your voice for spokesperson videos. It is your voice and your likeness — never used without your say-so.'),
   ('What does a blog post include?','The article, a Google Business post, a Facebook post and four custom images.'),
   ('Do you work in Spanish?','Yes. Content and posting run in both languages.'),
   ('How much does it cost?','It depends on volume and scope — the strategy call gives you a real number, no surprises.')],
  cta_eyebrow='Ready for content that ships?', cta_h2='Never Let Your Marketing Go Quiet.', cta_p='Schedule a free strategy call and get a month of content planned around your business.',
 ),
 'webapps-apps.html': dict(
  title='Webapps & Apps | HS Solutions',
  eyebrow='Webapps & Apps',
  h1='Custom Apps & AI, Built <span class="accent">Around Your Business.</span>',
  lead='From custom web apps to industry AI products — software built for how you actually operate, not a template with your logo on it.',
  checks=['Custom web apps','Mobile apps','AI products','Describe-it-and-it-builds App Builder','Bookings & payments','Dashboards that work'],
  photo='https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=900&q=85', photo_alt='Code on a laptop',
  note='Real<br>Software ↗',
  dash_title='Describe It.<br>Watch It<br>Get Built.',
  dms=[('Sites & apps shipped','24'),('Live AI products','3'),('Support','Ongoing')],
  phone='https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?auto=format&fit=crop&w=500&q=80', phone_alt='App on a phone',
  eyebrow2='Custom development',
  h2='Software Built Around How You Operate.',
  intro='Booking portals, calculators, AI products and full platforms — designed around your real workflows, integrated with your real tools.',
  pills=[('🖥️','Custom Web Apps'),('📱','Mobile Apps'),('🤖','AI Products'),('🛠️','App Builder'),('💳','Booking & Payments'),('📊','Dashboards'),('🔌','Integrations'),('🤝','Ongoing Support')],
  eyebrow3='What we build', h2b='From a Tool to a Platform.',
  cards=[
   ('https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=600&q=80','Custom Web Apps','Software built around your operation — booking, portals, calculators, workflows.'),
   ('https://images.unsplash.com/photo-1551650975-87deedd944c3?auto=format&fit=crop&w=600&q=80','Mobile Apps','Fast, focused apps for your customers and your team.'),
   ('https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=600&q=80','AI Products','CaseVault for law firms and DealerVault for dealership groups are built here.'),
   ('https://images.unsplash.com/photo-1517180102446-f3ece451e9d8?auto=format&fit=crop&w=600&q=80','App Builder','Describe the app you want and watch it get built in front of you.'),
   ('https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=600&q=80','Booking & Payments','Checkout, scheduling and payment flows that actually convert.'),
   ('https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=600&q=80','Dashboards','One screen for what matters: sales, inventory, leads, performance.')],
  eyebrow4='Why choose HS Solutions', h2c='Built, Not Templated.', sub='Your software, your data — and real products already running on it.',
  features=[('⚖️','CaseVault','An AI case operating system for attorneys: evidence search, timeline, live courtroom tools.'),
            ('🚗','DealerVault','An AI co-pilot for dealership groups, demoed on a live Texas Ford dealer.'),
            ('🧩','HS Quizzes','Live AI-hosted quizzes for engagement and leads.'),
            ('🛠️','Your Software, Your Data','Paid for, not rented — the build is yours.')],
  side_img='https://images.unsplash.com/photo-1550751827-5bd092c80758?auto=format&fit=crop&w=1000&q=85', side_alt='technology',
  h2d='Idea to Live.',
  steps=[('Discover','Your workflow, your tools, your real bottlenecks.'),
         ('Design','A solution shaped around how you actually operate.'),
         ('Build','Development, integrations and real data.'),
         ('Launch & Improve','Live, supported and improved as you grow.')],
  eyebrow5='Real results', h2e='Software Already Running.',
  cases=[
   ('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=500&q=80','489','Live Vehicle Inventory','DealerVault • a real Texas Ford dealer'),
   ('https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=500&q=80','24','Sites & Apps Shipped','Real businesses, real software'),
   ('https://images.unsplash.com/photo-1604076850742-4c7221f3101b?auto=format&fit=crop&w=500&q=80','Live','AI Quiz Platform','HS Quizzes • hosted quizzes')],
  h2f='Real Products. Real Users.',
  quotes=[('CaseVault','AI case OS for law firms: evidence search, timeline and live courtroom tools.','For attorneys'),
          ('DealerVault','Co-pilot for dealership groups, reading live inventory and business graphs.','For dealers'),
          ('HS Quizzes','Hosted quizzes with a live AI host.','For engagement & leads')],
  h2g='Got Questions?<br>We Have Answers.',
  faqs=[
   ('How long does a custom app take?','Weeks, not months, for most builds. The App Builder gets you a working first version in days.'),
   ('What does it cost?','Every build is scoped on the strategy call — you get a real number before anything starts.'),
   ('Do I own it?','Yes. Your software and your data are yours — paid for, not rented.'),
   ('Can it connect to my current tools?','Yes — CRM, email, calendars, payments and databases all integrate.'),
   ('Do you support it after launch?','Yes. Ongoing support and improvements are part of the deal.'),
   ('What are CaseVault and DealerVault?','Industry AI products built here: an AI case operating system for law firms, and an AI co-pilot for dealership groups.')],
  cta_eyebrow='Have an idea for an app?', cta_h2='Describe the App You Have Been Thinking About.', cta_p='Schedule a free strategy call and watch your idea become a working build.',
 ),
 'ai-webmaster.html': dict(
  title='AI Webmaster | HS Solutions',
  eyebrow='AI Webmaster',
  h1='The Website That <span class="accent">Runs Itself.</span>',
  lead='We build the site — 30 to 40 pages — then the Webmaster keeps publishing pages and blogs, posts to Google and Facebook, and tracks your rankings every night. You approve every word.',
  checks=['30–40 page site built for you','Publishes pages & blogs on command','Google & Facebook posts, verified','Rankings tracked nightly','Owner dashboard with approvals','From $300/mo'],
  photo='https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=900&q=85', photo_alt='Analytics dashboard',
  note='Your Site<br>Working ↗',
  dash_title='Built.<br>Publishing.<br>Ranking.',
  dms=[('Rankings tracked','60'),('Top-3','28'),('Approval','100%')],
  phone='https://images.unsplash.com/photo-1553877522-43269d4ea984?auto=format&fit=crop&w=500&q=80', phone_alt='Strategy meeting',
  eyebrow2='The flagship service',
  h2='A Website You Can Talk To.',
  intro='Build it, then ask it like an employee: new pages, new blogs, posts to Google and Facebook. You review everything, approve publishing and watch the rankings from one dashboard.',
  pills=[('🖥️','Site Build'),('✍️','Auto Blog Publishing'),('📌','GBP & Social Posts'),('📈','Nightly Rankings'),('📊','Owner Dashboard'),('✅','Preview & Approve'),('🧭','Strategy Board'),('💵','From $300/mo')],
  eyebrow3='What it does', h2b='Your Entire Marketing Team, One Dashboard.',
  cards=[
   ('https://images.unsplash.com/photo-1481487196290-c152efe083f5?auto=format&fit=crop&w=600&q=80','Site Build','A complete 30–40 page website built for your business and your market.'),
   ('https://images.unsplash.com/photo-1492724441997-5dc865305da7?auto=format&fit=crop&w=600&q=80','Blog Publishing','New pages and blogs written on command, queued for your approval.'),
   ('https://images.unsplash.com/photo-1611926653458-09294b3142bf?auto=format&fit=crop&w=600&q=80','Google & Facebook','GBP and social posts, verified live after publishing.'),
   ('https://images.unsplash.com/photo-1553484771-371a605b060b?auto=format&fit=crop&w=600&q=80','Nightly Rankings','Keyword tracking every night, so you see what is working.'),
   ('https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=600&q=80','Owner Dashboard','One screen: drafts, approvals, rankings, strategy.'),
   ('https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=600&q=80','Approve Everything','Nothing publishes without your yes. The business owns the site.')],
  eyebrow4='Why businesses choose it', h2c='An Employee That Never Stops.', sub='The cheapest lead machine you can buy — and every word is still yours to approve.',
  features=[('🗣️','Talk to Your Website','Ask the Webmaster for pages and blogs — like an employee.'),
            ('✅','You Approve Everything','Preview every post before it publishes.'),
            ('📈','Rankings Every Night','Nightly keyword tracking with a verification gate.'),
            ('🏠','You Own It','The business owns the website code and content.')],
  side_img='https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1000&q=85', side_alt='marketing dashboard',
  h2d='How It Works.',
  steps=[('We Build','Your 30–40 page site, built for your business.'),
         ('It Publishes','Pages, blogs and posts, drafted and queued.'),
         ('You Approve','Nothing goes live without your yes.'),
         ('It Ranks','Nightly tracking shows what is working.')],
  eyebrow5='Real results', h2e='Sites That Are Already Running Themselves.',
  cases=[
   ('https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&w=500&q=80','28','Top-3 Rankings','The Sugar Shack • nightly tracking'),
   ('https://images.unsplash.com/photo-1481487196290-c152efe083f5?auto=format&fit=crop&w=500&q=80','30–40','Pages Built','Complete site, then it keeps publishing'),
   ('https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?auto=format&fit=crop&w=500&q=80','100%','Approved Before Publish','The owner reviews every post')],
  h2f='Real Businesses. Running Sites.',
  quotes=[('The Sugar Shack','60 keywords tracked nightly, 28 in Google’s top 3.','South Padre Island, TX'),
          ('Custom Designs TX','Blogs drafted by the Webmaster, approved by the owner, published and verified.','McAllen, TX'),
          ('Juan Elizondo — RE/MAX Elite','Sites live, with the Webmaster watching rankings and site health.','McAllen, TX')],
  h2g='Got Questions?<br>We Have Answers.',
  faqs=[
   ('Is it really automatic?','It writes, drafts and queues. You approve. Nothing publishes without your yes.'),
   ('Do I need to know how to blog?','No — ask it in plain language, like an employee.'),
   ('Who owns the site?','You do. The code and the content are the business’s.'),
   ('What does it cost?','From $300 a month, including the site build, publishing, posting and nightly tracking.'),
   ('Does it work in Spanish?','Yes — content and posting run in both languages.'),
   ('What if I do not like a draft?','Ask for changes. It rewrites until you approve.')],
  cta_eyebrow='Ready to put your site to work?', cta_h2='Put Your Website to Work.', cta_p='See the Webmaster in action and get a free strategy call.',
 ),
}

def build(root_links=True):
    out = {}
    for fname, p in PAGES.items():
        secs = [hero(p), pills_section(p), cards_section(p), features_section(p),
                steps_section(p), results_section(p), results_band(p), faq_section(p), cta_section(p)]
        footer = FOOTER_LINE.replace(
            '<div><h4>Services</h4><a href="websites-landing-pages.html">Websites & Landing Pages</a><a href="pos-inventory.html">POS Systems</a><a href="automation.html">Automation</a><a href="ai-agents.html">AI Agents</a><a href="online-marketing.html">Online Marketing</a></div>',
            SERVICES_ROOT)
        body = PREFIX[:] + secs + [footer]
        html = '\r\n'.join(body)
        html = html.replace('<title>Online Marketing | HS Solutions</title>',
                            f'<title>{p["title"]}</title>')
        out[fname] = html
    return out

root_pages = build()
for fname, html in root_pages.items():
    with open(os.path.join(ROOT, fname), 'wb') as f:
        f.write(html.encode('utf-8'))
    print('wrote', fname)

# ⛔ There is deliberately NO services/ mirror any more. It served every page twice under two
# URLs with no canonical, which splits ranking signals. vercel.json 308s /services/:slug to
# the root page, and tools/seo.py refuses to run if services/ reappears.

# Update the Services column of the 5 existing service pages to the canonical 10-link block.
import re
SVC_RE = re.compile(r'<h4>Services</h4>.*?</div>')
for fname in ['ai-agents.html','automation.html','online-marketing.html','pos-inventory.html','websites-landing-pages.html']:
    p = os.path.join(ROOT, fname)
    t = open(p, 'rb').read().decode('utf-8')
    t2, n = SVC_RE.subn(SERVICES_ROOT, t)
    assert n == 1, f'{fname}: services block matched {n} times'
    open(p, 'wb').write(t2.encode('utf-8'))
    print('footer updated', fname)
print('done -- now run: python tools/seo.py  (these pages were rebuilt from a template '
      'and carry its title until it runs)')
