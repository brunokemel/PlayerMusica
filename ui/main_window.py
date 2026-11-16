"""
Janela Principal (MainWindow) do PlayMusica.
Orquestra todos os componentes visuais (Sidebar, Tabela, Barra de Busca e PlayerBar),
gerencia os atalhos de teclado globais e conecta a camada de apresentação ao AudioEngine.
"""

import os
from typing import List, Optional
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFrame,
    QMainWindow,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from core.audio_engine import AudioEngine
from core.config import ConfigManager
from core.models import FolderNode, Track
from core.scanner import LibraryScannerWorker
from ui.components.player_bar import PlayerBar
from ui.components.search_bar import SearchBar
from ui.components.settings_dialog import SettingsDialog
from ui.components.sidebar import Sidebar
from ui.components.track_table import TrackTable
from ui.icons import IconFactory
from ui.theme import MAIN_STYLESHEET


# =============================================================================
# BLOCO 1: Classe MainWindow e Inicialização de Estado
# =============================================================================

class MainWindow(QMainWindow):
    """
    Controlador mestre da janela do aplicativo.
    Responsável por gerenciar os dados da biblioteca, filtros e ciclo de vida do app.
    """

    def __init__(self, config_manager: ConfigManager) -> None:
        super().__init__()
        self.config_manager = config_manager
        self.setWindowTitle("PlayMusica")

        # Restaura tamanho e estado maximizado da janela salvos na última sessão
        w = self.config_manager.get("window_width", 1120)
        h = self.config_manager.get("window_height", 720)
        self.resize(w, h)
        if self.config_manager.get("is_maximized", False):
            self.showMaximized()

        # Define o ícone de janela e barra de tarefas do Windows
        self.setWindowIcon(IconFactory.get_icon("music_library", size=32, color="#FF5722"))

        # Inicializa o motor de áudio nativo com as preferências salvas no config.json
        self.audio_engine = AudioEngine(
            initial_volume=self.config_manager.volume,
            shuffle=self.config_manager.shuffle,
            repeat_mode=self.config_manager.repeat_mode,
        )

        # Estado da biblioteca na memória RAM
        self._all_tracks: List[Track] = []
        self._current_folder_filter: Optional[str] = None
        self._current_search_query: str = ""
        self._scanner_worker: Optional[LibraryScannerWorker] = None

        # Montagem dos componentes e conexões
        self._setup_ui()
        self._setup_shortcuts()
        self._wire_signals()

        # Aplica a folha de estilos global do Dark Mode
        self.setStyleSheet(MAIN_STYLESHEET)

        # Inicializa a barra de reprodução com os valores salvos
        self.player_bar.update_volume_display(self.audio_engine.volume)
        self.player_bar.update_shuffle_state(self.audio_engine.shuffle)
        self.player_bar.update_repeat_state(self.audio_engine.repeat_mode)

        # Dispara o escaneamento inicial assíncrono da pasta de músicas
        self.start_library_scan(self.config_manager.music_directory)

    # =========================================================================
    # BLOCO 2: Construção da Estrutura de Layout da Interface
    # =========================================================================

    def _setup_ui(self) -> None:
        central_widget = QWidget()
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Divisor horizontal ajustável: Painel Lateral (Esquerda) + Área Central
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # 1. Painel Lateral Esquerdo (Navegação de Pastas)
        self.sidebar = Sidebar()
        splitter.addWidget(self.sidebar)

        # 2. Área Central (Barra de Busca Superior + Tabela de Músicas)
        center_frame = QFrame()
        center_frame.setObjectName("CenterFrame")
        center_layout = QVBoxLayout(center_frame)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        self.search_bar = SearchBar()
        center_layout.addWidget(self.search_bar)

        self.track_table = TrackTable()
        center_layout.addWidget(self.track_table, stretch=1)

        splitter.addWidget(center_frame)
        splitter.setStretchFactor(0, 0)  # Sidebar mantém largura padrão
        splitter.setStretchFactor(1, 1)  # Área central expande para preencher

        root_layout.addWidget(splitter, stretch=1)

        # 3. Barra de Reprodução Fixa Inferior (Player Bar)
        self.player_bar = PlayerBar()
        root_layout.addWidget(self.player_bar)

        self.setCentralWidget(central_widget)

    # =========================================================================
    # BLOCO 3: Mapeamento de Atalhos Globais de Teclado
    # =========================================================================

    def _setup_shortcuts(self) -> None:
        """Configura os atalhos de teclado principais."""
        # Ctrl + F: Foca imediatamente no campo de busca
        sc_search = QShortcut(QKeySequence("Ctrl+F"), self)
        sc_search.activated.connect(self.search_bar.focus_search)

        # Ctrl + Seta Esquerda: Faixa Anterior
        sc_prev = QShortcut(QKeySequence("Ctrl+Left"), self)
        sc_prev.activated.connect(self.audio_engine.previous_track)

        # Ctrl + Seta Direita: Próxima Faixa
        sc_next = QShortcut(QKeySequence("Ctrl+Right"), self)
        sc_next.activated.connect(self.audio_engine.next_track)

    def keyPressEvent(self, event) -> None:
        """Captura teclas de ação rápida (Espaço, Setas e Escape)."""
        # Tecla Espaço: Play / Pause (ignora se o usuário estiver digitando na busca)
        if event.key() == Qt.Key.Key_Space:
            if not self.search_bar.input_field.hasFocus():
                self.audio_engine.toggle_play_pause()
                event.accept()
                return

        # Seta Esquerda e Direita: Avança ou retrocede 5 segundos na música
        if event.key() == Qt.Key.Key_Left and not self.search_bar.input_field.hasFocus():
            pos = self.audio_engine.player.position()
            self.audio_engine.seek(max(0, pos - 5000))
            event.accept()
            return
        elif event.key() == Qt.Key.Key_Right and not self.search_bar.input_field.hasFocus():
            pos = self.audio_engine.player.position()
            self.audio_engine.seek(pos + 5000)
            event.accept()
            return

        # Seta Cima e Baixo: Ajusta o volume em +/- 5%
        if event.key() == Qt.Key.Key_Up and not self.search_bar.input_field.hasFocus():
            new_vol = min(1.0, self.audio_engine.volume + 0.05)
            self.audio_engine.set_volume(new_vol)
            self.config_manager.volume = new_vol
            event.accept()
            return
        elif event.key() == Qt.Key.Key_Down and not self.search_bar.input_field.hasFocus():
            new_vol = max(0.0, self.audio_engine.volume - 0.05)
            self.audio_engine.set_volume(new_vol)
            self.config_manager.volume = new_vol
            event.accept()
            return

        # Tecla Escape: Limpa o campo de busca e devolve o foco para a lista de faixas
        if event.key() == Qt.Key.Key_Escape:
            self.search_bar.clear()
            self.track_table.setFocus()
            event.accept()
            return

        super().keyPressEvent(event)

    # =========================================================================
    # BLOCO 4: Conexão de Sinais entre Componentes (Arquitetura Reativa)
    # =========================================================================

    def _wire_signals(self) -> None:
        # 1. Eventos emitidos pelo AudioEngine para atualizar a UI
        self.audio_engine.track_changed.connect(self.player_bar.update_track)
        self.audio_engine.track_changed.connect(self.track_table.set_active_track)
        self.audio_engine.state_changed.connect(self.player_bar.update_playback_state)
        self.audio_engine.position_changed.connect(self.player_bar.update_position)
        self.audio_engine.duration_changed.connect(self.player_bar.update_duration)
        self.audio_engine.volume_changed.connect(self.player_bar.update_volume_display)
        self.audio_engine.shuffle_changed.connect(self.player_bar.update_shuffle_state)
        self.audio_engine.repeat_changed.connect(self.player_bar.update_repeat_state)

        # 2. Eventos da PlayerBar enviados para o AudioEngine
        self.player_bar.play_pause_clicked.connect(self.audio_engine.toggle_play_pause)
        self.player_bar.next_clicked.connect(self.audio_engine.next_track)
        self.player_bar.previous_clicked.connect(self.audio_engine.previous_track)
        self.player_bar.seek_requested.connect(self.audio_engine.seek)

        # 3. Preferências e alternâncias
        self.player_bar.shuffle_toggled.connect(self._on_shuffle_toggled)
        self.player_bar.repeat_toggled.connect(self._on_repeat_toggled)
        self.player_bar.volume_changed.connect(self._on_volume_changed)

        # 4. Abertura do diálogo de configurações
        self.player_bar.settings_clicked.connect(self._open_settings)
        self.sidebar.change_folder_requested.connect(self._open_settings)

        # 5. Seleção e clique duplo na tabela de faixas
        self.track_table.track_double_clicked.connect(self._on_track_selected_from_table)
        self.track_table.play_requested.connect(self._on_track_selected_from_table)

        # 6. Navegação na árvore de pastas da Sidebar
        self.sidebar.all_tracks_selected.connect(self._on_all_tracks_selected)
        self.sidebar.folder_selected.connect(self._on_folder_selected)

        # 7. Busca em tempo real
        self.search_bar.search_changed.connect(self._on_search_query_changed)

    # =========================================================================
    # BLOCO 5: Varredura Assíncrona e Atualização da Biblioteca
    # =========================================================================

    def start_library_scan(self, directory: str) -> None:
        """Inicia o scanner em uma QThread dedicada para não travar a UI."""
        # Se um scanner anterior estiver rodando, interrompe com segurança
        if self._scanner_worker and self._scanner_worker.isRunning():
            self._scanner_worker.requestInterruption()
            self._scanner_worker.wait()

        self.sidebar.set_directory_display(directory)
        self.sidebar.show_scanning(True, "Indexando arquivos de áudio...")

        self._scanner_worker = LibraryScannerWorker(directory)
        self._scanner_worker.progress.connect(self._on_scan_progress)
        self._scanner_worker.finished.connect(self._on_scan_finished)
        self._scanner_worker.error.connect(self._on_scan_error)
        self._scanner_worker.start()

    def _on_scan_progress(self, count: int, current_folder: str) -> None:
        """Atualiza a mensagem de status da sidebar durante a indexação."""
        self.sidebar.show_scanning(True, f"Indexando ({count} faixas)...")

    def _on_scan_finished(self, tracks: List[Track], folder_tree: FolderNode) -> None:
        """Chamado quando todas as pastas e arquivos foram lidos."""
        self._all_tracks = tracks
        self.sidebar.show_scanning(False, f"{len(tracks)} faixas carregadas")
        self.sidebar.populate_tree(len(tracks), folder_tree)

        # Reseta os filtros e atualiza a exibição da tabela
        self._current_folder_filter = None
        self._apply_filters()

        # Se nenhuma música estiver tocando, define a biblioteca como fila padrão
        if not self.audio_engine.current_track and tracks:
            self.audio_engine.set_playlist(tracks, start_index=-1)

    def _on_scan_error(self, message: str) -> None:
        """Trata possíveis erros ao acessar a pasta selecionada."""
        self.sidebar.show_scanning(False, "Erro ao ler pasta")

    # =========================================================================
    # BLOCO 6: Filtragem Combinada (Pasta + Texto de Busca)
    # =========================================================================

    def _apply_filters(self) -> None:
        """
        Combina o filtro de diretório selecionado na barra lateral com o texto
        digitado no campo de busca, atualizando a tabela instantaneamente.
        """
        filtered = self._all_tracks

        # Filtro 1: Diretório específico selecionado na árvore lateral
        if self._current_folder_filter:
            norm_filter = os.path.normpath(self._current_folder_filter)
            filtered = [
                t for t in filtered
                if os.path.normpath(t.file_path).startswith(norm_filter)
            ]

        # Filtro 2: Texto de busca em tempo real
        if self._current_search_query:
            filtered = [t for t in filtered if t.matches_query(self._current_search_query)]

        # Preenche a tabela com as faixas resultantes
        self.track_table.populate(filtered)
        self.search_bar.set_track_count(len(filtered), len(self._all_tracks))

    def _on_search_query_changed(self, query: str) -> None:
        """Disparado quando o usuário digita na busca."""
        self._current_search_query = query
        self._apply_filters()

    def _on_all_tracks_selected(self) -> None:
        """Remove o filtro de pasta específica para exibir toda a biblioteca."""
        self._current_folder_filter = None
        self._apply_filters()

    def _on_folder_selected(self, folder_path: str) -> None:
        """Aplica o filtro da pasta clicada na barra lateral."""
        self._current_folder_filter = folder_path
        self._apply_filters()

    def _on_track_selected_from_table(self, track: Track) -> None:
        """
        Quando o usuário dá duplo-clique em uma música:
        Define a lista atualmente visível na tabela como a nova fila de reprodução
        e inicia imediatamente a faixa selecionada.
        """
        displayed = self.track_table.get_displayed_tracks()
        try:
            idx = displayed.index(track)
        except ValueError:
            idx = 0
        self.audio_engine.set_playlist(displayed, start_index=idx)

    # =========================================================================
    # BLOCO 7: Ajuste de Configurações e Persistência no config.json
    # =========================================================================

    def _on_shuffle_toggled(self) -> None:
        is_shuffled = self.audio_engine.toggle_shuffle()
        self.config_manager.shuffle = is_shuffled

    def _on_repeat_toggled(self) -> None:
        mode = self.audio_engine.cycle_repeat_mode()
        self.config_manager.repeat_mode = mode

    def _on_volume_changed(self, val: float) -> None:
        self.audio_engine.set_volume(val)
        self.config_manager.volume = val

    def _open_settings(self) -> None:
        """Abre o diálogo modal de configuração da biblioteca."""
        dlg = SettingsDialog(self.config_manager, self)
        dlg.directory_changed.connect(self._on_directory_changed_from_settings)
        dlg.exec()

    def _on_directory_changed_from_settings(self, new_dir: str) -> None:
        """Chamado quando o usuário escolhe uma nova pasta no modal de configurações."""
        self.start_library_scan(new_dir)

    # =========================================================================
    # BLOCO 8: Encerramento Seguro da Aplicação (closeEvent)
    # =========================================================================

    def closeEvent(self, event) -> None:
        """
        Executado ao fechar a janela:
        1. Salva dimensões atuais da janela no config.json para a próxima execução.
        2. Interrompe graciosamente qualquer thread de escaneamento em andamento.
        3. Para o motor de áudio.
        """
        if not self.isMaximized():
            self.config_manager.set("window_width", self.width(), auto_save=False)
            self.config_manager.set("window_height", self.height(), auto_save=False)
        self.config_manager.set("is_maximized", self.isMaximized(), auto_save=False)
        self.config_manager.save()

        # Interrompe o scanner caso ainda esteja indexando
        if self._scanner_worker and self._scanner_worker.isRunning():
            self._scanner_worker.requestInterruption()
            self._scanner_worker.wait(1000)

        # Para o áudio
        self.audio_engine.stop()
        super().closeEvent(event)
