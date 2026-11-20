// src/app/_layout.tsx
import 'react-native-gesture-handler';
import { Drawer } from 'expo-router/drawer';
import React from 'react';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Spacing } from '@/constants/colors';
import { Sidebar } from '@/components/Sidebar';

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
    <Drawer
      screenOptions={{
        headerStyle: {
          backgroundColor: Colors.surface,
          borderBottomWidth: 1,
          borderBottomColor: Colors.divider,
        },
        headerTitleStyle: {
          color: Colors.textPrimary,
          fontWeight: '600',
        },
        headerTintColor: Colors.textPrimary,
        drawerStyle: {
          backgroundColor: Colors.sidebarBg,
          width: 280,
        },
        drawerContentStyle: {
          flex: 1,
        },
        drawerActiveBackgroundColor: Colors.surfaceHover,
        drawerInactiveTintColor: Colors.textSecondary,
        drawerActiveTintColor: Colors.primary,
        drawerItemStyle: {
          paddingHorizontal: Spacing.md,
          marginVertical: Spacing.xs,
        },
        drawerLabelStyle: {
          fontSize: 14,
          fontWeight: '500',
        },
      }}
      drawerContent={(props) => <Sidebar {...props} />}
    >
      <Drawer.Screen
        name="(tabs)"
        options={{
          drawerLabel: 'Biblioteca',
          drawerIcon: ({ focused, color, size }) => (
            <Ionicons name={focused ? 'library' : 'library-outline'} size={size} color={color} />
          ),
        }}
      />
      <Drawer.Screen
        name="settings"
        options={{
          drawerLabel: 'Configurações',
          drawerIcon: ({ focused, color, size }) => (
            <Ionicons name={focused ? 'settings' : 'settings-outline'} size={size} color={color} />
          ),
        }}
      />
    </Drawer>
    </GestureHandlerRootView>
  );
}
