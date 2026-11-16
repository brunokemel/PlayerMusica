"""
Painel Lateral Esquerdo de Navegação (Sidebar) do PlayMusica.
Exibe a marca, atalho para 'Todas as Músicas', a hierarquia de pastas
escaneadas e o botão de atalho para alteração da pasta raiz.
"""

import os
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.models import FolderNode
from ui.icons import IconFactory
from ui.theme import (
    ACCENT_COLOR,
    BG_CARD,
    BORDER_COLOR,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


# =============================================================================
# BLOCO 1: Classe Sidebar e Sinais de Navegação
# =============================================================================

class Sidebar(QFrame):
    """
    Componente da barra lateral esquerda.
    Gerencia a árvore de navegação por diretórios da biblioteca.
    """

    # Sinais emitidos para a janela principal (MainWindow):
    # 1. all_tracks_selected: o usuário quer ver todas as faixas sem filtro de pasta
    all_tracks_selected = Signal()
    # 2. folder_selected: o usuário clicou em uma pasta específica
    folder_selected = Signal(str)
    # 3. change_folder_requested: o usuário clicou para alterar a pasta de músicas
    change_folder_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SidebarFrame")
        self.setFixedWidth(260)
        self._current_path: str = ""
        self._setup_ui()

    # =========================================================================
    # BLOCO 2: Construção da Interface do Painel Lateral
    # =========================================================================

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 12)
        layout.setSpacing(12)

        # ---------------------------------------------------------------------
        # SEÇÃO 1: Cabeçalho com Logo e Título do Aplicativo
        # ---------------------------------------------------------------------
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(4, 0, 4, 0)
        header_layout.setSpacing(10)

        # Ícone de nota musical em destaque laranja
        logo_lbl = QLabel()
        logo_lbl.setPixmap(IconFactory.get_pixmap("music_library", size=28, color=ACCENT_COLOR))

        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(1)
        brand_layout.setContentsMargins(0, 0, 0, 0)

        app_title = QLabel("PlayMusica")
        app_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 16px; font-weight: bold; letter-spacing: 0.5px;")

        app_sub = QLabel("Reprodutor Local")
        app_sub.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")

        brand_layout.addWidget(app_title)
        brand_layout.addWidget(app_sub)

        header_layout.addWidget(logo_lbl)
        header_layout.addLayout(brand_layout)
        header_layout.addStretch()
        layout.addWidget(header_widget)

        # Linha divisória horizontal sutil
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {BORDER_COLOR}; max-height: 1px;")
        layout.addWidget(divider)

        # ---------------------------------------------------------------------
        # SEÇÃO 2: Árvore de Navegação da Biblioteca e Pastas
        # ---------------------------------------------------------------------
        nav_lbl = QLabel("BIBLIOTECA")
        nav_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 10px; font-weight: bold; margin-left: 6px; letter-spacing: 1px;")
        layout.addWidget(nav_lbl)

        # Árvore do Qt (QTreeWidget) estilizada
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setAnimated(True)
        self.tree.setIndentation(16)
        self.tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.tree, stretch=1)

        # ---------------------------------------------------------------------
        # SEÇÃO 3: Barra de Progresso e Mensagem de Escaneamento
        # ---------------------------------------------------------------------
        self.scan_progress = QProgressBar()
        self.scan_progress.setFixedHeight(4)
        self.scan_progress.setTextVisible(False)
        self.scan_progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {BG_CARD};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {ACCENT_COLOR};
                border-radius: 2px;
            }}
        """)
        self.scan_progress.setRange(0, 0)  # Modo indeterminado (animação contínua)
        self.scan_progress.hide()
        layout.addWidget(self.scan_progress)

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; margin-left: 4px;")
        layout.addWidget(self.lbl_status)

        # ---------------------------------------------------------------------
        # SEÇÃO 4: Rodapé com a Pasta Atual e Botão de Alterar Pasta
        # ---------------------------------------------------------------------
        footer_card = QFrame()
        footer_card.setStyleSheet(f"""
            background-color: {BG_CARD};
            border: 1px solid {BORDER_COLOR};
            border-radius: 8px;
            padding: 8px;
        """)
        footer_layout = QVBoxLayout(footer_card)
        footer_layout.setContentsMargins(8, 8, 8, 8)
        footer_layout.setSpacing(6)

        dir_label_title = QLabel("PASTA RAIZ")
        dir_label_title.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 9px; font-weight: bold;")

        self.lbl_current_dir = QLabel("Carregando...")
        self.lbl_current_dir.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px;")
        self.lbl_current_dir.setWordWrap(True)

        btn_change = QPushButton("Alterar Pasta")
        btn_change.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_change.setIcon(IconFactory.get_icon("folder", size=14, color=TEXT_PRIMARY))
        btn_change.setStyleSheet(f"""
            QPushButton {{
                background-color: #2F2F2F;
                color: {TEXT_PRIMARY};
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 11px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #3D3D3D;
            }}
        """)
        btn_change.clicked.connect(self.change_folder_requested.emit)

        footer_layout.addWidget(dir_label_title)
        footer_layout.addWidget(self.lbl_current_dir)
        footer_layout.addWidget(btn_change)

        layout.addWidget(footer_card)

    # =========================================================================
    # BLOCO 3: Métodos de Atualização e Povoamento da Árvore
    # =========================================================================

    def set_directory_display(self, path: str):
        """Atualiza o rótulo do rodapé encurtando caminhos longos."""
        self._current_path = path
        norm = os.path.normpath(path)
        display = "..." + norm[-25:] if len(norm) > 28 else norm
        self.lbl_current_dir.setText(display)
        self.lbl_current_dir.setToolTip(norm)

    def show_scanning(self, is_scanning: bool, message: str = ""):
        """Exibe ou esconde a barra animada de progresso de indexação."""
        if is_scanning:
            self.scan_progress.show()
            self.lbl_status.setText(message or "Escaneando músicas...")
        else:
            self.scan_progress.hide()
            self.lbl_status.setText(message)

    def populate_tree(self, total_tracks: int, root_node: Optional[FolderNode]):
        """
        Gera os itens visuais da árvore de pastas a partir do resultado do scanner.
        1. Item raiz 'Todas as Músicas' com o total.
        2. Ramos recursivos para pastas e subpastas.
        """
        self.tree.clear()

        # Item fixo no topo: Todas as Músicas
        all_item = QTreeWidgetItem(self.tree)
        all_item.setText(0, f"Todas as Músicas ({total_tracks})")
        all_item.setIcon(0, IconFactory.get_icon("music_library", size=16, color=ACCENT_COLOR))
        all_item.setData(0, Qt.ItemDataRole.UserRole, "__ALL__")
        self.tree.setCurrentItem(all_item)

        # Pastas filhas encontradas
        if root_node and root_node.children:
            folders_root = QTreeWidgetItem(self.tree)
            folders_root.setText(0, "Pastas")
            folders_root.setIcon(0, IconFactory.get_icon("folder", size=16, color=TEXT_MUTED))
            folders_root.setData(0, Qt.ItemDataRole.UserRole, "__FOLDERS_HEADER__")
            folders_root.setExpanded(True)

            for child in root_node.children:
                self._add_folder_item(folders_root, child)

    def _add_folder_item(self, parent_item: QTreeWidgetItem, node: FolderNode):
        """Método recursivo que adiciona cada pasta e seus subdiretórios à árvore."""
        item = QTreeWidgetItem(parent_item)
        count_str = f" ({node.track_count})" if node.track_count > 0 else ""
        item.setText(0, f"{node.name}{count_str}")
        item.setIcon(0, IconFactory.get_icon("folder", size=15, color=TEXT_SECONDARY))
        item.setData(0, Qt.ItemDataRole.UserRole, node.full_path)
        item.setExpanded(True)

        for child in node.children:
            self._add_folder_item(item, child)

    # =========================================================================
    # BLOCO 4: Tratamento do Clique em Itens da Árvore
    # =========================================================================

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Dispara os sinais de filtro adequados conforme o item selecionado."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data == "__ALL__":
            self.all_tracks_selected.emit()
        elif data == "__FOLDERS_HEADER__":
            # Alterna expansão da pasta raiz
            item.setExpanded(not item.isExpanded())
        elif isinstance(data, str) and data:
            self.folder_selected.emit(data)
