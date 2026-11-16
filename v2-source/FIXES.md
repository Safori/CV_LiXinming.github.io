# v2 fixes applied by Muse (2026-11-16) — local preview package, NOT deployed

Base: Dots' v2 preview snapshot 2026-11-14 (zip sha256 49cebe36…198c, 13 files).
This package fixes the 5 items from Muse's v2 review #vtmzvk. Original live site and GitHub repo untouched. No deployment without owner's confirmation.

1. P0 author matching no longer crashes the build (scripts/build.py)
   - Was: p['authors'].index(site['name']) twice per paper, no fallback; "X. Li" raised ValueError and killed the whole build.
   - Now: index() in try/except, mi=-1 on variant/missing; highlighting only when mi>=0 and shown; short list falls back to first 3 authors.
   - Verified: synthetic test (one paper "X. Li", one paper with no Xinming at all) builds clean, exit 0; other papers still highlight (8 author-me spans in index).

2. P1 search now finds venue abbreviations (scripts/build.py)
   - Was: data-search = title + authors + year + full venue only.
   - Now: short_venue and type included.
   - Verified live in headless Chromium: IEDM -> 2 of 5, EDL -> 1 of 5, ACS ANM -> 1 of 5 (all were 0 of 5 before).

3. P1 OG / social meta added (templates/index.html, CV head in build.py)
   - og:title, og:description, og:type, og:url, og:image (assets/og-image.jpg, 1200x630), twitter:card summary_large_image on both index and CV.
   - Verified: grep og: = 5 tags on each page.

4. P1 images shrunk, dimensions corrected
   - portrait.png 1122x1402 1.8MB -> 304x380, 122KB; vlsi-2026.jpg 4096x3072 3.0MB -> 1280x960, 112KB; new og-image.jpg 1200x630, 50KB. Assets total 4.8MB -> 289KB.
   - News <img> dimensions fixed: was width=3669 height=3261 (wrong), now 1280x960 matching the resized file; portrait width/height in template updated to 304x380 (same aspect ratio).

5. P1 highlighted name no longer breaks mid-name at 320px (dist/style.css)
   - Added .author-me{white-space:nowrap}; highlight spans now carry class="author-me" in index and CV.
   - Verified at 320px: all 10 author-me spans are 16px high (single line; was 40.5px / two lines for the 2025 VLSI paper). 320/390px index+CV: scrollWidth == innerWidth, no horizontal overflow.

Rebuild: python scripts/build.py (deterministic, stdlib only). Screenshots in ../screenshots/ (*-fixed.png).
