import { useMyTeam } from "../hooks/useMyTeam";

interface ProfileProps {
  address: string;
}

export function Profile({ address }: ProfileProps) {
  const { data: team, isLoading } = useMyTeam(address);
  return (
    <div className="p-4">
      <div className="rounded border border-line bg-panel p-5">
        <div className="text-sm text-slate-400">Manager</div>
        <div className="mt-1 text-xl font-semibold">{team?.username ?? team?.team_name ?? (address ? "No on-chain profile yet" : "No wallet connected")}</div>
        <div className="mt-1 text-sm text-slate-400">{address || "Connect wallet to resume your team"}</div>
        <div className="mt-5 grid gap-3 md:grid-cols-3">
          <div className="rounded border border-line bg-ink p-4"><div className="text-sm text-slate-400">Squad</div><div className="text-2xl font-black text-gold">{isLoading ? "..." : `${team?.player_ids.length ?? 0}/15`}</div></div>
          <div className="rounded border border-line bg-ink p-4"><div className="text-sm text-slate-400">Total</div><div className="text-2xl font-black text-gold">{team?.total_points ?? 0}</div></div>
          <div className="rounded border border-line bg-ink p-4"><div className="text-sm text-slate-400">Rank</div><div className="text-2xl font-black text-gold">-</div></div>
        </div>
      </div>
    </div>
  );
}
