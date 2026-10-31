# Defensive Trenches Rating (DTR)

## Inputs
Use the verified 2026 CFBD advanced season fields and all-FBS empirical percentiles, restricted to the approved Power 4 model population and with OSA-Offense applied field by field:
- Defensive EPA/PPA percentile, oriented so lower defensive EPA/PPA is better.
- Defensive Success Rate percentile, oriented so lower opponent success is better.
- Defensive explosiveness percentile, oriented so lower opponent explosiveness is better.
- Defensive Havoc percentile, oriented so higher havoc generated is better.
- Defensive Line Yards percentile, oriented so lower offensive line yards allowed is better.
- Defensive Stuff Rate percentile, oriented so higher stuff rate is better.

## Calculation
DTR is the arithmetic mean of the available, correctly oriented, OSA-adjusted defensive field percentiles. Each available field receives equal weight. This is the initial production weighting, chosen in the absence of a validated backtest supporting differential weights.

Do not include QB-only passing fields. Do not silently impute missing fields. Record the number of available fields and any missing inputs.
