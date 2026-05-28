# Fantasy World Cup (FWC)

FWC is a free-entry 2026 World Cup fantasy game built for GenLayer Intelligent Contracts. Managers build 15-player squads, pick captains, play chips, and earn points from live match settlement. GenLayer validators fetch web data and use AI consensus for the parts ordinary smart contracts cannot handle.

## Network

- RPC: `https://studio.genlayer.com/api`
- Chain ID: `61999`
- Currency: `GEN`
- Explorer: `https://explorer-studio.genlayer.com`
- Deployed contract: pending deployment

## Architecture

```text
Frontend -> SDK/scripts -> FantasyWorldCup contract
                         -> GenLayer validators
                         -> strict_eq facts + prompt_comparative bonus
                         -> match results -> leaderboard
```

## Setup

```bash
python3 -m pip install -e ".[test,scripts]"
cd frontend && npm install
```

Create `.env` from `.env.example` and set `COMMISSIONER_PRIVATE_KEY` plus the deployed `FWC_CONTRACT_ADDRESS`.

## Contract

The Intelligent Contract is at `contracts/fantasy_world_cup.py`. Entry is free in this build, so `ENTRY_FEE_WEI = 0` and `create_team` does not add to the prize pool.

Run local tests:

```bash
python3 -m pytest tests
```

Run GenLayer lint after installing the official linter:

```bash
git clone https://github.com/genlayerlabs/genvm-linter /tmp/genvm-linter
# follow that repository's install instructions, then:
genvm-lint contracts/fantasy_world_cup.py
```

## Deploy

```bash
genlayer account import --name fwc-commissioner --private-key "$COMMISSIONER_PRIVATE_KEY" --overwrite
genlayer deploy --rpc https://studio.genlayer.com/api --contract contracts/fantasy_world_cup.py
```

Or:

```bash
python3 scripts/deploy.py
```

If deployment returns an error, fix the surfaced contract or account issue, then rerun deploy. The project currently uses the GenLayer CLI because it is installed locally and exposes Studionet deployment commands.

## Commissioner Workflow

1. Deploy contract.
2. Set `FWC_CONTRACT_ADDRESS`.
3. Call `activate_tournament`.
4. Run `python3 scripts/seed_players.py`.
5. Run `python3 scripts/seed_gameweek_matches.py`.
6. For each GW, run `python3 scripts/settle_gameweek.py --gw N`.
7. Resolve awards after the final.

## Manager Workflow

Connect wallet, create a team for free, build a 15-player squad, set captain and vice, activate chips, then watch validator consensus settle matches and update your points.

## Consensus In Plain English

FWC asks validators to agree on objective facts like score, scorers, cards, saves, and clean sheets with `strict_eq`. For the more subjective top-three bonus performers, validators compare answers with a natural-language equivalence rule: at least two of the three names must overlap.

## Chips

- Wildcard: reset transfers to three for the current gameweek.
- Bench Boost: all bench players score.
- Triple Captain: captain scores 3x.
- Free Hit: one-week squad swap handled off-chain in v1.
- World Cup Hero: +10 if the selected player wins Golden Boot, Golden Glove, or Golden Ball.

## Points System

GK/DEF/MID/FWD all get appearance, card, own-goal, penalty-miss, bonus, knockout, final, and shootout points. Goals are GK +10, DEF +6, MID +5, FWD +4. Assists are +3. Clean sheets are GK/DEF +4, MID +1. GK saves are +1 per three saves. Defensive contribution bonuses are DEF +2 for 10+ CBIT and MID/FWD +2 for 12+ CBIRT.

## Data Status

`data/players_2026.json` contains exact prompt-specified key prices and pending markers for squads that are not final. Before mainnet or public launch, update this file from official FIFA 2026 squad lists.

## Frontend

```bash
cd frontend
npm run dev
```

Build:

```bash
cd frontend
npm run build
```

## Contributing

Keep contract changes minimal, test every public method, and make GenLayer-specific behavior visible in the UI. Any lint-driven contract change should include a `# LINT FIX:` comment.
