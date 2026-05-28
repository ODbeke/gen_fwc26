import json

import pytest

from tests.conftest import gl


def test_resolve_awards_stores_winners_and_awards_hero(monkeypatch, deployed_contract, as_sender, manager_address, manager2_address, commissioner_address):
    def strict_eq(fn):
        return json.dumps({
            "golden_boot": "Bukayo Saka",
            "golden_glove": "Jordan Pickford",
            "golden_ball": "Kylian Mbappe",
        }, sort_keys=True)

    monkeypatch.setattr(gl.eq_principle, "strict_eq", strict_eq)
    for owner, hero in [(manager_address, "ENG_saka_bukayo"), (manager2_address, "BRA_alisson")]:
        as_sender(owner)
        deployed_contract.create_team(f"{owner} FC")
        deployed_contract.play_chip("hero", hero)
    as_sender(commissioner_address)
    deployed_contract.resolve_tournament_awards()
    awards = deployed_contract.get_awards()
    assert awards["resolved"] is True
    assert awards["golden_boot"] == "Bukayo Saka"
    assert deployed_contract.get_team(manager_address)["total_points"] == 10
    assert deployed_contract.get_team(manager2_address)["total_points"] == 0


def test_resolve_awards_rejects_second_call(monkeypatch, deployed_contract, as_sender, commissioner_address, user_error):
    monkeypatch.setattr(gl.eq_principle, "strict_eq", lambda fn: json.dumps({}))
    as_sender(commissioner_address)
    deployed_contract.resolve_tournament_awards()
    with pytest.raises(user_error, match="already resolved"):
        deployed_contract.resolve_tournament_awards()
