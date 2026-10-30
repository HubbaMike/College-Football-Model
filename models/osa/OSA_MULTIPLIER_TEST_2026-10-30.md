# OSA v1 — empirical multiplier test (2026-10-30)

Status: **candidate only; not yet approved for production**.

## Test design

- Source: CollegeFootballData 2026 advanced game stats and advanced season stats retrieved 2026-10-30.
- Eligible sample: completed games where both teams are in SEC, Big Ten, Big 12, or ACC.
- Observations: 174 completed games, 348 team-game offensive observations.
- Opponent strength: FBS-wide empirical percentile OSA components, with higher scores representing stronger defense.
- For each team-game, compare game-level offensive metric with that team's season-level baseline. Regress relative deviation (game metric / season metric - 1) against (opponent OSA - 50).
- This is an initial in-sample calibration, not an independent holdout validation. Season averages include the game being evaluated, so estimated slopes are likely attenuated and are not production-ready.

## Empirical results

| Metric | Team-game observations | Slope per OSA point | Correlation |
|---|---:|---:|---:|
| Rushing Success Rate relative deviation vs opponent OSA-Rush | 348 | -0.003542 | -0.381 |
| Passing Success Rate relative deviation vs opponent OSA-Pass | 348 | -0.003390 | -0.398 |
| Offensive Line Yards relative deviation vs opponent OSA-Rush | 348 | -0.003333 | -0.362 |
| Overall offensive Success Rate relative deviation vs opponent OSA-Defense | 348 | -0.002956 | -0.456 |
| Offensive explosiveness relative deviation vs opponent OSA-Defense | 348 | -0.001232 | -0.164 |

EPA/play was also tested as an additive outcome because it can be negative or near zero and therefore should not be adjusted by a multiplicative ratio. Estimated game-minus-season EPA/play slopes per OSA point were -0.00422 for rushing EPA, -0.00554 for passing EPA, and -0.00382 for overall EPA/play; correlations were -0.416, -0.445, and -0.488 respectively.

## Candidate multiplier for further validation

The median of the three trench-oriented relative-deviation slopes (rushing Success Rate, passing Success Rate, Line Yards) is approximately -0.00339 per OSA point. This suggests the candidate field multiplier:

    multiplier = clamp(1 + 0.0034 * (opponent_OSA - 50), 0.80, 1.20)

Interpretation: a stronger-than-average opponent is harder; increase the observed offensive field value to account for that difficulty. A weaker-than-average opponent reduces the field value. The current FBS 0–100 OSA scale implies a maximum candidate adjustment of about ±17%, within the ±20% cap.

For offensive rushing fields use opponent OSA-Rush; for offensive passing fields use opponent OSA-Pass; for overall offensive fields use opponent OSA-Defense. For defensive performance fields, the opponent's relevant OSA-Offense dimension would be used, subject to separate validation.

## Important restrictions

1. This multiplier is a candidate, **not an approved production formula**.
2. Do not apply it to EPA/play or other signed/near-zero metrics. Those require a separately validated additive correction.
3. The test used season baselines that include each tested game; this creates leakage and attenuates effects. A proper test must use prior-game / leave-one-game-out baselines and chronological holdout validation.
4. Before production adoption, run week-based out-of-sample validation, compare raw vs adjusted prediction error, and test stability by metric and sample size.
5. Preserve raw and adjusted values side by side; never overwrite raw observations.
6. This test does not authorize publication of official adjusted OM rankings. QB and offensive trench composites must be rebuilt with a validated adjustment, then checked against saved model definitions.
