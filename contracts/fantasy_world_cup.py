# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
# ============================================================
#  Fantasy World Cup (FWC) — GenLayer Intelligent Contract
#  Built for the GenLayer community
# ============================================================
#
#  GenLayer features used:
#    - gl.nondet.web.render()         → live match stat fetching
#    - gl.nondet.exec_prompt()        → AI bonus-point adjudication
#    - gl.eq_principle.strict_eq()    → deterministic consensus (scores/goals)
#    - gl.eq_principle.prompt_comparative() → subjective consensus (bonus pts)
#    - gl.vm.UserError                → safe user-facing error handling
#    - @gl.public.write / @gl.public.view → state-mutating vs read-only methods
#    - Typed state variables (dict, list, int, str, bool)
#    - gl.message.sender             → caller address
# ============================================================

from genlayer import *
import json

# ──────────────────────────────────────────────────────────────
#  DATACLASS DEFINITIONS
#  GenLayer requires plain Python dataclasses for complex types
#  stored in contract state.
# ──────────────────────────────────────────────────────────────

@dataclass
class Player:
    name: str
    country: str
    position: str       # "GK" | "DEF" | "MID" | "FWD"
    price: int          # price in FWC tokens (e.g. 80 = 8.0m)


@dataclass
class MatchResult:
    match_id: str
    home_team: str
    away_team: str
    home_goals: int
    away_goals: int
    scorers: list        # list of str — "PlayerName (team)"
    assisters: list      # list of str
    yellow_cards: list
    red_cards: list
    gk_saves: dict       # {"PlayerName": saves_count}
    clean_sheet_teams: list  # teams that kept a clean sheet
    bonus_top3: list     # ["PlayerName", ...] top 3 performers
    is_knockout: bool
    is_final: bool
    settled: bool


@dataclass
class FWCTeam:
    owner: str
    team_name: str
    budget_remaining: int   # in tenths of millions (1000 = 100.0m budget)
    player_ids: list        # list of up to 15 player_ids
    captain_id: str
    vice_captain_id: str
    gameweek_points: dict   # {gameweek: total_points}
    total_points: int
    chip_wildcard_used: int       # 0 = not used, gameweek number otherwise
    chip_bench_boost_used: int
    chip_triple_captain_used: int
    chip_free_hit_used: int
    chip_hero_player_id: str      # for the World Cup Hero chip
    hero_bonus_awarded: bool
    transfers_available: int      # free transfers banked (max 3)


# ──────────────────────────────────────────────────────────────
#  CONSTANTS
# ──────────────────────────────────────────────────────────────

MAX_PLAYERS        = 15
STARTING_BUDGET    = 1000    # 100.0m, stored in tenths of millions
MAX_PER_COUNTRY    = 3
TRANSFER_COST_PTS  = 4
MAX_BANKED_XFERS   = 3
ENTRY_FEE_WEI      = 0           # free entry — no fee required

# Base points table — mirrors FPL adapted for World Cup
POINTS = {
    "played_lt60":   1,
    "played_ge60":   2,
    "goal_gk":      10,
    "goal_def":      6,
    "goal_mid":      5,
    "goal_fwd":      4,
    "assist":        3,
    "clean_sheet_gk_def": 4,
    "clean_sheet_mid": 1,
    "save_3":        1,   # per 3 saves
    "penalty_save":  5,
    "goals_conceded_2": -1,   # per 2 goals conceded (GK/DEF)
    "yellow_card":  -1,
    "red_card":     -3,
    "own_goal":     -2,
    "penalty_miss": -2,
    "bonus_1st":     3,
    "bonus_2nd":     2,
    "bonus_3rd":     1,
    "knockout_extra": 1,   # goals/assists in knockouts +1
    "final_extra":   2,    # goals/assists in final +2
    "defensive_contrib_def": 2,   # 10+ CBIT in one match
    "defensive_contrib_mid_fwd": 2,  # 12+ CBIRT in one match
    "penalty_shootout_scored": 2,
    "penalty_shootout_missed": -2,
}

# FIFA stat source (used by validators to fetch live data)
FIFA_STATS_URL = "https://www.fifa.com/fifaplus/en/tournaments/mens/worldcup/canadamexicousa2026/match-centre"


# ──────────────────────────────────────────────────────────────
#  THE CONTRACT
# ──────────────────────────────────────────────────────────────

