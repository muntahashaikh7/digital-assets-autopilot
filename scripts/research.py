#!/usr/bin/env python3
"""Phase 1 — free trend research. No API keys. Never fails the run."""
import json, re, urllib.request, datetime, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "daily")
os.makedirs(OUT, exist_ok=True)

def get(url, headers=None, timeout=25):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0 (MJS-DesignLab-Autopilot/1.0)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")

def google_trends():
    try:
        raw = get("https://trends.google.com/trends/api/dailytrends?hl=en-US&tz=-300&geo=US")
        data = json.loads(raw[5:])  # strip ")]}',"
        out = []
        for day in data.get("default", {}).get("trendingSearchesDays", []):
            for t in day.get("trendingSearches", []):
                out.append(t["title"]["query"].lower())
        return out[:25]
    except Exception as e:
        return [f"_err:{type(e).__name__}"]

def reddit_signals():
    try:
        raw = get("https://www.reddit.com/r/EtsySellers/hot/.json?limit=25")
        data = json.loads(raw)
        return [c["data"]["title"].lower() for c in data["data"]["children"]][:25]
    except Exception as e:
        return [f"_err:{type(e).__name__}"]

def news_rss(query):
    """Google News RSS — free, no key, usually reachable."""
    try:
        import urllib.parse
        q = urllib.parse.quote(query)
        raw = get(f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en")
        titles = re.findall(r"<title>(.*?)</title>", raw)
        # first <title> is the feed title itself
        out = []
        for t in titles[1:16]:
            t = re.sub(r"<[^>]+>", "", t).strip().lower()
            if t:
                out.append(t)
        return out
    except Exception as e:
        return [f"_err:{type(e).__name__}"]

def seasonal(today):
    cal = json.load(open(os.path.join(ROOT, "config", "seasonal-calendar.json")))
    near = []
    for ev in cal["events"]:
        for key in ("date_2026", "date_2027"):
            d = ev.get(key)
            if not d:
                continue
            try:
                dt = datetime.date.fromisoformat(d)
            except ValueError:
                continue
            delta = (dt - today).days
            if 0 <= delta <= 60:
                near.append({"event": ev["name"], "date": d, "in_days": delta, "keywords": ev["keywords"]})
                break
    near.sort(key=lambda x: x["in_days"])
    return near

def main():
    today = datetime.date.today()
    payload = {
        "date": today.isoformat(),
        "google_trends_us": google_trends(),
        "reddit_etsy_sellers": reddit_signals(),
        "news_digital_templates": news_rss("digital templates etsy sellers"),
        "news_printable_planner": news_rss("printable planner 2027"),
        "news_canva_creators": news_rss("canva templates creators sell"),
        "seasonal_next_60d": seasonal(today),
        "note": "Free sources only. _err entries mean that source failed and was skipped.",
    }
    tmp = os.path.join(OUT, "trends-today.json")
    json.dump(payload, open(tmp, "w"), indent=1)
    print(json.dumps({"trends": len(payload["google_trends_us"]),
                      "reddit": len(payload["reddit_etsy_sellers"]),
                      "seasonal": len(payload["seasonal_next_60d"])}))

if __name__ == "__main__":
    main()
