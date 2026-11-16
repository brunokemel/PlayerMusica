"""
Definições de Tema Visual e Folha de Estilos (QSS) para o PlayMusica.
Inspirado na identidade visual escura e refinada do Google Play Music.
"""

# =============================================================================
# BLOCO 1: Constantes da Paleta de Cores (Dark Mode de Alto Conforto Visual)
# =============================================================================

# Cor de fundo principal da aplicação (Preto fosco profundo)
BG_MAIN = "#121212"

# Cor de fundo do painel lateral esquerdo (Sidebar)
BG_SIDEBAR = "#181818"

# Cor de fundo da barra inferior de reprodução (Player Bar)
BG_PLAYER = "#1E1E1E"

# Cor de cartões, campos de texto e áreas elevadas
BG_CARD = "#232323"

# Cor de fundo para itens sob hover (passagem do mouse)
BG_HOVER = "#2A2A2A"

# Cor de fundo para itens selecionados na lista/árvore
BG_SELECTED = "#333333"

# Bordas e divisores sutis
BORDER_COLOR = "#292929"
BORDER_FOCUS = "#FF5722"

# Cor de Destaque Primária (Laranja icônico do Google Play Music)
ACCENT_COLOR = "#FF5722"
ACCENT_HOVER = "#FF7043"
ACCENT_ACTIVE = "#E64A19"

# Cores de Tipografia
TEXT_PRIMARY = "#FFFFFF"     # Texto principal em branco de alto contraste
TEXT_SECONDARY = "#B0B0B0"   # Texto secundário (artistas, álbuns)
TEXT_MUTED = "#707070"       # Texto discreto (durações, números de faixa)
SLIDER_GROOVE = "#3A3A3A"    # Trilho de fundo dos sliders de volume e progresso

# Família de fontes nativas do sistema com renderização limpa
FONT_FAMILY = 'Segoe UI, -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif'


# =============================================================================
# BLOCO 2: Folha de Estilos Completa em Qt Style Sheet (QSS)
# =============================================================================

