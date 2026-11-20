// src/constants/extensions.ts
export const SUPPORTED_EXTENSIONS = new Set([
  '.mp3',
  '.wav',
  '.flac',
  '.ogg',
  '.oga',
  '.m4a',
  '.aac',
  '.wma',
]);

export const AUDIO_MIME_TYPES: Record<string, string> = {
  '.mp3': 'audio/mpeg',
  '.wav': 'audio/wav',
  '.flac': 'audio/flac',
  '.ogg': 'audio/ogg',
  '.oga': 'audio/ogg',
  '.m4a': 'audio/mp4',
  '.aac': 'audio/aac',
  '.wma': 'audio/x-ms-wma',
};

export function isAudioFile(filename: string): boolean {
  const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'));
  return SUPPORTED_EXTENSIONS.has(ext);
}

export function getMimeType(filename: string): string {
  const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'));
  return AUDIO_MIME_TYPES[ext] || 'audio/mpeg';
}

export function formatDuration(ms: number): string {
  if (ms <= 0) return '00:00';
  const totalSeconds = Math.floor(ms / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  }
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

export function cleanFilenameTitle(filename: string): string {
  const base = filename.substring(0, filename.lastIndexOf('.'));
  const cleaned = base.replace(/^\d+[\s\.\-_]+/, '').trim();
  return cleaned ? cleaned.replace(/_/g, ' ') : base.replace(/_/g, ' ');
}