// src/components/TrackRow.tsx
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Track } from '@/types';
import { Colors, Spacing, BorderRadius, Typography } from '@/constants/colors';
import { formatDuration } from '@/constants/extensions';

interface TrackRowProps {
  track: Track;
  index: number;
  isActive: boolean;
  onPress: () => void;
  onLongPress?: () => void;
}

export const TrackRow: React.FC<TrackRowProps> = ({
  track,
  index,
  isActive,
  onPress,
  onLongPress,
}) => {
  return (
    <TouchableOpacity
      style={[
        styles.row,
        isActive && styles.rowActive,
      ]}
      onPress={onPress}
      onLongPress={onLongPress}
      activeOpacity={0.8}
    >
      <View style={styles.indexContainer}>
        <Text style={[styles.indexText, isActive ? styles.indexTextActive : {}]}>
          {isActive ? '▶' : index + 1}
        </Text>
      </View>
      
      <View style={styles.trackInfo} >
        <Text style={[styles.trackTitle, isActive && styles.trackTitleActive]} numberOfLines={1}>
          {track.title}
        </Text>
        <Text style={[styles.trackMeta, isActive && styles.trackMetaActive]} numberOfLines={1}>
          {track.artist} • {track.album}
        </Text>
      </View>
      
      <View style={styles.durationContainer}>
        <Text style={[styles.durationText, isActive && styles.durationTextActive]}>
          {formatDuration(track.durationMs)}
        </Text>
      </View>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
    backgroundColor: Colors.surface,
    borderBottomWidth: 1,
    borderBottomColor: Colors.divider,
  },
  rowActive: {
    backgroundColor: Colors.surfaceHover,
  },
  indexContainer: {
    width: 36,
    alignItems: 'center',
  },
  indexText: {
    color: Colors.textSecondary,
    fontSize: 13,
    fontVariant: ['tabular-nums'],
  },
  indexTextActive: {
    color: Colors.primary,
    fontWeight: '600',
  },
  trackInfo: {
    flex: 1,
    minWidth: 0,
    marginHorizontal: Spacing.sm,
  },
  trackTitle: {
    color: Colors.textPrimary,
    fontSize: 14,
    fontWeight: '500',
  },
  trackTitleActive: {
    color: Colors.primary,
  },
  trackMeta: {
    color: Colors.textSecondary,
    fontSize: 12,
    marginTop: 2,
  },
  trackMetaActive: {
    color: Colors.primaryLight,
  },
  durationContainer: {
    width: 56,
    alignItems: 'flex-end',
  },
  durationText: {
    color: Colors.textSecondary,
    fontSize: 12,
    fontVariant: ['tabular-nums'],
    fontFamily: 'monospace',
  },
  durationTextActive: {
    color: Colors.primary,
  },
});

export default TrackRow;