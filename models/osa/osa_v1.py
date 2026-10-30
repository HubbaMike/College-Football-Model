"""OSA v1 rating calculations.

Implements the approved rank-to-percentile conversion, weighted OSA component
ratings, and qualifying-opponent schedule averaging. Deliberately does NOT
convert OSA ratings into field adjustment multipliers: the previously discussed
linear mapping was withdrawn as unvalidated.
"""
from __future__ import annotations

from typing import Mapping, Sequence

P4_CONFERENCES = {"SEC", "Big Ten", "Big 12", "ACC"}
RANK_FIELD_WEIGHTS = {
    "osa_rush": {
        "defensive_rush_epa": 0.35,
        "defensive_success_rate_allowed": 0.25,
        "line_yards_allowed": 0.25,
        "explosiveness_allowed": 0.15,
    },
    "osa_pass": {
        "defensive_pass_epa": 0.45,
        "success_rate_allowed": 0.35,
        "explosiveness_allowed": 0.20,
    },
    "osa_defense": {
        "defensive_epa_per_play": 0.35,
        "success_rate_allowed": 0.30,
        "explosiveness_allowed": 0.20,
        "havoc": 0.15,
    },
    "osa_offense": {
        "offensive_epa_per_play": 0.35,
        "offensive_success_rate": 0.30,
        "offensive_explosiveness": 0.20,
        "average_offensive_rush_pass_epa": 0.15,
    },
}


def fbs_rank_to_percentile(rank: int, fbs_teams: int = 138) -> float:
    """Convert a best-is-rank-1 FBS rank to a 0–100 percentile."""
    if not 1 <= rank <= fbs_teams:
        raise ValueError(f"rank must be between 1 and {fbs_teams}")
    if fbs_teams < 2:
        raise ValueError("fbs_teams must be at least 2")
    return ((fbs_teams - rank) / (fbs_teams - 1)) * 100.0


def weighted_osa_rating(
    component: str, percentiles: Mapping[str, float | None]
) -> float:
    """Calculate one OSA rating; omit missing inputs and renormalize weights."""
    if component not in RANK_FIELD_WEIGHTS:
        raise KeyError(f"Unknown OSA component: {component}")
    weights = RANK_FIELD_WEIGHTS[component]
    available = {
        field: (weight, percentiles[field])
        for field, weight in weights.items()
        if field in percentiles and percentiles[field] is not None
    }
    if not available:
        raise ValueError(f"No usable inputs for {component}")
    for field, (_, value) in available.items():
        if value is None or not 0.0 <= float(value) <= 100.0:
            raise ValueError(f"{field} must be a percentile from 0 to 100")
    total_weight = sum(weight for weight, _ in available.values())
    return sum(weight * float(value) for weight, value in available.values()) / total_weight


def qualifying_p4_opponent_average(
    opponent_ratings: Sequence[tuple[str, float | None]],
) -> tuple[float, int]:
    """Average available ratings for opponents already filtered to P4-vs-P4 games.

    The caller must apply the both-teams-P4 eligibility filter before passing
    rows. None ratings are excluded and should be separately reported.
    """
    values = [float(rating) for _, rating in opponent_ratings if rating is not None]
    if not values:
        raise ValueError("No qualifying opponent ratings available")
    if any(not 0.0 <= value <= 100.0 for value in values):
        raise ValueError("Opponent ratings must be between 0 and 100")
    return sum(values) / len(values), len(values)


def osa_adjustment_multiplier(*_args, **_kwargs):
    """Not implemented: the approved OSA-to-multiplier mapping is unvalidated."""
    raise NotImplementedError(
        "OSA v1 multiplier mapping is pending validation and approval; "
        "do not use the withdrawn provisional linear formula."
    )
