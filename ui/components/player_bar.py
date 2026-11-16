"""
Barra Inferior Fixa de Reprodução (PlayerBar) do PlayMusica.
Inspirada no clássico Google Play Music: contém informações da faixa atual,
botões de controle centralizados, barra de progresso (seek) e controle de volume.
"""

from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.models import Track
from core.tag_reader import format_duration
from ui.components.slider import ClickableSlider
from ui.icons import IconFactory
from ui.theme import (
    ACCENT_COLOR,
    BG_CARD,
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)


# =============================================================================
# BLOCO 1: Classe PlayerBar e Definição de Sinais
# =============================================================================

class PlayerBar(QFrame):
    """
    Componente fixo no rodapé da janela principal.
    Emite eventos para o AudioEngine e recebe notificações de progresso de áudio.
    """

    # Sinais emitidos em resposta a interações do usuário:
    play_pause_clicked = Signal()
    next_clicked = Signal()
    previous_clicked = Signal()
    shuffle_toggled = Signal()
    repeat_toggled = Signal()
    seek_requested = Signal(int)
    volume_changed = Signal(float)
    settings_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PlayerBarFrame")
        self.setFixedHeight(88)

        self._current_track: Optional[Track] = None
        self._is_seeking = False
        self._is_muted = False
        self._prev_volume = 0.8

        self._setup_ui()

    # =========================================================================
    # BLOCO 2: Construção da Interface Gráfica (Layout em 3 Seções)
    # =========================================================================

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 8, 16, 8)
        main_layout.setSpacing(16)

        # ---------------------------------------------------------------------
        # SEÇÃO 1 (Esquerda): Informações da Música em Reprodução
        # ---------------------------------------------------------------------
        left_container = QWidget()
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        # Miniatura / Ícone representativo da capa do álbum
        self.art_box = QLabel()
        self.art_box.setFixedSize(52, 52)
        self.art_box.setStyleSheet(f"""
            background-color: {BG_CARD};
            border-radius: 6px;
            border: 1px solid #2B2B2B;
        """)
        self.art_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.art_box.setPixmap(IconFactory.get_pixmap("music_library", size=26, color="#666666"))

        # Rótulos de texto (Título e Artista/Álbum)
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 4, 0, 4)
        text_layout.setSpacing(2)

        self.lbl_title = QLabel("Nenhuma música em reprodução")
        self.lbl_title.setStyleSheet(f"color: {TEXT_PRIMARY}; font-weight: 600; font-size: 13px;")
        self.lbl_title.setMaximumWidth(260)

        self.lbl_artist_album = QLabel("Selecione uma faixa da biblioteca")
        self.lbl_artist_album.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        self.lbl_artist_album.setMaximumWidth(260)

        text_layout.addWidget(self.lbl_title)
        text_layout.addWidget(self.lbl_artist_album)

        left_layout.addWidget(self.art_box)
        left_layout.addLayout(text_layout)
        left_container.setFixedWidth(320)
        main_layout.addWidget(left_container, alignment=Qt.AlignmentFlag.AlignVCenter)

        # ---------------------------------------------------------------------
        # SEÇÃO 2 (Centro): Botões de Controle e Barra de Progresso (Seek)
        # ---------------------------------------------------------------------
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 2, 0, 2)
        center_layout.setSpacing(4)

        # Linha Superior: Botões de Ação
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(14)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Botão Shuffle (Aleatório)
        self.btn_shuffle = QPushButton()
        self.btn_shuffle.setObjectName("ControlBtn")
        self.btn_shuffle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_shuffle.setToolTip("Ordem Aleatória (Shuffle)")
        self.btn_shuffle.setIcon(IconFactory.get_icon("shuffle", size=18, color=TEXT_MUTED))
        self.btn_shuffle.clicked.connect(self.shuffle_toggled.emit)

        # Botão Faixa Anterior
        self.btn_prev = QPushButton()
        self.btn_prev.setObjectName("ControlBtn")
        self.btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_prev.setToolTip("Faixa Anterior (Ctrl+Esquerda)")
        self.btn_prev.setIcon(IconFactory.get_icon("previous", size=20, color=TEXT_SECONDARY))
        self.btn_prev.clicked.connect(self.previous_clicked.emit)

        # Botão Primário Circular Play/Pause (Laranja)
        self.btn_play = QPushButton()
        self.btn_play.setObjectName("PlayPauseButton")
        self.btn_play.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_play.setToolTip("Reproduzir / Pausar (Espaço)")
        self.btn_play.setIcon(IconFactory.get_icon("play", size=22, color="#FFFFFF"))
        self.btn_play.clicked.connect(self.play_pause_clicked.emit)

        # Botão Próxima Faixa
        self.btn_next = QPushButton()
        self.btn_next.setObjectName("ControlBtn")
        self.btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_next.setToolTip("Próxima Faixa (Ctrl+Direita)")
        self.btn_next.setIcon(IconFactory.get_icon("next", size=20, color=TEXT_SECONDARY))
        self.btn_next.clicked.connect(self.next_clicked.emit)

        # Botão Repeat (Repetição)
        self.btn_repeat = QPushButton()
        self.btn_repeat.setObjectName("ControlBtn")
        self.btn_repeat.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_repeat.setToolTip("Repetir: Desligado / Todas / Uma")
        self.btn_repeat.setIcon(IconFactory.get_icon("repeat", size=18, color=TEXT_MUTED))
        self.btn_repeat.clicked.connect(self.repeat_toggled.emit)

        btn_layout.addWidget(self.btn_shuffle)
        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.btn_play)
        btn_layout.addWidget(self.btn_next)
        btn_layout.addWidget(self.btn_repeat)

        # Linha Inferior: Barra de Progresso com Rótulos de Tempo
        progress_layout = QHBoxLayout()
        progress_layout.setSpacing(10)

        # Rótulo de tempo decorrido
        self.lbl_elapsed = QLabel("00:00")
        self.lbl_elapsed.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        self.lbl_elapsed.setFixedWidth(40)
        self.lbl_elapsed.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Slider clicável de busca temporal
        self.seek_slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.setValue(0)
        self.seek_slider.user_seeked.connect(self._on_seek_released)
        self.seek_slider.sliderPressed.connect(self._on_seek_pressed)

        # Rótulo de tempo total
        self.lbl_total = QLabel("00:00")
        self.lbl_total.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px;")
        self.lbl_total.setFixedWidth(40)
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        progress_layout.addWidget(self.lbl_elapsed)
        progress_layout.addWidget(self.seek_slider)
        progress_layout.addWidget(self.lbl_total)

        center_layout.addLayout(btn_layout)
        center_layout.addLayout(progress_layout)
        main_layout.addWidget(center_container, stretch=1)

        # ---------------------------------------------------------------------
        # SEÇÃO 3 (Direita): Controle de Volume e Acesso a Configurações
        # ---------------------------------------------------------------------
        right_container = QWidget()
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Ícone de alto-falante (clique rápido muta/desmuta)
        self.btn_volume = QPushButton()
        self.btn_volume.setObjectName("ControlBtn")
        self.btn_volume.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_volume.setToolTip("Silenciar / Ativar Som")
        self.btn_volume.setIcon(IconFactory.get_icon("volume_high", size=18, color=TEXT_SECONDARY))
        self.btn_volume.clicked.connect(self._toggle_mute)

        # Slider de volume (0 a 100%)
        self.vol_slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setFixedWidth(100)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(80)
        self.vol_slider.user_seeked.connect(self._on_volume_changed)
        self.vol_slider.valueChanged.connect(self._on_volume_changed)

        # Botão de Engrenagem (Abre modal de configurações)
        self.btn_settings = QPushButton()
        self.btn_settings.setObjectName("ControlBtn")
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setToolTip("Configurações da Biblioteca (config.json)")
        self.btn_settings.setIcon(IconFactory.get_icon("settings", size=20, color=TEXT_SECONDARY))
        self.btn_settings.clicked.connect(self.settings_clicked.emit)

        right_layout.addWidget(self.btn_volume)
        right_layout.addWidget(self.vol_slider)
        right_layout.addWidget(self.btn_settings)
        right_container.setFixedWidth(240)
        main_layout.addWidget(right_container, alignment=Qt.AlignmentFlag.AlignVCenter)

    # =========================================================================
    # BLOCO 3: Slots Públicos de Atualização Visual (Recebem Dados do AudioEngine)
    # =========================================================================

    def update_track(self, track: Optional[Track]):
        """Atualiza títulos, capas e tempos ao trocar de música."""
        self._current_track = track
        if track:
            # Encurta com reticências (...) caso o título ultrapasse o espaço
            fm = QFontMetrics(self.lbl_title.font())
            title_text = fm.elidedText(track.title, Qt.TextElideMode.ElideRight, 250)
            self.lbl_title.setText(title_text)
            self.lbl_title.setToolTip(track.title)

            sub_text = f"{track.artist} • {track.album}"
            fm_sub = QFontMetrics(self.lbl_artist_album.font())
            self.lbl_artist_album.setText(fm_sub.elidedText(sub_text, Qt.TextElideMode.ElideRight, 250))
            self.lbl_artist_album.setToolTip(sub_text)

            self.lbl_total.setText(track.duration_str)
            self.seek_slider.setRange(0, max(1, track.duration_ms))
            self.seek_slider.setValue(0)
            self.lbl_elapsed.setText("00:00")
            # Destaque em laranja no ícone da capa
            self.art_box.setPixmap(IconFactory.get_pixmap("music_library", size=26, color=ACCENT_COLOR))
        else:
            self.lbl_title.setText("Nenhuma música em reprodução")
            self.lbl_artist_album.setText("Selecione uma faixa da biblioteca")
            self.lbl_elapsed.setText("00:00")
            self.lbl_total.setText("00:00")
            self.seek_slider.setRange(0, 1000)
            self.seek_slider.setValue(0)
            self.art_box.setPixmap(IconFactory.get_pixmap("music_library", size=26, color="#666666"))

    def update_playback_state(self, is_playing: bool):
        """Muda o ícone do botão principal entre Play e Pause."""
        self.btn_play.setIcon(
            IconFactory.get_icon("pause" if is_playing else "play", size=22, color="#FFFFFF")
        )

    def update_position(self, pos_ms: int, duration_ms: int):
        """Atualiza a posição do slider e texto de tempo decorrido."""
        # Se o usuário estiver arrastando manualmente o slider, não sobrescreve
        if not self._is_seeking:
            if duration_ms > 0:
                self.seek_slider.setRange(0, duration_ms)
            self.seek_slider.setValue(pos_ms)
            self.lbl_elapsed.setText(format_duration(pos_ms))
            if duration_ms > 0:
                self.lbl_total.setText(format_duration(duration_ms))

    def update_duration(self, dur_ms: int, dur_str: str):
        """Ajusta o limite máximo do slider quando a duração real é identificada."""
        if dur_ms > 0:
            self.seek_slider.setRange(0, dur_ms)
            self.lbl_total.setText(dur_str)

    def update_volume_display(self, vol: float):
        """Sincroniza o slider e o ícone de volume com o valor do sistema."""
        percent = int(vol * 100)
        self.vol_slider.blockSignals(True)
        self.vol_slider.setValue(percent)
        self.vol_slider.blockSignals(False)
        self._update_volume_icon(vol)

    def update_shuffle_state(self, active: bool):
        """Ilumina o botão de Shuffle em laranja quando ativado."""
        if active:
            self.btn_shuffle.setObjectName("ControlBtnActive")
            self.btn_shuffle.setIcon(IconFactory.get_icon("shuffle", size=18, color=ACCENT_COLOR))
        else:
            self.btn_shuffle.setObjectName("ControlBtn")
            self.btn_shuffle.setIcon(IconFactory.get_icon("shuffle", size=18, color=TEXT_MUTED))
        # Força o Qt a reaplicar o stylesheet
        self.btn_shuffle.style().unpolish(self.btn_shuffle)
        self.btn_shuffle.style().polish(self.btn_shuffle)

    def update_repeat_state(self, mode: str):
        """Altera o ícone e tooltip de repetição ('none', 'all', 'one')."""
        if mode == "all":
            self.btn_repeat.setObjectName("ControlBtnActive")
            self.btn_repeat.setIcon(IconFactory.get_icon("repeat", size=18, color=ACCENT_COLOR))
            self.btn_repeat.setToolTip("Repetir: Todas as faixas")
        elif mode == "one":
            self.btn_repeat.setObjectName("ControlBtnActive")
            self.btn_repeat.setIcon(IconFactory.get_icon("repeat_one", size=18, color=ACCENT_COLOR))
            self.btn_repeat.setToolTip("Repetir: Faixa atual")
        else:
            self.btn_repeat.setObjectName("ControlBtn")
            self.btn_repeat.setIcon(IconFactory.get_icon("repeat", size=18, color=TEXT_MUTED))
            self.btn_repeat.setToolTip("Repetir: Desligado")
        self.btn_repeat.style().unpolish(self.btn_repeat)
        self.btn_repeat.style().polish(self.btn_repeat)

    # =========================================================================
    # BLOCO 4: Handlers Internos de Eventos de Interação
    # =========================================================================

    def _on_seek_pressed(self):
        """Pausa a atualização automática da barra enquanto o usuário arrasta."""
        self._is_seeking = True

    def _on_seek_released(self, val: int):
        """Envia o comando de seek definitivo para o AudioEngine."""
        self._is_seeking = False
        self.seek_requested.emit(val)

    def _on_volume_changed(self, val: int):
        """Converte valor percentual (0-100) para float (0.0-1.0) e emite."""
        vol_float = val / 100.0
        self._update_volume_icon(vol_float)
        self.volume_changed.emit(vol_float)

    def _toggle_mute(self):
        """Silencia ou restaura o volume ao estado anterior ao clique."""
        if self._is_muted:
            self._is_muted = False
            self.vol_slider.setValue(int(self._prev_volume * 100))
        else:
            self._is_muted = True
            self._prev_volume = self.vol_slider.value() / 100.0
            self.vol_slider.setValue(0)

    def _update_volume_icon(self, vol: float):
        """Muda dinamicamente o ícone de alto-falante (alto, baixo ou mudo)."""
        if vol <= 0.001:
            self.btn_volume.setIcon(IconFactory.get_icon("volume_mute", size=18, color=TEXT_MUTED))
        elif vol < 0.5:
            self.btn_volume.setIcon(IconFactory.get_icon("volume_low", size=18, color=TEXT_SECONDARY))
        else:
            self.btn_volume.setIcon(IconFactory.get_icon("volume_high", size=18, color=TEXT_SECONDARY))
