# College Football Reports — Reproducible Runbook

Last successful run documented: 2026-10-31 (Saturday slate)
Repository: `HubbaMike/College-Football-Model`
Branch: `main`

This file is the operational memory for producing BOTH the OM Ratio Report and OM Spread Gap Report. Follow it on every run; do not restart the GitHub setup or redesign the model.

## 1. Required outputs

For each report run, save:
- `reports/om-ratio/YYYY-MM-DD_om_ratio.csv`
- `reports/om-spread-gap/YYYY-MM-DD_om_spread_gap.csv`
- `data/derived/YYYY-MM-DD_team_ratings_om.csv`

The team ratings file must include team, QB, OTR, DTR, OTM, and OM. Preserve full precision in the CSV (at least 3 decimals); round only for display.

## 2. Approved report scope

- Saturday FBS games involving at least one team in the official AP Top 25 poll issued at the beginning of that week. Freeze that poll for the whole report; do not substitute game-time rankings.
- Score only games where BOTH teams belong to SEC, Big Ten, Big 12, or ACC.
- Matchup display is away team @ home team.
- Put AP rank before team name, e.g. `(#9)Ole Miss`.
- Put the favorite's negative spread immediately after the favorite's name, e.g. `(#9)Ole Miss(-9) @ Vandy`.
- The OM Advantage Team is always the team with the higher calculated OM score, regardless of betting favorite.

## 3. Repository data inputs

Use the latest successful committed snapshot and record its timestamp:
- `data/raw/cfbd_advanced_season_stats_2026_20261030T223557Z.json`
- `data/derived/osa_schedule_2026.csv`
- `data/derived/osa_coverage_2026.json`

The 2026-10-30 snapshot contained 138 FBS season-stat team rows, 67 Power 4 team OSA schedule rows, 174 completed P4-vs-P4 games, and 328 scheduled P4-vs-P4 games.

Important retrieval note from the successful run: GitHub `fetch_file` returned empty content for the large raw advanced-game-stat and games JSON paths, while it successfully returned the advanced season-stat JSON and OSA schedule CSV. Do not mistake an empty fetch response for a zero-row dataset. Use the season-level fallback below unless game-level data is actually retrieved and parsed successfully.

## 4. Percentile construction

For each numeric field, calculate empirical percentile across the 138 FBS teams from the same advanced-season-stat snapshot. Use a midrank for ties:
- Sort ascending when higher raw values are better.
- Sort descending when lower raw values are better.
- Percentile = `100 * (1 - average_zero_based_rank / (N - 1))`.
- Thus best = 100 and worst = 0.
- Higher percentile must always mean better performance for the component being scored.

Do not copy the old QB-adjusted columns in `data/derived/2026_osa_v2_adjusted_team_fields.csv`; that export had an erroneous direct OSA adjustment to QB fields.

## 5. QB Matchup v2 (no direct OSA adjustment)

Use raw FBS percentiles:
- Offensive passing PPA percentile.
- Offensive passing Success Rate percentile.
- Reversed defensive passing PPA percentile (lower defensive passing PPA is better).

Formula:
`QB = 0.55 * offense_passing_PPA_pct + 0.25 * offense_passing_SR_pct + 0.20 * reversed_defense_passing_PPA_pct`

QB Matchup is NOT directly OSA-adjusted in the current production implementation.

## 6. OSA v2 schedule ratings and field adjustment

Use the four team schedule ratings already calculated in `data/derived/osa_schedule_2026.csv`:
- OSA_Rush
- OSA_Pass
- OSA_Defense
- OSA_Offense

These are schedule averages from qualifying SEC, Big Ten, Big 12, and ACC opponents. Do not use standings points as opponent strength. Retain the opponent names and qualifying-game count for audit.

For each trench field, apply:
`multiplier = clamp(1 + (OSA_dimension - 50) / 250, 0.80, 1.20)`
`adjusted_percentile = clamp(raw_percentile * multiplier, 0, 100)`

Apply OSA at the individual field level before averaging. Preserve raw field value, raw percentile, OSA dimension, multiplier, and adjusted percentile in an audit export when available.

### Approved offensive trench mapping (OTR)
- Offensive rushing PPA → OSA-Rush.
- Offensive rushing Success Rate → OSA-Defense.
- Offensive Line Yards → OSA-Rush.
- Offensive Stuff Rate → OSA-Rush; orient lower offensive stuff rate as better before adjustment.
- Offensive Havoc Allowed proxy (`offense.havoc.total`) → OSA-Pass; orient lower havoc allowed as better.

OTR is the arithmetic mean of the five available adjusted field percentiles. Equal weight per field.

### Approved defensive trench mapping (DTR)
Use defensive:
- Overall defensive PPA, lower is better.
- Defensive Success Rate allowed, lower is better.
- Defensive explosiveness allowed, lower is better.
- Defensive Havoc generated, higher is better.
- Defensive Line Yards allowed, lower is better.
- Defensive Stuff Rate, higher is better.

Apply OSA-Offense to each of these six fields. DTR is the arithmetic mean of the six available adjusted, correctly oriented percentiles. Equal weight per field.

### OTM and OM
`OTM = 0.50 * OTR + 0.50 * (100 - DTR)`
`OM = 0.50 * QB + 0.50 * OTM`

No discretionary weights. No silent imputation. If an input is missing, record it and reduce confidence under the rule below.

## 7. Confidence

