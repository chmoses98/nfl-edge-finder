# Errata — 2026 weekly research reports

Recorded reports are append-only: a correction is a new record here, never an edit of the report it corrects.

## 2026-10-01 — Week 1 autopsy coverage: 2026_01_NE_SEA exclusion reason

**Affects:** `week_01/SCRIPT_AUTOPSY.md` and `cumulative_wk01-03/SCRIPT_AUTOPSY.md`, section "Autopsy coverage".

**As recorded:** `2026_01_NE_SEA: eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed)`.

**Correct:** `2026_01_NE_SEA: no player-anatomy corpus for this game (no instrumented pregame projection)`.

**Why:** the Week 1 opener (2026-09-09) predates the player-anatomy job, so `market-data` holds no
`data/shadow/player_anatomy/2026_01_NE_SEA/` and nothing can ever diagnose it. The weekly pipeline did not read
anatomy presence, so it fell back to "pending". A postgame-settle dispatch with a 30-day autopsy window (run
36836668988) confirmed there is no autopsy work for it. `PA.coverage_manifest(..., anatomy_games=...)` now
names the reason correctly, and every report the weekly workflow publishes to `market-data` carries the
corrected line. Regenerating over the same inputs (market-data 57d2a797, handicap-data dec47b61) changes that
line only. Counts are unchanged: Week 1 expected 16, diagnosed 15, excluded 1.
