// src/components/SearchBar.tsx
import React, { useRef, useEffect } from 'react';
import { View, Text, TextInput, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useLibraryStore } from '@/store/useLibraryStore';
import { Colors, Spacing, BorderRadius, Typography } from '@/constants/colors';

interface SearchBarProps {
  onFocus?: () => void;
  onClear?: () => void;
}

export const SearchBar: React.FC<SearchBarProps> = ({ onFocus, onClear }) => {
  const { searchQuery, setSearchQuery, filteredTracks, allTracks } = useLibraryStore();
  const inputRef = useRef<TextInput>(null);

  useEffect(() => {
    if (onFocus) {
      // Could add focus handling here
    }
  }, [onFocus]);

  const handleChange = (text: string) => {
    setSearchQuery(text);
  };

  const handleClear = () => {
    setSearchQuery('');
    onClear?.();
  };

  return (
    <View style={styles.container}>
      <View style={styles.inputWrapper}>
        <Ionicons name="search" size={22} color={Colors.textSecondary} style={styles.icon} />
        <TextInput
          ref={inputRef}
          style={[styles.input, Typography.body1]}
          placeholder="Buscar músicas, artistas, álbuns..."
          placeholderTextColor={Colors.textDisabled}
          value={searchQuery}
          onChangeText={handleChange}
          onFocus={onFocus}
          clearButtonMode="never"
          autoCapitalize="none"
        />
        {searchQuery && (
          <TouchableOpacity onPress={handleClear} style={styles.clearBtn} accessible accessibilityLabel="Limpar busca">
            <Ionicons name="close" size={20} color={Colors.textSecondary} />
          </TouchableOpacity>
        )}
      </View>
      <View style={styles.counter}>
        <Text style={[styles.counterText, Typography.caption]}>
          {filteredTracks.length} de {allTracks.length} faixas
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: Colors.searchBg,
    borderBottomWidth: 1,
    borderBottomColor: Colors.searchBorder,
    paddingHorizontal: Spacing.md,
    paddingVertical: Spacing.sm,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: Colors.surface,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: Colors.searchBorder,
    paddingHorizontal: Spacing.sm,
  },
  icon: {
    marginRight: Spacing.xs,
  },
  input: {
    flex: 1,
    color: Colors.textPrimary,
    paddingVertical: Spacing.xs,
  },
  clearBtn: {
    padding: Spacing.xs,
  },
  counter: {
    marginTop: Spacing.xs,
    alignSelf: 'flex-end',
  },
  counterText: {
    color: Colors.textSecondary,
  },
});

export default SearchBar;
