import pytest


def _team_with_players(contract, owner, as_sender, players, captain="", vice=""):
    as_sender(owner)
    contract.create_team(f"{owner} FC")
    team = contract.fwc_teams[owner]
    team.player_ids = list(players)
    team.captain_id = captain
    team.vice_captain_id = vice
    team.budget_remaining = 0
    contract.fwc_teams[owner] = team


def test_settle_match_writes_result_and_scores_actions(
    deployed_contract, as_sender, manager_address, commissioner_address, patched_consensus
):
    _team_with_players(
        deployed_contract,
        manager_address,
        as_sender,
        ["ENG_pickford_jordan", "ENG_stones_john", "ENG_saka_bukayo", "ENG_kane_harry", "ESP_rodri", "ESP_carvajal_dani"],
        captain="ENG_saka_bukayo",
    )
    as_sender(commissioner_address)
    deployed_contract.settle_match("GW1_ENG_ESP", "England", "Spain", False, False)
    result = deployed_contract.get_match_result("GW1_ENG_ESP")
    team = deployed_contract.get_team(manager_address)
    assert result["score"] == "2–0"
    assert result["bonus_top3"][0] == "Bukayo Saka"
    assert team["total_points"] == 55
    assert team["total_points"] == deployed_contract.get_leaderboard()[0]["total_points"]


def test_knockout_and_final_extras_are_distinct(deployed_contract, as_sender, manager_address, commissioner_address, patched_consensus):
    _team_with_players(deployed_contract, manager_address, as_sender, ["ENG_kane_harry"], captain="")
    as_sender(commissioner_address)
    deployed_contract.settle_match("KO", "England", "Spain", True, False)
    knockout_total = deployed_contract.get_team(manager_address)["total_points"]
    deployed_contract.settle_match("FINAL", "England", "Spain", True, True)
    final_delta = deployed_contract.get_team(manager_address)["total_points"] - knockout_total
    assert final_delta == knockout_total + 1


def test_triple_captain_and_vice_cover(deployed_contract, as_sender, manager_address, commissioner_address, patched_consensus):
    _team_with_players(deployed_contract, manager_address, as_sender, ["ENG_kane_harry"], captain="ENG_kane_harry")
    as_sender(manager_address)
    deployed_contract.play_chip("triple_captain")
    as_sender(commissioner_address)
    deployed_contract.settle_match("TC", "England", "Spain", False, False)
    assert deployed_contract.get_team(manager_address)["total_points"] == 24

    as_sender("0xVICE")
    deployed_contract.create_team("Vice FC")
    team = deployed_contract.fwc_teams["0xVICE"]
    team.player_ids = ["ENG_kane_harry"]
    team.captain_id = ""
    team.vice_captain_id = "ENG_kane_harry"
    deployed_contract.fwc_teams["0xVICE"] = team
    as_sender(commissioner_address)
    deployed_contract.settle_match("VICE", "England", "Spain", False, False)
    assert deployed_contract.get_team("0xVICE")["total_points"] == 16


def test_settle_match_rejects_duplicate_and_non_commissioner(deployed_contract, as_sender, manager_address, commissioner_address, patched_consensus, user_error):
    as_sender(manager_address)
    with pytest.raises(user_error, match="Only the commissioner"):
        deployed_contract.settle_match("GW1_ENG_ESP", "England", "Spain", False, False)
    as_sender(commissioner_address)
    deployed_contract.settle_match("GW1_ENG_ESP", "England", "Spain", False, False)
    with pytest.raises(user_error, match="already settled"):
        deployed_contract.settle_match("GW1_ENG_ESP", "England", "Spain", False, False)
