#!/usr/bin/env python3
"""Phase 1 — product-lane picker. Scores keyword-bank lanes against trends + season."""
import json, re, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, "bank", "keyword-bank.md")
STATE = os.path.join(ROOT, "state", "state.json")
OUT = os.path.join(ROOT, "daily")
COOLDOWN_DAYS = 30

HEAD_RE = re.compile(r"^##\s+\d+\.\s+(.+?)\s*$", re.M)
CAT_PRICE_KEY = {"thumbnail": "thumbnail_pack"}

def lane_category(name, desc):
    t = (name + " " + desc).lower()
    for cat, keys in {"planner": ["planner", "journal", "tracker"], "storybook": ["storybook", "story"],
                      "prompt_pack": ["prompt"], "media_kit": ["media kit", "rate card"],
                      "thumbnail": ["thumbnail"], "templates": ["template"]}.items():
        if any(k in t for k in keys):
            return cat
    return "other"

def parse_bank():
    text = open(BANK, encoding="utf-8").read()
    rules = {}
    try:
        rules = json.load(open(os.path.join(ROOT, "config", "pricing-rules.json"))).get("lane_prices", {})
    except Exception:
        pass
    lanes = []
    for m in HEAD_RE.finditer(text):
        raw = m.group(1).strip()
        price_m = re.search(r"\(\$(\d+)\)", raw)
        price = int(price_m.group(1)) if price_m else None
        added_m = re.search(r"\bNEW\s+(\d{4}-\d{2}-\d{2})", raw)
        added = added_m.group(1) if added_m else None
        head = re.sub(r"\(\$\d+\)", "", raw)
        head = re.sub(r"\s*[—–]\s*NEW\s+\d{4}-\d{2}-\d{2}\s*$", "", head)
        head = re.sub(r"\s*[—–]\s*(?:refreshed|updated).*$", "", head, flags=re.I)
        head = head.strip()
        if re.search(r"[—–]", head):
            name, desc = re.split(r"\s*[—–]\s*", head, maxsplit=1)
        else:
            name, desc = head, head
        name, desc = name.strip(), desc.strip()
        # keywords = comma lines right after the header block
        start = m.end()
        seg = text[start:start + 4000]
        kws = []
        for line in seg.splitlines():
            if line.startswith("##"):
                break
            if "," in line and len(line) < 400 and "[" not in line:
                kws += [k.strip().lower() for k in line.split(",") if k.strip()]
        cat = lane_category(name, desc)
        if price is None:
            price = rules.get(CAT_PRICE_KEY.get(cat, cat), 12)
        lanes.append({"lane": name, "desc": desc, "price": price, "keywords": kws[:20],
                      "added": added, "category": cat})
    return lanes

def main():
    today = datetime.date.today()
    trends = json.load(open(os.path.join(OUT, "trends-today.json")))
    state = json.load(open(STATE))
    used = {u["lane"].lower() for u in state.get("used_lanes", [])
            if (today - datetime.date.fromisoformat(u["date"])).days < COOLDOWN_DAYS}
    trend_text = " ".join(trends.get("google_trends_us", []) + trends.get("reddit_etsy_sellers", [])
                          + trends.get("news_digital_templates", []) + trends.get("news_printable_planner", [])
                          + trends.get("news_canva_creators", [])).lower()
    seasonal_kws = [k for ev in trends.get("seasonal_next_60d", []) for k in ev["keywords"]]
    lanes = parse_bank()
    last_cat = None
    if state.get("used_lanes"):
        last_pick = state["used_lanes"][-1]["lane"].lower()
        for l in lanes:
            if l["lane"].lower() == last_pick:
                last_cat = l["category"]
                break

    scored = []
    for lane in lanes:
        if lane["lane"].lower() in used:
            continue
        score, why = 0, []
        lane_text = (lane["lane"] + " " + lane["desc"]).lower()
        for kw in seasonal_kws:
            if kw in lane_text:
                score += 3
                why.append(f"seasonal:{kw}")
                break
        overlap = sum(1 for k in lane["keywords"] if len(k) > 3 and k in trend_text)
        if overlap:
            score += min(overlap, 4)
            why.append(f"trend-overlap:{overlap}")
        if lane.get("added"):
            try:
                age = (today - datetime.date.fromisoformat(lane["added"])).days
                if 0 <= age <= 14:
                    score += 2
                    why.append(f"fresh:{age}d")
            except ValueError:
                pass
        if last_cat and lane["category"] == last_cat and lane["category"] != "other":
            score -= 2
            why.append("same-category-penalty")
        if 7 <= lane["price"] <= 19:
            score += 1
        scored.append((score, lane, why))
    scored.sort(key=lambda x: -x[0])
    best, why = (scored[0][1], scored[0][2]) if scored else (None, ["bank-empty"])

    idea = {
        "date": today.isoformat(),
        "lane": best["lane"] if best else None,
        "desc": best["desc"] if best else None,
        "price_usd": best["price"] if best else None,
        "keywords": best["keywords"] if best else [],
        "why": why,
        "honest_rules": ["No fake scarcity or invented urgency",
                         "No 'guaranteed sales' claims", "No invented reviews/quotes",
                         "Real seasonal deadlines only"],
    }
    json.dump(idea, open(os.path.join(OUT, "product-idea.json"), "w"), indent=1)
    if best:
        state.setdefault("used_lanes", []).append({"date": today.isoformat(), "lane": best["lane"]})
        json.dump(state, open(STATE, "w"), indent=1)
    print(json.dumps({"picked": idea["lane"], "why": why}))

if __name__ == "__main__":
    main()
