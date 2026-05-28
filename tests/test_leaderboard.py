def test_leaderboard_sorted_and_equal_squads_match(deployed_contract, as_sender, manager_address, manager2_address, commissioner_address, patched_consensus):
    for owner in [manager_address, manager2_address]:
        as_sender(owner)
        deployed_contract.create_team(f"{owner} FC")
        team = deployed_contract.fwc_teams[owner]
        team.player_ids = ["ENG_kane_harry"]
        deployed_contract.fwc_teams[owner] = team
    as_sender(commissioner_address)
    deployed_contract.settle_match("GW1", "England", "Spain", False, False)
    board = deployed_contract.get_leaderboard()
    assert len(board) == 2
    assert board[0]["total_points"] == board[1]["total_points"] == 8


def test_captain_scorer_outscores_non_captain_and_accumulates(deployed_contract, as_sender, manager_address, manager2_address, commissioner_address, patched_consensus):
    for owner, captain in [(manager_address, "ENG_kane_harry"), (manager2_address, "")]:
        as_sender(owner)
        deployed_contract.create_team(f"{owner} FC")
        team = deployed_contract.fwc_teams[owner]
        team.player_ids = ["ENG_kane_harry"]
        team.captain_id = captain
        deployed_contract.fwc_teams[owner] = team
    as_sender(commissioner_address)
    deployed_contract.settle_match("GW1", "England", "Spain", False, False)
    deployed_contract.advance_gameweek()
    deployed_contract.settle_match("GW2", "England", "Spain", False, False)
    board = deployed_contract.get_leaderboard()
    assert board[0]["owner"] == manager_address
    assert board[0]["total_points"] == 32
    assert board[1]["total_points"] == 16
