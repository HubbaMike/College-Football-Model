"""Unit tests for the approved OSA v1 calculations.

Run from the repository root with: python -m unittest discover -s tests -v
"""
import unittest

from models.osa.osa_v1 import (
    fbs_rank_to_percentile,
    qualifying_p4_opponent_average,
    weighted_osa_rating,
    osa_adjustment_multiplier,
)


class TestRankPercentiles(unittest.TestCase):
    def test_rank_one_is_100(self):
        self.assertAlmostEqual(fbs_rank_to_percentile(1), 100.0)

    def test_last_rank_is_zero(self):
        self.assertAlmostEqual(fbs_rank_to_percentile(138), 0.0)

    def test_middle_rank_uses_approved_138_team_formula(self):
        self.assertAlmostEqual(fbs_rank_to_percentile(69), 50.364963503649635)

    def test_invalid_rank_rejected(self):
        with self.assertRaises(ValueError):
            fbs_rank_to_percentile(139)


class TestWeightedRatings(unittest.TestCase):
    def test_full_rush_component(self):
        values = {
            "defensive_rush_epa": 80,
            "defensive_success_rate_allowed": 60,
            "line_yards_allowed": 40,
            "explosiveness_allowed": 20,
        }
        self.assertAlmostEqual(weighted_osa_rating("osa_rush", values), 56.0)

    def test_missing_line_yards_renormalizes(self):
        values = {
            "defensive_rush_epa": 80,
            "defensive_success_rate_allowed": 60,
            "line_yards_allowed": None,
            "explosiveness_allowed": 20,
        }
        expected = (0.35 * 80 + 0.25 * 60 + 0.15 * 20) / 0.75
        self.assertAlmostEqual(weighted_osa_rating("osa_rush", values), expected)

    def test_no_available_fields_rejected(self):
        with self.assertRaises(ValueError):
            weighted_osa_rating("osa_pass", {})

    def test_unknown_component_rejected(self):
        with self.assertRaises(KeyError):
            weighted_osa_rating("unknown", {})


class TestOpponentAverages(unittest.TestCase):
    def test_average_and_count(self):
        avg, count = qualifying_p4_opponent_average(
            [("Team A", 60), ("Team B", 80), ("Team C", None)]
        )
        self.assertAlmostEqual(avg, 70.0)
        self.assertEqual(count, 2)

    def test_no_ratings_rejected(self):
        with self.assertRaises(ValueError):
            qualifying_p4_opponent_average([("Team A", None)])


class TestUnapprovedMultiplier(unittest.TestCase):
    def test_multiplier_is_blocked_until_approved(self):
        with self.assertRaises(NotImplementedError):
            osa_adjustment_multiplier(70)


if __name__ == "__main__":
    unittest.main()
