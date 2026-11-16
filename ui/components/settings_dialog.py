"""
Diálogo Modal de Configurações (SettingsDialog) do PlayMusica.
Permite ao usuário selecionar uma nova pasta raiz de músicas pelo Windows Explorer,
digitar/colar um caminho manualmente e salvar diretamente no config.json.
"""

import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.config import ConfigManager
from ui.icons import IconFactory
from ui.theme import (
    ACCENT_COLOR,
    ACCENT_HOVER,
    BG_CARD,
    BORDER_COLOR,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


# =============================================================================
# BLOCO 1: Classe SettingsDialog e Sinais
# =============================================================================

class SettingsDialog(QDialog):
    """
    Modal de preferências de diretório.
    Atualiza imediatamente o config.json e dispara sinal para reindexar a biblioteca.
    """

    # Sinal emitido com o novo caminho validado da pasta
    directory_changed = Signal(str)

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Configurações - PlayMusica")
        self.setFixedSize(540, 280)
        # Remove o botão '?' de ajuda do cabeçalho da janela do Windows
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self._setup_ui()

    # =========================================================================
    # BLOCO 2: Construção da Interface do Diálogo
    # =========================================================================

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Título da janela modal
        title_lbl = QLabel("Configuração da Biblioteca de Música")
        title_lbl.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: bold;")
        layout.addWidget(title_lbl)

        # Texto explicativo
        desc_lbl = QLabel(
            "Selecione ou cole o caminho da pasta onde estão seus arquivos de áudio (.mp3, .wav, .flac). "
            "As alterações são salvas automaticamente no config.json ao lado do executável."
        )
        desc_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; line-height: 1.4;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        # Linha com campo de texto e botão 'Procurar...'
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(8)

        self.path_input = QLineEdit()
        self.path_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {BG_CARD};
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 1px solid {ACCENT_COLOR};
            }}
        """)
        # Preenche com o caminho atual do config.json
        self.path_input.setText(self.config_manager.music_directory)

        btn_browse = QPushButton("Procurar...")
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.setIcon(IconFactory.get_icon("folder", size=16, color=TEXT_PRIMARY))
        btn_browse.setStyleSheet(f"""
            QPushButton {{
                background-color: #2E2E2E;
                color: {TEXT_PRIMARY};
                border: 1px solid {BORDER_COLOR};
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #3C3C3C;
            }}
        """)
        btn_browse.clicked.connect(self._browse_directory)

        input_layout.addWidget(self.path_input, stretch=1)
        input_layout.addWidget(btn_browse)
        layout.addWidget(input_container)

        # Rótulo informativo exibindo o local físico exato do config.json
        cfg_loc = QLabel(f"Arquivo de configuração: {self.config_manager.config_path}")
        cfg_loc.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        cfg_loc.setWordWrap(True)
        layout.addWidget(cfg_loc)

        layout.addStretch()

        # Botões de Ação Inferiores (Cancelar e Salvar)
        button_container = QWidget()
        btn_layout = QHBoxLayout(button_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {TEXT_SECONDARY};
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: #282828;
                color: {TEXT_PRIMARY};
            }}
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Salvar e Reindexar")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_COLOR};
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_HOVER};
            }}
        """)
        btn_save.clicked.connect(self._save_and_close)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)
        layout.addWidget(button_container)

    # =========================================================================
    # BLOCO 3: Handlers de Eventos do Diálogo
    # =========================================================================

    def _browse_directory(self):
        """Abre a janela nativa do Windows para seleção visual de pastas."""
        curr = self.path_input.text()
        start_dir = curr if os.path.isdir(curr) else os.path.expanduser("~")
        chosen = QFileDialog.getExistingDirectory(self, "Selecionar Pasta de Músicas", start_dir)
        if chosen:
            self.path_input.setText(os.path.normpath(chosen))

    def _save_and_close(self):
        """Valida se o caminho inserido existe no disco antes de salvar no config.json."""
        new_path = os.path.normpath(self.path_input.text().strip())
        if new_path and os.path.isdir(new_path):
            self.config_manager.music_directory = new_path
            self.directory_changed.emit(new_path)
            self.accept()
        else:
            # Borda vermelha de alerta em caso de pasta inválida
            self.path_input.setStyleSheet("border: 1px solid #FF5252;")
