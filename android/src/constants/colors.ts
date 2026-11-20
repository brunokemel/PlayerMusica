// src/constants/colors.ts
export const Colors = {
  // Dark Mode Palette (inspired by Google Play Music)
  background: '#121212',
  surface: '#181818',
  surfaceElevated: '#1E1E1E',
  surfaceHover: '#2A2A2A',
  
  // Primary - Google Play Music Orange
  primary: '#FF5722',
  primaryLight: '#FF7043',
  primaryDark: '#E64A19',
  
  // Text
  textPrimary: '#FFFFFF',
  textSecondary: '#B3B3B3',
  textDisabled: '#757575',
  textOnPrimary: '#FFFFFF',
  
  // Borders & Dividers
  border: '#333333',
  divider: '#2A2A2A',
  
  // States
  error: '#CF6679',
  success: '#4CAF50',
  warning: '#FFB74D',
  
  // Player Bar
  playerBarBg: '#181818',
  playerBarBorder: '#2A2A2A',
  
  // Sidebar
  sidebarBg: '#181818',
  sidebarActive: '#FF5722',
  
  // Search
  searchBg: '#1E1E1E',
  searchBorder: '#333333',
  searchFocusBorder: '#FF5722',
};

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const BorderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  round: 9999,
};

export const Typography = {
  h1: { fontSize: 28, fontWeight: '700' as const, lineHeight: 36 },
  h2: { fontSize: 22, fontWeight: '600' as const, lineHeight: 30 },
  h3: { fontSize: 18, fontWeight: '600' as const, lineHeight: 24 },
  body1: { fontSize: 16, fontWeight: '400' as const, lineHeight: 24 },
  body2: { fontSize: 14, fontWeight: '400' as const, lineHeight: 20 },
  caption: { fontSize: 12, fontWeight: '400' as const, lineHeight: 16 },
  button: { fontSize: 14, fontWeight: '600' as const, lineHeight: 20, letterSpacing: 0.5 },
  overline: { fontSize: 10, fontWeight: '500' as const, lineHeight: 16, letterSpacing: 1.5, textTransform: 'uppercase' as const },
};