import { useQuery } from "@tanstack/react-query";
import type { Player } from "../lib/constants";

export function usePlayers() {
  return useQuery({
    queryKey: ["players"],
    queryFn: async (): Promise<Player[]> => {
      const response = await fetch("/players_2026.json");
      if (!response.ok) throw new Error("Could not load players");
      return (await response.json()) as Player[];
    },
  });
}
