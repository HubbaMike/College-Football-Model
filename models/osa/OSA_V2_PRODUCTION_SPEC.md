# OSA v2 — production field-adjustment implementation (2026)

Status: production implementation of the user's approved simplified OSA v2 workflow. This is distinct from the older OSA v1 weighted-component proposal and the experimental 0.0034 multiplier test.

## Data
- Source: CollegeFootballData 2026 advanced season statistics, retrieved 2026-10-30 22:35:57 UTC.
- Population for raw-field percentiles: 138 FBS teams.
- Schedule OSA source: `data/derived/osa_schedule_2026.csv`, 67 Power 4 teams.
- Qualifying schedule: SEC, Big Ten, Big 12, ACC opponents only; schedule OSA is based on Power 4-vs-Power 4 games.
- Empirical percentile: average-rank percentile across all 138 FBS teams; best = 100, worst = 0. Metrics are oriented so higher percentile means better performance.

## Field adjustment
For a field's raw FBS percentile and its mapped schedule OSA dimension:

`Adjusted percentile = min(100, Raw percentile * (1 + (OSA - 50) / 250))`

The factor is bounded to [0.80, 1.20], implementing the ±20% cap. Raw values and raw percentiles are retained. If the team has no qualifying P4 schedule OSA row, the adjusted percentile is blank rather than imputed.

## Approved mappings implemented
- QB pass EPA/PPA: OSA-Pass.
- QB passing Success Rate: unadjusted (raw percentile), consistent with QB Matchup v2.
- Opposing defensive pass EPA/PPA: reverse-ranked defensive pass PPA, adjusted with OSA-Offense.
- Offensive rushing PPA: OSA-Rush.
- Offensive rushing Success Rate: OSA-Defense.
- Offensive Line Yards and offensive Stuff Rate: OSA-Rush.
- Offensive Havoc Allowed proxy: offense.havoc.total, mapped to OSA-Pass.
- Defensive EPA/PPA, Success Rate, explosiveness, Havoc, Line Yards, and Stuff Rate: OSA-Offense. Defensive metrics are oriented so higher percentile means better defense.

## Boundaries
- This is a team-season dataset. It applies the team's schedule-average OSA dimension to its season-level percentile.
- The data contains 138 FBS teams; adjusted values are available for the 67 teams with P4 schedule OSA records. Non-P4 teams retain raw values/percentiles and blank adjusted values.
- This file does not invent a QB/OTM composite weight set. QB Matchup v2 remains 55% adjusted pass EPA percentile + 25% raw passing Success Rate percentile + 20% reversed, opponent-adjusted defensive pass EPA percentile.
- OTM composite weights remain governed by the approved OTM definition; this file supplies the adjusted field inputs.
