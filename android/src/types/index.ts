// src/types/index.ts
export interface Track {
  id: number;
  filePath: string;
  fileName: string;
  title: string;
  artist: string;
  album: string;
  durationMs: number;
  durationStr: string;
  fileSize: number;
  folderRelative: string;
  extension: string;
}

export interface FolderNode {
  name: string;
  fullPath: string;
  relativePath: string;
  trackCount: number;
  children: FolderNode[];
}

export interface AudioMetadata {
  title: string;
  artist: string;
  album: string;
  durationMs: number;
  durationStr: string;
}

export interface AppConfig {
  musicDirectory: string;
  volume: number;
  shuffle: boolean;
  repeatMode: 'none' | 'all' | 'one';
  windowWidth: number;
  windowHeight: number;
  isMaximized: boolean;
}

export type RepeatMode = 'none' | 'all' | 'one';

export interface PlayerState {
  currentTrack: Track | null;
  isPlaying: boolean;
  position: number;
  duration: number;
  volume: number;
  shuffle: boolean;
  repeatMode: RepeatMode;
  playlist: Track[];
  currentIndex: number;
}