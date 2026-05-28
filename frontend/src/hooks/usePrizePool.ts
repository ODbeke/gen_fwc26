import { useQuery } from "@tanstack/react-query";
import { callView } from "../lib/genlayer";

export function usePrizePool() {
  return useQuery({
    queryKey: ["prizePool"],
    refetchInterval: 60_000,
    queryFn: async (): Promise<number> => callView<number>("get_prize_pool", []),
  });
}
