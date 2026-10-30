"""Build OSA v1 ratings from verified FBS rank and schedule CSVs.

Input team_ranks.csv:
  team,conference,<rank-field columns>
Each rank field must be a published FBS rank where 1 is best. Use blank cells
for unavailable values; do not enter estimates.

Input games.csv:
  home_team,away_team,home_conference,away_conference
Only games with both conferences in the approved Power 4 set are included.

Example:
  python models/osa/build_osa_dataset.py \
      --ranks data/team_ranks.csv --games data/games.csv \
      --out data/osa_2026.csv --season 2026

This produces team component ratings and schedule opponent-strength averages.
It does not apply any field-adjustment multiplier.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from osa_v1 import (
    P4_CONFERENCES,
    RANK_FIELD_WEIGHTS,
    fbs_rank_to_percentile,
    weighted_osa_rating,
)

# Source CSV headers mapped to the approved OSA component input names.
# Change only when the source's actual numeric field names have been verified.
REQUIRED_RANK_COLUMNS = sorted(
    {field for weights in RANK_FIELD_WEIGHTS.values() for field in weights}
)


def number_or_none(value: str | None) -> float | None:
    if value is None or value.strip() == "":
        return None
    return float(value)


def load_team_ranks(path: Path, fbs_teams: int) -> dict[str, dict[str, Any]]:
    teams: dict[str, dict[str, Any]] = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"team", "conference", *REQUIRED_RANK_COLUMNS}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing columns: {sorted(missing)}")
        for row in reader:
            name = row["team"].strip()
            if not name:
                continue
            if name in teams:
                raise ValueError(f"Duplicate team row: {name}")
            percentiles: dict[str, float | None] = {}
            for field in REQUIRED_RANK_COLUMNS:
                raw_rank = number_or_none(row.get(field))
                if raw_rank is None:
                    percentiles[field] = None
                else:
                    if not raw_rank.is_integer():
                        raise ValueError(f"{name}: {field} rank must be an integer")
                    percentiles[field] = fbs_rank_to_percentile(
                        int(raw_rank), fbs_teams
                    )
            components: dict[str, float | None] = {}
            for component in RANK_FIELD_WEIGHTS:
                try:
                    components[component] = weighted_osa_rating(
                        component, percentiles
                    )
                except ValueError:
                    components[component] = None
            teams[name] = {
                "conference": row["conference"].strip(),
                "components": components,
            }
    return teams


def load_p4_opponents(path: Path, teams: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    opponents = {team: [] for team in teams}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"home_team", "away_team", "home_conference", "away_conference"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} is missing columns: {sorted(missing)}")
        for row in reader:
            home, away = row["home_team"].strip(), row["away_team"].strip()
            home_conf = row["home_conference"].strip()
            away_conf = row["away_conference"].strip()
            if home_conf not in P4_CONFERENCES or away_conf not in P4_CONFERENCES:
                continue
            if home not in teams or away not in teams:
                continue
            # Protect against stale or conflicting conference labels in either file.
            if teams[home]["conference"] != home_conf:
                raise ValueError(f"Conference mismatch for {home}: games vs ranks CSV")
            if teams[away]["conference"] != away_conf:
                raise ValueError(f"Conference mismatch for {away}: games vs ranks CSV")
            opponents[home].append(away)
            opponents[away].append(home)
    return opponents


def mean_available(values: list[float | None]) -> tuple[float | None, int]:
    usable = [value for value in values if value is not None]
    if not usable:
        return None, 0
    return sum(usable) / len(usable), len(usable)


def build_rows(
    teams: dict[str, dict[str, Any]], opponents: dict[str, list[str]], season: int
) -> list[dict[str, Any]]:
    rows = []
    for team, details in teams.items():
        # OSA-Rush/Pass measure opposing defensive strength.
        # OSA-Defense measures opposing offensive strength.
        # OSA-Offense measures opposing defensive strength overall.
        mappings = {
            "OSA_Rush": ("osa_rush", "osa_rush"),
            "OSA_Pass": ("osa_pass", "osa_pass"),
            "OSA_Defense": ("osa_offense", "osa_defense"),
            "OSA_Offense": ("osa_defense", "osa_offense"),
        }
        row: dict[str, Any] = {
            "season": season,
            "team": team,
            "conference": details["conference"],
            "qualifying_p4_games": len(opponents[team]),
        }
        for component, value in details["components"].items():
            row[component.upper()] = value
        for output_name, (opponent_component, _) in mappings.items():
            value, count = mean_available(
                [
                    teams[opp]["components"][opponent_component]
                    for opp in opponents[team]
                ]
            )
            row[output_name] = value
            row[output_name + "_OPPONENTS_WITH_DATA"] = count
        rows.append(row)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ranks", type=Path, required=True)
    parser.add_argument("--games", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--fbs-teams", type=int, default=138)
    args = parser.parse_args()

    teams = load_team_ranks(args.ranks, args.fbs_teams)
    opponents = load_p4_opponents(args.games, teams)
    rows = build_rows(teams, opponents, args.season)
    if not rows:
        raise SystemExit("No FBS team rows were loaded.")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} team rows to {args.out}")


if __name__ == "__main__":
    main()
