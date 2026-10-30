# OSA v1 — Approved specification

Status: working approved design. This document records the agreed ratings and data rules. It does not claim that a complete 2026 numerical dataset has been retrieved or that the adjustment-to-multiplier mapping has been validated.

## Purpose

Calculate four season-level opponent-strength ratings from actual retrievable numerical statistics:

- `OSA-Rush`: opponent rushing-defense strength.
- `OSA-Pass`: opponent passing-defense strength.
- `OSA-Defense`: opponent overall defensive strength.
- `OSA-Offense`: opponent offensive strength.

Calculate each rating for a team's qualifying schedule by averaging the relevant rating for each qualifying opponent.

## Eligible games and opponents

- Include Power 4-vs-Power 4 games only: both teams must be members of the SEC, Big Ten, Big 12, or ACC.
- Build opponent ratings from actual numerical season statistics. Do not use standings points as a proxy for opponent strength.
- Use one consistent public source and a consistent FBS-wide play/team filter when producing published FBS ranks or percentiles.
- Record the source, retrieval date, season, field, filter, and any missing or estimated value.
- Do not treat a field as available merely because a website says it publishes it; a numerical value must actually be retrieved.

## FBS rank to percentile

For a published FBS rank (r), use:

`P = ((138 - r) / 137) * 100`

This maps rank 1 to 100 and rank 138 to 0. Ratings are oriented so higher means stronger performance in the named category. For defensive metrics where lower raw values are better (for example EPA allowed, Success Rate allowed, Line Yards allowed, and explosiveness allowed), use the source's defensive rank or reverse the raw metric before ranking so the strongest defense receives the highest percentile.

## Component weights

All component inputs are FBS-wide percentiles on a 0–100 scale, oriented so higher means stronger in the named category.

### OSA-Rush — opponent rushing defense

- Defensive Rush EPA: 35%
- Defensive Success Rate allowed: 25%
- Line Yards allowed: 25%
- Explosiveness allowed: 15%

If Line Yards is unavailable, omit it and renormalize the remaining available weights proportionally. Do not invent or impute a value silently.

### OSA-Pass — opponent passing defense

- Defensive Pass EPA: 45%
- Success Rate allowed: 35% (overall Success Rate allowed is the approved proxy when a pass-specific value is not available)
- Explosiveness allowed: 20%

### OSA-Defense — opponent overall defense

- Defensive EPA/play: 35%
- Success Rate allowed: 30%
- Explosiveness allowed: 20%
- Havoc: 15%

### OSA-Offense — opponent offense

- Offensive EPA/play: 35%
- Offensive Success Rate: 30%
- Offensive explosiveness: 20%
- Average of offensive Rush EPA and offensive Pass EPA: 15%

## Schedule aggregation

For each team, average the relevant opponent rating across its qualifying Power 4 opponents. Use the same eligible-game rule consistently. Retain the opponent-by-opponent values and count so the aggregate is auditable. Do not substitute a full-FBS opponent pool for the Power 4-only schedule average without explicitly marking that deviation.

## Applying OSA to individual fields

Apply the relevant opponent-strength dimension to individual raw fields before constructing the downstream trench composites. Keep raw and adjusted field values side by side.

- Offensive rushing fields are adjusted using the opponent's OSA-Rush.
- Offensive passing fields are adjusted using the opponent's OSA-Pass.
- Defensive fields are adjusted using the opponent's OSA-Offense.
- Use the appropriate opponent offensive/rushing/passing strength for the specific defensive field where the model's field mapping requires it; document the mapping.

The adjustment is capped at ±20%.

## Important implementation boundary

A previously discussed linear mapping, `1 + (OSA - 50) / 250`, was explicitly withdrawn as an unvalidated provisional formula. It must not be implemented or presented as approved. The final conversion from an OSA rating to a per-field adjustment multiplier remains to be validated and approved. Until then, calculate and store the four OSA ratings, but do not fabricate adjusted field values or apply an assumed multiplier.

## Audit and confidence

- Preserve raw values, source ranks/percentiles, weighted component contributions, missing-field decisions, opponent-level ratings, schedule average, and eligible-opponent count.
- If a component is unavailable, calculate from the available approved fields and renormalize weights where specified; disclose the omission.
- Never silently estimate a core metric. Mark estimates/imputations explicitly and apply the project's confidence penalties.
