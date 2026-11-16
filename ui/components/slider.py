"""
Slider Horizontal com Pulo Direto ao Clique (ClickableSlider).
Resolve a limitação padrão do QSlider do Qt, que apenas avança em blocos (pageStep),
permitindo que o usuário clique em qualquer ponto da barra para buscar a música imediatamente.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QSlider, QStyleOptionSlider


# =============================================================================
# BLOCO 1: Subclasse ClickableSlider
# =============================================================================

class ClickableSlider(QSlider):
    """
    Slider customizado para a barra de progresso (seek) e barra de volume.
    Suporta tanto clique direto em qualquer ponto quanto arrasto fluido.
    """

    # Sinal emitido com o valor final quando o usuário clica ou arrasta
    user_seeked = Signal(int)

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        # Cursor em formato de mãozinha indicando que o elemento é clicável
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._is_dragging = False

    # =========================================================================
    # BLOCO 2: Captura e Tratamento de Eventos do Mouse
    # =========================================================================

    def mousePressEvent(self, event):
        """Disparado quando o botão do mouse é pressionado sobre o slider."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            # Converte a coordenada X do clique para o valor correspondente no slider
            val = self._pos_to_val(event.position().x() if hasattr(event, "position") else event.x())
            self.setValue(val)
            self.user_seeked.emit(val)
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Disparado enquanto o usuário mantém o botão pressionado e arrasta o cursor."""
        if self._is_dragging:
            val = self._pos_to_val(event.position().x() if hasattr(event, "position") else event.x())
            self.setValue(val)
            self.user_seeked.emit(val)
            event.accept()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Disparado quando o botão do mouse é solto."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            val = self._pos_to_val(event.position().x() if hasattr(event, "position") else event.x())
            self.setValue(val)
            self.user_seeked.emit(val)
            event.accept()
        super().mouseReleaseEvent(event)

    # =========================================================================
    # BLOCO 3: Cálculo Geométrico da Posição Relativa
    # =========================================================================

    def _pos_to_val(self, click_x: float) -> int:
        """
        Calcula matematicamente o valor correspondente à coordenada horizontal:
        ratio = x_clique / largura_total_do_slider
        valor = min + ratio * (max - min)
        """
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        slider_length = self.width()
        slider_min = self.minimum()
        slider_max = self.maximum()

        if slider_max <= slider_min or slider_length <= 0:
            return slider_min

        # Garante que a razão fique estritamente entre 0.0 e 1.0
        ratio = max(0.0, min(1.0, click_x / float(slider_length)))
        return int(slider_min + ratio * (slider_max - slider_min))
