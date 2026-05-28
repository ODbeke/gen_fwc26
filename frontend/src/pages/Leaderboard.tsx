import { useMemo, useState } from "react";
import { LeagueTable } from "../components/LeagueTable";
import { useLeaderboard } from "../hooks/useLeaderboard";
import { usePrizePool } from "../hooks/usePrizePool";

interface LeaderboardProps {
  address: string;
}

export function Leaderboard({ address }: LeaderboardProps) {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<"global" | "mini">("global");
  const { data = [], isLoading } = useLeaderboard();
  const { data: prizePool = 0 } = usePrizePool();
  const rows = useMemo(() => data.filter((entry) => entry.team_name.toLowerCase().includes(query.toLowerCase())).slice(0, 25), [data, query]);
  return (
    <div className="space-y-4 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3 rounded border border-line bg-panel p-4">
        <div>
          <div className="text-sm text-slate-400">Prize Pool</div>
          <div className="text-2xl font-black text-gold">{(prizePool / 10 ** 18).toFixed(2)} GEN</div>
        </div>
        <div className="flex rounded border border-line p-1">
          <button type="button" onClick={() => setMode("global")} className={`rounded px-3 py-2 text-sm ${mode === "global" ? "bg-gold text-ink" : ""}`}>Global</button>
          <button type="button" onClick={() => setMode("mini")} className={`rounded px-3 py-2 text-sm ${mode === "mini" ? "bg-gold text-ink" : ""}`}>My Mini-Leagues</button>
        </div>
        <input value={query} onChange={(event) => setQuery(event.target.value)} className="rounded border border-line bg-ink px-3 py-2" placeholder="Search team" aria-label="Search team name" />
      </div>
      {isLoading ? <div className="rounded border border-line bg-panel p-8">Loading leaderboard...</div> : <LeagueTable rows={rows} currentOwner={address} />}
    </div>
  );
}
