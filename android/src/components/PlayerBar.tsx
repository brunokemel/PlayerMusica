// src/components/PlayerBar.tsx
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import Slider from '@react-native-community/slider';
import { Ionicons } from '@expo/vector-icons';
import { usePlayerStore } from '@/store/usePlayerStore';
import { formatDuration } from '@/constants/extensions';
import { Colors, Spacing, BorderRadius } from '@/constants/colors';

export const PlayerBar: React.FC = () => {
  const {
    currentTrack,
    isPlaying,
    position,
    duration,
    volume,
    shuffle,
    repeatMode,
    togglePlayPause,
    nextTrack,
    previousTrack,
    seek,
    setVolume,
    toggleShuffle,
    cycleRepeatMode,
  } = usePlayerStore();

  const handleSeek = (value: number) => {
    seek(value);
  };

  const handleVolumeChange = (value: number) => {
    setVolume(value);
  };

  const getRepeatIcon = () => {
    switch (repeatMode) {
      case 'one': return 'repeat';
      case 'all': return 'repeat';
      default: return 'repeat-outline';
    }
  };

  const getRepeatColor = () => {
    return repeatMode !== 'none' ? Colors.primary : Colors.textSecondary;
  };

  if (!currentTrack) {
    return null;
  }

  return (
    <View style={styles.container}>
      <View style={styles.trackInfo}>
        <View style={styles.artworkContainer}>
          <Ionicons name="musical-note" size={40} color={Colors.textSecondary} />
        </View>
        <View style={styles.trackDetails}>
          <Text style={styles.trackTitle} numberOfLines={1}>{currentTrack.title}</Text>
          <Text style={styles.trackArtist} numberOfLines={1}>{currentTrack.artist}</Text>
        </View>
      </View>

      <View style={styles.controls}>
        <View style={styles.controlRow}>
          <TouchableOpacity onPress={toggleShuffle} style={[styles.controlBtn, shuffle && styles.controlBtnActive]}>
            <Ionicons name="shuffle" size={22} color={shuffle ? Colors.primary : Colors.textSecondary} />
          </TouchableOpacity>
          
          <TouchableOpacity onPress={previousTrack} style={styles.controlBtn}>
            <Ionicons name="play-skip-back" size={32} color={Colors.textPrimary} />
          </TouchableOpacity>
          
          <TouchableOpacity onPress={togglePlayPause} style={styles.playBtn}>
            <Ionicons name={isPlaying ? 'pause' : 'play'} size={36} color={Colors.textPrimary} />
          </TouchableOpacity>
          
          <TouchableOpacity onPress={nextTrack} style={styles.controlBtn}>
            <Ionicons name="play-skip-forward" size={32} color={Colors.textPrimary} />
          </TouchableOpacity>
          
          <TouchableOpacity onPress={cycleRepeatMode} style={[styles.controlBtn, repeatMode !== 'none' && styles.controlBtnActive]}>
            <Ionicons name={getRepeatIcon()} size={22} color={getRepeatColor()} />
          </TouchableOpacity>
        </View>

        <View style={styles.progressRow}>
          <Text style={styles.timeText}>{formatDuration(position)}</Text>
          <Slider
            style={styles.slider}
            minimumValue={0}
            maximumValue={duration || 1}
            value={position}
            onValueChange={handleSeek}
            minimumTrackTintColor={Colors.primary}
            maximumTrackTintColor={Colors.border}
            thumbTintColor={Colors.primary}
          />
          <Text style={styles.timeText}>{formatDuration(duration)}</Text>
        </View>

        <View style={styles.volumeRow}>
          <Ionicons name={volume === 0 ? 'volume-off' : volume < 0.5 ? 'volume-low' : 'volume-high'} size={22} color={Colors.textSecondary} />
          <Slider
            style={styles.volumeSlider}
            minimumValue={0}
            maximumValue={1}
            value={volume}
            onValueChange={handleVolumeChange}
            minimumTrackTintColor={Colors.primary}
            maximumTrackTintColor={Colors.border}
            thumbTintColor={Colors.primary}
          />
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.playerBarBg,
    borderTopWidth: 1,
    borderTopColor: Colors.playerBarBorder,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    paddingBottom: Spacing.md + 20, // Safe area for home indicator
  },
  trackInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    marginBottom: Spacing.sm,
  },
  artworkContainer: {
    width: 48,
    height: 48,
    borderRadius: BorderRadius.sm,
    backgroundColor: Colors.surfaceElevated,
    justifyContent: 'center',
    alignItems: 'center',
  },
  trackDetails: {
    flex: 1,
    minWidth: 0,
  },
  trackTitle: {
    color: Colors.textPrimary,
    fontSize: 14,
    fontWeight: '600',
  },
  trackArtist: {
    color: Colors.textSecondary,
    fontSize: 12,
    marginTop: 2,
  },
  controls: {
    alignItems: 'center',
  },
  controlRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.md,
    marginBottom: Spacing.xs,
  },
  controlBtn: {
    padding: Spacing.xs,
  },
  controlBtnActive: {
    // Active state handled by icon color
  },
  playBtn: {
    width: 48,
    height: 48,
    borderRadius: BorderRadius.round,
    backgroundColor: Colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: Spacing.xs,
  },
  progressRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    width: '100%',
    marginBottom: Spacing.xs,
  },
  timeText: {
    color: Colors.textSecondary,
    fontSize: 11,
    fontVariant: ['tabular-nums'],
    minWidth: 40,
    textAlign: 'center',
  },
  slider: {
    flex: 1,
    height: 4,
  },
  volumeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.sm,
    width: '100%',
    maxWidth: 200,
    alignSelf: 'center',
  },
  volumeSlider: {
    flex: 1,
    height: 4,
  },
});

export default PlayerBar;
