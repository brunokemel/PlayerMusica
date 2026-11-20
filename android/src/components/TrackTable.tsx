// src/components/TrackTable.tsx
import React, { useCallback } from 'react';
import { View, FlatList, StyleSheet, Text, ActivityIndicator } from 'react-native';
import { Asset as MediaLibraryAsset } from 'expo-media-library';
import { TrackRow } from './TrackRow';
import { Colors, Spacing, Typography } from '@/constants/colors';
import { useLibraryStore } from '@/store/useLibraryStore';
import { usePlayerStore } from '@/store/usePlayerStore';

interface TrackTableProps {
  onTrackPress?: (track: MediaLibraryAsset, index: number) => void;
}

export const TrackTable: React.FC<TrackTableProps> = ({ onTrackPress }) => {
  const { filteredTracks, isScanning } = useLibraryStore();
  const { currentTrack, setPlaylist, currentIndex } = usePlayerStore();

  const renderItem = useCallback(({ item, index }: { item: MediaLibraryAsset; index: number }) => {
    const isActive = currentTrack?.filePath === item.uri;
    return (
      <TrackRow
        track={{
          id: index,
          filePath: item.uri,
          fileName: item.filename,
          title: item.filename.replace(/\.[^.]+$/, ''),
          artist: 'Artista Desconhecido',
          album: 'Álbum Desconhecido',
          durationMs: item.duration ? Math.round(item.duration * 1000) : 0,
          durationStr: '',
          fileSize: 0,
          folderRelative: '',
          extension: '',
        }}
        index={index}
        isActive={isActive}
        onPress={() => {
          setPlaylist(
            filteredTracks.map((t, i) => ({
              id: i,
              filePath: t.uri,
              fileName: t.filename,
              title: t.filename.replace(/\.[^.]+$/, ''),
              artist: 'Artista Desconhecido',
              album: 'Álbum Desconhecido',
              durationMs: t.duration ? Math.round(t.duration * 1000) : 0,
              durationStr: '',
              fileSize: 0,
              folderRelative: '',
              extension: '',
            })),
            index
          );
          onTrackPress?.(item, index);
        }}
      />
    );
  }, [currentTrack, filteredTracks, setPlaylist, onTrackPress]);

  const getItemLayout = useCallback((data: any, index: number) => ({
    length: 64,
    offset: 64 * index,
    index,
  }), []);

  if (filteredTracks.length === 0 && !isScanning) {
    return (
      <View style={styles.emptyContainer}>
        <Text style={[styles.emptyText, Typography.body1]}>Nenhuma música encontrada</Text>
        <Text style={[styles.emptySubtext, Typography.caption]}>
          Adicione músicas à sua biblioteca ou selecione uma pasta
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={filteredTracks}
        renderItem={renderItem}
        keyExtractor={(_, index) => String(index)}
        getItemLayout={getItemLayout}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        ListFooterComponent={
          isScanning ? (
            <View style={styles.loadingFooter}>
              <ActivityIndicator color={Colors.primary} size="small" />
            </View>
          ) : null
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  listContent: {
    paddingBottom: Spacing.xl, // Space for player bar
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Spacing.xl,
  },
  emptyText: {
    color: Colors.textPrimary,
    marginBottom: Spacing.xs,
    textAlign: 'center',
  },
  emptySubtext: {
    color: Colors.textSecondary,
    textAlign: 'center',
  },
  loadingFooter: {
    padding: Spacing.md,
    alignItems: 'center',
  },
});

export default TrackTable;
