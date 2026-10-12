"""Point-in-time (PIT) availability sources for NFL: certification evidence, refusing loaders, prospective capture.

RESEARCH ONLY. Nothing here feeds a prop gate, a recommendation, a stake or a production surface.

Every row a loader returns carries `observed_at` (the instant the value is PROVABLY known to have existed) and
`pit_basis` (why that instant is trustworthy). A row whose value cannot be shown to precede the caller's cutoff is
REFUSED -- dropped and counted in the loader's report -- never returned with a guessed time. See
docs/research/NFL_PIT_AVAILABILITY_CERTIFICATION.md for the measured evidence behind each verdict.

    source                                  verdict (see certification doc)            basis
    nflverse injuries 2010-2024             CERTIFIED (final weekly report)            row-level `date_modified`
    nflverse injuries 2025                  REJECTED                                   no row time, no pre-season-end vintage
    nflverse injuries 2026+                 CERTIFIED via vintages only                content-addressed snapshots + retrieved_at
    nflverse depth_charts 2025+             CERTIFIED (daily snapshots)                row-level `dt` snapshot time
    nflverse depth_charts <= 2024           REJECTED                                   weekly file, no time
    ESPN injuries endpoint (captured)       CERTIFIED prospectively (2026-09-04 ->)    our capture's retrieved_at
    ESPN summary `inactives` block          REJECTED                                   0 of 31 in-window game observations usable
    nflverse weekly_rosters status INA      REJECTED as a pregame source               no time; usable only as a realised label
"""
PIT_VERSION = "nfl-pit-availability-1.0.0"
CERTIFIED_INJURY_SEASONS = range(2010, 2025)        # row-level date_modified present and precedes kickoff
DEPTH_CHART_FIRST_SEASON = 2025                    # first season of timestamped (`dt`) snapshots
STORE_SUBDIR = "data/pit_availability/nfl"
