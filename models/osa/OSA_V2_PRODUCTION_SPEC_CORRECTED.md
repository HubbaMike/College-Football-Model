# OSA v2 — production field adjustment (corrected)
Approved production v2, not OSA v1 or the experimental 0.0034 test.
- Adjust individual trench fields before trench composites.
- Formula: adjusted percentile = min(100, raw percentile × [1 + (OSA - 50)/250]); multiplier bounded 0.80–1.20.
- OSA-Rush maps to offensive rushing EPA/PPA, Line Yards, and Stuff Rate.
- OSA-Defense maps to offensive rushing Success Rate.
- OSA-Pass maps to offensive Havoc Allowed proxy (CFBD offense.havoc.total).
- OSA-Offense maps to opposing defensive-trench fields.
- QB Matchup fields are not directly OSA-adjusted; calculate QB Matchup separately.
- Preserve raw values and percentiles; do not impute missing schedule OSA.
Data: 138 FBS teams, 67 Power 4 schedule OSA rows, 14 fields. Source: CFBD 2026 advanced season stats snapshot 2026-10-30 22:35:57 UTC. Percentiles are empirical FBS average-rank percentiles (best 100, worst 0), higher=better.
