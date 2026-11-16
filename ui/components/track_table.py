"""
Tabela Virtualizada de Músicas (TrackTable) do PlayMusica.
Renderiza a listagem de faixas com colunas de metadados, destaque visual da faixa
em reprodução, duplo-clique para tocar e menu de contexto com atalhos do Windows Explorer.
"""

import os
import subprocess
from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QColor, QFont
from PySide6.QtWidgets import (
    QApplication,
    QHeaderView,
    QMenu,
    QTableWidget,
    QTableWidgetItem,
)

from core.models import Track
from ui.icons import IconFactory
from ui.theme import ACCENT_COLOR, TEXT_MUTED, TEXT_PRIMARY, TEXT_SECONDARY


# =============================================================================
# BLOCO 1: Classe TrackTable e Definição de Sinais
# =============================================================================

class TrackTable(QTableWidget):
    """
    Tabela customizada para exibição de músicas.
    Herda de QTableWidget com renderização otimizada e colunas responsivas.
    """

    # Sinais emitidos ao selecionar/tocar uma música:
    track_double_clicked = Signal(object)
    play_requested = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._displayed_tracks: List[Track] = []
        self._currently_playing_track: Optional[Track] = None

        self._setup_ui()

    # =========================================================================
    # BLOCO 2: Configuração e Estilização da Tabela
    # =========================================================================

    def _setup_ui(self):
        # 5 Colunas: Índice/Status, Título, Artista, Álbum e Duração
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["#", "TÍTULO", "ARTISTA", "ÁLBUM", "DURAÇÃO"])
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        # Regras de redimensionamento de cada coluna
        header = self.horizontalHeader()
        # Coluna 0 (#): Largura fixa para o número ou ícone equalizador
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(0, 48)

        # Coluna 1 (Título): Estica para ocupar todo o espaço restante
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        # Coluna 2 (Artista) e 3 (Álbum): Largura padrão redimensionável
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.setColumnWidth(2, 190)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.setColumnWidth(3, 190)

        # Coluna 4 (Duração): Largura fixa alinhada ao centro
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.setColumnWidth(4, 75)

        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.setHighlightSections(False)

        # Conexões de eventos de duplo-clique e clique com botão direito
        self.cellDoubleClicked.connect(self._on_cell_double_clicked)
        self.customContextMenuRequested.connect(self._show_context_menu)

    # =========================================================================
    # BLOCO 3: Povoamento e Atualização dos Registros da Tabela
    # =========================================================================

    def populate(self, tracks: List[Track]):
        """
        Preenche as linhas da tabela com os dados da lista de faixas fornecida.
        Aplica formatações de cor, tipografia e ícone na faixa atualmente em reprodução.
        """
        self._displayed_tracks = list(tracks)
        self.setRowCount(len(tracks))
        self.setSortingEnabled(False)

        accent_color = QColor(ACCENT_COLOR)
        primary_color = QColor(TEXT_PRIMARY)
        secondary_color = QColor(TEXT_SECONDARY)
        muted_color = QColor(TEXT_MUTED)

        bold_font = QFont()
        bold_font.setBold(True)
        normal_font = QFont()

        for row, track in enumerate(tracks):
            is_active = (self._currently_playing_track and self._currently_playing_track.id == track.id)

            # Coluna 0: Número da faixa ou Ícone de Equalizador se estiver tocando
            item_num = QTableWidgetItem()
            item_num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if is_active:
                item_num.setIcon(IconFactory.get_icon("playing_indicator", size=16, color=ACCENT_COLOR))
            else:
                item_num.setText(str(row + 1))
                item_num.setForeground(muted_color)
            item_num.setFlags(item_num.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 0, item_num)

            # Coluna 1: Título da faixa (em destaque laranja e negrito se ativa)
            item_title = QTableWidgetItem(track.title)
            if is_active:
                item_title.setForeground(accent_color)
                item_title.setFont(bold_font)
            else:
                item_title.setForeground(primary_color)
                item_title.setFont(normal_font)
            item_title.setToolTip(f"{track.title}\n{track.file_path}")
            item_title.setFlags(item_title.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 1, item_title)

            # Coluna 2: Artista
            item_artist = QTableWidgetItem(track.artist)
            item_artist.setForeground(secondary_color)
            item_artist.setFlags(item_artist.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 2, item_artist)

            # Coluna 3: Álbum
            item_album = QTableWidgetItem(track.album)
            item_album.setForeground(muted_color)
            item_album.setFlags(item_album.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 3, item_album)

            # Coluna 4: Duração formatada (MM:SS)
            item_dur = QTableWidgetItem(track.duration_str)
            item_dur.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_dur.setForeground(muted_color)
            item_dur.setFlags(item_dur.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row, 4, item_dur)

    def set_active_track(self, current_track: Optional[Track]):
        """
        Atualiza o destaque visual da faixa ativa sem recriar todas as células da tabela.
        Operação de altíssima performance (atualização in-place).
        """
        self._currently_playing_track = current_track
        accent_color = QColor(ACCENT_COLOR)
        primary_color = QColor(TEXT_PRIMARY)
        muted_color = QColor(TEXT_MUTED)

        bold_font = QFont()
        bold_font.setBold(True)
        normal_font = QFont()

        for row, track in enumerate(self._displayed_tracks):
            item_num = self.item(row, 0)
            item_title = self.item(row, 1)

            if not item_num or not item_title:
                continue

            # Se esta linha for a música atual:
            if current_track and track.id == current_track.id:
                item_num.setText("")
                item_num.setIcon(IconFactory.get_icon("playing_indicator", size=16, color=ACCENT_COLOR))
                item_title.setForeground(accent_color)
                item_title.setFont(bold_font)
            # Se não for a música atual:
            else:
                item_num.setIcon(IconFactory.get_icon("none", size=0))
                item_num.setText(str(row + 1))
                item_num.setForeground(muted_color)
                item_title.setForeground(primary_color)
                item_title.setFont(normal_font)

    def get_track_at_row(self, row: int) -> Optional[Track]:
        """Recupera o objeto Track associado ao índice de uma linha."""
        if 0 <= row < len(self._displayed_tracks):
            return self._displayed_tracks[row]
        return None

    def get_displayed_tracks(self) -> List[Track]:
        """Retorna a lista atual de faixas visíveis (filtradas)."""
        return list(self._displayed_tracks)

    # =========================================================================
    # BLOCO 4: Eventos de Interação (Duplo-Clique e Menu de Contexto)
    # =========================================================================

    def _on_cell_double_clicked(self, row: int, column: int):
        """Duplo-clique em qualquer coluna da linha inicia a reprodução imediatamente."""
        track = self.get_track_at_row(row)
        if track:
            self.track_double_clicked.emit(track)

    def _show_context_menu(self, pos):
        """Abre o menu flutuante com ações rápidas ao clicar com o botão direito."""
        item = self.itemAt(pos)
        if not item:
            return

        row = item.row()
        track = self.get_track_at_row(row)
        if not track:
            return

        menu = QMenu(self)

        # Ação 1: Reproduzir
        act_play = QAction(IconFactory.get_icon("play", size=16, color=ACCENT_COLOR), "Reproduzir", self)
        act_play.triggered.connect(lambda: self.play_requested.emit(track))
        menu.addAction(act_play)

        menu.addSeparator()

        # Ação 2: Revelar no Windows Explorer
        act_open_dir = QAction(IconFactory.get_icon("folder", size=16, color=TEXT_SECONDARY), "Abrir na Pasta do Windows", self)
        act_open_dir.triggered.connect(lambda: self._open_file_in_explorer(track.file_path))
        menu.addAction(act_open_dir)

        # Ação 3: Copiar caminho para a Área de Transferência
        act_copy_path = QAction("Copiar Caminho do Arquivo", self)
        act_copy_path.triggered.connect(lambda: QApplication.clipboard().setText(track.file_path))
        menu.addAction(act_copy_path)

        menu.exec(self.viewport().mapToGlobal(pos))

    def _open_file_in_explorer(self, file_path: str):
        """Chama nativamente o processo do Windows Explorer destacando o arquivo exato."""
        if not os.path.exists(file_path):
            return
        try:
            # Comando nativo do Windows: explorer /select,"C:\caminho\arquivo.mp3"
            subprocess.Popen(f'explorer /select,"{os.path.normpath(file_path)}"')
        except Exception:
            try:
                os.startfile(os.path.dirname(file_path))
            except Exception:
                pass
