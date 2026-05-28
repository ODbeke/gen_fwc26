import pytest


def test_create_team_is_free(deployed_contract, as_sender, manager_address):
    as_sender(manager_address)
    deployed_contract.create_team("Lagos Lions")
    team = deployed_contract.get_team(manager_address)
    assert team["team_name"] == "Lagos Lions"
    assert deployed_contract.get_prize_pool() == 0


def test_create_team_blocks_duplicate(deployed_contract, as_sender, manager_address, user_error):
    as_sender(manager_address)
    deployed_contract.create_team("One")
    with pytest.raises(user_error, match="already have a team"):
        deployed_contract.create_team("Two")


def test_update_username_is_wallet_bound(deployed_contract, as_sender, manager_address, user_error):
    as_sender(manager_address)
    deployed_contract.create_team("Original")
    deployed_contract.update_username("Lagos Stars")
    team = deployed_contract.get_team(manager_address)
    assert team["team_name"] == "Lagos Stars"
    as_sender("0xNO_TEAM")
    with pytest.raises(user_error, match="team"):
        deployed_contract.update_username("Nope")


def test_pick_player_deducts_budget(deployed_contract, as_sender, manager_address):
    as_sender(manager_address)
    deployed_contract.create_team("Budget FC")
    deployed_contract.pick_player("ENG_pickford_jordan")
    team = deployed_contract.get_team(manager_address)
    assert team["player_ids"] == ["ENG_pickford_jordan"]
    assert team["budget_remaining"] == 945


def test_pick_player_rejects_full_squad(deployed_contract, as_sender, manager_address, user_error):
    as_sender(manager_address)
    deployed_contract.create_team("Full FC")
    team = deployed_contract.fwc_teams[manager_address]
    team.player_ids = [f"P{i}" for i in range(15)]
    deployed_contract.fwc_teams[manager_address] = team
    with pytest.raises(user_error, match="Squad full"):
        deployed_contract.pick_player("ENG_pickford_jordan")


def test_pick_player_rejects_budget_duplicate_and_country_limit(deployed_contract, as_sender, manager_address, user_error):
    as_sender(manager_address)
    deployed_contract.create_team("Rules FC")
    deployed_contract.pick_player("NOR_haaland_erling")
    team = deployed_contract.fwc_teams[manager_address]
    team.budget_remaining = 100
    deployed_contract.fwc_teams[manager_address] = team
    with pytest.raises(user_error, match="Insufficient budget"):
        deployed_contract.pick_player("FRA_mbappe_kylian")
    deployed_contract.pick_player("ENG_pickford_jordan")
    with pytest.raises(user_error, match="already in your squad"):
        deployed_contract.pick_player("ENG_pickford_jordan")
    team = deployed_contract.fwc_teams[manager_address]
    team.player_ids = ["ENG_pickford_jordan", "ENG_stones_john", "ENG_saka_bukayo"]
    team.budget_remaining = 200
    deployed_contract.fwc_teams[manager_address] = team
    with pytest.raises(user_error, match="Max 3 players"):
        deployed_contract.pick_player("ENG_kane_harry")


def test_set_captain_and_reject_non_squad(deployed_contract, as_sender, manager_address, user_error):
    as_sender(manager_address)
    deployed_contract.create_team("Armband FC")
    deployed_contract.pick_player("ENG_pickford_jordan")
    deployed_contract.set_captain("ENG_pickford_jordan")
    deployed_contract.set_captain("ENG_pickford_jordan", vice=True)
    team = deployed_contract.get_team(manager_address)
    assert team["captain_id"] == "ENG_pickford_jordan"
    assert team["vice_captain_id"] == "ENG_pickford_jordan"
    with pytest.raises(user_error, match="not in your squad"):
        deployed_contract.set_captain("BRA_alisson")


def test_make_transfer_success_and_extra_transfer_cost(deployed_contract, as_sender, manager_address):
    as_sender(manager_address)
    deployed_contract.create_team("Market FC")
    deployed_contract.pick_player("ENG_pickford_jordan")
    deployed_contract.make_transfer("ENG_pickford_jordan", "ESP_unai_simon")
    team = deployed_contract.get_team(manager_address)
    assert team["player_ids"] == ["ESP_unai_simon"]
    assert team["budget_remaining"] == 940
    team_obj = deployed_contract.fwc_teams[manager_address]
    team_obj.total_points = 12
    team_obj.budget_remaining = 100
    team_obj.player_ids = ["ESP_unai_simon"]
    deployed_contract.fwc_teams[manager_address] = team_obj
    deployed_contract.make_transfer("ESP_unai_simon", "ENG_pickford_jordan")
    assert deployed_contract.get_team(manager_address)["total_points"] == 8


def test_make_transfer_rejects_budget_and_country_limit(deployed_contract, as_sender, manager_address, user_error):
    as_sender(manager_address)
    deployed_contract.create_team("Blocked FC")
    team = deployed_contract.fwc_teams[manager_address]
    team.player_ids = ["ENG_pickford_jordan", "ENG_stones_john", "FRA_maignan_mike"]
    team.budget_remaining = 0
    deployed_contract.fwc_teams[manager_address] = team
    with pytest.raises(user_error, match="Insufficient budget"):
        deployed_contract.make_transfer("FRA_maignan_mike", "ENG_saka_bukayo")
    team.player_ids = ["ENG_pickford_jordan", "ENG_stones_john", "ENG_kane_harry", "FRA_maignan_mike"]
    team.budget_remaining = 200
    deployed_contract.fwc_teams[manager_address] = team
    with pytest.raises(user_error, match="max 3 players"):
        deployed_contract.make_transfer("FRA_maignan_mike", "ENG_saka_bukayo")


def test_bank_transfer_caps_at_three(deployed_contract, as_sender, manager_address):
    as_sender(manager_address)
    deployed_contract.create_team("Bank FC")
    deployed_contract.bank_transfer()
    deployed_contract.bank_transfer()
    deployed_contract.bank_transfer()
    deployed_contract.bank_transfer()
    assert deployed_contract.get_team(manager_address)["transfers_available"] == 3
