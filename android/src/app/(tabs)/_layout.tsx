// src/app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';
import React from 'react';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Spacing } from '@/constants/colors';
import { PlayerBar } from '@/components/PlayerBar';

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: Colors.primary,
        tabBarInactiveTintColor: Colors.textSecondary,
        tabBarStyle: {
          backgroundColor: Colors.surface,
          borderTopWidth: 1,
          borderTopColor: Colors.divider,
          paddingBottom: Spacing.xs + 20, // Safe area
          height: 60 + 20,
        },
        tabBarLabelStyle: {
          fontSize: 11,
          fontWeight: '600',
          marginTop: 2,
        },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Biblioteca',
          tabBarIcon: ({ focused, color, size }) => (
            <Ionicons name={focused ? 'musical-notes' : 'musical-notes-outline'} size={size} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}
