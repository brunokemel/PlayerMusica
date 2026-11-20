// src/utils/storage.ts
import { MMKV } from 'react-native-mmkv';
import { AppConfig } from '@/types';

const storage = new MMKV({
  id: 'playmusica-config',
  encryptionKey: 'playmusica-secure-key-2024',
});

const CONFIG_KEY = 'app_config';

export const DEFAULT_CONFIG: AppConfig = {
  musicDirectory: '',
  volume: 0.8,
  shuffle: false,
  repeatMode: 'none',
  windowWidth: 360,
  windowHeight: 640,
  isMaximized: false,
};

export function getConfig(): AppConfig {
  try {
    const json = storage.getString(CONFIG_KEY);
    if (!json) return DEFAULT_CONFIG;
    const parsed = JSON.parse(json);
    return { ...DEFAULT_CONFIG, ...parsed };
  } catch {
    return DEFAULT_CONFIG;
  }
}

export function saveConfig(config: Partial<AppConfig>): void {
  try {
    const current = getConfig();
    const updated = { ...current, ...config };
    storage.set(CONFIG_KEY, JSON.stringify(updated));
  } catch (error) {
    console.error('[Storage] Failed to save config:', error);
  }
}

export function getMusicDirectory(): string {
  return getConfig().musicDirectory;
}

export function setMusicDirectory(path: string): void {
  saveConfig({ musicDirectory: path });
}

export function getVolume(): number {
  return getConfig().volume;
}

export function setVolume(volume: number): void {
  saveConfig({ volume: Math.max(0, Math.min(1, volume)) });
}

export function getShuffle(): boolean {
  return getConfig().shuffle;
}

export function setShuffle(shuffle: boolean): void {
  saveConfig({ shuffle });
}

export function getRepeatMode(): AppConfig['repeatMode'] {
  return getConfig().repeatMode;
}

export function setRepeatMode(mode: AppConfig['repeatMode']): void {
  saveConfig({ repeatMode: mode });
}

export function clearConfig(): void {
  storage.delete(CONFIG_KEY);
}