from __future__ import annotations

import os
import json
from pathlib import Path
from dotenv import load_dotenv

from sdk.client import FWCClient


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "data" / "fixtures_2026.json"


def load_fixtures() -> list[dict]:
    return json.loads(FIXTURE_PATH.read_text())


FIXTURES = [(fixture["gameweek"], fixture["match_id"]) for fixture in load_fixtures()]


def main() -> None:
    load_dotenv()
    client = FWCClient(
        contract_address=os.environ["FWC_CONTRACT_ADDRESS"],
        private_key=os.environ["COMMISSIONER_PRIVATE_KEY"],
        rpc_url=os.getenv("GENLAYER_RPC_URL", "https://studio.genlayer.com/api"),
    )
    for gw, match_id in FIXTURES:
        try:
            print(f"GW{gw} {match_id}: {client.assign_gameweek_match(gw, match_id)}")
        except RuntimeError as exc:
            print(f"failed {match_id}: {exc}")


if __name__ == "__main__":
    main()
