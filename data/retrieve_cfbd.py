"""Retrieve raw CFBD season data using a GitHub Actions secret.

The API key is read only from CFBD_API_KEY. It is never printed or written
to disk. Raw responses are retained unchanged for auditability.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://api.collegefootballdata.com"
OUT_DIR = Path("data/raw")


def get_json(path: str, params: dict[str, str]) -> object:
    key = os.environ.get("CFBD_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "Missing CFBD_API_KEY. Add it under GitHub Settings > Secrets and variables > Actions."
        )
    url = f"{BASE_URL}{path}?{urlencode(params)}"
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
            "User-Agent": "College-Football-Model/CFBD-data-refresh",
        },
    )
    try:
        with urlopen(request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        # Do not print request headers or the credential.
        body = exc.read().decode("utf-8", errors="replace")[:1000]
        raise RuntimeError(f"CFBD returned HTTP {exc.code} for {path}: {body}") from None
    except URLError as exc:
        raise RuntimeError(f"Could not reach CFBD for {path}: {exc.reason}") from None


def save_json(name: str, payload: object) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved {path} ({len(payload) if isinstance(payload, list) else 'object'} records)")


def main() -> int:
    season = os.environ.get("CFBD_SEASON", "2026").strip()
    if not season.isdigit():
        raise ValueError("CFBD_SEASON must be a four-digit year")
    end_week = os.environ.get("CFBD_END_WEEK", "").strip()

    # Validate the credential and retrieve source records. Keep these raw;
    # downstream field mapping will be based on the returned numeric schema.
    games_params = {"year": season, "seasonType": "regular"}
    if end_week:
        games_params["week"] = end_week

    teams = get_json("/teams/fbs", {})
    games = get_json("/games", games_params)
    advanced_params = {"year": season, "seasonType": "regular"}
    if end_week:
        advanced_params["week"] = end_week
    advanced_games = get_json("/stats/game/advanced", advanced_params)
    advanced_season = get_json(
        "/stats/season/advanced",
        {"year": season, "classification": "fbs"},
    )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    save_json(f"cfbd_fbs_teams_{stamp}.json", teams)
    save_json(f"cfbd_games_{season}_{stamp}.json", games)
    save_json(f"cfbd_advanced_game_stats_{season}_{stamp}.json", advanced_games)
    save_json(f"cfbd_advanced_season_stats_{season}_{stamp}.json", advanced_season)

    # Emit only high-level counts and never credential material.
    print(
        "CFBD retrieval complete: "
        f"FBS teams={len(teams)}, games={len(games)}, "
        f"advanced game rows={len(advanced_games)}, "
        f"advanced season rows={len(advanced_season)}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
