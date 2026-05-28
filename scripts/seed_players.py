from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from sdk.client import FWCClient


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    load_dotenv(ROOT / ".env")
    client = FWCClient(
        contract_address=os.environ["FWC_CONTRACT_ADDRESS"],
        private_key=os.environ["COMMISSIONER_PRIVATE_KEY"],
        rpc_url=os.getenv("GENLAYER_RPC_URL", "https://studio.genlayer.com/api"),
    )
    players = json.loads((ROOT / "data" / "players_2026.json").read_text())
    registered = skipped = failed = 0
    for player in players:
        try:
            tx = client.register_player(
                player["player_id"],
                player["name"],
                player["country"],
                player["position"],
                int(player["price"]),
            )
            registered += 1
            print(f"registered {player['player_id']}: {tx}")
        except RuntimeError as exc:
            if "already registered" in str(exc):
                skipped += 1
                print(f"skipped {player['player_id']}: already registered")
            else:
                failed += 1
                print(f"failed {player['player_id']}: {exc}")
    print(f"Summary: {registered} registered, {skipped} skipped, {failed} failed")


if __name__ == "__main__":
    main()
