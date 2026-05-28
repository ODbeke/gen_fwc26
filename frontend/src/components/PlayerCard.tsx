import { Crown, ShieldCheck, X } from "lucide-react";
import { flagFor, formatPrice, POSITION_COLORS, type Player } from "../lib/constants";

interface PlayerCardProps {
  player: Player;
  compact?: boolean;
  pitchToken?: boolean;
  captain?: boolean;
  vice?: boolean;
  onRemove?: () => void;
  onClick?: () => void;
}

function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

export function PlayerCard({ player, compact = false, pitchToken = false, captain, vice, onRemove, onClick }: PlayerCardProps) {
  if (pitchToken) {
    return (
      <div className="relative flex min-h-[92px] flex-col items-center justify-center">
        <button
          type="button"
          onClick={onClick}
          className="focus-ring group relative grid h-[76px] w-[76px] place-items-center rounded-full border-2 border-white/70 bg-slate-950/80 text-center shadow-xl hover:border-gold"
          aria-label={`${player.name}, ${player.position}, ${formatPrice(player.price)}`}
        >
          <span className="absolute -top-2 rounded-full px-2 py-0.5 text-[10px] font-black text-ink" style={{ backgroundColor: POSITION_COLORS[player.position] }}>
            {player.position}
          </span>
          <span className="text-lg font-black text-white">{initials(player.name)}</span>
          <span className="absolute bottom-2 text-[10px] text-slate-300">{formatPrice(player.price)}</span>
          {captain && <span className="absolute -left-2 -top-2 grid h-6 w-6 place-items-center rounded-full bg-gold text-[11px] font-black text-ink">C</span>}
          {vice && <span className="absolute -left-2 -top-2 grid h-6 w-6 place-items-center rounded-full bg-sky-300 text-[11px] font-black text-ink">V</span>}
          {captain && <Crown className="absolute -right-1 bottom-1 h-4 w-4 text-gold" aria-hidden="true" />}
          {vice && <ShieldCheck className="absolute -right-1 bottom-1 h-4 w-4 text-sky-300" aria-hidden="true" />}
        </button>
        <div className="mt-2 max-w-[130px] truncate rounded-full bg-slate-950/75 px-3 py-1 text-center text-xs font-semibold text-white shadow">
          {flagFor(player.country)} {player.name}
        </div>
        {onRemove && (
          <button
            type="button"
            onClick={onRemove}
            className="focus-ring absolute right-[calc(50%-48px)] top-0 grid h-6 w-6 place-items-center rounded-full bg-red-500 text-white"
            aria-label={`Remove ${player.name}`}
          >
            <X className="h-3 w-3" aria-hidden="true" />
          </button>
        )}
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={`focus-ring relative w-full rounded border border-white/15 bg-slate-950/70 p-2 text-left shadow-lg hover:border-gold ${compact ? "min-h-[70px]" : "min-h-[92px]"}`}
      aria-label={`${player.name}, ${player.position}, ${formatPrice(player.price)}`}
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="text-xs text-slate-300">{flagFor(player.country)} {player.country}</div>
          <div className="mt-1 line-clamp-2 text-sm font-semibold">{player.name}</div>
        </div>
        <span className="rounded px-2 py-1 text-[11px] font-bold text-ink" style={{ backgroundColor: POSITION_COLORS[player.position] }}>
          {player.position}
        </span>
      </div>
      <div className="mt-2 flex items-center justify-between text-xs text-slate-300">
        <span>{formatPrice(player.price)}</span>
        <span>{Math.max(2, Math.round(player.price / 18))} pts</span>
      </div>
      {captain && <span className="absolute -left-2 -top-2 grid h-6 w-6 place-items-center rounded-full bg-gold text-[11px] font-black text-ink">C</span>}
      {vice && <span className="absolute -left-2 -top-2 grid h-6 w-6 place-items-center rounded-full bg-sky-300 text-[11px] font-black text-ink">V</span>}
      {captain && <Crown className="absolute bottom-2 right-2 h-4 w-4 text-gold" aria-hidden="true" />}
      {vice && <ShieldCheck className="absolute bottom-2 right-2 h-4 w-4 text-sky-300" aria-hidden="true" />}
      {onRemove && (
        <span
          role="button"
          tabIndex={0}
          onClick={(event) => {
            event.stopPropagation();
            onRemove();
          }}
          className="absolute -right-2 -top-2 grid h-6 w-6 place-items-center rounded-full bg-red-500 text-white"
          aria-label={`Remove ${player.name}`}
        >
          <X className="h-3 w-3" aria-hidden="true" />
        </span>
      )}
    </button>
  );
}
