# 🎵 PlayMusica Mobile - React Native (Expo)

Versão mobile do PlayMusica convertida de Python/PySide6 para React Native com Expo, mantendo a mesma experiência do player desktop.

## 📱 Funcionalidades

- **🎵 Reprodução de áudio nativa** via `expo-av` (MediaPlayer Android / AVPlayer iOS)
- **📁 Biblioteca de mídia** via `expo-media-library` (acesso às músicas do dispositivo)
- **🌙 Dark Mode** com paleta inspirada no Google Play Music (`#121212`, `#FF5722`)
- **🔍 Busca em tempo real** pelo nome do arquivo
- **📂 Navegação por pastas** (Drawer lateral com árvore de diretórios)
- **▶️ Controles completos**: Play/Pause, Anterior/Próxima, Seek, Volume
- **🔀 Reprodução aleatória** e **🔁 Repeat** (Nenhuma / Todas / Uma)
- **⚙️ Configurações persistidas** com MMKV (ultra-rápido)

> A biblioteca do Android entrega nome do arquivo e duração. Leitura de tags ID3 para artista e álbum ainda não está implementada.

## 🛠️ Tecnologias

| Camada | Tecnologia |
|--------|------------|
| Framework | Expo Router (React Native) |
| Navegação | Drawer + Bottom Tabs |
| Estado | Zustand + MMKV (persistência) |
| Áudio | expo-av (Audio.Sound) |
| Mídia | expo-media-library |
| Ícones | @expo/vector-icons (Ionicons) |
| Estilo | StyleSheet (Dark Mode nativo) |

## 📂 Estrutura do Projeto

```
android/
├── app.json              # Configuração Expo
├── eas.json              # Perfis de build EAS
├── package.json
├── package-lock.json       # Dependências reproduzíveis
├── tsconfig.json
├── src/
│   ├── app/
│   │   ├── _layout.tsx           # Root layout (Drawer Navigator)
│   │   ├── (tabs)/
│   │   │   ├── _layout.tsx       # Tabs layout (Bottom tabs)
│   │   │   └── index.tsx         # Home screen (Biblioteca)
│   │   └── settings.tsx          # Tela de configurações
│   ├── components/
│   │   ├── PlayerBar.tsx         # Barra de reprodução fixa
│   │   ├── SearchBar.tsx         # Busca instantânea
│   │   ├── Sidebar.tsx           # Drawer lateral (árvore de pastas)
│   │   ├── TrackRow.tsx          # Linha de faixa na tabela
│   │   ├── TrackTable.tsx        # Lista virtualizada de faixas
│   │   └── SettingsScreen.tsx    # Modal de configurações
│   ├── hooks/
│   │   ├── useAudioPlayer.ts     # Hook do expo-av
│   │   └── useLibraryScanner.ts  # Hook de escaneamento de mídia
│   ├── store/
│   │   ├── usePlayerStore.ts     # Estado do player (Zustand + MMKV)
│   │   └── useLibraryStore.ts    # Estado da biblioteca
│   ├── utils/
│   │   ├── storage.ts            # Wrapper MMKV para config.json
│   │   └── metadata.ts           # Utilitários de metadados/árvore
│   ├── constants/
│   │   ├── colors.ts             # Paleta Dark Mode + spacing
│   │   └── extensions.ts         # Extensões suportadas + formatação
│   └── types/
│       └── index.ts              # Types TypeScript
```

## 🚀 Como Executar

### 1. Pré-requisitos
- Node.js 18+
- Expo CLI: `npm install -g expo-cli`
- EAS CLI: `npm install -g eas-cli`
- Android Studio (para emulador) ou dispositivo físico

### 2. Instalar dependências
```bash
cd android
npm ci
```

### 3. Desenvolvimento
```bash
# Iniciar Metro para um development build instalado no dispositivo
npm start

# Ou direto no Android
npm run android
```

### 4. Gerar APK (EAS Build)

#### Preview (APK interno para teste)
```bash
npm run build:android
# ou
eas build --platform android --profile preview
```

#### Produção (AAB para Play Store)
```bash
npm run build:android:prod
# ou
eas build --platform android --profile production
```

> **Nota**: O app usa MMKV nativo, então precisa de um development build ou APK instalado; não funciona no Expo Go padrão. O EAS Build compila na nuvem.

## 📦 Configuração de Build (eas.json)

| Perfil | Tipo | Uso |
|--------|------|-----|
| `development` | Dev Client | Desenvolvimento com hot reload |
| `preview` | **APK** | Testes internos, instalação direta |
| `production` | **AAB** | Publicação na Play Store |

## 🔧 Permissões Android (app.json)

```json
"android": {
  "permissions": [
    "READ_EXTERNAL_STORAGE",
    "WRITE_EXTERNAL_STORAGE", 
    "READ_MEDIA_AUDIO",
    "FOREGROUND_SERVICE",
    "FOREGROUND_SERVICE_MEDIA_PLAYBACK"
  ]
}
```

## 🎨 Paleta de Cores (Dark Mode)

| Cor | Hex | Uso |
|-----|-----|-----|
| Background | `#121212` | Fundo principal |
| Surface | `#181818` | Cards, Sidebar, PlayerBar |
| Surface Elevated | `#1E1E1E` | Inputs, elementos elevados |
| Primary | `#FF5722` | Laranja Google Play Music |
| Text Primary | `#FFFFFF` | Texto principal |
| Text Secondary | `#B3B3B3` | Texto secundário |

## 🔄 Migração do Desktop (Python → React Native)

| Desktop (PySide6) | Mobile (React Native) |
|-------------------|----------------------|
| `QMediaPlayer` + `QAudioOutput` | `expo-av` `Audio.Sound` |
| `QThread` Scanner | `expo-media-library` `getAssetsAsync` |
| `config.json` (arquivo) | `MMKV` (key-value nativo) |
| `Sidebar` (QTreeView) | `Drawer Navigator` + árvore customizada |
| `TrackTable` (QTableView) | `FlatList` virtualizada |
| `PlayerBar` (QWidget) | Componente fixo no layout |
| ID3 Parser (Python) | Metadados do MediaStore Android |

## 📝 Próximos Passos

- [ ] Implementar parser de metadados local (para arquivos fora do MediaStore)
- [ ] Adicionar equalizador básico
- [ ] Suporte a playlists personalizadas
- [ ] Widget de tela de bloqueio (MediaSession)
- [ ] Sincronização com versão desktop (config.json compartilhado)
- [ ] Tema claro (Light Mode)

## 📄 Licença

MIT - Mesmo esquema do projeto desktop original.
