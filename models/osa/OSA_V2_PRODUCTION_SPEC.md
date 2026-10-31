# OSA v2 — production field-adjustment implementation (2026)

Status: approved production design. This supersedes the older OSA v1 weighted-component proposal and the experimental 0.0034 multiplier test.

## Data and population
- Source: CollegeFootballData 2026 advanced season statistics, snapshot 2026-10-30 22:35:57 UTC.
- Raw-field percentiles use all 138 FBS teams; best = 100 and worst = 0.
- Schedule-strength ratings use SEC, Big Ten, Big 12, and ACC opponents only, based on the qualifying Power 4-vs-Power 4 schedule.
- The current schedule file contains 67 Power 4 team rows. The current snapshot records 174 completed and 328 scheduled P4-vs-P4 games.

## OSA dimensions
Each team has four schedule-average ratings on a 0–100 scale:
- OSA-Rush
- OSA-Pass
- OSA-Defense
- OSA-Offense

Use the opponent's relevant numerical performance ratings, averaged across qualifying Power 4 opponents. Do not use standings points as a proxy for opponent strength.

## Approved field mapping
Apply OSA to trench inputs only; QB Matchup is not directly OSA-adjusted.

Offensive trench fields:
- Offensive rushing PPA/EPA → OSA-Rush.
- Offensive Line Yards → OSA-Rush.
- Offensive Stuff Rate → OSA-Rush.
- Offensive rushing Success Rate → OSA-Defense.
- Offensive Havoc Allowed proxy (CFBD offense.havoc.total) → OSA-Pass.

Defensive trench fields:
- Defensive EPA/PPA, Success Rate, explosiveness, Havoc, Line Yards, and Stuff Rate → OSA-Offense.
- Orient defensive fields so higher percentile always means better defense before adjustment.

QB Matchup fields remain raw FBS percentiles for the QB composite:
- Offensive passing PPA/EPA percentile.
- Offensive passing Success Rate percentile.
- Reversed defensive passing PPA/EPA percentile.
The saved QB Matchup v2 weights remain 55% / 25% / 20%.

## Field adjustment formula
For each mapped trench field:
`adjusted_percentile = raw_percentile * (1 + (OSA_dimension - 50) / 250)`
Clamp the multiplier to [0.80, 1.20]. Clamp the final percentile to [0, 100].
Keep raw values, raw percentiles, OSA dimension, multiplier, and adjusted percentile as separate fields. If a team has no qualifying OSA schedule row, leave the adjusted trench field blank; do not invent an OSA score.

## Composite construction
- OTR = arithmetic mean of the available, correctly oriented, OSA-adjusted offensive trench field percentiles.
- DTR = arithmetic mean of the available, correctly oriented, OSA-adjusted defensive trench field percentiles.
- OTM = 0.50 * OTR + 0.50 * (100 - DTR).
- Within OTR and DTR, use equal weights for each available field. This is the initial production choice pending a validated backtest; do not introduce discretionary weights.
- OM = 0.50 * QB Matchup + 0.50 * OTM.

## Important correction
The earlier 2026 adjusted-team-fields export applied OSA to QB passing PPA and reversed defensive passing PPA. Those QB adjusted columns are not valid for the production QB calculation and must not be used. Recalculate QB Matchup from the raw FBS percentile columns. The trench adjusted columns use the mappings above and may be used only after confirming their OSA dimensions and orientation.

## Reproducibility
Record source snapshot, qualifying-game count, missing fields, field-level percentiles, OSA dimension, multiplier, adjusted percentile, component scores, and confidence penalties in the report dataset. Never silently impute a missing core metric.
