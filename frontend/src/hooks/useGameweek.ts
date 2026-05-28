import { useQuery } from "@tanstack/react-query";
import { callView } from "../lib/genlayer";

export function useGameweek() {
  return useQuery({
    queryKey: ["gameweek"],
    refetchInterval: 30_000,
    queryFn: async (): Promise<number> => callView<number>("get_gameweek", []),
  });
}
