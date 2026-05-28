import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import { flagFor, formatPrice, MAX_PER_COUNTRY, STARTING_BUDGET, type Player, type Position } from "../lib/constants";

interface TransferPanelProps {
  players: Player[];
  squad: Player[];
  position: string | null;
  onAdd: (player: Player) => void;
  onClose: () => void;
}

export function TransferPanel({ players, squad, position, onAdd, onClose }: TransferPanelProps) {
  const [query, setQuery] = useState("");
  const [country, setCountry] = useState("");
  const [sort, setSort] = useState("price");
  const spent = squad.reduce((sum, player) => sum + player.price, 0);
  const remaining = STARTING_BUDGET - spent;
  const countries = Array.from(new Set(players.map((player) => player.country))).sort();

  const filtered = useMemo(() => {
    return players
      .filter((player) => !position || player.position === position)
      .filter((player) => !country || player.country === country)
      .filter((player) => player.name.toLowerCase().includes(query.toLowerCase()))
      .sort((a, b) => {
        if (sort === "name") return a.name.localeCompare(b.name);
        if (sort === "projected") return b.price - a.price;
        return b.price - a.price;
      });
  }, [country, players, position, query, sort]);

  const countryCount = (player: Player) => squad.filter((item) => item.country === player.country).length;
  const alreadySelected = (player: Player) => squad.some((item) => item.player_id === player.player_id);
  const disabledReason = (player: Player) => {
    if (alreadySelected(player)) return "Selected";
    if (player.price > remaining) return "Budget";
    if (countryCount(player) >= MAX_PER_COUNTRY) return "Country";
    return "";
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 p-4">
      <div className="mx-auto max-h-[92vh] max-w-4xl overflow-hidden rounded border border-line bg-ink shadow-2xl">
        <div className="flex items-center justify-between border-b border-line p-4">
          <h2 className="text-lg font-semibold">Player Market</h2>
          <button type="button" onClick={onClose} className="focus-ring rounded px-3 py-2 text-sm hover:bg-panel">Close</button>
        </div>
        <div className="grid gap-3 border-b border-line p-4 md:grid-cols-4">
          <label className="flex items-center gap-2 rounded border border-line bg-panel px-3 py-2 md:col-span-2">
            <Search className="h-4 w-4 text-slate-400" aria-hidden="true" />
            <input value={query} onChange={(event) => setQuery(event.target.value)} className="w-full bg-transparent outline-none" placeholder="Search player" aria-label="Search player" />
          </label>
          <select value={country} onChange={(event) => setCountry(event.target.value)} className="rounded border border-line bg-panel px-3 py-2" aria-label="Country filter">
            <option value="">All countries</option>
            {countries.map((item) => <option key={item}>{item}</option>)}
          </select>
          <select value={sort} onChange={(event) => setSort(event.target.value)} className="rounded border border-line bg-panel px-3 py-2" aria-label="Sort players">
            <option value="price">Price desc</option>
            <option value="projected">Projected pts desc</option>
            <option value="name">Name asc</option>
          </select>
        </div>
        <div className="max-h-[62vh] overflow-y-auto">
          {filtered.map((player) => {
            const reason = disabledReason(player);
            return (
              <div key={player.player_id} className="grid grid-cols-[1fr_auto] items-center gap-3 border-b border-line p-3 text-sm md:grid-cols-[80px_1fr_80px_80px_110px]">
                <div>{flagFor(player.country)} {player.country.slice(0, 3).toUpperCase()}</div>
                <div>
                  <div className="font-semibold">{player.name}</div>
                  <div className="text-xs text-slate-400">{player.pending ? "Pending squad estimate" : "Projected roster"}</div>
                </div>
                <div>{player.position as Position}</div>
                <div>{formatPrice(player.price)}</div>
                <button
                  type="button"
                  disabled={Boolean(reason)}
                  onClick={() => onAdd(player)}
                  className="focus-ring rounded bg-gold px-3 py-2 text-xs font-bold text-ink disabled:bg-slate-700 disabled:text-slate-400"
                >
                  {reason || `Add (${formatPrice(remaining - player.price)})`}
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
