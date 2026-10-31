# Opponent Strength Adjustment (OSA)

## Current implementation
The approved production design is **OSA v2**, documented in [OSA_V2_PRODUCTION_SPEC.md](OSA_V2_PRODUCTION_SPEC.md). OSA v1 and the experimental 0.0034 multiplier are historical only and are not the active model.

OSA v2 produces four schedule-strength dimensions (OSA-Rush, OSA-Pass, OSA-Defense, OSA-Offense) from numerical performance ratings of qualifying Power 4 opponents. It then applies the relevant dimension to each trench field using the bounded field-level adjustment in the v2 specification.

## Scope and rules
- Qualifying opponents are SEC, Big Ten, Big 12, and ACC teams.
- Use actual retrieved numerical fields and the current approved data snapshot.
- Raw FBS percentiles use the full FBS population and are oriented so higher is better for the component being scored.
- Apply OSA to offensive and defensive trench inputs only. QB Matchup is calculated from its raw FBS percentile inputs and is not directly OSA-adjusted.
- Missing OSA rows or missing core metrics remain blank; never silently impute.

## Current data
- Schedule ratings: `data/derived/osa_schedule_2026.csv`
- Field-level export: `data/derived/2026_osa_v2_adjusted_team_fields.csv`
- Snapshot and coverage details are recorded in `data/derived/osa_coverage_2026.json`.

The adjusted-team-fields export contains legacy QB-adjustment columns that must not be used. Use the raw QB percentile columns for QB Matchup. Trench columns must follow the mappings in the v2 production specification.
