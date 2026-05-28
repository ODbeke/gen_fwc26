import { useQuery } from "@tanstack/react-query";
import { callView } from "../lib/genlayer";
import type { LeaderboardEntry } from "../lib/constants";

export interface RankedEntry extends LeaderboardEntry {
  rank: number;
  movement: "up" | "down" | "same";
}

export function useLeaderboard() {
  return useQuery({
    queryKey: ["leaderboard"],
    refetchInterval: 60_000,
    queryFn: async (): Promise<RankedEntry[]> => {
      const rows = await callView<LeaderboardEntry[]>("get_leaderboard", []);
      return rows.map((entry, index) => ({ ...entry, rank: index + 1, movement: "same" }));
    },
  });
}
