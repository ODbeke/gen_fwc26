import type { Player, Position } from "../lib/constants";
import { PlayerCard } from "./PlayerCard";

const formationRows: Record<string, number[]> = {
  "3-4-3": [1, 3, 4, 3],
  "4-3-3": [1, 4, 3, 3],
  "4-4-2": [1, 4, 4, 2],
  "3-5-2": [1, 3, 5, 2],
  "5-3-2": [1, 5, 3, 2],
  "5-4-1": [1, 5, 4, 1],
  "4-2-3-1": [1, 4, 2, 3, 1],
};

interface PitchViewProps {
  formation: string;
  players: Player[];
  captainId: string;
  viceCaptainId: string;
  onSlotClick: (position: string) => void;
  onPlayerClick: (player: Player) => void;
  onRemove: (playerId: string) => void;
}

function preferredPosition(row: number, rows: number): Position {
  if (row === 0) return "GK";
  if (row === 1) return "DEF";
  if (row === rows - 1) return "FWD";
  return "MID";
}

export function PitchView({ formation, players, captainId, viceCaptainId, onSlotClick, onPlayerClick, onRemove }: PitchViewProps) {
  const rows = formationRows[formation] ?? formationRows["4-2-3-1"];
  const positionQueues: Record<Position, Player[]> = {
    GK: players.filter((player) => player.position === "GK"),
    DEF: players.filter((player) => player.position === "DEF"),
    MID: players.filter((player) => player.position === "MID"),
    FWD: players.filter((player) => player.position === "FWD"),
  };
  const assignedIds = new Set<string>();
  const pitchRows = rows.map((count, rowIndex) => {
    const position = preferredPosition(rowIndex, rows.length);
    const rowPlayers = Array.from({ length: count }, () => {
      const player = positionQueues[position].shift();
      if (player) assignedIds.add(player.player_id);
      return player;
    });

    return { count, position, rowPlayers };
  });
  const bench = players.filter((player) => !assignedIds.has(player.player_id)).slice(0, 4);

  return (
    <div className="rounded border border-line bg-[#0c422b] p-3 shadow-2xl">
      <div className="relative overflow-hidden rounded border-2 border-white/70 bg-[linear-gradient(90deg,#12643e_0%,#157649_50%,#12643e_100%)] px-3 py-5">
        <svg className="pointer-events-none absolute inset-0 h-full w-full opacity-70" viewBox="0 0 100 140" preserveAspectRatio="none" aria-hidden="true">
          <rect x="4" y="4" width="92" height="132" fill="none" stroke="white" strokeWidth="0.8" />
          <line x1="4" y1="70" x2="96" y2="70" stroke="white" strokeWidth="0.8" />
          <circle cx="50" cy="70" r="12" fill="none" stroke="white" strokeWidth="0.8" />
          <rect x="28" y="4" width="44" height="18" fill="none" stroke="white" strokeWidth="0.8" />
          <rect x="28" y="118" width="44" height="18" fill="none" stroke="white" strokeWidth="0.8" />
        </svg>
        <div className="relative z-10 flex min-h-[620px] flex-col justify-between gap-4">
          {pitchRows.map(({ count, position, rowPlayers }, rowIndex) => {
            return (
              <div key={`${formation}-${rowIndex}`} className="grid gap-3" style={{ gridTemplateColumns: `repeat(${count}, minmax(0, 1fr))` }}>
                {Array.from({ length: count }).map((_, index) => {
                  const player = rowPlayers[index];
                  return player ? (
                    <PlayerCard
                      key={player.player_id}
                      player={player}
                      pitchToken
                      captain={player.player_id === captainId}
                      vice={player.player_id === viceCaptainId}
                      onClick={() => onPlayerClick(player)}
                      onRemove={() => onRemove(player.player_id)}
                    />
                  ) : (
                    <button
                      key={`${rowIndex}-${index}`}
                      type="button"
                      onClick={() => onSlotClick(position)}
                      className="focus-ring min-h-[92px] rounded border border-dashed border-white/50 bg-white/10 text-sm font-semibold text-white hover:border-gold"
                    >
                      Add {position}
                    </button>
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>
      <div className="mt-3 grid grid-cols-2 gap-3 md:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => {
          const player = bench[index];
          return player ? (
            <PlayerCard key={player.player_id} compact player={player} onClick={() => onPlayerClick(player)} onRemove={() => onRemove(player.player_id)} />
          ) : (
            <button
              key={index}
              type="button"
              onClick={() => onSlotClick(index === 0 ? "GK" : "MID")}
              className="focus-ring min-h-[70px] rounded border border-dashed border-line bg-panel text-sm text-slate-300"
            >
              Bench
            </button>
          );
        })}
      </div>
    </div>
  );
}
