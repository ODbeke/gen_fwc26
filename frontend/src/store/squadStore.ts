import { create } from "zustand";
import type { Player } from "../lib/constants";

interface SquadState {
  selectedIds: string[];
  captainId: string;
  viceCaptainId: string;
  formation: string;
  setFormation: (formation: string) => void;
  hydrateSquad: (playerIds: string[], captainId: string, viceCaptainId: string) => void;
  clearSquad: () => void;
  setSquad: (players: Player[]) => void;
  addPlayer: (player: Player) => void;
  removePlayer: (playerId: string) => void;
  setCaptain: (playerId: string) => void;
  setViceCaptain: (playerId: string) => void;
}

export const useSquadStore = create<SquadState>((set) => ({
  selectedIds: [],
  captainId: "",
  viceCaptainId: "",
  formation: "4-2-3-1",
  setFormation: (formation) => set({ formation }),
  hydrateSquad: (playerIds, captainId, viceCaptainId) => set({ selectedIds: playerIds, captainId, viceCaptainId }),
  clearSquad: () => set({ selectedIds: [], captainId: "", viceCaptainId: "" }),
  setSquad: (players) => set({
    selectedIds: players.map((player) => player.player_id),
    captainId: players[0]?.player_id ?? "",
    viceCaptainId: players[1]?.player_id ?? "",
  }),
  addPlayer: (player) => set((state) => (
    state.selectedIds.includes(player.player_id) ? state : { selectedIds: [...state.selectedIds, player.player_id] }
  )),
  removePlayer: (playerId) => set((state) => ({ selectedIds: state.selectedIds.filter((id) => id !== playerId) })),
  setCaptain: (playerId) => set({ captainId: playerId }),
  setViceCaptain: (playerId) => set({ viceCaptainId: playerId }),
}));
