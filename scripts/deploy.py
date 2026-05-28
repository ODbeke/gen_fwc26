from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from sdk.client import FWCClient


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contracts" / "fantasy_world_cup.py"


def main() -> None:
    load_dotenv(ROOT / ".env")
    rpc_url = os.getenv("GENLAYER_RPC_URL", "https://studio.genlayer.com/api")
    private_key = os.environ["COMMISSIONER_PRIVATE_KEY"]
    print(f"Deploying {CONTRACT} to {rpc_url}")
    output = FWCClient.deploy_contract(CONTRACT, private_key=private_key, rpc_url=rpc_url)
    print(output)


if __name__ == "__main__":
    main()
