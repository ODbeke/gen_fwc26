from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv

from sdk.client import FWCClient
from scripts.seed_gameweek_matches import load_fixtures


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gw", type=int, required=True)
    args = parser.parse_args()
    load_dotenv()
    client = FWCClient(
        contract_address=os.environ["FWC_CONTRACT_ADDRESS"],
        private_key=os.environ["COMMISSIONER_PRIVATE_KEY"],
        rpc_url=os.getenv("GENLAYER_RPC_URL", "https://studio.genlayer.com/api"),
    )
    matches = [fixture for fixture in load_fixtures() if fixture["gameweek"] == args.gw]
    for fixture in matches:
        match_id = fixture["match_id"]
        home = fixture["home"]
        away = fixture["away"]
        is_final = fixture["stage"] == "Final"
        is_knockout = fixture["stage"] != "First Stage"
        print(f"settling {match_id}")
        tx = client.settle_match(match_id, home, away, is_knockout, is_final)
        print(tx)
    print("advancing gameweek")
    print(client.advance_gameweek())


if __name__ == "__main__":
    main()
