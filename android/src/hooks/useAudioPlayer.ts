// src/hooks/useAudioPlayer.ts
import { useEffect, useRef, useCallback } from 'react';
import { Audio } from 'expo-av';
import { Track } from '@/types';
import { usePlayerStore } from '@/store/usePlayerStore';

export function useAudioPlayer() {
  const soundRef = useRef<Audio.Sound | null>(null);
  const reportedPositionRef = useRef(0);
  const {
    currentTrack,
    isPlaying,
    position,
    volume,
    setPlaying,
    setPosition,
    setDuration,
    nextTrack,
  } = usePlayerStore();

  useEffect(() => {
    void Audio.setAudioModeAsync({
      playsInSilentModeIOS: true,
      shouldDuckAndroid: true,
    }).catch((error) => console.error('[AudioPlayer] Failed to configure audio:', error));
  }, []);

  const loadTrack = useCallback(async (track: Track | null) => {
    if (soundRef.current) {
      try {
        await soundRef.current.unloadAsync();
      } catch {}
      soundRef.current = null;
    }

    if (!track) return;

    try {
      const { sound } = await Audio.Sound.createAsync(
        { uri: track.filePath },
        { shouldPlay: isPlaying, volume, positionMillis: position },
        (status) => {
          if (!status.isLoaded) {
            setPlaying(false);
            return;
          }
          setDuration(status.durationMillis || 0);
          if (status.didJustFinish) {
            if (usePlayerStore.getState().repeatMode === 'one') {
              soundRef.current?.replayAsync().catch(() => {});
              setPosition(0);
              setPlaying(true);
            } else {
              nextTrack();
            }
            return;
          }
          reportedPositionRef.current = status.positionMillis || 0;
          setPosition(reportedPositionRef.current);
          setPlaying(status.isPlaying);
        }
      );
      soundRef.current = sound;
    } catch (error) {
      console.error('[AudioPlayer] Failed to load track:', error);
      setPlaying(false);
    }
  }, [setDuration, setPosition, setPlaying, nextTrack]);

  useEffect(() => {
    void loadTrack(currentTrack);
    return () => {
      if (soundRef.current) {
        soundRef.current.unloadAsync().catch(() => {});
      }
    };
  }, [currentTrack?.filePath, loadTrack]);

  useEffect(() => {
    if (soundRef.current) {
      soundRef.current.setVolumeAsync(volume).catch(() => {});
    }
  }, [volume]);

  useEffect(() => {
    const sound = soundRef.current;
    if (!sound) return;
    void sound.getStatusAsync().then((status) => {
      if (status.isLoaded && status.isPlaying !== isPlaying) {
        return isPlaying ? sound.playAsync() : sound.pauseAsync();
      }
    }).catch(() => {});
  }, [isPlaying]);

  useEffect(() => {
    const sound = soundRef.current;
    if (sound && Math.abs(reportedPositionRef.current - position) > 1200) {
      sound.setPositionAsync(position).catch(() => {});
    }
  }, [position]);

  const seek = useCallback(async (pos: number) => {
    if (soundRef.current) {
      await soundRef.current.setPositionAsync(pos);
    }
  }, []);

  const play = useCallback(async () => {
    if (soundRef.current) {
      await soundRef.current.playAsync();
    }
  }, []);

  const pause = useCallback(async () => {
    if (soundRef.current) {
      await soundRef.current.pauseAsync();
    }
  }, []);

  const togglePlayPause = useCallback(async () => {
    if (soundRef.current) {
      const status = await soundRef.current.getStatusAsync();
      if (status.isLoaded) {
        if (status.isPlaying) {
          await soundRef.current.pauseAsync();
        } else {
          await soundRef.current.playAsync();
        }
      }
    }
  }, []);

  return {
    play,
    pause,
    togglePlayPause,
    seek,
    loadTrack,
  };
}
