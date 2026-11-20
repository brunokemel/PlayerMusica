// src/components/Sidebar.tsx
import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { DrawerContentComponentProps, DrawerContentScrollView, DrawerItemList } from '@react-navigation/drawer';
import { Colors, Spacing, BorderRadius, Typography } from '@/constants/colors';
import { useLibraryStore } from '@/store/useLibraryStore';
import { getMusicDirectory } from '@/utils/storage';

interface FolderItem {
  path: string;
  name: string;
  count: number;
  level: number;
  isExpanded: boolean;
  children: FolderItem[];
}

export const Sidebar: React.FC<DrawerContentComponentProps> = (props) => {
  const {
    allTracks,
    folderTree,
    currentFolderFilter,
    setCurrentFolderFilter,
    isScanning,
    scanProgress,
  } = useLibraryStore();

  const musicDir = getMusicDirectory();

  const buildFolderItems = (): FolderItem[] => {
    const items: FolderItem[] = [];
    // Root "Todas as músicas" item
    items.push({
      path: '',
      name: 'Todas as músicas',
      count: allTracks.length,
      level: 0,
      isExpanded: true,
      children: [],
    });

    if (folderTree.size > 0) {
      // Convert folderTree Map to tree structure
      const folderArray = Array.from(folderTree.entries()).sort((a, b) => a[0].localeCompare(b[0]));
      
      const pathToItem = new Map<string, FolderItem>();
      
      // Create items for all folders
      for (const [path, data] of folderArray) {
        const level = path.split('/').length;
        pathToItem.set(path, {
          path,
          name: data.name,
          count: data.count,
          level,
          isExpanded: level <= 1,
          children: [],
        });
      }

      // Build hierarchy
      for (const [path, item] of pathToItem) {
        const parts = path.split('/');
        if (parts.length === 1) {
          items[0].children.push(item);
        } else {
          const parentPath = parts.slice(0, -1).join('/');
          const parent = pathToItem.get(parentPath);
          if (parent) {
            parent.children.push(item);
          }
        }
      }
    }

    return items;
  };

  const folderItems = buildFolderItems();
  const [expandedFolders, setExpandedFolders] = React.useState<Set<string>>(new Set(['']));

  const toggleFolder = (path: string) => {
    setExpandedFolders(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const renderFolder = (item: FolderItem, index: number): React.ReactElement => {
    const isSelected = currentFolderFilter === item.path;
    const hasChildren = item.children.length > 0;
    const isExpanded = expandedFolders.has(item.path);

    return (
      <View key={`${item.path}-${index}`} style={styles.folderContainer}>
        <TouchableOpacity
          style={[
            styles.folderRow,
            isSelected && styles.folderRowSelected,
            { paddingLeft: Spacing.md + item.level * Spacing.md },
          ]}
          onPress={() => {
            setCurrentFolderFilter(item.path || null);
            if (hasChildren) {
              toggleFolder(item.path);
            }
          }}
          activeOpacity={0.8}
        >
          {hasChildren && (
            <Ionicons
              name={isExpanded ? 'chevron-down' : 'chevron-forward'}
              size={18}
              color={Colors.textSecondary}
              style={styles.chevron}
            />
          )}
          {!hasChildren && <View style={styles.chevronPlaceholder} />}
          
          <Ionicons
            name={item.path === '' ? 'musical-notes' : 'folder-outline'}
            size={20}
            color={isSelected ? Colors.primary : Colors.textSecondary}
            style={styles.folderIcon}
          />
          
          <Text
            style={[
              styles.folderName,
              isSelected && styles.folderNameSelected,
            ]}
            numberOfLines={1}
          >
            {item.name}
          </Text>
          
          <Text style={styles.folderCount}>
            {item.count}
          </Text>
        </TouchableOpacity>

        {hasChildren && isExpanded && (
          <View>
            {item.children.map((child, i) => renderFolder(child, i))}
          </View>
        )}
      </View>
    );
  };

  return (
    <DrawerContentScrollView {...props} style={styles.container}>
      <DrawerItemList {...props} />
      <View style={styles.header}>
        <Text style={[styles.headerTitle, Typography.h3]}>Biblioteca</Text>
        {musicDir && (
          <Text style={[styles.headerSubtitle, Typography.caption]}>{musicDir}</Text>
        )}
      </View>
      
      <View style={styles.divider} />
      
      <View style={styles.listContent}>
        {folderItems.map((item, index) => renderFolder(item, index))}
      </View>
      {isScanning && (
        <View style={styles.scanningContainer}>
          <Ionicons name="refresh" size={24} color={Colors.primary} style={styles.spinningIcon} />
          <Text style={[styles.scanningText, Typography.body2]}>{scanProgress}</Text>
        </View>
      )}
    </DrawerContentScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.sidebarBg,
    borderRightWidth: 1,
    borderRightColor: Colors.border,
  },
  header: {
    padding: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.divider,
  },
  headerTitle: {
    color: Colors.textPrimary,
    marginBottom: Spacing.xs,
  },
  headerSubtitle: {
    color: Colors.textSecondary,
  },
  divider: {
    height: 1,
    backgroundColor: Colors.divider,
  },
  scanningContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Spacing.md,
  },
  spinningIcon: {
    marginBottom: Spacing.sm,
  },
  scanningText: {
    color: Colors.textSecondary,
    textAlign: 'center',
  },
  folderContainer: {
    // Container for folder and its children
  },
  folderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: Spacing.xs,
    minHeight: 40,
    gap: Spacing.xs,
  },
  folderRowSelected: {
    backgroundColor: Colors.surfaceHover,
  },
  chevron: {
    width: 20,
  },
  chevronPlaceholder: {
    width: 20,
  },
  folderIcon: {
    marginRight: Spacing.xs,
  },
  folderName: {
    flex: 1,
    color: Colors.textPrimary,
    fontSize: 14,
  },
  folderNameSelected: {
    color: Colors.primary,
    fontWeight: '600',
  },
  folderCount: {
    color: Colors.textSecondary,
    fontSize: 12,
    fontVariant: ['tabular-nums'],
    minWidth: 28,
    textAlign: 'right',
    marginRight: Spacing.sm,
  },
  listContent: {
    paddingVertical: Spacing.sm,
  },
});

export default Sidebar;
