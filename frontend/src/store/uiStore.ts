import { create } from "zustand";

interface UiState {
  pickerPosition: string | null;
  notification: string;
  openPicker: (position: string) => void;
  closePicker: () => void;
  notify: (message: string) => void;
}

export const useUiStore = create<UiState>((set) => ({
  pickerPosition: null,
  notification: "",
  openPicker: (position) => set({ pickerPosition: position }),
  closePicker: () => set({ pickerPosition: null }),
  notify: (message) => set({ notification: message }),
}));
