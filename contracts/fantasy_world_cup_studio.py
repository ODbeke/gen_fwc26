# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json
import typing


MAX_PLAYERS = 15
STARTING_BUDGET = 1000
MAX_PER_COUNTRY = 3
TRANSFER_COST_PTS = 4
MAX_BANKED_XFERS = 3
ENTRY_FEE_WEI = 0

POINTS = {
    "played_lt60": 1,
    "played_ge60": 2,
    "goal_gk": 10,
    "goal_def": 6,
    "goal_mid": 5,
    "goal_fwd": 4,
    "assist": 3,
    "clean_sheet_gk_def": 4,
    "clean_sheet_mid": 1,
    "save_3": 1,
    "penalty_save": 5,
    "goals_conceded_2": -1,
    "yellow_card": -1,
    "red_card": -3,
    "own_goal": -2,
    "penalty_miss": -2,
    "bonus_1st": 3,
    "bonus_2nd": 2,
    "bonus_3rd": 1,
    "knockout_extra": 1,
    "final_extra": 2,
    "defensive_contrib_def": 2,
    "defensive_contrib_mid_fwd": 2,
    "penalty_shootout_scored": 2,
    "penalty_shootout_missed": -2,
}

FIFA_STATS_URL = "https://www.fifa.com/fifaplus/en/tournaments/mens/worldcup/canadamexicousa2026/match-centre"
FIFA_AWARDS_URL = "https://www.fifa.com/fifaplus/en/tournaments/mens/worldcup/canadamexicousa2026/awards"


