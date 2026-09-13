#!/usr/bin/env python3
"""Guard: the homepage may only show proof we can back up. Exit 0 = clean.

    python tools/check_proof.py                  # check index.html
    python tools/check_proof.py --file <path>    # check another copy (used to prove it goes RED)

What it refuses, in the VISIBLE text (scripts, styles and JSON-LD stripped first):
  - claim-shaped numbers: 500+, 3.2M+, 98%, +243%, $24.6K
  - star ratings and review-style quotations
  - the invented testimonial names, and concept/spec builds presented without a label
It reads names from tools/proof_sources.json, never from the page, so a page cannot vouch for itself.
"""
import argparse
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ap = argparse.ArgumentParser()
ap.add_argument("--file", default=os.path.join(ROOT, "index.html"))
PATH = ap.parse_args().file
SRC = json.load(open(os.path.join(HERE, "proof_sources.json"), encoding="utf-8"))

raw = open(PATH, encoding="utf-8").read()
body = re.sub(r"<(script|style)\b.*?</\1>", " ", raw, flags=re.S | re.I)
body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
text = html.unescape(re.sub(r"<[^>]+>", " ", body))
text = re.sub(r"\s+", " ", text)

fails = []
passes = 0


def check(ok, msg):
    global passes
    if ok:
        passes += 1
    else:
        fails.append(msg)


CLAIM_NUMBER = re.compile(
    r"(?<![\w(])[+-]?\d[\d,.]*\s*(?:[KkMm]\+?|\+|%)(?!\w)"   # 500+  3.2M+  98%  +243%  120K+
    r"|\$\s?\d[\d,.]*\s*[KkMm]?"                             # $24.6K  $1,200
)
hits = sorted(set(m.group(0).strip() for m in CLAIM_NUMBER.finditer(text)))
check(not hits, f"claim-shaped numbers with no source: {hits}")

check("★" not in text and "☆" not in text, "star rating glyphs on the page")
check(not re.search(r"\b\d(\.\d)?\s*/\s*5\b|\b[45]\.\d\s*stars?\b", text, re.I), "a numeric star rating")
quotes = [q for q in re.findall(r"“([^”]{25,})”", text)]
check(not quotes, f"review-style quotations with no source: {[q[:40] for q in quotes]}")
check("<blockquote" not in raw.lower(), "a <blockquote> (testimonial) with no source")

for name in SRC["invented_people"]:
    check(name not in text, f"invented testimonial name: {name}")
for name in SRC["concept_only"]:
    for m in re.finditer(re.escape(name), text):
        window = text[max(0, m.start() - 80): m.end() + 80].lower()
        check("concept" in window or "spec" in window or "demo" in window,
              f"concept/demo build '{name}' shown without a concept, spec or demo label")
for banned in ("Case Studies", "Success stories", "Real Results for Real Businesses", "Customer Satisfaction"):
    check(banned.lower() not in text.lower(), f"results framing with no results behind it: '{banned}'")

# Positive control: the page must actually name real clients, or a blank page passes.
named = [n for n in SRC["clients"] if n in text]
check(len(named) >= 4, f"only {len(named)} real client names on the page: {named}")

for m in fails:
    print("FAIL", m)
print(f"{passes} checks passed, {len(fails)} failed ({os.path.basename(PATH)}; clients named: {len(named)})")
sys.exit(1 if fails else 0)
