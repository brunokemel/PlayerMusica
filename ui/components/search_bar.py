"""
Barra de Busca Instantânea em Tempo Real (SearchBar) do PlayMusica.
Permite filtrar faixas imediatamente conforme o usuário digita, exibindo
um botão de limpeza rápida e a contagem dinâmica de resultados.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QWidget,
)

from ui.icons import IconFactory
from ui.theme import TEXT_MUTED


# =============================================================================
# BLOCO 1: Classe SearchBar e Sinais de Filtragem
# =============================================================================

class SearchBar(QWidget):
    """
    Componente de busca com campo de texto e indicador visual de contagem de faixas.
    """

    # Sinal emitido a cada caractere digitado ou apagado
    search_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    # =========================================================================
    # BLOCO 2: Construção da Interface da Barra de Busca
    # =========================================================================

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 8)
        layout.setSpacing(12)

        # Campo de entrada de texto
        self.input_field = QLineEdit()
        self.input_field.setObjectName("SearchInput")
        self.input_field.setPlaceholderText("Buscar por música, artista, álbum ou pasta... (Ctrl+F)")
        # Habilita o botão nativo 'X' do Qt para limpar o texto com 1 clique
        self.input_field.setClearButtonEnabled(True)
        self.input_field.textChanged.connect(self._on_text_changed)

        # Adiciona o ícone de lupa no canto esquerdo interno do campo
        search_icon = IconFactory.get_icon("search", size=16, color=TEXT_MUTED)
        self.input_field.addAction(search_icon, QLineEdit.ActionPosition.LeadingPosition)

        # Badge indicador do número de músicas encontradas
        self.lbl_count = QLabel("0 faixas")
        self.lbl_count.setObjectName("BadgeLabel")
        self.lbl_count.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.input_field, stretch=1)
        layout.addWidget(self.lbl_count)

    # =========================================================================
    # BLOCO 3: Métodos de Controle e Notificação
    # =========================================================================

    def _on_text_changed(self, text: str):
        """Propaga o texto atual para a janela principal filtrar a tabela."""
        self.search_changed.emit(text)

    def set_track_count(self, visible_count: int, total_count: int):
        """
        Atualiza o rótulo da contagem:
        - Se todas visíveis: '150 faixas'
        - Se filtrado: '25 de 150 faixas'
        """
        if visible_count == total_count:
            self.lbl_count.setText(f"{total_count} faixas")
        else:
            self.lbl_count.setText(f"{visible_count} de {total_count} faixas")

    def focus_search(self):
        """Foca o cursor no campo de busca (acionado pelo atalho Ctrl+F)."""
        self.input_field.setFocus()
        self.input_field.selectAll()

    def clear(self):
        """Limpa o texto do campo de busca."""
        self.input_field.clear()
