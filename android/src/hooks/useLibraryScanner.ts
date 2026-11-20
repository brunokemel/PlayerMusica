// src/hooks/useLibraryScanner.ts
import { useCallback, useEffect } from 'react';
import { requestPermissionsAsync } from 'expo-media-library';
import { useLibraryStore } from '@/store/useLibraryStore';
import { buildFolderTree, scanMusicLibrary } from '@/utils/metadata';
import { getMusicDirectory } from '@/utils/storage';

export function useLibraryScanner() {
  const {
    setAllTracks,
    setFilteredTracks,
    setFolderTree,
    setScanning,
    setError,
    applyFilters,
    currentFolderFilter,
    searchQuery,
    allTracks,
  } = useLibraryStore();

  const scanLibrary = useCallback(async () => {
    setScanning(true, 'Solicitando permissões...');
    
    try {
      const { status } = await requestPermissionsAsync();
      if (status !== 'granted') {
        setError('Permissão de acesso aos arquivos de mídia negada');
        setScanning(false, 'Erro de permissão');
        return;
      }

      setScanning(true, 'Indexando biblioteca de música...');
      
      const musicDir = getMusicDirectory();
      const assets = await scanMusicLibrary(musicDir || undefined);
      
      if (!assets.length) {
        setAllTracks([]);
        setFilteredTracks([]);
        setFolderTree(new Map());
        setScanning(false, 'Nenhuma música encontrada');
        return;
      }

      const folderTree = buildFolderTree(assets);
      
      setAllTracks(assets);
      setFilteredTracks(assets);
      setFolderTree(folderTree);
      setScanning(false, `${assets.length} faixas carregadas`);
    } catch (error) {
      console.error('[LibraryScanner] Error:', error);
      setError('Erro ao escanear biblioteca');
      setScanning(false, 'Erro ao carregar');
    }
  }, [setAllTracks, setFilteredTracks, setFolderTree, setScanning, setError]);

  useEffect(() => {
    applyFilters();
  }, [currentFolderFilter, searchQuery, allTracks, applyFilters]);

  return { scanLibrary };
}
