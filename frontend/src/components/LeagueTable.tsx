import type { RankedEntry } from "../hooks/useLeaderboard";

interface LeagueTableProps {
  rows: RankedEntry[];
  currentOwner?: string;
}

export function LeagueTable({ rows, currentOwner }: LeagueTableProps) {
  return (
    <div className="overflow-x-auto rounded border border-line">
      <table className="w-full min-w-[620px] border-collapse text-sm">
        <thead className="bg-panel text-left text-slate-300">
          <tr>
            <th className="p-3">Rank</th>
            <th className="p-3">Manager</th>
            <th className="p-3">Team Name</th>
            <th className="p-3">GW Points</th>
            <th className="p-3">Total</th>
            <th className="p-3">Move</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.owner} className={row.owner === currentOwner ? "bg-gold/15 text-gold" : "border-t border-line"}>
              <td className="p-3 font-semibold">{row.rank}</td>
              <td className="p-3">{row.owner.slice(0, 8)}...</td>
              <td className="p-3">{row.team_name}</td>
              <td className="p-3">{row.gameweek_points ?? 0}</td>
              <td className="p-3 font-semibold">{row.total_points}</td>
              <td className="p-3">same</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
