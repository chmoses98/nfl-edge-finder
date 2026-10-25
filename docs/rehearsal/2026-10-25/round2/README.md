# Round-2 rehearsal artifacts (2026-10-25, packet 889d4eb7aefafc751f20)

PLUMBING TEST, NOT HANDICAPPING. `PLUMBING_SUBMISSION.json` was written to exercise the machinery on the real week-7 packet (review check, evidence-id resolution, ladder pricing, challenge, dispositions);
its shifts are arbitrary and its "reasoning" says so. Nothing here is a pick. Run:

    python3 scripts/handicap/build_dossiers.py --reports-dir <hr/latest copy> --schedule-csv <schedule> --raw-root data/raw/nflverse
    python3 scripts/handicap/run_card.py --reports-dir <same> --submission PLUMBING_SUBMISSION.json --schedule-csv <schedule> --mode REHEARSAL --out out

Observed: PIT @ NO (the 9:30 ET game) is ranked first and handled as its own state; the other 12 unstarted games are `NOT_REVIEWED` (no review record); NE @ CHI is `POST_KICKOFF_EXCLUDED`.
The Kendre Miller receptions ladder (RB receptions, NO) is priced on both sides, rung by rung; Rico Dowdle (Questionable) is blocked by C5 *for that decision only* while the Miller expression is
selected; the card lists the best clearing expression per contract family.
