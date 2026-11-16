# V2 unfinished review snapshot — not a release

Prepared 2026-11-14 for Muse's authorized bounded read-only design review.
Original deployed website and GitHub repository have NOT been modified by this handoff.

## Run locally
Python 3 standard library only. From this folder: `python scripts/build.py`, then `python -m http.server 8000 --directory dist`. Open http://localhost:8000/ . No installation needed.

## Scope and limitations
- JSON content/template separation, search/filter, full author expansion, citation copy/fallback and printable CV implemented. Desktop functionality was previously reported as tested; this handoff is not a new test certification.
- 320px/390px mobile visual testing NOT completed. No screenshots or claims of visual signoff included.
- Known open issue: build.py relies on exact name matching and authors.index(site['name']); absent/variant names can fail. Consider structured author IDs/me markers.
- Check narrow venue/title wrapping, accessible controls and print layout in the actual snapshot.
- Homepage already has personal title and description; social OG metadata remains a review item. Do not carry old-template findings over without checking.
- Public academic profile/publication data reproduced from the working v2; author source verification remains pending. Do not invent missing authors or assert source verification.
- Only selected production files included. Hosting configuration, local paths, credentials, QA pages and unrelated work excluded.
- Included portrait/conference images are current site assets; no added private materials. No GPS/date/device identifiers found in image metadata.

## Review request
One bounded pass, at most 5 prioritized actionable improvements with evidence, fix and acceptance check. No deployment, overwriting existing site or publishing without owner's further confirmation. Weekly remaining quota floor70% cannot be verified here; do not infer available quota or start unbounded/high-cost work.
