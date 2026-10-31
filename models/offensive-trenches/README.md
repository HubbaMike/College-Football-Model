# Offensive Trenches Matchup (OTR)

## Inputs
Use the verified 2026 CFBD advanced season fields and all-FBS empirical percentiles, with Power 4 schedule OSA applied field by field:
- Offensive rushing PPA/EPA percentile — OSA-Rush.
- Offensive rushing Success Rate percentile — OSA-Defense.
- Offensive Line Yards percentile — OSA-Rush.
- Offensive Stuff Rate percentile — OSA-Rush.
- Offensive Havoc Allowed proxy (offense.havoc.total), reverse-oriented so lower havoc is better — OSA-Pass.

## Calculation
OTR is the arithmetic mean of the available, correctly oriented, OSA-adjusted field percentiles. Each available field receives equal weight. This is the initial production weighting, chosen in the absence of a validated backtest supporting differential weights.

Do not use QB passing fields in OTR. Do not silently impute missing fields. Record the number of available fields and any missing inputs.
