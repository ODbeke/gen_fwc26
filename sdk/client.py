from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class FWCClient:
    """
    High-level Python client for the FWC Intelligent Contract.

    The current implementation uses the GenLayer CLI, which is available in
    this workspace and supports Studionet RPC calls. If a Python GenLayer SDK
    is installed later, this class can keep the same public surface.
    """

    contract_address: str
    private_key: str
    rpc_url: str = "https://studio.genlayer.com/api"

    def _run(self, args: list[str]) -> str:
        try:
            result = subprocess.run(
                ["genlayer", *args],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as exc:
            message = exc.stderr.strip() or exc.stdout.strip()
            raise RuntimeError(f"GenLayer CLI command failed: {message}") from exc

    def _write(self, method: str, args: list[Any] | None = None) -> str:
        cli_args = ["write", "--rpc", self.rpc_url, self.contract_address, method]
        if args:
            cli_args.extend(["--args", *[self._encode_arg(arg) for arg in args]])
        return self._run(cli_args)

    def _call(self, method: str, args: list[Any] | None = None) -> Any:
        cli_args = ["call", "--rpc", self.rpc_url, self.contract_address, method]
        if args:
            cli_args.extend(["--args", *[self._encode_arg(arg) for arg in args]])
        output = self._run(cli_args)
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return output

    @staticmethod
    def _encode_arg(arg: Any) -> str:
        if isinstance(arg, bool):
            return "true" if arg else "false"
        if isinstance(arg, (dict, list)):
            return json.dumps(arg)
        return str(arg)

    def import_account(self, name: str = "fwc-commissioner") -> str:
        """Import the configured private key into GenLayer CLI account storage."""
        return self._run([
            "account",
            "import",
            "--name",
            name,
            "--private-key",
            self.private_key,
            "--overwrite",
        ])

    @classmethod
    def deploy_contract(cls, contract_path: str | Path, private_key: str, rpc_url: str) -> str:
        """Deploy the FWC contract and return the CLI output containing the address."""
        temp = cls(contract_address="", private_key=private_key, rpc_url=rpc_url)
        temp.import_account()
        return temp._run(["deploy", "--rpc", rpc_url, "--contract", str(contract_path)])

    def wait_for_receipt(self, tx_hash: str, status: str = "FINALIZED") -> dict | str:
        """Wait for a transaction receipt from GenLayer."""
        output = self._run(["receipt", "--rpc", self.rpc_url, "--status", status, tx_hash])
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return output

    def activate_tournament(self) -> str:
        """Open registration and play."""
        return self._write("activate_tournament")

    def advance_gameweek(self) -> str:
        """Advance the contract to the next gameweek."""
        return self._write("advance_gameweek")

    def register_player(self, player_id: str, name: str, country: str, position: str, price: int) -> str:
        """Register a player in the contract pool."""
        return self._write("register_player", [player_id, name, country, position, price])

    def assign_gameweek_match(self, gameweek: int, match_id: str) -> str:
        """Assign a match id to a gameweek."""
        return self._write("assign_gameweek_match", [gameweek, match_id])

    def settle_match(self, match_id: str, home_team: str, away_team: str, is_knockout: bool, is_final: bool) -> str:
        """Settle a match through the contract's AI consensus flow."""
        return self._write("settle_match", [match_id, home_team, away_team, is_knockout, is_final])

    def resolve_tournament_awards(self) -> str:
        """Resolve end-of-tournament FIFA award winners."""
        return self._write("resolve_tournament_awards")

    def create_team(self, team_name: str) -> str:
        """Create a manager team. Entry is free in this build."""
        return self._write("create_team", [team_name])

    def pick_player(self, player_id: str) -> str:
        """Add a player to the caller's squad."""
        return self._write("pick_player", [player_id])

    def set_captain(self, player_id: str, vice: bool = False) -> str:
        """Set a captain or vice captain."""
        return self._write("set_captain", [player_id, vice])

    def make_transfer(self, out_id: str, in_id: str) -> str:
        """Swap one squad player for another."""
        return self._write("make_transfer", [out_id, in_id])

    def play_chip(self, chip: str, hero_player_id: str = "") -> str:
        """Activate a chip."""
        return self._write("play_chip", [chip, hero_player_id])

    def bank_transfer(self) -> str:
        """Bank an unused transfer."""
        return self._write("bank_transfer")

    def get_team(self, owner: str) -> dict:
        """Read a manager team."""
        return self._call("get_team", [owner])

    def get_player(self, player_id: str) -> dict:
        """Read player metadata."""
        return self._call("get_player", [player_id])

    def get_leaderboard(self) -> list[dict]:
        """Read the sorted leaderboard."""
        return self._call("get_leaderboard")

    def get_match_result(self, match_id: str) -> dict:
        """Read a settled match result."""
        return self._call("get_match_result", [match_id])

    def get_gameweek(self) -> int:
        """Read the current gameweek."""
        return int(self._call("get_gameweek"))

    def get_prize_pool(self) -> int:
        """Read the prize pool in wei."""
        return int(self._call("get_prize_pool"))

    def get_prize_pool_gen(self) -> float:
        """Read the prize pool in GEN."""
        return self.get_prize_pool() / 10**18

    def get_awards(self) -> dict:
        """Read FIFA award resolution state."""
        return self._call("get_awards")