class FantasyWorldCup(gl.Contract):

    # ── State variables (all typed for genvm-lint) ─────────────

    commissioner: str           # deployer address — admin
    current_gameweek: int
    tournament_active: bool
    prize_pool: int             # accumulated entry fees (wei)

    # player registry: player_id → Player
    players: dict

    # team registry: owner_address → FWCTeam
    fwc_teams: dict

    # settled match results: match_id → MatchResult
    match_results: dict

    # gameweek metadata: gameweek_number → list of match_ids
    gameweek_matches: dict

    # leaderboard snapshot: owner_address → total_points (cached)
    leaderboard: dict

    # golden award winners (resolved end of tournament)
    golden_boot_player: str
    golden_glove_player: str
    golden_ball_player: str
    awards_resolved: bool

    # ── Constructor ────────────────────────────────────────────

    def __init__(self):
        self.commissioner = str(gl.message.sender)
        # Start at GW1 because chip usage stores 0 as the "unused" sentinel.
        self.current_gameweek = 1
        self.tournament_active = False
        self.prize_pool = 0

        self.players = {}
        self.fwc_teams = {}
        self.match_results = {}
        self.gameweek_matches = {}
        self.leaderboard = {}

        self.golden_boot_player = ""
        self.golden_glove_player = ""
        self.golden_ball_player = ""
        self.awards_resolved = False

    # ══════════════════════════════════════════════════════════
    #  ADMIN — COMMISSIONER ONLY
    # ══════════════════════════════════════════════════════════

    @gl.public.write
    def activate_tournament(self) -> None:
        """Open the tournament. Only the commissioner can call this."""
        self._require_commissioner()
        if self.tournament_active:
            raise gl.vm.UserError("Tournament already active.")
        self.tournament_active = True

    @gl.public.write
    def advance_gameweek(self) -> None:
        """Move to the next gameweek. Called by commissioner after all
        matches in the current GW are settled."""
        self._require_commissioner()
        self.current_gameweek += 1

    @gl.public.write
    def register_player(
        self,
        player_id: str,
        name: str,
        country: str,
        position: str,
        price: int,
    ) -> None:
        """Add a player to the pool. Commissioner-only.
        position must be one of: GK, DEF, MID, FWD.
        price is in FWC token units (e.g. 80 = 8.0m)."""
        self._require_commissioner()
        if position not in ("GK", "DEF", "MID", "FWD"):
            raise gl.vm.UserError(f"Invalid position: {position}")
        if player_id in self.players:
            raise gl.vm.UserError(f"Player {player_id} already registered.")
        self.players[player_id] = Player(
            name=name,
            country=country,
            position=position,
            price=price,
        )

    @gl.public.write
    def assign_gameweek_match(self, gameweek: int, match_id: str) -> None:
        """Link a match_id to a gameweek."""
        self._require_commissioner()
        if str(gameweek) not in self.gameweek_matches:
            self.gameweek_matches[str(gameweek)] = []
        gw_list = list(self.gameweek_matches[str(gameweek)])
        gw_list.append(match_id)
        self.gameweek_matches[str(gameweek)] = gw_list

    # ══════════════════════════════════════════════════════════
    #  MANAGER ACTIONS — any registered user
    # ══════════════════════════════════════════════════════════

    @gl.public.write
    def create_team(self, team_name: str) -> None:
        """Register a new FWC team. Entry is free — open to all."""
        if not self.tournament_active:
            raise gl.vm.UserError("Tournament is not yet active.")
        if len(team_name.strip()) == 0:
            raise gl.vm.UserError("Username is required.")
        owner = str(gl.message.sender)
        if owner in self.fwc_teams:
            raise gl.vm.UserError("You already have a team.")

        self.fwc_teams[owner] = FWCTeam(
            owner=owner,
            team_name=team_name.strip(),
            budget_remaining=STARTING_BUDGET,
            player_ids=[],
            captain_id="",
            vice_captain_id="",
            gameweek_points={},
            total_points=0,
            chip_wildcard_used=0,
            chip_bench_boost_used=0,
            chip_triple_captain_used=0,
            chip_free_hit_used=0,
            chip_hero_player_id="",
            hero_bonus_awarded=False,
            transfers_available=1,
        )
        self.leaderboard[owner] = 0

    @gl.public.write
    def update_username(self, username: str) -> None:
        """Update the wallet-bound manager username/team name."""
        if len(username.strip()) == 0:
            raise gl.vm.UserError("Username is required.")
        owner = str(gl.message.sender)
        team = self._get_team(owner)
        team.team_name = username.strip()
        self.fwc_teams[owner] = team

    @gl.public.write
    def pick_player(self, player_id: str) -> None:
        """Add a player to your squad (pre-tournament draft).
        Enforces budget, squad size, and max-3-per-country rules."""
        owner = str(gl.message.sender)
        team = self._get_team(owner)
        player = self._get_player(player_id)

        if len(team.player_ids) >= MAX_PLAYERS:
            raise gl.vm.UserError(
                f"Squad full: {MAX_PLAYERS} players maximum."
            )
        if player_id in team.player_ids:
            raise gl.vm.UserError("Player already in your squad.")
        if player.price > team.budget_remaining:
            raise gl.vm.UserError(
                f"Insufficient budget. Need {player.price / 10:.1f}m, "
                f"have {team.budget_remaining / 10:.1f}m."
            )

        # Enforce max 3 from same country
        country_count = sum(
            1 for pid in team.player_ids
            if pid in self.players and self.players[pid].country == player.country
        )
        if country_count >= MAX_PER_COUNTRY:
            raise gl.vm.UserError(
                f"Max {MAX_PER_COUNTRY} players per country. "
                f"You already have {country_count} from {player.country}."
            )

        team.player_ids = list(team.player_ids) + [player_id]
        team.budget_remaining -= player.price
        self.fwc_teams[owner] = team

    @gl.public.write
    def set_captain(self, player_id: str, vice: bool = False) -> None:
        """Set captain or vice-captain. Player must be in your squad."""
        owner = str(gl.message.sender)
        team = self._get_team(owner)
        if player_id not in team.player_ids:
            raise gl.vm.UserError("Player not in your squad.")
        if vice:
            team.vice_captain_id = player_id
        else:
            team.captain_id = player_id
        self.fwc_teams[owner] = team

    @gl.public.write
    def make_transfer(self, out_player_id: str, in_player_id: str) -> None:
        """Swap a player in your squad. Uses a free transfer if available,
        otherwise deducts TRANSFER_COST_PTS points from current total.
        Only allowed before a gameweek's deadline (enforced off-chain via
        the commissioner advancing gameweeks)."""
        owner = str(gl.message.sender)
        team = self._get_team(owner)
        in_player = self._get_player(in_player_id)
        out_player = self._get_player(out_player_id)

        if out_player_id not in team.player_ids:
            raise gl.vm.UserError("Player to sell is not in your squad.")
        if in_player_id in team.player_ids:
            raise gl.vm.UserError("Player to buy is already in your squad.")

        # Budget check: refund out, deduct in
        new_budget = team.budget_remaining + out_player.price - in_player.price
        if new_budget < 0:
            raise gl.vm.UserError(
                f"Insufficient budget for transfer. "
                f"Need {(in_player.price - out_player.price) / 10:.1f}m more."
            )

        # Max-3-per-country check for incoming player
        country_count = sum(
            1 for pid in team.player_ids
            if pid != out_player_id
            and pid in self.players
            and self.players[pid].country == in_player.country
        )
        if country_count >= MAX_PER_COUNTRY:
            raise gl.vm.UserError(
                f"Transfer blocked: max {MAX_PER_COUNTRY} players per country."
            )

        # Transfer point cost
        if team.transfers_available > 0:
            team.transfers_available -= 1
        else:
            team.total_points = max(0, team.total_points - TRANSFER_COST_PTS)

        # Execute swap
        new_players = [
            in_player_id if pid == out_player_id else pid
            for pid in team.player_ids
        ]
        team.player_ids = new_players
        team.budget_remaining = new_budget

        # If captain/vice transferred out, clear them
        if team.captain_id == out_player_id:
            team.captain_id = ""
        if team.vice_captain_id == out_player_id:
            team.vice_captain_id = ""

        self.fwc_teams[owner] = team

    @gl.public.write
    def play_chip(self, chip: str, hero_player_id: str = "") -> None:
        """Activate a chip. chip must be one of:
          'wildcard'       — rebuild squad freely this GW
          'bench_boost'    — bench players score too (resolved at settlement)
          'triple_captain' — captain gets 3x instead of 2x this GW
          'free_hit'       — one-GW full squad swap
          'hero'           — pick a World Cup Hero for end-of-tournament bonus
        """
        owner = str(gl.message.sender)
        team = self._get_team(owner)
        gw = self.current_gameweek

        if chip == "wildcard":
            if team.chip_wildcard_used != 0:
                raise gl.vm.UserError("Wildcard already used.")
            team.chip_wildcard_used = gw
            # Wildcard resets transfer cost for this GW — banked xfers preserved
            team.transfers_available = MAX_BANKED_XFERS

        elif chip == "bench_boost":
            if team.chip_bench_boost_used != 0:
                raise gl.vm.UserError("Bench Boost already used.")
            team.chip_bench_boost_used = gw

        elif chip == "triple_captain":
            if team.chip_triple_captain_used != 0:
                raise gl.vm.UserError("Triple Captain already used.")
            team.chip_triple_captain_used = gw

        elif chip == "free_hit":
            if team.chip_free_hit_used != 0:
                raise gl.vm.UserError("Free Hit already used.")
            team.chip_free_hit_used = gw

        elif chip == "hero":
            if team.chip_hero_player_id != "":
                raise gl.vm.UserError("World Cup Hero already picked.")
            if hero_player_id not in self.players:
                raise gl.vm.UserError("Hero player not found in registry.")
            team.chip_hero_player_id = hero_player_id

        else:
            raise gl.vm.UserError(
                f"Unknown chip '{chip}'. Valid: wildcard, bench_boost, "
                "triple_captain, free_hit, hero."
            )

        self.fwc_teams[owner] = team

    @gl.public.write
    def bank_transfer(self) -> None:
        """Roll over an unused free transfer (max 3 banked).
        Call once per gameweek if you skip making a transfer."""
        owner = str(gl.message.sender)
        team = self._get_team(owner)
        if team.transfers_available < MAX_BANKED_XFERS:
            team.transfers_available += 1
        self.fwc_teams[owner] = team

    # ══════════════════════════════════════════════════════════
    #  MATCH SETTLEMENT  ←  GenLayer's core AI/web features
    # ══════════════════════════════════════════════════════════

    @gl.public.write
    def settle_match(
        self,
        match_id: str,
        home_team: str,
        away_team: str,
        is_knockout: bool,
        is_final: bool,
    ) -> None:
        """Settle a completed match using live web data + LLM adjudication.

        Consensus flow:
          1. Fetch raw match stats from FIFA (gl.nondet.web.render)
          2. Use LLM to extract structured JSON from raw HTML/text
             → gl.eq_principle.strict_eq (deterministic JSON fields)
          3. Use gl.eq_principle.prompt_comparative for bonus-point top-3
             (subjective — LLMs may rank differently, equivalence defined
             as "at least 2 of 3 players overlap")
          4. Write MatchResult to state and score all FWC teams.
        """
        self._require_commissioner()
        if match_id in self.match_results:
            raise gl.vm.UserError(f"Match {match_id} already settled.")

        # ── Step 1 & 2: Fetch and extract deterministic match data ──
        # Non-deterministic block must be wrapped in an inner function
        # and passed to gl.eq_principle.*  — genvm-lint enforces this.

        def fetch_match_stats():
            """Fetch live stats and extract structured data via LLM.
            Multiple validators run this independently; strict_eq consensus
            means they must agree on every field (score, scorers, etc.)."""

            raw_html = gl.nondet.web.render(
                f"{FIFA_STATS_URL}?match={match_id}",
                mode="text",
            )

            extract_prompt = f"""
You are a football statistics extractor.
Below is the match page text for the game:
  {home_team} vs {away_team}   (match_id: {match_id})

Extract the following and respond ONLY with valid JSON, no markdown:
{{
  "home_goals": <int>,
  "away_goals": <int>,
  "scorers": ["PlayerName (team)", ...],
  "assisters": ["PlayerName (team)", ...],
  "yellow_cards": ["PlayerName (team)", ...],
  "red_cards": ["PlayerName (team)", ...],
  "gk_saves": {{"PlayerName": <int>, ...}},
  "clean_sheet_teams": ["TeamName", ...],
  "minutes_played": {{"PlayerName": <int>, ...}},
  "defensive_contributions": {{"PlayerName": <int>, ...}},
  "penalty_saves": ["PlayerName", ...],
  "own_goals": ["PlayerName", ...],
  "penalty_misses": ["PlayerName", ...]
}}

If a field has no data, use an empty list or empty dict.
Match text:
{raw_html[:6000]}
"""
            result = gl.nondet.exec_prompt(
                extract_prompt,
                response_format="json",
            )
            # Serialise with sorted keys so strict_eq byte-compares correctly
            return json.dumps(result, sort_keys=True)

        # strict_eq: all validators must produce the same JSON string.
        # This is correct for factual data (scorelines, card counts).
        raw_stats_str = gl.eq_principle.strict_eq(fetch_match_stats)
        stats = json.loads(raw_stats_str)

        # ── Step 3: Subjective bonus-point top-3 via LLM ──
        # prompt_comparative allows validators to disagree on exact wording
        # while agreeing on semantic outcome ("top 3 performers overlap ≥2").

        def fetch_bonus_top3():
            """Ask the LLM to rate the 3 best performers this match.
            Different validators/LLMs may produce slightly different rankings.
            The Equivalence Principle (prompt_comparative) accepts them
            if they substantially agree on the top performers."""

            raw_html = gl.nondet.web.render(
                f"{FIFA_STATS_URL}?match={match_id}",
                mode="text",
            )
            bonus_prompt = f"""
You are an expert football analyst scoring match performances for a
fantasy football game. Review the stats below for the match:
  {home_team} {stats.get('home_goals', 0)}–{stats.get('away_goals', 0)} {away_team}

Identify the THREE best performing outfield players based on:
  - Goals and assists
  - Key passes and chance creation
  - Successful dribbles and tackles
  - Defensive contributions (clearances, blocks, interceptions)
  - Overall influence on the game

Return ONLY a JSON array of exactly 3 player name strings, best first:
["BestPlayer", "SecondBest", "ThirdBest"]

Match stats text:
{raw_html[:4000]}
"""
            result = gl.nondet.exec_prompt(
                bonus_prompt,
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        # prompt_comparative: equivalence criterion passed as a natural-language
        # string.  Validators compare each other's outputs against this rule.
        bonus_equivalence_principle = (
            "Two bonus-point top-3 lists are equivalent if at least 2 out of "
            "3 players appear in both lists, regardless of exact ordering."
        )
        bonus_raw = gl.eq_principle.prompt_comparative(
            fetch_bonus_top3,
            bonus_equivalence_principle,
        )
        try:
            bonus_top3 = json.loads(bonus_raw)
        except Exception:
            bonus_top3 = []

        # ── Step 4: Build and store MatchResult ──────────────────
        result = MatchResult(
            match_id=match_id,
            home_team=home_team,
            away_team=away_team,
            home_goals=stats.get("home_goals", 0),
            away_goals=stats.get("away_goals", 0),
            scorers=stats.get("scorers", []),
            assisters=stats.get("assisters", []),
            yellow_cards=stats.get("yellow_cards", []),
            red_cards=stats.get("red_cards", []),
            gk_saves=stats.get("gk_saves", {}),
            clean_sheet_teams=stats.get("clean_sheet_teams", []),
            bonus_top3=bonus_top3,
            is_knockout=is_knockout,
            is_final=is_final,
            settled=True,
        )
        self.match_results[match_id] = result

        # ── Step 5: Score all FWC teams ───────────────────────────
        self._score_all_teams(match_id, stats, bonus_top3, is_knockout, is_final)

    # ══════════════════════════════════════════════════════════
    #  AWARD RESOLUTION — end of tournament
    # ══════════════════════════════════════════════════════════

    @gl.public.write
    def resolve_tournament_awards(self) -> None:
        """Fetch official FIFA award winners (Golden Boot, Glove, Ball)
        and apply Hero chip bonuses.  Uses web fetch + LLM extraction.
        Commissioner-only, called after the final."""
        self._require_commissioner()
        if self.awards_resolved:
            raise gl.vm.UserError("Awards already resolved.")

        def fetch_awards():
            """Fetch and extract the three FIFA award winners via LLM."""
            awards_html = gl.nondet.web.render(
                "https://www.fifa.com/fifaplus/en/tournaments/mens/worldcup/"
                "canadamexicousa2026/awards",
                mode="text",
            )
            awards_prompt = f"""
Extract the winners of the three individual awards at the 2026 FIFA World Cup.
Respond ONLY with JSON, no markdown:
{{
  "golden_boot": "PlayerFullName",
  "golden_glove": "PlayerFullName",
  "golden_ball": "PlayerFullName"
}}

Page text:
{awards_html[:4000]}
"""
            result = gl.nondet.exec_prompt(
                awards_prompt,
                response_format="json",
            )
            return json.dumps(result, sort_keys=True)

        # Strict equality — award winner names are objective facts.
        awards_str = gl.eq_principle.strict_eq(fetch_awards)
        awards = json.loads(awards_str)

        self.golden_boot_player  = awards.get("golden_boot", "")
        self.golden_glove_player = awards.get("golden_glove", "")
        self.golden_ball_player  = awards.get("golden_ball", "")

        award_winners = {
            self.golden_boot_player,
            self.golden_glove_player,
            self.golden_ball_player,
        }

        # Apply +10 bonus to all teams whose Hero player won an award
        for owner, team in self.fwc_teams.items():
            if team.chip_hero_player_id and not team.hero_bonus_awarded:
                hero = self.players.get(team.chip_hero_player_id)
                if hero and hero.name in award_winners:
                    team.total_points += 10
                    team.hero_bonus_awarded = True
                    self.leaderboard[owner] = team.total_points
                    self.fwc_teams[owner] = team

        self.awards_resolved = True

    # ══════════════════════════════════════════════════════════
    #  READ-ONLY VIEWS
    # ══════════════════════════════════════════════════════════

    @gl.public.view
    def get_team(self, owner: str) -> dict:
        """Return the FWCTeam for a given owner address."""
        if owner not in self.fwc_teams:
            raise gl.vm.UserError("No team found for that address.")
        t = self.fwc_teams[owner]
        return {
            "owner":              t.owner,
            "team_name":          t.team_name,
            "budget_remaining":   t.budget_remaining,
            "player_ids":         t.player_ids,
            "captain_id":         t.captain_id,
            "vice_captain_id":    t.vice_captain_id,
            "total_points":       t.total_points,
            "transfers_available": t.transfers_available,
            "chips": {
                "wildcard_gw":       t.chip_wildcard_used,
                "bench_boost_gw":    t.chip_bench_boost_used,
                "triple_captain_gw": t.chip_triple_captain_used,
                "free_hit_gw":       t.chip_free_hit_used,
                "hero_player_id":    t.chip_hero_player_id,
                "hero_bonus_awarded": t.hero_bonus_awarded,
            },
        }

    @gl.public.view
    def get_player(self, player_id: str) -> dict:
        """Return player metadata."""
        p = self._get_player(player_id)
        return {
            "player_id": player_id,
            "name":      p.name,
            "country":   p.country,
            "position":  p.position,
            "price":     p.price,
        }

    @gl.public.view
    def get_leaderboard(self) -> list:
        """Return sorted leaderboard: [{owner, team_name, total_points}]."""
        board = []
        for owner, pts in self.leaderboard.items():
            if owner in self.fwc_teams:
                board.append({
                    "owner":       owner,
                    "username":    self.fwc_teams[owner].team_name,
                    "team_name":   self.fwc_teams[owner].team_name,
                    "total_points": pts,
                })
        board.sort(key=lambda x: x["total_points"], reverse=True)
        return board

    @gl.public.view
    def get_match_result(self, match_id: str) -> dict:
        """Return the settled result for a match."""
        if match_id not in self.match_results:
            raise gl.vm.UserError(f"Match {match_id} not yet settled.")
        r = self.match_results[match_id]
        return {
            "match_id":      r.match_id,
            "home_team":     r.home_team,
            "away_team":     r.away_team,
            "score":         f"{r.home_goals}–{r.away_goals}",
            "scorers":       r.scorers,
            "assisters":     r.assisters,
            "yellow_cards":  r.yellow_cards,
            "red_cards":     r.red_cards,
            "clean_sheets":  r.clean_sheet_teams,
            "bonus_top3":    r.bonus_top3,
            "is_knockout":   r.is_knockout,
            "is_final":      r.is_final,
        }

    @gl.public.view
    def get_gameweek(self) -> int:
        """Return the current gameweek number."""
        return self.current_gameweek

    @gl.public.view
    def get_prize_pool(self) -> int:
        """Return total prize pool in wei."""
        return self.prize_pool

    @gl.public.view
    def get_awards(self) -> dict:
        """Return resolved tournament award winners."""
        return {
            "golden_boot":  self.golden_boot_player,
            "golden_glove": self.golden_glove_player,
            "golden_ball":  self.golden_ball_player,
            "resolved":     self.awards_resolved,
        }

    # ══════════════════════════════════════════════════════════
    #  INTERNAL SCORING ENGINE — deterministic Python
    # ══════════════════════════════════════════════════════════

    def _score_all_teams(
        self,
        match_id: str,
        stats: dict,
        bonus_top3: list,
        is_knockout: bool,
        is_final: bool,
    ) -> None:
        """Compute FWC points for every player that appears in `stats`
        and distribute them to all FWC teams owning those players."""

        # Pre-compute per-player raw points from the match
        player_match_pts = {}  # player_name → int

        # ── Minutes played ──────────────────────────────────────
        minutes = stats.get("minutes_played", {})
        for name, mins in minutes.items():
            pts = player_match_pts.get(name, 0)
            if mins >= 60:
                pts += POINTS["played_ge60"]
            elif mins > 0:
                pts += POINTS["played_lt60"]
            player_match_pts[name] = pts

        # ── Goals scored ────────────────────────────────────────
        for entry in stats.get("scorers", []):
            name = self._extract_name(entry)
            pos  = self._player_position_by_name(name)
            pts  = player_match_pts.get(name, 0)
            pts += POINTS.get(f"goal_{pos.lower()}", POINTS["goal_fwd"])
            if is_final:
                pts += POINTS["final_extra"]
            elif is_knockout:
                pts += POINTS["knockout_extra"]
            player_match_pts[name] = pts

        # ── Assists ─────────────────────────────────────────────
        for entry in stats.get("assisters", []):
            name = self._extract_name(entry)
            pts  = player_match_pts.get(name, 0)
            pts += POINTS["assist"]
            if is_final:
                pts += POINTS["final_extra"]
            elif is_knockout:
                pts += POINTS["knockout_extra"]
            player_match_pts[name] = pts

        # ── Clean sheets ────────────────────────────────────────
        clean_teams = stats.get("clean_sheet_teams", [])
        for pid, player in self.players.items():
            if player.country in clean_teams:
                pts = player_match_pts.get(player.name, 0)
                if player.position in ("GK", "DEF"):
                    pts += POINTS["clean_sheet_gk_def"]
                elif player.position == "MID":
                    pts += POINTS["clean_sheet_mid"]
                player_match_pts[player.name] = pts

        # ── Goalkeeper saves ────────────────────────────────────
        for name, saves in stats.get("gk_saves", {}).items():
            pts = player_match_pts.get(name, 0)
            pts += (saves // 3) * POINTS["save_3"]
            player_match_pts[name] = pts

        # ── Goals conceded (GK/DEF penalty) ────────────────────
        # Any GK or DEF whose team was NOT in clean_sheet_teams gets -1
        # per 2 goals conceded by their team.
        home_goals = stats.get("home_goals", 0)
        away_goals = stats.get("away_goals", 0)
        for pid, player in self.players.items():
            if player.position not in ("GK", "DEF"):
                continue
            goals_against = 0
            # Determine how many goals the player's team conceded
            # Crude heuristic: match home_team/away_team to player.country
            r = self.match_results.get(match_id)
            if r:
                if player.country == r.home_team:
                    goals_against = away_goals
                elif player.country == r.away_team:
                    goals_against = home_goals
            if goals_against >= 2:
                pts = player_match_pts.get(player.name, 0)
                pts += (goals_against // 2) * POINTS["goals_conceded_2"]
                player_match_pts[player.name] = pts

        # ── Yellow cards ────────────────────────────────────────
        for entry in stats.get("yellow_cards", []):
            name = self._extract_name(entry)
            pts  = player_match_pts.get(name, 0)
            pts += POINTS["yellow_card"]
            player_match_pts[name] = pts

        # ── Red cards ───────────────────────────────────────────
        for entry in stats.get("red_cards", []):
            name = self._extract_name(entry)
            pts  = player_match_pts.get(name, 0)
            # Red card wipes the yellow (-1 was already applied); net is -3
            pts += POINTS["red_card"]
            player_match_pts[name] = pts

        # ── Own goals ───────────────────────────────────────────
        for entry in stats.get("own_goals", []):
            name = self._extract_name(entry)
            pts  = player_match_pts.get(name, 0)
            pts += POINTS["own_goal"]
            player_match_pts[name] = pts

        # ── Penalty misses ──────────────────────────────────────
        for entry in stats.get("penalty_misses", []):
            name = self._extract_name(entry)
            pts  = player_match_pts.get(name, 0)
            pts += POINTS["penalty_miss"]
            player_match_pts[name] = pts

        # ── Penalty saves ───────────────────────────────────────
        for entry in stats.get("penalty_saves", []):
            name = self._extract_name(entry)
            pts  = player_match_pts.get(name, 0)
            pts += POINTS["penalty_save"]
            player_match_pts[name] = pts

        # ── Defensive contributions ─────────────────────────────
        for name, contrib in stats.get("defensive_contributions", {}).items():
            pos = self._player_position_by_name(name)
            pts = player_match_pts.get(name, 0)
            if pos == "DEF" and contrib >= 10:
                pts += POINTS["defensive_contrib_def"]
            elif pos in ("MID", "FWD") and contrib >= 12:
                pts += POINTS["defensive_contrib_mid_fwd"]
            player_match_pts[name] = pts

        # ── Bonus points ────────────────────────────────────────
        bonus_awards = {
            0: POINTS["bonus_1st"],
            1: POINTS["bonus_2nd"],
            2: POINTS["bonus_3rd"],
        }
        for idx, name in enumerate(bonus_top3[:3]):
            pts = player_match_pts.get(name, 0)
            pts += bonus_awards.get(idx, 0)
            player_match_pts[name] = pts

        # ── Build name→player_id lookup ─────────────────────────
        name_to_id = {p.name: pid for pid, p in self.players.items()}

        # ── Distribute points to all FWC teams ──────────────────
        gw_str = str(self.current_gameweek)

        for owner, team in self.fwc_teams.items():
            gw_pts = 0

            # Determine multiplier modifiers active for this team this GW
            triple_captain = (team.chip_triple_captain_used == self.current_gameweek)
            bench_boost    = (team.chip_bench_boost_used    == self.current_gameweek)

            for pid in team.player_ids:
                player = self.players.get(pid)
                if not player:
                    continue
                raw_pts = player_match_pts.get(player.name, 0)

                # Captain/vice-captain multiplier
                if pid == team.captain_id:
                    if triple_captain:
                        raw_pts *= 3
                    else:
                        raw_pts *= 2
                elif pid == team.vice_captain_id and team.captain_id == "":
                    # Vice covers when captain has no points set
                    raw_pts *= 2

                gw_pts += raw_pts

            # Update team totals
            gw_map = dict(team.gameweek_points)
            gw_map[gw_str] = gw_pts
            team.gameweek_points = gw_map
            team.total_points += gw_pts

            # Add banked transfer at end of gameweek (auto-bank)
            if team.transfers_available < MAX_BANKED_XFERS:
                team.transfers_available += 1

            self.fwc_teams[owner] = team
            self.leaderboard[owner] = team.total_points

    # ══════════════════════════════════════════════════════════
    #  PRIVATE HELPERS  (deterministic — no gl.nondet calls)
    # ══════════════════════════════════════════════════════════

    def _require_commissioner(self) -> None:
        if str(gl.message.sender) != self.commissioner:
            raise gl.vm.UserError("Only the commissioner can call this method.")

    def _get_team(self, owner: str) -> FWCTeam:
        if owner not in self.fwc_teams:
            raise gl.vm.UserError("You do not have a team. Call create_team first.")
        return self.fwc_teams[owner]

    def _get_player(self, player_id: str) -> Player:
        if player_id not in self.players:
            raise gl.vm.UserError(f"Player '{player_id}' not found in registry.")
        return self.players[player_id]

    def _extract_name(self, entry: str) -> str:
        """LLM returns 'PlayerName (Team)' — extract just the name."""
        return entry.split("(")[0].strip() if "(" in entry else entry.strip()

    def _player_position_by_name(self, name: str) -> str:
        """Find a player's position from the registry by name.
        Falls back to 'FWD' if not found (least generous default)."""
        for pid, player in self.players.items():
            if player.name.lower() == name.lower():
                return player.position
        return "FWD"
