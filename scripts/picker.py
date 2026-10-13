#!/usr/bin/env python3
"""Phase 1 — product-lane picker. Scores keyword-bank lanes against trends + season."""
import json, re, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, "bank", "keyword-bank.md")
STATE = os.path.join(ROOT, "state", "state.json")
OUT = os.path.join(ROOT, "daily")
COOLDOWN_DAYS = 30

LANE_RE = re.compile(r"^##\s+\d+\.\s+(.+?)\s+—\s+(.+?)\s+\(\$(\d+)\)", re.M)

def parse_bank():
    text = open(BANK, encoding="utf-8").read()
    lanes = []
    for m in LANE_RE.finditer(text):
        name, desc, price = m.group(1).strip(), m.group(2).strip(), int(m.group(3))
        # keywords = comma lines right after the header block
        start = m.end()
        seg = text[start:start + 4000]
        kws = []
        for line in seg.splitlines():
            if line.startswith("##"):
                break
            if "," in line and len(line) < 400 and "[" not in line:
                kws += [k.strip().lower() for k in line.split(",") if k.strip()]
        lanes.append({"lane": name, "desc": desc, "price": price, "keywords": kws[:20]})
    return lanes

def main():
    today = datetime.date.today()
    trends = json.load(open(os.path.join(OUT, "trends-today.json")))
    state = json.load(open(STATE))
    used = {u["lane"].lower() for u in state.get("used_lanes", [])
            if (today - datetime.date.fromisoformat(u["date"])).days < COOLDOWN_DAYS}
    trend_text = " ".join(trends.get("google_trends_us", []) + trends.get("reddit_etsy_sellers", [])).lower()
    seasonal_kws = [k for ev in trends.get("seasonal_next_60d", []) for k in ev["keywords"]]

    scored = []
    for lane in parse_bank():
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
