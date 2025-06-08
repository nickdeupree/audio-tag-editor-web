import { create } from 'zustand';

type InputOption = 'upload' | 'youtube' | 'soundcloud';

interface InputState {
    selectedOption: InputOption;
    setSelectedOption: (option: InputOption) => void;
}

export const useInputStore = create<InputState>((set) => ({
    selectedOption: 'upload',
    setSelectedOption: (option) => set({ selectedOption: option }),
}));