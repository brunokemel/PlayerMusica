// src/app/(tabs)/index.tsx
import React, { useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { SearchBar } from '@/components/SearchBar';
import { TrackTable } from '@/components/TrackTable';
import { PlayerBar } from '@/components/PlayerBar';
import { useLibraryScanner } from '@/hooks/useLibraryScanner';
import { useAudioPlayer } from '@/hooks/useAudioPlayer';
import { Colors } from '@/constants/colors';

export default function HomeScreen() {
  const { scanLibrary } = useLibraryScanner();
  useAudioPlayer();

  useEffect(() => {
    scanLibrary();
  }, [scanLibrary]);

  return (
    <SafeAreaView style={styles.container} edges={['top', 'left', 'right']}>
      <View style={styles.content}>
        <SearchBar />
        <TrackTable />
      </View>
      <PlayerBar />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
  content: {
    flex: 1,
  },
});
