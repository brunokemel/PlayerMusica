// src/store/useLibraryStore.ts
import { create } from 'zustand';
import { Asset as MediaLibraryAsset } from 'expo-media-library';
import { FolderNode } from '@/types';

interface LibraryStore {
  allTracks: MediaLibraryAsset[];
  filteredTracks: MediaLibraryAsset[];
  folderTree: Map<string, { name: string; count: number; children: Set<string> }>;
  currentFolderFilter: string | null;
  searchQuery: string;
  isScanning: boolean;
  scanProgress: string;
  error: string | null;
  
  setAllTracks: (tracks: MediaLibraryAsset[]) => void;
  setFilteredTracks: (tracks: MediaLibraryAsset[]) => void;
  setFolderTree: (tree: Map<string, { name: string; count: number; children: Set<string> }>) => void;
  setCurrentFolderFilter: (folder: string | null) => void;
  setSearchQuery: (query: string) => void;
  setScanning: (scanning: boolean, message?: string) => void;
  setError: (error: string | null) => void;
  applyFilters: () => void;
  clear: () => void;
}

const initialState = {
  allTracks: [],
  filteredTracks: [],
  folderTree: new Map(),
  currentFolderFilter: null,
  searchQuery: '',
  isScanning: false,
  scanProgress: '',
  error: null,
};

export const useLibraryStore = create<LibraryStore>((set, get) => ({
  ...initialState,
  
  setAllTracks: (tracks) => set({ allTracks: tracks }),
  
  setFilteredTracks: (tracks) => set({ filteredTracks: tracks }),
  
  setFolderTree: (tree) => set({ folderTree: tree }),
  
  setCurrentFolderFilter: (folder) => set({ currentFolderFilter: folder }),
  
  setSearchQuery: (query) => set({ searchQuery: query }),
  
  setScanning: (isScanning, message = '') => set({ isScanning, scanProgress: message }),
  
  setError: (error) => set({ error }),
  
  applyFilters: () => {
    const { allTracks, currentFolderFilter, searchQuery } = get();
    let filtered = [...allTracks];
    
    if (currentFolderFilter) {
      const folder = decodeURIComponent(currentFolderFilter)
        .replace(/^file:\/\/+/, '')
        .replace(/^\/+|\/+$/g, '');
      filtered = filtered.filter(t => {
        const path = decodeURIComponent(t.uri)
          .replace(/^file:\/\/+/, '')
          .replace(/^\/+/, '');
        return path === folder || path.startsWith(`${folder}/`);
      });
    }
    
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase().trim();
      filtered = filtered.filter(t => {
        const title = t.filename.replace(/\.[^.]+$/, '').toLowerCase();
        const artist = '';
        const album = '';
        const fileName = t.filename.toLowerCase();
        return title.includes(q) || artist.includes(q) || album.includes(q) || fileName.includes(q);
      });
    }
    
    set({ filteredTracks: filtered });
  },
  
  clear: () => set(initialState),
}));
