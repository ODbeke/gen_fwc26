import { useEffect, useMemo, useState } from "react";
import { Send, UserRound } from "lucide-react";
import { BudgetBar } from "../components/BudgetBar";
import { ChipCard } from "../components/ChipCard";
import { PitchView } from "../components/PitchView";
import { TransferPanel } from "../components/TransferPanel";
import { useMyTeam } from "../hooks/useMyTeam";
import { usePlayers } from "../hooks/usePlayers";
import { formatPrice, STARTING_BUDGET, type Player } from "../lib/constants";
import { callWrite } from "../lib/genlayer";
import { useSquadStore } from "../store/squadStore";
import { useUiStore } from "../store/uiStore";

const formations = ["3-4-3", "4-3-3", "4-4-2", "3-5-2", "5-3-2", "5-4-1", "4-2-3-1"];

interface SquadProps {
  address: string;
}

export function Squad({ address }: SquadProps) {
  const { data: players = [], isLoading } = usePlayers();
  const { data: onchainTeam, isLoading: isTeamLoading, refetch: refetchTeam } = useMyTeam(address);
  const { selectedIds, captainId, viceCaptainId, formation, addPlayer, removePlayer, setCaptain, setViceCaptain, setFormation, hydrateSquad, clearSquad } = useSquadStore();
  const { pickerPosition, openPicker, closePicker, notify } = useUiStore();
  const [username, setUsername] = useState("");
  const squad = useMemo(() => selectedIds.map((id) => players.find((player) => player.player_id === id)).filter(Boolean) as Player[], [players, selectedIds]);
  const spent = squad.reduce((sum, player) => sum + player.price, 0);
  const remaining = STARTING_BUDGET - spent;
  const hasTeam = Boolean(onchainTeam);

  useEffect(() => {
    if (!address) {
      clearSquad();
      setUsername("");
      return;
    }
    if (onchainTeam) {
      hydrateSquad(onchainTeam.player_ids, onchainTeam.captain_id, onchainTeam.vice_captain_id);
      setUsername(onchainTeam.username ?? onchainTeam.team_name);
    }
  }, [address, clearSquad, hydrateSquad, onchainTeam]);

  const confirmSquad = async () => {
    if (!address) {
      notify("Connect wallet to save your FWC team.");
      return;
    }
    if (!hasTeam && username.trim().length === 0) {
      notify("Choose a username before saving.");
      return;
    }
    notify(hasTeam ? "Saving squad to your wallet profile..." : "Creating your wallet-bound FWC profile...");
    try {
      if (!hasTeam) await callWrite("create_team", [username.trim()]);
      for (const player of squad) await callWrite("pick_player", [player.player_id]);
      if (captainId) await callWrite("set_captain", [captainId, false]);
      if (viceCaptainId) await callWrite("set_captain", [viceCaptainId, true]);
      await refetchTeam();
      notify("Saved on-chain. This wallet will resume here next time.");
    } catch (error) {
      notify(error instanceof Error ? error.message : "Could not save team.");
    }
  };

  const updateUsername = async () => {
    if (!address || !hasTeam || username.trim().length === 0) return;
    notify("Updating username on-chain...");
    try {
      await callWrite("update_username", [username.trim()]);
      await refetchTeam();
      notify("Username updated.");
    } catch (error) {
      notify(error instanceof Error ? error.message : "Could not update username.");
    }
  };

  return (
    <div className="grid gap-5 p-4 xl:grid-cols-[minmax(0,1.5fr)_minmax(360px,0.8fr)]">
      <section>
        <div className="mb-3 flex flex-wrap items-center gap-2">
          {formations.map((item) => (
            <button key={item} type="button" onClick={() => setFormation(item)} className={`focus-ring rounded px-3 py-2 text-sm ${formation === item ? "bg-gold text-ink" : "bg-panel text-slate-300"}`}>
              {item}
            </button>
          ))}
        </div>
        {isLoading ? (
          <div className="rounded border border-line bg-panel p-10 text-center">Loading player pool...</div>
        ) : (
          <PitchView
            formation={formation}
            players={squad}
            captainId={captainId}
            viceCaptainId={viceCaptainId}
            onSlotClick={openPicker}
            onPlayerClick={(player) => (captainId === player.player_id ? setViceCaptain(player.player_id) : setCaptain(player.player_id))}
            onRemove={removePlayer}
          />
        )}
      </section>
      <aside className="space-y-4">
        <div className="rounded border border-line bg-panel p-4">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
            <UserRound className="h-4 w-4 text-gold" aria-hidden="true" />
            Manager Profile
          </div>
          {address ? (
            <>
              <label className="text-xs text-slate-400" htmlFor="username">Username</label>
              <div className="mt-1 flex gap-2">
                <input id="username" value={username} onChange={(event) => setUsername(event.target.value)} disabled={isTeamLoading} className="min-w-0 flex-1 rounded border border-line bg-ink px-3 py-2 text-sm outline-none focus:border-gold" placeholder="Choose username" />
                {hasTeam ? <button type="button" onClick={updateUsername} className="focus-ring rounded bg-ink px-3 py-2 text-xs font-semibold">Save</button> : null}
              </div>
              <div className="mt-2 text-xs text-slate-400">{hasTeam ? "Loaded from your connected wallet." : "This creates your on-chain FWC identity."}</div>
            </>
          ) : (
            <div className="text-sm text-slate-400">Connect wallet to create or resume your on-chain team.</div>
          )}
        </div>
        <BudgetBar spent={spent} remaining={remaining} />
        <div className="rounded border border-line bg-panel p-4">
          <div className="flex justify-between text-sm">
            <span>Squad</span>
            <span className="font-semibold">{squad.length}/15</span>
          </div>
          <div className="mt-3 text-sm text-slate-300">{onchainTeam?.transfers_available ?? 1} free transfer remaining | Next cost: -4 pts</div>
          <div className="mt-2 text-xs text-slate-400">Budget after next pick: {formatPrice(remaining)}</div>
        </div>
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
          <ChipCard name="Wildcard" description="Rebuild freely and reset banked transfers to three." />
          <ChipCard name="Bench Boost" description="All 15 squad players score in this gameweek." />
          <ChipCard name="Triple Captain" description="Captain points are tripled for one gameweek." />
          <ChipCard name="World Cup Hero" description="Pick one player for a +10 award bonus." />
        </div>
        <div className="rounded border border-line bg-panel p-4">
          <div className="text-sm text-slate-300">GW points | Total points</div>
          <div className="mt-2 text-3xl font-black text-gold">0 | {onchainTeam?.total_points ?? 0}</div>
        </div>
        <button type="button" onClick={confirmSquad} className="focus-ring flex w-full items-center justify-center gap-2 rounded bg-gold px-4 py-3 font-bold text-ink">
          <Send className="h-4 w-4" aria-hidden="true" />
          Confirm squad
        </button>
      </aside>
      {pickerPosition && <TransferPanel players={players} squad={squad} position={pickerPosition} onAdd={(player) => { addPlayer(player); closePicker(); }} onClose={closePicker} />}
    </div>
  );
}
