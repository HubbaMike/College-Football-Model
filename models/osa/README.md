# Opponent Strength Adjustment (OSA)

## Current implementation

- `OSA_V1_SPEC.md` is the approved component and data-handling specification.
- `osa_v1.py` implements the approved 0–100 rank-percentile conversion, weighted components, missing-field renormalization, and opponent averaging.
- `build_osa_dataset.py` builds team component scores and the four schedule-level OSA averages from verified rank and game CSVs.
- `../../tests/test_osa_v1.py` contains unit tests.

## Run

From the repository root:

```bash
python -m unittest discover -s tests -v
python models/osa/build_osa_dataset.py \
  --ranks data/team_ranks.csv \
  --games data/games.csv \
  --out data/osa_2026.csv \
  --season 2026
```

## Input requirements

`team_ranks.csv` must contain `team`, `conference`, and the exact rank-field columns listed in `build_osa_dataset.py`. Values must be actual retrieved FBS ranks, where rank 1 is best. Leave a field blank when its numeric value has not been retrieved; do not estimate it.

`games.csv` must contain `home_team`, `away_team`, `home_conference`, and `away_conference`. Only SEC, Big Ten, Big 12, and ACC vs those same conferences are counted.

## Important boundary

The builder currently calculates OSA ratings only. It does **not** apply the withdrawn provisional OSA-to-multiplier formula. The ±20% cap is a design constraint for the eventual field adjustment, not permission to use an unvalidated conversion.

## Data status

No 2026 OSA dataset is being represented as complete until the underlying numerical FBS ranks and game schedule have actually been retrieved, checked, and loaded. The next integration step is a source-specific CFBD data adapter and a verified field-name mapping.
