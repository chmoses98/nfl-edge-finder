# preflight-evidence

Append-only, public market evidence for NFL PRE-TRADE PREFLIGHT.

Each file is one candidate's live Kalshi market object and depth-10 order book, with the timestamps at which
each was retrieved, hashed so an approval can cite it and a later replay can prove it has not changed.

Public read-only market data only. No account data, no credentials, no positions, no fills, no stakes, no
theses. Never merge into main; see docs/PREFLIGHT.md on main.
