#!/usr/bin/env python3
"""Phase 1 — listing package generator (SEO title, description, tags, price)."""
import json, os, datetime, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "daily")

def slug(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:60]

def main():
    today = datetime.date.today().isoformat()
    idea = json.load(open(os.path.join(OUT, "product-idea.json")))
    if not idea.get("lane"):
        # Bank genuinely empty (e.g. every lane inside the 30-day cooldown):
        # succeed with nothing to publish instead of crashing the daily run.
        print(json.dumps({"skipped": "bank-empty",
                          "reason": "no eligible lane - all lanes in 30-day cooldown"}))
        return
    kws = (idea.get("keywords") or [])[:15]
    primary = kws[0] if kws else idea["lane"].lower()
    lane, desc, price = idea["lane"], idea["desc"], idea["price_usd"]

    title = f"{primary.title()} — {desc} | Instant Download"
    tags = kws[:13]
    description = f"""{desc} — a done-for-you digital pack for creators and small businesses.

WHAT YOU GET
- {desc} (PNG + editable SVG files)
- Organized, ready-to-customize files — no design skills needed
- Instant download after purchase

WHO IT IS FOR
- Content creators, coaches, and small business owners who want professional {primary} without hiring a designer

PLEASE NOTE
- This is a DIGITAL product. No physical item will be shipped.
- Files are for your own business use. Resale of the raw files as-is is not allowed.
- Colors may vary slightly across screens.

Questions before you buy? Message us anytime — happy to help you pick the right pack.
"""

    pkg = {
        "date": today,
        "lane": lane,
        "seo_title": title[:140],
        "description": description.strip(),
        "tags": tags,
        "price_usd": price,
        "primary_keyword": primary,
        "compliance": {"fake_scarcity": False, "guaranteed_sales_claims": False,
                        "invented_reviews": False, "real_deadline_only": True},
    }
    day_dir = os.path.join(OUT, today)
    os.makedirs(day_dir, exist_ok=True)
    json.dump(pkg, open(os.path.join(day_dir, "listing-package.json"), "w"), indent=1)

    md = f"""# Listing Package — {today}

**Product:** {lane} — {desc}
**Price:** ${price} USD
**Primary keyword:** {primary}

## SEO title
{title[:140]}

## Description
{description.strip()}

## Tags
{", ".join(tags)}

## Compliance (honest copy)
- [x] No fake scarcity / invented urgency
- [x] No "guaranteed sales" claims
- [x] No invented reviews or quotes
- [x] Real seasonal deadlines only

## Why this lane (autopilot)
{", ".join(idea.get("why", []))}
"""
    open(os.path.join(day_dir, "listing-package.md"), "w").write(md)
    print(json.dumps({"package": os.path.join(day_dir, "listing-package.md"), "tags": len(tags)}))

if __name__ == "__main__":
    main()
