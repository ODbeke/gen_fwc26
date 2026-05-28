import { useQuery } from "@tanstack/react-query";
import { callView } from "../lib/genlayer";

export interface MatchResultView {
  match_id: string;
  home_team: string;
  away_team: string;
  score: string;
  scorers: string[];
  assisters: string[];
  yellow_cards: string[];
  red_cards: string[];
  clean_sheets: string[];
  bonus_top3: string[];
  is_knockout: boolean;
  is_final: boolean;
}

export function useMatchResult(matchId: string) {
  return useQuery({
    queryKey: ["match", matchId],
    enabled: Boolean(matchId),
    queryFn: async (): Promise<MatchResultView> => callView<MatchResultView>("get_match_result", [matchId]),
  });
}
