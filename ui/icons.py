"""
Gerador de Ícones Vetoriais SVG para o PlayMusica.
Renderiza ícones nítidos em qualquer resolução ou densidade de pixels (High-DPI / 4K)
sem depender de arquivos de imagem externos (.png/.jpg) que poderiam ser perdidos.
"""

from PySide6.QtCore import QByteArray, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


# =============================================================================
# BLOCO 1: Templates Vetoriais SVG Inline (Ícones Minimalistas)
# =============================================================================

SVG_ICONS = {
    # Triângulo de Play clássico
    "play": """<svg viewBox="0 0 24 24" fill="{color}"><polygon points="6,4 20,12 6,20"/></svg>""",
    # Duas barras verticais de Pause
    "pause": """<svg viewBox="0 0 24 24" fill="{color}"><rect x="5" y="4" width="4" height="16" rx="1"/><rect x="15" y="4" width="4" height="16" rx="1"/></svg>""",
    # Pular para próxima faixa (triângulo + barra)
    "next": """<svg viewBox="0 0 24 24" fill="{color}"><polygon points="5,4 15,12 5,20"/><rect x="16" y="4" width="3" height="16" rx="1"/></svg>""",
    # Voltar para faixa anterior (barra + triângulo)
    "previous": """<svg viewBox="0 0 24 24" fill="{color}"><polygon points="19,4 9,12 19,20"/><rect x="5" y="4" width="3" height="16" rx="1"/></svg>""",
    # Flechas cruzadas de Shuffle (ordem aleatória)
    "shuffle": """<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="16 3 21 3 21 8"></polyline>
        <line x1="4" y1="20" x2="21" y2="3"></line>
        <polyline points="21 16 21 21 16 21"></polyline>
        <line x1="15" y1="15" x2="21" y2="21"></line>
        <line x1="4" y1="4" x2="9" y2="9"></line>
    </svg>""",
    # Flechas circulares de Repetição (Repeat All)
    "repeat": """<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="17 1 21 5 17 9"></polyline>
        <path d="M3 11V9a4 4 0 0 1 4-4h14"></path>
        <polyline points="7 23 3 19 7 15"></polyline>
        <path d="M21 13v2a4 4 0 0 1-4 4H3"></path>
    </svg>""",
    # Repetição de faixa única com número 1 centralizado (Repeat One)
    "repeat_one": """<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="17 1 21 5 17 9"></polyline>
        <path d="M3 11V9a4 4 0 0 1 4-4h14"></path>
        <polyline points="7 23 3 19 7 15"></polyline>
        <path d="M21 13v2a4 4 0 0 1-4 4H3"></path>
        <text x="12" y="14" fill="{color}" stroke="none" font-size="9" font-family="sans-serif" font-weight="bold" text-anchor="middle">1</text>
    </svg>""",
    # Alto-falante com volume alto
    "volume_high": """<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polygon fill="{color}" points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
        <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
        <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
    </svg>""",
    # Alto-falante com volume baixo
    "volume_low": """<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polygon fill="{color}" points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
        <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
    </svg>""",
    # Alto-falante silenciado (Mute)
    "volume_mute": """<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polygon fill="{color}" points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
        <line x1="23" y1="9" x2="17" y2="15"></line>
        <line x1="17" y1="9" x2="23" y2="15"></line>
    </svg>""",
    # Lupa de busca
    "search": """<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
    </svg>""",
    # Pasta de arquivos
    "folder": """<svg viewBox="0 0 24 24" fill="{color}">
        <path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/>
    </svg>""",
    # Nota musical (Logo e biblioteca)
    "music_library": """<svg viewBox="0 0 24 24" fill="{color}">
        <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/>
    </svg>""",
    # Engrenagem de configurações
    "settings": """<svg viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="3"></circle>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
    </svg>""",
    # Indicador de equalizador / música tocando
    "playing_indicator": """<svg viewBox="0 0 24 24" fill="{color}">
        <rect x="3" y="10" width="3" height="10" rx="1.5"/>
        <rect x="9" y="4" width="3" height="16" rx="1.5"/>
        <rect x="15" y="8" width="3" height="12" rx="1.5"/>
        <rect x="21" y="12" width="3" height="8" rx="1.5"/>
    </svg>""",
}


# =============================================================================
# BLOCO 2: Fábrica de Renderização de Ícones (IconFactory)
# =============================================================================

class IconFactory:
    """
    Fábrica que converte strings SVG em objetos QPixmap e QIcon do Qt.
    Permite passar qualquer cor em formato hexadecimal dinamicamente.
    """

    @classmethod
    def get_pixmap(cls, name: str, size: int = 24, color: str = "#E0E0E0") -> QPixmap:
        """Renderiza o SVG para um mapa de bits QPixmap com transparência."""
        svg_template = SVG_ICONS.get(name)
        if not svg_template:
            # Fallback seguro: pixmap transparente caso o nome não exista
            pm = QPixmap(size, size)
            pm.fill(Qt.GlobalColor.transparent)
            return pm

        # Substitui a tag de cor no SVG
        svg_content = svg_template.format(color=color)
        byte_array = QByteArray(svg_content.encode("utf-8"))
        renderer = QSvgRenderer(byte_array)

        # Desenha o vetor no buffer transparente
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return pixmap

    @classmethod
    def get_icon(cls, name: str, size: int = 24, color: str = "#E0E0E0") -> QIcon:
        """Cria e retorna uma instância de QIcon pronta para uso em botões e menus."""
        return QIcon(cls.get_pixmap(name, size, color))
