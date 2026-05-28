import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

interface Fixture {
  match_number: number;
  match_id: string;
  gameweek: number;
  round: string;
  stage: string;
  date_utc: string;
  local_date: string;
  home: string;
  away: string;
  home_code: string;
  away_code: string;
  venue: string;
  city: string;
}

function useFixtures() {
  return useQuery({
    queryKey: ["fixtures-2026"],
    queryFn: async (): Promise<Fixture[]> => {
      const response = await fetch("/fixtures_2026.json");
      if (!response.ok) throw new Error("Could not load fixtures.");
      return response.json();
    },
  });
}

function formatKickoff(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    timeZoneName: "short",
  }).format(new Date(value));
}

export function Fixtures() {
  const { data: fixtures = [], isLoading } = useFixtures();
  const [gameweek, setGameweek] = useState("all");
  const [round, setRound] = useState("all");
  const gameweeks = useMemo(() => Array.from(new Set(fixtures.map((fixture) => fixture.gameweek))).sort((a, b) => a - b), [fixtures]);
  const rounds = useMemo(() => Array.from(new Set(fixtures.map((fixture) => fixture.round))).filter(Boolean), [fixtures]);
  const filtered = fixtures.filter((fixture) => (gameweek === "all" || fixture.gameweek === Number(gameweek)) && (round === "all" || fixture.round === round));

  return (
    <div className="space-y-4 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-black">Fixtures</h1>
          <p className="text-sm text-slate-400">Official FIFA World Cup 2026 schedule. Knockout opponents remain as FIFA placeholders until known.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <select value={gameweek} onChange={(event) => setGameweek(event.target.value)} className="rounded border border-line bg-panel px-3 py-2 text-sm" aria-label="Filter by gameweek">
            <option value="all">All GWs</option>
            {gameweeks.map((item) => <option key={item} value={item}>GW{item}</option>)}
          </select>
          <select value={round} onChange={(event) => setRound(event.target.value)} className="rounded border border-line bg-panel px-3 py-2 text-sm" aria-label="Filter by round">
            <option value="all">All rounds</option>
            {rounds.map((item) => <option key={item}>{item}</option>)}
          </select>
        </div>
      </div>
      <div className="grid gap-3">
        {isLoading ? <div className="rounded border border-line bg-panel p-8 text-center">Loading FIFA fixtures...</div> : null}
        {filtered.map((fixture) => (
          <div key={fixture.match_id} className="grid gap-3 rounded border border-line bg-panel p-3 text-sm lg:grid-cols-[80px_120px_1fr_120px_1fr_220px] lg:items-center">
            <span className="text-slate-400">GW{fixture.gameweek}</span>
            <span className="font-semibold text-gold">M{fixture.match_number}</span>
            <span className="font-semibold">{fixture.home} <span className="text-xs text-slate-500">{fixture.home_code}</span></span>
            <span className="text-center text-slate-400">vs</span>
            <span className="font-semibold">{fixture.away} <span className="text-xs text-slate-500">{fixture.away_code}</span></span>
            <div className="text-xs text-slate-400 lg:text-right">
              <div>{formatKickoff(fixture.date_utc)}</div>
              <div>{fixture.round} · {fixture.venue}, {fixture.city}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
