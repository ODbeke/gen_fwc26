import { useQuery } from "@tanstack/react-query";
import { callView } from "../lib/genlayer";
import type { Team } from "../lib/constants";

export function useMyTeam(owner?: string) {
  return useQuery({
    queryKey: ["team", owner],
    enabled: Boolean(owner),
    refetchInterval: 30_000,
    queryFn: async (): Promise<Team | null> => {
      if (!owner) return null;
      try {
        return await callView<Team>("get_team", [owner]);
      } catch {
        return null;
      }
    },
  });
}
