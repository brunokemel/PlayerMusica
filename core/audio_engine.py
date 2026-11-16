"""
Motor de Reprodução de Áudio do PlayMusica.
Encapsula o QMediaPlayer e QAudioOutput da biblioteca Qt Multimedia.
Gerencia a fila de reprodução, ordem aleatória (Shuffle) e modos de repetição (Repeat).
"""

import random
from typing import List, Optional
from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer

from core.models import Track
from core.tag_reader import format_duration


# =============================================================================
# BLOCO 1: Classe Principal do Motor de Áudio (AudioEngine)
# =============================================================================

class AudioEngine(QObject):
    """
    Controlador central de reprodução de áudio.
    Converte comandos da interface em ações no pipeline de áudio nativo do Windows.
    """

    # Sinais Qt para atualizar a interface do usuário em tempo real:
    # 1. track_changed: emite a nova faixa que começou a tocar
    track_changed = Signal(object)
    # 2. state_changed: emite True se está tocando ou False se pausado/parado
    state_changed = Signal(bool)
    # 3. position_changed: emite (posição_atual_ms, duração_total_ms)
    position_changed = Signal(int, int)
    # 4. duration_changed: emite (duração_ms, duração_formatada_str)
    duration_changed = Signal(int, str)
    # 5. volume_changed: emite o novo volume normalizado [0.0 - 1.0]
    volume_changed = Signal(float)
    # 6. shuffle_changed: emite True se o modo aleatório estiver ativo
    shuffle_changed = Signal(bool)
    # 7. repeat_changed: emite o modo atual ('none', 'all', 'one')
    repeat_changed = Signal(str)
    # 8. error_occurred: emite mensagem de erro caso o arquivo não possa ser tocado
    error_occurred = Signal(str)

    def __init__(self, initial_volume: float = 0.8, shuffle: bool = False, repeat_mode: str = "none") -> None:
        super().__init__()

        # Inicializa o player e a saída de áudio nativa do Qt 6
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        # Estado da fila de reprodução
        self._playlist: List[Track] = []
        self._current_index: int = -1
        self._shuffle: bool = shuffle
        self._repeat_mode: str = repeat_mode

        # Fila de índices para o modo Shuffle (garante que todas as músicas toquem sem repetição)
        self._shuffled_order: List[int] = []
        self._shuffle_pos: int = 0

        # Aplica o volume inicial
        self.set_volume(initial_volume)

        # Conecta os sinais de hardware do QMediaPlayer aos métodos internos
        self.player.positionChanged.connect(self._on_position_changed)
        self.player.durationChanged.connect(self._on_duration_changed)
        self.player.playbackStateChanged.connect(self._on_state_changed)
        self.player.mediaStatusChanged.connect(self._on_media_status_changed)
        self.player.errorOccurred.connect(self._on_error)

    # =========================================================================
    # BLOCO 2: Propriedades e Getters de Consulta
    # =========================================================================

    @property
    def current_track(self) -> Optional[Track]:
        """Retorna o objeto Track da música que está carregada no momento."""
        if 0 <= self._current_index < len(self._playlist):
            return self._playlist[self._current_index]
        return None

    @property
    def is_playing(self) -> bool:
        """Verifica se o player está ativamente emitindo áudio."""
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    @property
    def volume(self) -> float:
        """Retorna o volume da saída de áudio [0.0 a 1.0]."""
        return self.audio_output.volume()

    @property
    def shuffle(self) -> bool:
        """Retorna se o modo aleatório está ligado."""
        return self._shuffle

    @property
    def repeat_mode(self) -> str:
        """Retorna o modo de repetição atual: 'none', 'all' ou 'one'."""
        return self._repeat_mode

    # =========================================================================
    # BLOCO 3: Gerenciamento da Playlist e Seleção de Faixas
    # =========================================================================

    def set_playlist(self, tracks: List[Track], start_index: int = -1) -> None:
        """
        Define uma nova lista de reprodução (ex: quando o usuário clica em uma pasta
        ou lista filtrada por busca).
        """
        self._playlist = list(tracks)
        self._current_index = -1
        # Reconstrói a ordem aleatória para a nova lista
        self._build_shuffle_order()

        if 0 <= start_index < len(self._playlist):
            self.play_track_at(start_index)

    def play_track(self, track: Track) -> None:
        """Toca uma faixa específica buscando sua posição na lista atual."""
        try:
            idx = self._playlist.index(track)
            self.play_track_at(idx)
        except ValueError:
            # Se não estiver na lista atual, define como lista unitária
            self._playlist = [track]
            self.play_track_at(0)

    def play_track_at(self, index: int) -> None:
        """Carrega e inicia a reprodução da faixa no índice especificado."""
        if not (0 <= index < len(self._playlist)):
            return

        self._current_index = index
        track = self._playlist[index]

        # Sincroniza a posição na fila do Shuffle caso esteja ativo
        if self._shuffle and self._shuffled_order:
            if index in self._shuffled_order:
                self._shuffle_pos = self._shuffled_order.index(index)

        # Converte o caminho local para formato de URL do Qt e toca
        url = QUrl.fromLocalFile(track.file_path)
        self.player.setSource(url)
        self.player.play()
        self.track_changed.emit(track)

    # =========================================================================
    # BLOCO 4: Controles de Reprodução (Play, Pause, Próxima, Anterior, Seek)
    # =========================================================================

    def toggle_play_pause(self) -> None:
        """Alterna entre reproduzir e pausar a música atual."""
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def play(self) -> None:
        """Inicia ou retoma a reprodução."""
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
            self.player.play()
        elif self.current_track is None and self._playlist:
            self.play_track_at(0)
        elif self.current_track is not None:
            self.player.play()

    def pause(self) -> None:
        """Pausa a reprodução no ponto atual."""
        self.player.pause()

    def stop(self) -> None:
        """Interrompe a reprodução e reseta o cursor."""
        self.player.stop()

    def next_track(self) -> None:
        """
        Avança para a próxima faixa respeitando os modos Shuffle e Repeat:
        - No modo Shuffle: escolhe a próxima música da fila embaralhada.
        - No modo Sequencial: avança para index + 1.
        - Se chegar ao fim: reinicia se repeat='all', ou para se repeat='none'.
        """
        if not self._playlist:
            return

        # Caminho 1: Reprodução Aleatória (Shuffle)
        if self._shuffle and self._shuffled_order:
            if self._shuffle_pos + 1 < len(self._shuffled_order):
                self._shuffle_pos += 1
                next_idx = self._shuffled_order[self._shuffle_pos]
                self.play_track_at(next_idx)
            elif self._repeat_mode == "all":
                # Reembaralha e começa do início da lista aleatória
                self._build_shuffle_order()
                self._shuffle_pos = 0
                self.play_track_at(self._shuffled_order[0])
            else:
                self.stop()
            return

        # Caminho 2: Reprodução Sequencial Normal
        next_idx = self._current_index + 1
        if next_idx < len(self._playlist):
            self.play_track_at(next_idx)
        elif self._repeat_mode == "all":
            self.play_track_at(0)
        else:
            self.stop()

    def previous_track(self) -> None:
        """
        Retorna para a faixa anterior com comportamento clássico de players:
        - Se mais de 3 segundos já tiverem sido tocados, reinicia a faixa atual do 00:00.
        - Se estiver nos primeiros 3 segundos, aí sim retrocede para a faixa anterior.
        """
        if not self._playlist:
            return

        # Regra UX: Se tocou mais de 3 segundos, volta ao início da música atual
        if self.player.position() > 3000:
            self.seek(0)
            return

        # Caminho 1: Shuffle
        if self._shuffle and self._shuffled_order:
            if self._shuffle_pos > 0:
                self._shuffle_pos -= 1
                prev_idx = self._shuffled_order[self._shuffle_pos]
                self.play_track_at(prev_idx)
            else:
                self.seek(0)
            return

        # Caminho 2: Sequencial
        prev_idx = self._current_index - 1
        if prev_idx >= 0:
            self.play_track_at(prev_idx)
        elif self._repeat_mode == "all":
            self.play_track_at(len(self._playlist) - 1)
        else:
            self.seek(0)

    def seek(self, position_ms: int) -> None:
        """Pula para um ponto arbitrário da música em milissegundos."""
        duration = self.player.duration()
        target = max(0, min(position_ms, duration if duration > 0 else position_ms))
        self.player.setPosition(target)

    def set_volume(self, val: float) -> None:
        """Ajusta o volume do áudio (normalizado entre 0.0 e 1.0)."""
        clamped = max(0.0, min(1.0, float(val)))
        self.audio_output.setVolume(clamped)
        self.volume_changed.emit(clamped)

    def toggle_shuffle(self) -> bool:
        """Alterna o modo Shuffle e reconstrói a fila aleatória."""
        self._shuffle = not self._shuffle
        if self._shuffle:
            self._build_shuffle_order()
        self.shuffle_changed.emit(self._shuffle)
        return self._shuffle

    def cycle_repeat_mode(self) -> str:
        """Cicla entre os modos de repetição: 'none' -> 'all' -> 'one' -> 'none'."""
        modes = ["none", "all", "one"]
        curr_idx = modes.index(self._repeat_mode) if self._repeat_mode in modes else 0
        self._repeat_mode = modes[(curr_idx + 1) % len(modes)]
        self.repeat_changed.emit(self._repeat_mode)
        return self._repeat_mode

    def _build_shuffle_order(self) -> None:
        """
        Gera uma permutação aleatória de índices para a fila de reprodução.
        Mantém a música atual como o primeiro item para que a reprodução não mude
        no momento em que o usuário liga o botão de Shuffle.
        """
        n = len(self._playlist)
        if n <= 1:
            self._shuffled_order = list(range(n))
            self._shuffle_pos = 0
            return

        indices = list(range(n))
        if self._current_index in indices:
            indices.remove(self._current_index)
            random.shuffle(indices)
            self._shuffled_order = [self._current_index] + indices
            self._shuffle_pos = 0
        else:
            random.shuffle(indices)
            self._shuffled_order = indices
            self._shuffle_pos = 0

    # =========================================================================
    # BLOCO 5: Handlers de Eventos Nativos do Qt Multimedia
    # =========================================================================

    def _on_position_changed(self, pos_ms: int) -> None:
        """Disparado periodicamente pelo hardware durante a reprodução da música."""
        duration_ms = self.player.duration()
        self.position_changed.emit(pos_ms, duration_ms)

    def _on_duration_changed(self, dur_ms: int) -> None:
        """Disparado quando a duração total do arquivo é detectada pelo decoder."""
        if dur_ms > 0 and self.current_track:
            self.current_track.duration_ms = dur_ms
            self.current_track.duration_str = format_duration(dur_ms)
        self.duration_changed.emit(dur_ms, format_duration(dur_ms))

    def _on_state_changed(self, state: QMediaPlayer.PlaybackState) -> None:
        """Disparado quando o player muda entre Playing, Paused ou Stopped."""
        is_playing = (state == QMediaPlayer.PlaybackState.PlayingState)
        self.state_changed.emit(is_playing)

    def _on_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None:
        """
        Disparado quando a música atual chega ao final (EndOfMedia).
        Se estiver no modo 'one', repete a mesma música.
        Caso contrário, pula automaticamente para a próxima faixa.
        """
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self._repeat_mode == "one":
                self.seek(0)
                self.play()
            else:
                self.next_track()

    def _on_error(self, error: QMediaPlayer.Error, error_string: str) -> None:
        """Disparado em caso de erro de codec, áudio ausente ou arquivo inacessível."""
        if error != QMediaPlayer.Error.NoError:
            self.error_occurred.emit(f"Erro no áudio: {error_string}")
