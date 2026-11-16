"""
Ponto de Entrada Principal (Main Entry Point) do PlayMusica.
Configura variáveis de ambiente para renderização em monitores High-DPI (4K),
registra o identificador do aplicativo no Windows para ícones na barra de tarefas,
instancia o gerenciador de configurações e inicializa a aplicação Qt.
"""

import os
import sys

# =============================================================================
# BLOCO 1: Otimizações de Renderização para Monitores Modernos (High-DPI / 4K)
# =============================================================================

# Garante que textos e ícones não fiquem borrados em monitores com escala de 125%, 150% ou 200%
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"


# =============================================================================
# BLOCO 2: Registro de Identidade do Processo no Windows (AppUserModelID)
# =============================================================================

# Permite que o Windows 10/11 exiba o ícone correto na barra de tarefas ao invés do ícone genérico do Python
if sys.platform == "win32":
    try:
        import ctypes
        app_id = "playmusica.desktop.player.v1"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from core.config import ConfigManager
from ui.main_window import MainWindow


# =============================================================================
# BLOCO 3: Função Principal de Inicialização (main)
# =============================================================================

def main():
    """
    Inicializa o loop de eventos da interface gráfica (QApplication),
    carrega ou cria o config.json e exibe a janela principal.
    """
    # Política de arredondamento suave de DPI para evitar artefatos visuais
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Cria o processo mestre de interface do Qt
    app = QApplication(sys.argv)
    app.setApplicationName("PlayMusica")
    app.setOrganizationName("PlayMusica")

    # 1. Carrega ou gera o arquivo config.json ao lado do executável
    config_mgr = ConfigManager()

    # 2. Instancia e renderiza a janela principal com o tema Dark Mode
    window = MainWindow(config_mgr)
    window.show()

    # 3. Inicia o loop de eventos que mantém o programa rodando e responsivo
    sys.exit(app.exec())


# Executa a função main caso o arquivo seja iniciado diretamente pelo Python
if __name__ == "__main__":
    main()