Start at 100 for each matchup.
- Subtract 5 when all-FBS season-level statistics are used as a proxy for P4-only team statistics.
- Subtract 15 for each estimated or imputed core metric, subject to the saved model's maximum penalty cap.
- Complete directly retrieved metrics incur no penalty.
- Confidence is game-specific reliability, not a function of OM Gap size.
- Bands: High 80–100; Medium 60–79; Low 0–59.

For the 2026-10-31 fallback run, the report used 95 because the team season stats were all-FBS rather than P4-only. Do not blindly reuse 95: calculate the penalty from the actual inputs on every run.

## 8. Report formulas

### OM Ratio
`OM Ratio = higher_team_OM / lower_team_OM`
Sort descending. If the lower OM is zero or negative, do not divide blindly; flag the row and use an explicitly documented handling rule before publishing.

### OM Spread Gap
`OM Spread Gap = abs(away_OM - home_OM) / sqrt(abs(point_spread)^2 + 16)`
The constant 16 is the approved four-point stabilizer. Sort descending.

Required OM Spread Gap columns:
- Rank
- Matchup
- OM Spread Gap
- OM Advantage Team
- Confidence

The OM Ratio report should include matchup, away OM, home OM, ratio, OM advantage team, and confidence.

## 9. Slate assembly and odds/ranking audit

Before calculating reports:
1. Retrieve the official AP poll issued at the beginning of the current week and freeze it as the ranking set.
2. Retrieve the Saturday FBS schedule and identify every game involving at least one ranked team.
3. Retain only matchups where both teams are in SEC, Big Ten, Big 12, or ACC.
4. Retrieve current point spreads at report runtime. Record the source and retrieval timestamp.
5. Store the exact game slate, AP ranks, home/away designations, favorites, and spreads in a dated input CSV or JSON alongside the reports.

Do not reuse the 2026-10-31 game slate, AP ranks, or spreads for a future week. They were manually supplied in the calculation run and are not stored in a dedicated source-input file. In particular, the 2026-10-31 report's displayed spread inputs were:
- Arizona @ Texas Tech: Texas Tech -3.5
- Wisconsin @ Iowa: Iowa -3.5
- SMU @ Syracuse: SMU -10.5
- Auburn @ Ole Miss: Ole Miss -13.5
- Minnesota @ Indiana: Indiana -21
- Northwestern @ Oregon: Oregon -3.5
- Florida @ Georgia: Georgia -11.5
- Arizona State @ BYU: BYU -16.5
- Utah @ Cincinnati: Utah -6.5
- Virginia @ Wake Forest: Wake Forest -12.5
- Oklahoma State @ Iowa State: Oklahoma State -8.5
- Miami @ North Carolina: Miami -14
- Ohio State @ USC: Ohio State -6.5
- Mississippi State @ Texas: Texas -20.5
- Missouri @ Arkansas: Missouri -10

The displayed AP ranks used in that report were manually included in the slate input. Verify against the official beginning-of-week AP poll before any rerun.

## 10. 2026-10-31 completed artifacts

- `reports/om-ratio/2026-10-31_om_ratio.csv`
- `reports/om-spread-gap/2026-10-31_om_spread_gap.csv`
- `data/derived/2026-10-30_team_ratings_om.csv`

These were committed to `main`. The run used the season-level FBS fallback described above; it was not a full recomputation from the 174 completed P4-vs-P4 game-level advanced-stat rows. The reports should therefore be described as completed fallback reports, not P4-only game-level reports.

## 11. Every-run execution checklist

- [ ] Fetch latest committed 2026 season advanced stats, OSA schedule, and coverage metadata.
- [ ] Confirm row counts, snapshot timestamp, P4 teams, and OSA coverage.
- [ ] Attempt to retrieve and parse game-level advanced stats and game schedule. Use P4-vs-P4 game aggregation only if the actual numerical rows are retrieved and validated.
- [ ] If game-level rows cannot be retrieved, use the documented season-level FBS fallback and apply the confidence penalty.
- [ ] Build FBS empirical percentiles with correct orientation and midrank ties.
- [ ] Calculate QB Matchup v2 without direct OSA adjustment.
- [ ] Apply OSA v2 to each OTR and DTR field using the exact mapping above.
- [ ] Calculate equal-weight OTR, DTR, OTM, and OM.
- [ ] Retrieve and freeze beginning-of-week AP Top 25; build the eligible Saturday P4-vs-P4 slate.
- [ ] Refresh spreads and save source/timestamp with the slate input.
- [ ] Calculate OM Ratio and OM Spread Gap; sort descending.
- [ ] Calculate confidence from actual data limitations.
- [ ] Save team ratings, slate inputs, and both report CSVs to the dated paths.
- [ ] Verify each committed file by fetching it back from GitHub and checking non-empty content and row counts.
- [ ] Present both reports and explicitly state any fallback or missing-data limitations.

## 12. Critical don't-repeat notes

- Do not restart GitHub authorization/setup; the repository is accessible and writes to `main` have succeeded.
- Do not ask the user for the data or API key when the repository already contains the snapshot.
- Do not use OSA v1 weights.
- Do not use the experimental `0.0034` multiplier.
- Do not apply OSA directly to QB Matchup.
- Do not use the legacy adjusted QB columns from the earlier export.
- Do not silently substitute all-FBS season averages while describing them as P4-only.
- Do not reuse stale AP rankings or betting spreads.
- Do not publish a report until the two report CSVs and team-rating CSV have been committed and verified.
