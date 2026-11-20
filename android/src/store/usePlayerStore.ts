// src/store/usePlayerStore.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { MMKV } from 'react-native-mmkv';
import { Track, PlayerState, RepeatMode } from '@/types';

const mmkv = new MMKV({ id: 'playmusica-player-state' });

const mmkvStorage = {
  getItem: (name: string) => mmkv.getString(name) ?? null,
  setItem: (name: string, value: string) => mmkv.set(name, value),
  removeItem: (name: string) => mmkv.delete(name),
};

interface PlayerStore extends PlayerState {
  setCurrentTrack: (track: Track | null) => void;
  setPlaying: (playing: boolean) => void;
  togglePlayPause: () => void;
  setPosition: (position: number) => void;
  setDuration: (duration: number) => void;
  setVolume: (volume: number) => void;
  toggleShuffle: () => boolean;
  setRepeatMode: (mode: RepeatMode) => void;
  cycleRepeatMode: () => RepeatMode;
  setPlaylist: (tracks: Track[], startIndex?: number) => void;
  setCurrentIndex: (index: number) => void;
  nextTrack: () => void;
  previousTrack: () => void;
  seek: (position: number) => void;
  reset: () => void;
}

const initialState: PlayerState = {
  currentTrack: null,
  isPlaying: false,
  position: 0,
  duration: 0,
  volume: 0.8,
  shuffle: false,
  repeatMode: 'none',
  playlist: [],
  currentIndex: -1,
};

export const usePlayerStore = create<PlayerStore>()(
  persist(
    (set, get) => ({
      ...initialState,
      
      setCurrentTrack: (track) => set({ currentTrack: track }),
      
      setPlaying: (isPlaying) => set({ isPlaying }),

      togglePlayPause: () => set((state) => ({ isPlaying: !state.isPlaying })),
      
      setPosition: (position) => set({ position }),
      
      setDuration: (duration) => set({ duration }),
      
      setVolume: (volume) => set({ volume: Math.max(0, Math.min(1, volume)) }),
      
      toggleShuffle: () => {
        const newShuffle = !get().shuffle;
        set({ shuffle: newShuffle });
        return newShuffle;
      },
      
      setRepeatMode: (mode) => set({ repeatMode: mode }),
      
      cycleRepeatMode: () => {
        const modes: RepeatMode[] = ['none', 'all', 'one'];
        const current = get().repeatMode;
        const currentIndex = modes.indexOf(current);
        const nextMode = modes[(currentIndex + 1) % modes.length];
        set({ repeatMode: nextMode });
        return nextMode;
      },
      
      setPlaylist: (playlist, startIndex = -1) => set({ 
        playlist, 
        currentIndex: startIndex >= 0 && startIndex < playlist.length ? startIndex : -1,
        currentTrack: startIndex >= 0 && startIndex < playlist.length ? playlist[startIndex] : null,
        position: 0,
        isPlaying: startIndex >= 0 && startIndex < playlist.length,
      }),
      
      setCurrentIndex: (index) => set({ currentIndex: index }),
      
      nextTrack: () => {
        const { playlist, currentIndex, shuffle, repeatMode } = get();
        if (!playlist.length) return;

        if (repeatMode === 'one') {
          set({ position: 0, isPlaying: true });
          return;
        }
        
        let nextIndex = currentIndex;
        
        if (shuffle) {
          if (playlist.length > 1) {
            do {
              nextIndex = Math.floor(Math.random() * playlist.length);
            } while (nextIndex === currentIndex);
          }
        } else {
          nextIndex = currentIndex + 1;
          if (nextIndex >= playlist.length) {
            if (repeatMode === 'all') {
              nextIndex = 0;
            } else {
              set({ isPlaying: false, position: 0 });
              return;
            }
          }
        }
        
        set({ 
          currentIndex: nextIndex, 
          currentTrack: playlist[nextIndex],
          position: 0,
          isPlaying: true,
        });
      },
      
      previousTrack: () => {
        const { playlist, currentIndex, position, shuffle, repeatMode } = get();
        if (!playlist.length) return;
        
        // If more than 3 seconds played, restart current track
        if (position > 3000) {
          set({ position: 0 });
          return;
        }
        
        let prevIndex = currentIndex;
        
        if (shuffle) {
          prevIndex = (currentIndex - 1 + playlist.length) % playlist.length;
        } else {
          prevIndex = currentIndex - 1;
          if (prevIndex < 0) {
            if (repeatMode === 'all') {
              prevIndex = playlist.length - 1;
            } else {
              set({ position: 0 });
              return;
            }
          }
        }
        
        set({ 
          currentIndex: prevIndex, 
          currentTrack: playlist[prevIndex],
          position: 0,
          isPlaying: true,
        });
      },
      
      seek: (position) => {
        const { duration } = get();
        const clamped = Math.max(0, Math.min(position, duration || position));
        set({ position: clamped });
      },
      
      reset: () => set(initialState),
    }),
    {
      name: 'player-state',
      storage: createJSONStorage(() => mmkvStorage),
      partialize: (state) => ({
        volume: state.volume,
        shuffle: state.shuffle,
        repeatMode: state.repeatMode,
      }),
    }
  )
);