class FantasyWorldCup(gl.Contract):
    commissioner: Address
    current_gameweek: u32
    tournament_active: bool
    prize_pool: u256
    players: TreeMap[str, str]
    fwc_teams: TreeMap[str, str]
    match_results: TreeMap[str, str]
    gameweek_matches: TreeMap[str, str]
    leaderboard: TreeMap[str, i256]
    golden_boot_player: str
    golden_glove_player: str
    golden_ball_player: str
    awards_resolved: bool

    def __init__(self):
        self.commissioner = gl.message.sender_address
        self.current_gameweek = u32(1)
        self.tournament_active = False
        self.prize_pool = u256(0)
        self.golden_boot_player = ""
        self.golden_glove_player = ""
        self.golden_ball_player = ""
        self.awards_resolved = False

    @gl.public.write
    def activate_tournament(self) -> None:
        self._require_commissioner()
        if self.tournament_active:
            raise gl.vm.UserError("Tournament already active.")
        self.tournament_active = True

    @gl.public.write
    def advance_gameweek(self) -> None:
        self._require_commissioner()
        self.current_gameweek = u32(int(self.current_gameweek) + 1)

    @gl.public.write
    def register_player(self, player_id: str, name: str, country: str, position: str, price: int) -> None:
        self._require_commissioner()
        if position not in ("GK", "DEF", "MID", "FWD"):
            raise gl.vm.UserError("Invalid position. Use GK, DEF, MID, or FWD.")
        if player_id in self.players:
            raise gl.vm.UserError(f"Player {player_id} already registered.")
        self.players[player_id] = self._dumps({
            "player_id": player_id,
            "name": name,
            "country": country,
            "position": position,
            "price": price,
        })

    @gl.public.write
    def assign_gameweek_match(self, gameweek: int, match_id: str) -> None:
        self._require_commissioner()
        key = str(gameweek)
        matches = self._loads(self.gameweek_matches.get(key, "[]"))
        matches.append(match_id)
        self.gameweek_matches[key] = self._dumps(matches)

    @gl.public.write
    def create_team(self, team_name: str) -> None:
        if not self.tournament_active:
            raise gl.vm.UserError("Tournament is not yet active.")
        if len(team_name.strip()) == 0:
            raise gl.vm.UserError("Username is required.")
        owner = self._sender()
        if owner in self.fwc_teams:
            raise gl.vm.UserError("You already have a team.")
        team = {
            "owner": owner,
            "username": team_name.strip(),
            "team_name": team_name.strip(),
            "budget_remaining": STARTING_BUDGET,
            "player_ids": [],
            "captain_id": "",
            "vice_captain_id": "",
            "gameweek_points": {},
            "total_points": 0,
            "chip_wildcard_used": 0,
            "chip_bench_boost_used": 0,
            "chip_triple_captain_used": 0,
            "chip_free_hit_used": 0,
            "chip_hero_player_id": "",
            "hero_bonus_awarded": False,
            "transfers_available": 1,
        }
        self._save_team(owner, team)
        self.leaderboard[owner] = i256(0)

    @gl.public.write
    def update_username(self, username: str) -> None:
        if len(username.strip()) == 0:
            raise gl.vm.UserError("Username is required.")
        owner = self._sender()
        team = self._get_team_data(owner)
        team["username"] = username.strip()
        team["team_name"] = username.strip()
        self._save_team(owner, team)

    @gl.public.write
    def pick_player(self, player_id: str) -> None:
        owner = self._sender()
        team = self._get_team_data(owner)
        player = self._get_player_data(player_id)
        if len(team["player_ids"]) >= MAX_PLAYERS:
            raise gl.vm.UserError("Squad full: 15 players maximum.")
        if player_id in team["player_ids"]:
            raise gl.vm.UserError("Player already in your squad.")
        if int(player["price"]) > int(team["budget_remaining"]):
            raise gl.vm.UserError("Insufficient budget for this player.")
        country_count = 0
        for pid in team["player_ids"]:
            if self._get_player_data(pid)["country"] == player["country"]:
                country_count += 1
        if country_count >= MAX_PER_COUNTRY:
            raise gl.vm.UserError("Max 3 players per country.")
        team["player_ids"].append(player_id)
        team["budget_remaining"] = int(team["budget_remaining"]) - int(player["price"])
        self._save_team(owner, team)

    @gl.public.write
    def set_captain(self, player_id: str, vice: bool = False) -> None:
        owner = self._sender()
        team = self._get_team_data(owner)
        if player_id not in team["player_ids"]:
            raise gl.vm.UserError("Player not in your squad.")
        if vice:
            team["vice_captain_id"] = player_id
        else:
            team["captain_id"] = player_id
        self._save_team(owner, team)

    @gl.public.write
    def make_transfer(self, out_player_id: str, in_player_id: str) -> None:
        owner = self._sender()
        team = self._get_team_data(owner)
        out_player = self._get_player_data(out_player_id)
        in_player = self._get_player_data(in_player_id)
        if out_player_id not in team["player_ids"]:
            raise gl.vm.UserError("Player to sell is not in your squad.")
        if in_player_id in team["player_ids"]:
            raise gl.vm.UserError("Player to buy is already in your squad.")
        new_budget = int(team["budget_remaining"]) + int(out_player["price"]) - int(in_player["price"])
        if new_budget < 0:
            raise gl.vm.UserError("Insufficient budget for transfer.")
        country_count = 0
        for pid in team["player_ids"]:
            if pid != out_player_id and self._get_player_data(pid)["country"] == in_player["country"]:
                country_count += 1
        if country_count >= MAX_PER_COUNTRY:
            raise gl.vm.UserError("Transfer blocked: max 3 players per country.")
        if int(team["transfers_available"]) > 0:
            team["transfers_available"] = int(team["transfers_available"]) - 1
        else:
            team["total_points"] = max(0, int(team["total_points"]) - TRANSFER_COST_PTS)
        team["player_ids"] = [in_player_id if pid == out_player_id else pid for pid in team["player_ids"]]
        team["budget_remaining"] = new_budget
        if team["captain_id"] == out_player_id:
            team["captain_id"] = ""
        if team["vice_captain_id"] == out_player_id:
            team["vice_captain_id"] = ""
        self._save_team(owner, team)

    @gl.public.write
    def play_chip(self, chip: str, hero_player_id: str = "") -> None:
        owner = self._sender()
        team = self._get_team_data(owner)
        gw = int(self.current_gameweek)
        if chip == "wildcard":
            if int(team["chip_wildcard_used"]) != 0:
                raise gl.vm.UserError("Wildcard already used.")
            team["chip_wildcard_used"] = gw
            team["transfers_available"] = MAX_BANKED_XFERS
        elif chip == "bench_boost":
            if int(team["chip_bench_boost_used"]) != 0:
                raise gl.vm.UserError("Bench Boost already used.")
            team["chip_bench_boost_used"] = gw
        elif chip == "triple_captain":
            if int(team["chip_triple_captain_used"]) != 0:
                raise gl.vm.UserError("Triple Captain already used.")
            team["chip_triple_captain_used"] = gw
        elif chip == "free_hit":
            if int(team["chip_free_hit_used"]) != 0:
                raise gl.vm.UserError("Free Hit already used.")
            team["chip_free_hit_used"] = gw
        elif chip == "hero":
            if team["chip_hero_player_id"] != "":
                raise gl.vm.UserError("World Cup Hero already picked.")
            self._get_player_data(hero_player_id)
            team["chip_hero_player_id"] = hero_player_id
        else:
            raise gl.vm.UserError("Unknown chip. Use wildcard, bench_boost, triple_captain, free_hit, or hero.")
        self._save_team(owner, team)

    @gl.public.write
    def bank_transfer(self) -> None:
        owner = self._sender()
        team = self._get_team_data(owner)
        if int(team["transfers_available"]) < MAX_BANKED_XFERS:
            team["transfers_available"] = int(team["transfers_available"]) + 1
        self._save_team(owner, team)

    @gl.public.write
    def settle_match(self, match_id: str, home_team: str, away_team: str, is_knockout: bool, is_final: bool) -> None:
        self._require_commissioner()
        if match_id in self.match_results:
            raise gl.vm.UserError(f"Match {match_id} already settled.")

        def fetch_match_stats():
            raw_html = gl.nondet.web.render(f"{FIFA_STATS_URL}?match={match_id}", mode="text")
            prompt = f"""
Extract objective football match statistics for {home_team} vs {away_team}.
Return only JSON with these keys:
home_goals, away_goals, scorers, assisters, yellow_cards, red_cards,
gk_saves, clean_sheet_teams, minutes_played, defensive_contributions,
penalty_saves, own_goals, penalty_misses.
Use empty arrays or objects when unknown.
Match page text:
{raw_html[:6000]}
"""
            return self._dumps(gl.nondet.exec_prompt(prompt, response_format="json"))

        stats = self._loads(gl.eq_principle.strict_eq(fetch_match_stats))

        def fetch_bonus_top3():
            raw_html = gl.nondet.web.render(f"{FIFA_STATS_URL}?match={match_id}", mode="text")
            prompt = f"""
Pick the three best performers in {home_team} vs {away_team}.
Return only a JSON array of exactly three player name strings.
Match page text:
{raw_html[:4000]}
"""
            return self._dumps(gl.nondet.exec_prompt(prompt, response_format="json"))

        bonus_raw = gl.eq_principle.prompt_comparative(
            fetch_bonus_top3,
            "Two top-three lists are equivalent if at least two player names overlap.",
        )
        try:
            bonus_top3 = self._loads(bonus_raw)
        except json.JSONDecodeError:
            bonus_top3 = []

        result = {
            "match_id": match_id,
            "home_team": home_team,
            "away_team": away_team,
            "home_goals": int(stats.get("home_goals", 0)),
            "away_goals": int(stats.get("away_goals", 0)),
            "scorers": stats.get("scorers", []),
            "assisters": stats.get("assisters", []),
            "yellow_cards": stats.get("yellow_cards", []),
            "red_cards": stats.get("red_cards", []),
            "gk_saves": stats.get("gk_saves", {}),
            "clean_sheet_teams": stats.get("clean_sheet_teams", []),
            "bonus_top3": bonus_top3,
            "is_knockout": is_knockout,
            "is_final": is_final,
            "settled": True,
        }
        self.match_results[match_id] = self._dumps(result)
        self._score_all_teams(match_id, stats, bonus_top3, is_knockout, is_final)

    @gl.public.write
    def resolve_tournament_awards(self) -> None:
        self._require_commissioner()
        if self.awards_resolved:
            raise gl.vm.UserError("Awards already resolved.")

        def fetch_awards():
            raw_html = gl.nondet.web.render(FIFA_AWARDS_URL, mode="text")
            prompt = f"""
Extract the 2026 FIFA World Cup award winners.
Return only JSON with golden_boot, golden_glove, golden_ball.
Page text:
{raw_html[:4000]}
"""
            return self._dumps(gl.nondet.exec_prompt(prompt, response_format="json"))

        awards = self._loads(gl.eq_principle.strict_eq(fetch_awards))
        self.golden_boot_player = awards.get("golden_boot", "")
        self.golden_glove_player = awards.get("golden_glove", "")
        self.golden_ball_player = awards.get("golden_ball", "")
        winners = [self.golden_boot_player, self.golden_glove_player, self.golden_ball_player]
        for owner, raw_team in self.fwc_teams.items():
            team = self._loads(raw_team)
            hero_id = team.get("chip_hero_player_id", "")
            if hero_id != "" and not bool(team.get("hero_bonus_awarded", False)):
                hero = self._get_player_data(hero_id)
                if hero["name"] in winners:
                    team["total_points"] = int(team["total_points"]) + 10
                    team["hero_bonus_awarded"] = True
                    self._save_team(owner, team)
        self.awards_resolved = True

    @gl.public.view
    def get_team(self, owner: str) -> dict[str, typing.Any]:
        return self._get_team_data(owner)

    @gl.public.view
    def get_player(self, player_id: str) -> dict[str, typing.Any]:
        return self._get_player_data(player_id)

    @gl.public.view
    def get_leaderboard(self) -> list[dict[str, typing.Any]]:
        board = []
        for owner, points in self.leaderboard.items():
            if owner in self.fwc_teams:
                team = self._loads(self.fwc_teams[owner])
                board.append({"owner": owner, "username": team.get("username", team["team_name"]), "team_name": team["team_name"], "total_points": int(points)})
        board.sort(key=lambda row: row["total_points"], reverse=True)
        return board

    @gl.public.view
    def get_match_result(self, match_id: str) -> dict[str, typing.Any]:
        if match_id not in self.match_results:
            raise gl.vm.UserError(f"Match {match_id} not yet settled.")
        result = self._loads(self.match_results[match_id])
        result["score"] = f"{result['home_goals']}-{result['away_goals']}"
        return result

    @gl.public.view
    def get_gameweek(self) -> int:
        return int(self.current_gameweek)

    @gl.public.view
    def get_prize_pool(self) -> int:
        return int(self.prize_pool)

    @gl.public.view
    def get_awards(self) -> dict[str, typing.Any]:
        return {
            "golden_boot": self.golden_boot_player,
            "golden_glove": self.golden_glove_player,
            "golden_ball": self.golden_ball_player,
            "resolved": self.awards_resolved,
        }

    def _score_all_teams(self, match_id: str, stats: dict[str, typing.Any], bonus_top3: list[str], is_knockout: bool, is_final: bool) -> None:
        player_points = {}
        for name, mins in stats.get("minutes_played", {}).items():
            player_points[name] = player_points.get(name, 0) + (POINTS["played_ge60"] if int(mins) >= 60 else POINTS["played_lt60"])
        for entry in stats.get("scorers", []):
            name = self._extract_name(entry)
            pos = self._player_position_by_name(name)
            player_points[name] = player_points.get(name, 0) + POINTS.get(f"goal_{pos.lower()}", POINTS["goal_fwd"])
            player_points[name] += POINTS["final_extra"] if is_final else POINTS["knockout_extra"] if is_knockout else 0
        for entry in stats.get("assisters", []):
            name = self._extract_name(entry)
            player_points[name] = player_points.get(name, 0) + POINTS["assist"]
            player_points[name] += POINTS["final_extra"] if is_final else POINTS["knockout_extra"] if is_knockout else 0
        for pid, raw_player in self.players.items():
            player = self._loads(raw_player)
            if player["country"] in stats.get("clean_sheet_teams", []):
                if player["position"] in ("GK", "DEF"):
                    player_points[player["name"]] = player_points.get(player["name"], 0) + POINTS["clean_sheet_gk_def"]
                elif player["position"] == "MID":
                    player_points[player["name"]] = player_points.get(player["name"], 0) + POINTS["clean_sheet_mid"]
        for name, saves in stats.get("gk_saves", {}).items():
            player_points[name] = player_points.get(name, 0) + (int(saves) // 3) * POINTS["save_3"]
        result = self._loads(self.match_results[match_id])
        for pid, raw_player in self.players.items():
            player = self._loads(raw_player)
            if player["position"] in ("GK", "DEF"):
                conceded = 0
                if player["country"] == result["home_team"]:
                    conceded = int(result["away_goals"])
                elif player["country"] == result["away_team"]:
                    conceded = int(result["home_goals"])
                player_points[player["name"]] = player_points.get(player["name"], 0) + (conceded // 2) * POINTS["goals_conceded_2"]
        for key, point_key in [("yellow_cards", "yellow_card"), ("red_cards", "red_card"), ("own_goals", "own_goal"), ("penalty_misses", "penalty_miss"), ("penalty_saves", "penalty_save")]:
            for entry in stats.get(key, []):
                name = self._extract_name(entry)
                player_points[name] = player_points.get(name, 0) + POINTS[point_key]
        for name, contrib in stats.get("defensive_contributions", {}).items():
            pos = self._player_position_by_name(name)
            if pos == "DEF" and int(contrib) >= 10:
                player_points[name] = player_points.get(name, 0) + POINTS["defensive_contrib_def"]
            elif pos in ("MID", "FWD") and int(contrib) >= 12:
                player_points[name] = player_points.get(name, 0) + POINTS["defensive_contrib_mid_fwd"]
        bonus_points = [POINTS["bonus_1st"], POINTS["bonus_2nd"], POINTS["bonus_3rd"]]
        for index, name in enumerate(bonus_top3[:3]):
            player_points[name] = player_points.get(name, 0) + bonus_points[index]
        gw_key = str(int(self.current_gameweek))
        for owner, raw_team in self.fwc_teams.items():
            team = self._loads(raw_team)
            gw_points = 0
            triple = int(team["chip_triple_captain_used"]) == int(self.current_gameweek)
            for pid in team["player_ids"]:
                player = self._get_player_data(pid)
                points = player_points.get(player["name"], 0)
                if pid == team["captain_id"]:
                    points *= 3 if triple else 2
                elif pid == team["vice_captain_id"] and team["captain_id"] == "":
                    points *= 2
                gw_points += points
            team["gameweek_points"][gw_key] = gw_points
            team["total_points"] = int(team["total_points"]) + gw_points
            if int(team["transfers_available"]) < MAX_BANKED_XFERS:
                team["transfers_available"] = int(team["transfers_available"]) + 1
            self._save_team(owner, team)

    def _require_commissioner(self) -> None:
        if gl.message.sender_address != self.commissioner:
            raise gl.vm.UserError("Only the commissioner can call this method.")

    def _sender(self) -> str:
        return gl.message.sender_address.as_hex

    def _get_player_data(self, player_id: str) -> dict[str, typing.Any]:
        if player_id not in self.players:
            raise gl.vm.UserError(f"Player '{player_id}' not found in registry.")
        return self._loads(self.players[player_id])

    def _get_team_data(self, owner: str) -> dict[str, typing.Any]:
        if owner not in self.fwc_teams:
            raise gl.vm.UserError("No team found for that address.")
        return self._loads(self.fwc_teams[owner])

    def _save_team(self, owner: str, team: dict[str, typing.Any]) -> None:
        self.fwc_teams[owner] = self._dumps(team)
        self.leaderboard[owner] = i256(int(team["total_points"]))

    def _extract_name(self, entry: str) -> str:
        return entry.split("(")[0].strip() if "(" in entry else entry.strip()

    def _player_position_by_name(self, name: str) -> str:
        for pid, raw_player in self.players.items():
            player = self._loads(raw_player)
            if player["name"].lower() == name.lower():
                return player["position"]
        return "FWD"

    def _dumps(self, value: typing.Any) -> str:
        return json.dumps(value, sort_keys=True)

    def _loads(self, value: str) -> typing.Any:
        return json.loads(value)
