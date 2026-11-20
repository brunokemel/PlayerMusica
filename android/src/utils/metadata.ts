// src/utils/metadata.ts
import { Asset as MediaLibraryAsset, getAssetsAsync } from 'expo-media-library';
import { AudioMetadata } from '@/types';
import { formatDuration, cleanFilenameTitle } from '@/constants/extensions';

export async function extractMetadataFromAsset(asset: MediaLibraryAsset): Promise<AudioMetadata> {
  const title = cleanFilenameTitle(asset.filename);
  const artist = 'Artista Desconhecido';
  const album = 'Álbum Desconhecido';
  const durationMs = asset.duration ? Math.round(asset.duration * 1000) : 0;
  
  return {
    title,
    artist,
    album,
    durationMs,
    durationStr: formatDuration(durationMs),
  };
}

export async function scanMusicLibrary(musicDirectory?: string): Promise<MediaLibraryAsset[]> {
  try {
    const allAssets: MediaLibraryAsset[] = [];
    let after: string | undefined;
    let hasNextPage = true;

    while (hasNextPage) {
      const page = await getAssetsAsync({
        mediaType: 'audio',
        first: 500,
        after,
        sortBy: ['creationTime', false],
      });
      allAssets.push(...page.assets);
      after = page.endCursor;
      hasNextPage = page.hasNextPage;
    }
    
    if (musicDirectory) {
      const dirPath = decodeURIComponent(musicDirectory).replace(/^\/+|\/+$/g, '');
      return allAssets.filter(asset => 
        decodeURIComponent(asset.uri).replace(/^file:\/\/+|^\/+/, '').startsWith(`${dirPath}/`)
      );
    }
    
    return allAssets;
  } catch (error) {
    console.error('[Metadata] Failed to scan library:', error);
    return [];
  }
}

export function buildFolderTree(assets: MediaLibraryAsset[]): Map<string, { name: string; count: number; children: Set<string> }> {
  const folderMap = new Map<string, { name: string; count: number; children: Set<string> }>();
  
  for (const asset of assets) {
    let folderPath = '';
    
    if (asset.uri.startsWith('file://')) {
      const pathParts = decodeURIComponent(asset.uri.replace('file://', '')).split('/');
      pathParts.pop(); // Remove filename
      folderPath = pathParts.join('/');
    }
    
    const parts = folderPath.split('/').filter(Boolean);
    let currentPath = '';
    
    for (const part of parts) {
      currentPath = currentPath ? `${currentPath}/${part}` : part;
      
      if (!folderMap.has(currentPath)) {
        folderMap.set(currentPath, { name: part, count: 0, children: new Set() });
      }
      
      folderMap.get(currentPath)!.count++;
      
      if (parts.length > 1) {
        const parentPath = currentPath.substring(0, currentPath.lastIndexOf('/'));
        if (parentPath) {
          folderMap.get(parentPath)?.children.add(currentPath);
        }
      }
    }
  }
  
  return folderMap;
}

export function filterTracksByFolder(assets: MediaLibraryAsset[], folderPath: string): MediaLibraryAsset[] {
  if (!folderPath) return assets;
  const prefix = `file://${folderPath}`;
  return assets.filter(asset => asset.uri.startsWith(prefix));
}

export function searchTracks(assets: MediaLibraryAsset[], query: string): MediaLibraryAsset[] {
  if (!query.trim()) return assets;
  const q = query.toLowerCase().trim();
  return assets.filter(asset => {
    const title = cleanFilenameTitle(asset.filename).toLowerCase();
    const artist = '';
    const album = '';
    const fileName = asset.filename.toLowerCase();
    return title.includes(q) || artist.includes(q) || album.includes(q) || fileName.includes(q);
  });
}
