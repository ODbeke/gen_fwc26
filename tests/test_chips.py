import pytest


def test_wildcard_sets_gameweek_and_resets_transfers(deployed_contract, as_sender, manager_address):
    as_sender(manager_address)
    deployed_contract.create_team("Chip FC")
    deployed_contract.play_chip("wildcard")
    team = deployed_contract.get_team(manager_address)
    assert team["chips"]["wildcard_gw"] == 1
    assert team["transfers_available"] == 3


def test_one_time_chips_reject_second_use(deployed_contract, as_sender, manager_address, user_error):
    as_sender(manager_address)
    deployed_contract.create_team("Once FC")
    for chip, message in [
        ("wildcard", "Wildcard already used"),
        ("bench_boost", "Bench Boost already used"),
        ("triple_captain", "Triple Captain already used"),
        ("free_hit", "Free Hit already used"),
    ]:
        deployed_contract.play_chip(chip)
        with pytest.raises(user_error, match=message):
            deployed_contract.play_chip(chip)


def test_hero_chip_stores_player_and_rejects_invalid_or_second_pick(deployed_contract, as_sender, manager_address, user_error):
    as_sender(manager_address)
    deployed_contract.create_team("Hero FC")
    with pytest.raises(user_error, match="not found"):
        deployed_contract.play_chip("hero", "NOPE")
    deployed_contract.play_chip("hero", "ENG_saka_bukayo")
    assert deployed_contract.get_team(manager_address)["chips"]["hero_player_id"] == "ENG_saka_bukayo"
    with pytest.raises(user_error, match="already picked"):
        deployed_contract.play_chip("hero", "ENG_kane_harry")


def test_unknown_chip_rejected(deployed_contract, as_sender, manager_address, user_error):
    as_sender(manager_address)
    deployed_contract.create_team("Mystery FC")
    with pytest.raises(user_error, match="Unknown chip"):
        deployed_contract.play_chip("mystery")
