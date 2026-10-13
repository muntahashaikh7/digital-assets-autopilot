# PHASE-PLAN — digital-assets-autopilot

**Maqsad:** digital-assets ka poora daily kaam GitHub Actions (muft) par le jana —
Muntaha ke tokens par **zero** bojh. Har phase independent hai; agla phase pichle par toot-ta nahi.

## Phase 1 — Research + Listing package (LIVE)
Roz 06:00 PKT: free trend research (Google Trends + Reddit + seasonal calendar) →
keyword-bank se lane pick (30-day cooldown) → SEO title/description/tags/price →
`daily/YYYY-MM-DD/` me commit. Koi secret nahi, koi API key nahi.

## Phase 2 — Asset build via code (next)
- `scripts/build_assets.py`: lane ke mutabiq **code-drawn** templates (PIL/SVG) — PNG + editable SVG.
- Cover mockup auto-generate (MJS cover style).
- Output: `daily/YYYY-MM-DD/assets/` (zip-ready).
- Koi AI image API nahi — deterministic, muft, honest (koi fake mockup nahi).

## Phase 3 — Promo copy pack (next)
- `scripts/promo_copy.py`: har product ke liye ready captions —
  - Gumroad description (lambi), Pinterest pin titles/descriptions (3-4),
    blog outline (400-600 words), YouTube Shorts title/description/hashtags.
  - Buyer-language me, viral keywords bank se, honest-copy rules enforced.
- Output: `daily/YYYY-MM-DD/promo/POST-COPY.md`.

## Phase 4 — API publishing (needs secrets — GitHub Secrets me)
- **Gumroad**: product create/update via Gumroad API (`GUMROAD_TOKEN` secret).
- **Pinterest**: pins via Pinterest API v5 (`PINTEREST_TOKEN` secret).
- **YouTube**: Shorts upload via YouTube Data API (`YT_CLIENT_JSON` secret, OAuth refresh).
- **Blogger**: blog post via Blogger API v3 (same Google OAuth).
- Har step idempotent: pehle check karo product/pin pehle se maujood to nahi (double-publish se bacho).
- Secrets kabhi repo me nahi — sirf GitHub Secrets.

## Phase 5 — Quality gate + reporting (last)
- Self-QC script: typos scan, image dimensions check, compliance checklist.
- Roz ka summary `daily/YYYY-MM-DD/report.md` — kya bana, kahan publish hua, kya ruka.
- Fail hone par workflow khud dobara try nahi karta — agli subah naya run.

## Notes
- Browser sessions (FB/IG login) GitHub Actions se nahi honge — wo lanes manual/browser par rahenge jab tak API rasta na ho.
- Prices kabhi auto-change nahi (standing rule).
