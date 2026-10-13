# digital-assets-autopilot

MJS Design Lab ke digital-assets ka **muft** daily autopilot — GitHub Actions par chalta hai,
Muntaha ke token budget se **zero** kharch.

## Phase 1 (live) — roz subah 06:00 PKT
1. **Trend research** (`scripts/research.py`) — Google Trends US + Reddit r/EtsySellers + seasonal calendar. Koi API key nahi.
2. **Lane picker** (`scripts/picker.py`) — `bank/keyword-bank.md` ke lanes ko score karta hai: seasonal match, trend overlap, 30-day cooldown (repeat nahi).
3. **Listing package** (`scripts/package.py`) — SEO title, description, tags, price suggestion + honest-copy compliance checklist.
4. Output `daily/YYYY-MM-DD/listing-package.md` me commit hota hai.

## Phases — dekho PHASE-PLAN.md
