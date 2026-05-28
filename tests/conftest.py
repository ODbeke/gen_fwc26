from __future__ import annotations

import importlib.util
import json
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator

import pytest


class UserError(Exception):
    pass


class Public:
    @staticmethod
    def write(fn: Callable) -> Callable:
        return fn

    @staticmethod
    def view(fn: Callable) -> Callable:
        return fn


class Message:
    sender = "0xCOMMISSIONER"
    value = 0


class Contract:
    pass


class VM:
    UserError = UserError


class EqPrinciple:
    @staticmethod
    def strict_eq(fn: Callable) -> str:
        return fn()

    @staticmethod
    def prompt_comparative(fn: Callable, equivalence_criterion: str) -> str:
        return fn()


class NondetWeb:
    @staticmethod
    def render(url: str, mode: str = "text") -> str:
        return ""


class Nondet:
    web = NondetWeb()

    @staticmethod
    def exec_prompt(prompt: str, response_format: str = "json"):
        return {}


class GL:
    Contract = Contract
    public = Public()
    message = Message()
    vm = VM()
    eq_principle = EqPrinciple()
    nondet = Nondet()


gl = GL()

fake_genlayer = types.ModuleType("genlayer")
fake_genlayer.gl = gl
fake_genlayer.dataclass = dataclass
fake_genlayer.__all__ = ["gl", "dataclass"]
sys.modules["genlayer"] = fake_genlayer

CONTRACT_PATH = Path(__file__).resolve().parents[1] / "contracts" / "fantasy_world_cup.py"
spec = importlib.util.spec_from_file_location("fantasy_world_cup_contract", CONTRACT_PATH)
contract_module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["fantasy_world_cup_contract"] = contract_module
spec.loader.exec_module(contract_module)


@pytest.fixture
def commissioner_address() -> str:
    return "0xCOMMISSIONER"


@pytest.fixture
def manager_address() -> str:
    return "0xMANAGER1"


@pytest.fixture
def manager2_address() -> str:
    return "0xMANAGER2"


@pytest.fixture
def as_sender() -> Iterator[Callable[[str], None]]:
    def set_sender(address: str) -> None:
        gl.message.sender = address

    yield set_sender
    gl.message.sender = "0xCOMMISSIONER"
    gl.message.value = 0


@pytest.fixture
def sample_players() -> list[dict]:
    return [
        {"player_id": "ENG_pickford_jordan", "name": "Jordan Pickford", "country": "England", "position": "GK", "price": 55},
        {"player_id": "ENG_stones_john", "name": "John Stones", "country": "England", "position": "DEF", "price": 60},
        {"player_id": "ENG_saka_bukayo", "name": "Bukayo Saka", "country": "England", "position": "MID", "price": 112},
        {"player_id": "ENG_kane_harry", "name": "Harry Kane", "country": "England", "position": "FWD", "price": 115},
        {"player_id": "FRA_maignan_mike", "name": "Mike Maignan", "country": "France", "position": "GK", "price": 60},
        {"player_id": "FRA_saliba_william", "name": "William Saliba", "country": "France", "position": "DEF", "price": 65},
        {"player_id": "FRA_mbappe_kylian", "name": "Kylian Mbappe", "country": "France", "position": "FWD", "price": 135},
        {"player_id": "BRA_alisson", "name": "Alisson", "country": "Brazil", "position": "GK", "price": 82},
        {"player_id": "BRA_marquinhos", "name": "Marquinhos", "country": "Brazil", "position": "DEF", "price": 70},
        {"player_id": "BRA_raphinha", "name": "Raphinha", "country": "Brazil", "position": "MID", "price": 100},
        {"player_id": "ESP_unai_simon", "name": "Unai Simon", "country": "Spain", "position": "GK", "price": 60},
        {"player_id": "ESP_carvajal_dani", "name": "Dani Carvajal", "country": "Spain", "position": "DEF", "price": 65},
        {"player_id": "ESP_rodri", "name": "Rodri", "country": "Spain", "position": "MID", "price": 110},
        {"player_id": "NOR_haaland_erling", "name": "Erling Haaland", "country": "Norway", "position": "FWD", "price": 140},
        {"player_id": "NOR_odegaard_martin", "name": "Martin Odegaard", "country": "Norway", "position": "MID", "price": 108},
        {"player_id": "JPN_mitoma_kaoru", "name": "Kaoru Mitoma", "country": "Japan", "position": "MID", "price": 75},
        {"player_id": "SEN_mane_sadio", "name": "Sadio Mane", "country": "Senegal", "position": "FWD", "price": 95},
        {"player_id": "GER_neuer_manuel", "name": "Manuel Neuer", "country": "Germany", "position": "GK", "price": 80},
    ]


@pytest.fixture
def deployed_contract(commissioner_address: str, sample_players: list[dict]):
    gl.message.sender = commissioner_address
    contract = contract_module.FantasyWorldCup()
    contract.activate_tournament()
    for player in sample_players:
        contract.register_player(**player)
    return contract


@pytest.fixture
def mock_match_stats() -> dict:
    return {
        "home_goals": 2,
        "away_goals": 0,
        "scorers": ["Harry Kane (England)", "Bukayo Saka (England)"],
        "assisters": ["Bukayo Saka (England)", "John Stones (England)"],
        "yellow_cards": ["Rodri (Spain)"],
        "red_cards": ["Dani Carvajal (Spain)"],
        "gk_saves": {"Jordan Pickford": 6},
        "clean_sheet_teams": ["England"],
        "minutes_played": {
            "Jordan Pickford": 90,
            "John Stones": 90,
            "Bukayo Saka": 90,
            "Harry Kane": 90,
            "Rodri": 90,
            "Dani Carvajal": 90,
        },
        "defensive_contributions": {"John Stones": 11, "Bukayo Saka": 12},
        "penalty_saves": [],
        "own_goals": ["Dani Carvajal (Spain)"],
        "penalty_misses": ["Rodri (Spain)"],
    }


@pytest.fixture
def mock_bonus_top3() -> list[str]:
    return ["Bukayo Saka", "Harry Kane", "John Stones"]


@pytest.fixture
def patched_consensus(monkeypatch: pytest.MonkeyPatch, mock_match_stats: dict, mock_bonus_top3: list[str]):
    def strict_eq(fn: Callable) -> str:
        return json.dumps(mock_match_stats, sort_keys=True)

    def prompt_comparative(fn: Callable, equivalence_criterion: str) -> str:
        return json.dumps(mock_bonus_top3)

    monkeypatch.setattr(gl.eq_principle, "strict_eq", strict_eq)
    monkeypatch.setattr(gl.eq_principle, "prompt_comparative", prompt_comparative)
    return None


@pytest.fixture
def user_error():
    return UserError
