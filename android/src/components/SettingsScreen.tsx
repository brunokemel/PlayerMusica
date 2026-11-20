// src/components/SettingsScreen.tsx
import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert, Modal, TextInput, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, Spacing, BorderRadius, Typography } from '@/constants/colors';
import { getConfig, setMusicDirectory, saveConfig, getMusicDirectory, clearConfig } from '@/utils/storage';
import { useLibraryStore } from '@/store/useLibraryStore';
import { useLibraryScanner } from '@/hooks/useLibraryScanner';

export const SettingsScreen: React.FC = () => {
  const [visible, setVisible] = useState(false);
  const [inputDir, setInputDir] = useState('');
  const [config, setConfig] = useState(getConfig());
  const { allTracks } = useLibraryStore();
  const { scanLibrary } = useLibraryScanner();

  useEffect(() => {
    if (visible) {
      setInputDir(config.musicDirectory);
    }
  }, [visible, config]);

  const handleOpen = () => {
    setConfig(getConfig());
    setVisible(true);
  };

  const handleClose = () => {
    setVisible(false);
  };

  const handleSaveDirectory = () => {
    setMusicDirectory(inputDir.trim());
    setConfig(getConfig());
    handleClose();
    void scanLibrary();
    Alert.alert('Biblioteca atualizada', 'A lista de músicas foi reindexada.');
  };

  const handleResetConfig = () => {
    Alert.alert(
      'Confirmar',
      'Isso restaurará todas as configurações padrão. Deseja continuar?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { text: 'Confirmar', onPress: () => {
            clearConfig();
            setConfig(getConfig());
            Alert.alert('Configurações restauradas', 'Os valores padrão foram aplicados.');
          } },
      ]
    );
  };

  return (
    <>
      <TouchableOpacity onPress={handleOpen} style={styles.settingsBtn} accessible accessibilityLabel="Configurações">
        <Ionicons name="settings" size={24} color={Colors.textSecondary} />
      </TouchableOpacity>

      <Modal visible={visible} animationType="slide" transparent={true} onRequestClose={handleClose}>
        <TouchableOpacity onPress={handleClose} style={styles.modalOverlay} activeOpacity={1}>
          <View style={styles.modalContainer}>
            <View style={styles.modalHeader}>
              <Text style={[styles.modalTitle, Typography.h3]}>Configurações</Text>
              <TouchableOpacity onPress={handleClose} style={styles.closeBtn}>
                <Ionicons name="close" size={24} color={Colors.textSecondary} />
              </TouchableOpacity>
            </View>

            <ScrollView contentContainerStyle={styles.modalContent}>
              <View style={styles.section}>
                <Text style={[styles.sectionTitle, Typography.overline]}>Biblioteca de Música</Text>
                <View style={styles.inputGroup}>
                  <Text style={[styles.label, Typography.body2]}>Pasta de músicas</Text>
                  <TextInput
                    style={styles.textInput}
                    value={inputDir}
                    onChangeText={setInputDir}
                    placeholder="Caminho da pasta (ex: /storage/emulated/0/Music)"
                    autoCapitalize="none"
                    editable
                  />
                  <View style={styles.inputHint}>
                    <Text style={[styles.hintText, Typography.caption]}>
                      Deixe em branco para usar a pasta padrão do sistema
                    </Text>
                  </View>
                </View>
                <TouchableOpacity onPress={handleSaveDirectory} style={styles.saveBtn}>
                  <Text style={[styles.saveBtnText, Typography.button]}>Salvar pasta</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.section}>
                <Text style={[styles.sectionTitle, Typography.overline]}>Reprodução</Text>
                <View style={styles.configRow}>
                  <Text style={[styles.configLabel, Typography.body1]}>Volume padrão</Text>
                  <Text style={[styles.configValue, Typography.body1]}>{Math.round(config.volume * 100)}%</Text>
                </View>
                <View style={styles.configRow}>
                  <Text style={[styles.configLabel, Typography.body1]}>Shuffle</Text>
                  <Text style={[styles.configValue, Typography.body1]}>{config.shuffle ? 'Ativado' : 'Desativado'}</Text>
                </View>
                <View style={styles.configRow}>
                  <Text style={[styles.configLabel, Typography.body1]}>Repetição</Text>
                  <Text style={[styles.configValue, Typography.body1]}>{config.repeatMode === 'one' ? 'Uma faixa' : config.repeatMode === 'all' ? 'Todas' : 'Desligado'}</Text>
                </View>
              </View>

              <View style={styles.section}>
                <Text style={[styles.sectionTitle, Typography.overline]}>Estatísticas</Text>
                <View style={styles.configRow}>
                  <Text style={[styles.configLabel, Typography.body1]}>Faixas na biblioteca</Text>
                  <Text style={[styles.configValue, Typography.body1]}>{allTracks.length}</Text>
                </View>
              </View>

              <View style={styles.section}>
                <Text style={[styles.sectionTitle, Typography.overline]}>Avançado</Text>
                <TouchableOpacity onPress={handleResetConfig} style={styles.dangerBtn}>
                  <Text style={[styles.dangerBtnText, Typography.button]}>Restaurar padrões</Text>
                </TouchableOpacity>
              </View>
            </ScrollView>
          </View>
        </TouchableOpacity>
      </Modal>
    </>
  );
};

const styles = StyleSheet.create({
  settingsBtn: {
    padding: Spacing.sm,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'flex-end',
  },
  modalContainer: {
    backgroundColor: Colors.surface,
    borderTopLeftRadius: BorderRadius.xl,
    borderTopRightRadius: BorderRadius.xl,
    maxHeight: '85%',
    width: '100%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.divider,
  },
  modalTitle: {
    color: Colors.textPrimary,
  },
  closeBtn: {
    padding: Spacing.xs,
  },
  modalContent: {
    padding: Spacing.md,
  },
  section: {
    marginBottom: Spacing.xl,
  },
  sectionTitle: {
    color: Colors.textSecondary,
    marginBottom: Spacing.md,
  },
  inputGroup: {
    marginBottom: Spacing.md,
  },
  label: {
    color: Colors.textSecondary,
    marginBottom: Spacing.xs,
  },
  textInput: {
    backgroundColor: Colors.surfaceElevated,
    borderRadius: BorderRadius.md,
    borderWidth: 1,
    borderColor: Colors.border,
    padding: Spacing.sm,
    color: Colors.textPrimary,
    fontSize: 14,
  },
  inputHint: {
    marginTop: Spacing.xs,
  },
  hintText: {
    color: Colors.textDisabled,
  },
  saveBtn: {
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.md,
    padding: Spacing.sm,
    alignItems: 'center',
  },
  saveBtnText: {
    color: Colors.textOnPrimary,
  },
  configRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: Spacing.xs,
    borderBottomWidth: 1,
    borderBottomColor: Colors.divider,
  },
  configLabel: {
    color: Colors.textPrimary,
  },
  configValue: {
    color: Colors.textSecondary,
  },
  dangerBtn: {
    backgroundColor: Colors.error,
    borderRadius: BorderRadius.md,
    padding: Spacing.sm,
    alignItems: 'center',
    marginTop: Spacing.sm,
  },
  dangerBtnText: {
    color: Colors.textOnPrimary,
  },
});

export default SettingsScreen;