MAIN_STYLESHEET = f"""
/* -------------------------------------------------------------------------
   Reset Global: Tipografia, fundo e seleção padrão
   ------------------------------------------------------------------------- */
QWidget {{
    background-color: {BG_MAIN};
    color: {TEXT_PRIMARY};
    font-family: {FONT_FAMILY};
    font-size: 13px;
    selection-background-color: {BG_SELECTED};
    selection-color: {TEXT_PRIMARY};
    outline: none;
}}

/* Janela principal */
QMainWindow {{
    background-color: {BG_MAIN};
}}

/* -------------------------------------------------------------------------
   Containers Estruturais (Sidebar, Centro e Player Bar)
   ------------------------------------------------------------------------- */
QFrame#SidebarFrame {{
    background-color: {BG_SIDEBAR};
    border-right: 1px solid {BORDER_COLOR};
}}

QFrame#CenterFrame {{
    background-color: {BG_MAIN};
}}

QFrame#PlayerBarFrame {{
    background-color: {BG_PLAYER};
    border-top: 1px solid {BORDER_COLOR};
}}

/* Divisor redimensionável entre Sidebar e Conteúdo Central */
QSplitter::handle {{
    background-color: {BORDER_COLOR};
    width: 1px;
}}

/* -------------------------------------------------------------------------
   Campo de Busca (Pill-shaped minimalista)
   ------------------------------------------------------------------------- */
QLineEdit#SearchInput {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_COLOR};
    border-radius: 18px;
    padding: 8px 16px;
    font-size: 13px;
}}
QLineEdit#SearchInput:focus {{
    border: 1px solid {ACCENT_COLOR};
    background-color: #262626;
}}
QLineEdit#SearchInput:hover {{
    border: 1px solid #444444;
}}

/* Badges e Pílulas de Contagem */
QLabel#BadgeLabel {{
    background-color: {BG_CARD};
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER_COLOR};
    border-radius: 10px;
    padding: 3px 8px;
    font-size: 11px;
}}

/* -------------------------------------------------------------------------
   Árvore de Navegação Lateral (Pastas e Bibliotecas)
   ------------------------------------------------------------------------- */
QTreeWidget {{
    background-color: transparent;
    border: none;
    color: {TEXT_PRIMARY};
    font-size: 13px;
    show-decoration-selected: 1;
}}
QTreeWidget::item {{
    height: 34px;
    padding: 2px 8px;
    border-radius: 6px;
    margin: 1px 6px;
    color: {TEXT_SECONDARY};
}}
QTreeWidget::item:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_PRIMARY};
}}
QTreeWidget::item:selected {{
    background-color: {BG_SELECTED};
    color: {ACCENT_COLOR};
    font-weight: bold;
}}
QTreeWidget::branch {{
    background: transparent;
}}

/* -------------------------------------------------------------------------
   Tabela de Músicas (Lista de Faixas Virtualizada)
   ------------------------------------------------------------------------- */
QTableWidget {{
    background-color: {BG_MAIN};
    border: none;
    gridline-color: transparent;
    color: {TEXT_PRIMARY};
    alternate-background-color: #161616;
}}
QTableWidget::item {{
    padding-left: 12px;
    padding-right: 12px;
    border-bottom: 1px solid #1C1C1C;
    height: 40px;
}}
QTableWidget::item:hover {{
    background-color: {BG_HOVER};
}}
QTableWidget::item:selected {{
    background-color: {BG_SELECTED};
    color: {TEXT_PRIMARY};
}}

/* Cabeçalho da Tabela de Músicas */
QHeaderView::section {{
    background-color: {BG_MAIN};
    color: {TEXT_MUTED};
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    padding: 8px 12px;
    border: none;
    border-bottom: 1px solid {BORDER_COLOR};
}}

/* -------------------------------------------------------------------------
   Botões e Controles de Mídia
   ------------------------------------------------------------------------- */
QPushButton {{
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    color: {TEXT_SECONDARY};
}}
QPushButton:hover {{
    background-color: {BG_HOVER};
    color: {TEXT_PRIMARY};
}}
QPushButton:pressed {{
    background-color: #353535;
}}

/* Botão Circular Primário de Play/Pause com Cor de Destaque */
QPushButton#PlayPauseButton {{
    background-color: {ACCENT_COLOR};
    border-radius: 23px;
    border: none;
    min-width: 46px;
    max-width: 46px;
    min-height: 46px;
    max-height: 46px;
}}
QPushButton#PlayPauseButton:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton#PlayPauseButton:pressed {{
    background-color: {ACCENT_ACTIVE};
}}

/* Botões de Controle Secundários (Próxima, Anterior, etc.) */
QPushButton#ControlBtn {{
    border-radius: 18px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    padding: 0px;
}}
QPushButton#ControlBtn:hover {{
    background-color: {BG_HOVER};
}}

/* Estado Ativo para Botões de Alternância (Shuffle e Repeat Ligados) */
QPushButton#ControlBtnActive {{
    border-radius: 18px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    background-color: rgba(255, 87, 34, 0.15);
    color: {ACCENT_COLOR};
}}

/* -------------------------------------------------------------------------
   Sliders de Progresso (Seek) e Volume
   ------------------------------------------------------------------------- */
QSlider::groove:horizontal {{
    height: 4px;
    background: {SLIDER_GROOVE};
    border-radius: 2px;
}}
QSlider::sub-page:horizontal {{
    background: {ACCENT_COLOR};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {TEXT_PRIMARY};
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}}
QSlider::handle:horizontal:hover {{
    background: #FFFFFF;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}}

/* -------------------------------------------------------------------------
   Barras de Rolagem Minimalistas (Scrollbars)
   ------------------------------------------------------------------------- */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0px;
}}
QScrollBar::handle:vertical {{
    background: #3A3A3A;
    min-height: 30px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background: #555555;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    margin: 0px;
}}
QScrollBar::handle:horizontal {{
    background: #3A3A3A;
    min-width: 30px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal:hover {{
    background: #555555;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    background: none;
}}

/* -------------------------------------------------------------------------
   Menu de Contexto (Botão Direito) e Diálogos Modais
   ------------------------------------------------------------------------- */
QMenu {{
    background-color: {BG_CARD};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_COLOR};
    border-radius: 8px;
    padding: 6px 0px;
}}
QMenu::item {{
    padding: 8px 24px 8px 16px;
    border-radius: 4px;
    margin: 1px 4px;
}}
QMenu::item:selected {{
    background-color: {BG_HOVER};
    color: {ACCENT_COLOR};
}}
QMenu::separator {{
    height: 1px;
    background-color: {BORDER_COLOR};
    margin: 4px 0px;
}}

QDialog {{
    background-color: {BG_PLAYER};
    border: 1px solid {BORDER_COLOR};
    border-radius: 10px;
}}
"""
