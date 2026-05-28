from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Player:
    name: str
    country: str
    position: str
    price: int


@dataclass
class MatchResult:
    match_id: str
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    scorers: list[str]
    assisters: list[str]
    yellow_cards: list[str]
    red_cards: list[str]
    gk_saves: dict[str, int]
    clean_sheet_teams: list[str]
    bonus_top3: list[str]
    is_knockout: bool
    is_final: bool
    settled: bool


@dataclass
class FWCTeam:
    owner: str
    team_name: str
    budget_remaining: int
    player_ids: list[str]
    captain_id: str
    vice_captain_id: str
    gameweek_points: dict[str, int]
    total_points: int
    chip_wildcard_used: int
    chip_bench_boost_used: int
    chip_triple_captain_used: int
    chip_free_hit_used: int
    chip_hero_player_id: str
    hero_bonus_awarded: bool
    transfers_available: int
