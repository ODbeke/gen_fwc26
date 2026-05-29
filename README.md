# Fantasy World Cup (FWC)

![Fantasy World Cup 2026 mascots](frontend/public/world-cup-mascots.jpeg)

FWC is a free-entry 2026 World Cup fantasy game built for GenLayer Intelligent Contracts. Managers build 15-player squads, pick captains, play chips, and earn points from live match settlement. GenLayer validators fetch web data and use AI consensus for the parts ordinary smart contracts cannot handle.

## Network

- RPC: `https://studio.genlayer.com/api`
- Chain ID: `61999`
- Currency: `GEN`
- Explorer: `https://explorer-studio.genlayer.com`
- Deployed contract: `0x3C0A23588889af044409d37D3dF82A8E989d02bE`

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

## How FWC Uses The GenLayer Stack

FWC is not just a fantasy football frontend with a contract attached. The core idea is to use GenLayer where normal smart contracts are weakest: reading real-world match information, interpreting messy public web data, and reaching a shared result that can safely update on-chain state.

In a normal EVM contract, the World Cup scoring flow would require a trusted oracle or an admin manually entering match facts. In FWC, the Intelligent Contract can ask validators to fetch the match page, extract football stats, compare their answers, and only then write the settled result and fantasy points.

### Optimistic Democracy

Optimistic Democracy is the settlement model that lets GenLayer validators execute Intelligent Contract logic involving web data and AI reasoning without every participant needing to redo all work forever. For FWC, that means the commissioner can call `settle_match`, validators independently run the contract's nondeterministic data-gathering steps, and the network finalizes the result if the validators converge and no successful challenge overturns it.

In product terms, this is what makes the game feel like an autonomous fantasy protocol instead of a spreadsheet run by the game owner. The commissioner triggers a gameweek settlement, but the actual scoring evidence is produced and checked by GenLayer validators.

FWC uses this for:

- Fetching FIFA match pages during match settlement.
- Extracting objective match stats from those pages.
- Agreeing on the settled match result.
- Updating every manager's team points and leaderboard from that agreed result.
- Resolving tournament awards after the final.

### Equivalence Principle

The Equivalence Principle is how FWC tells validators what it means for their answers to be “the same” when AI or web extraction is involved.

FWC uses two styles:

- `strict_eq` for objective facts that should match exactly.
- `prompt_comparative` for subjective or fuzzy football judgments where equivalent answers may not be byte-for-byte identical.

For match settlement, `strict_eq` is used to agree on structured facts such as:

- final score,
- scorers,
- assisters,
- yellow and red cards,
- goalkeeper saves,
- clean sheet teams,
- minutes played,
- penalties,
- own goals,
- defensive contributions.

For bonus points, FWC uses a comparative equivalence rule. Validators are asked to identify the top three performers from the match. Because one validator may write “Kylian Mbappe” and another may include slightly different formatting or ordering, the contract uses `prompt_comparative` with a football-specific rule: the answers are treated as equivalent when at least two of the three selected names overlap.

That lets FWC support the type of fantasy bonus system users expect from FPL/FIFA Fantasy while still keeping the result validator-mediated rather than manually assigned by the app owner.

### Why This Matters For FWC

The GenLayer stack gives FWC three properties that are difficult to combine in a normal fantasy game:

- Real-world awareness: the contract can use public football data as part of execution.
- Shared settlement: match outcomes are not controlled only by the frontend or by a private backend.
- Transparent game state: teams, usernames, squads, points, chips, and leaderboard state live on-chain.

So the build is best described as an on-chain fantasy World Cup game where GenLayer validators act as the match-stat settlement layer. The frontend is the FPL/Sorare-style user experience; the Intelligent Contract is the game engine; Optimistic Democracy and the Equivalence Principle are the trust and consensus layer that turn real-world World Cup data into on-chain fantasy points.

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
