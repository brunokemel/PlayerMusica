"""
Gerenciador de Configuração do PlayMusica.
Responsável por carregar, validar, atualizar e salvar o arquivo config.json
localizado no mesmo diretório do executável ou script principal.
"""

import json
import os
import sys
from typing import Any, Dict


# =============================================================================
# BLOCO 1: Detecção de Diretórios do Sistema e Aplicação
# =============================================================================

def get_application_dir() -> str:
    """
    Retorna o caminho absoluto do diretório onde a aplicação está rodando.
    - Se estiver compilado via PyInstaller (sys.frozen == True): usa o diretório do .exe.
    - Se estiver rodando como script Python (.py): usa a pasta raiz do projeto.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    # Diretório pai da pasta 'core'
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_default_music_dir() -> str:
    """
    Detecta a pasta padrão de Músicas do Windows do usuário logado (ex: C:\\Users\\Nome\\Music).
    Se por algum motivo a pasta não existir, faz fallback para a pasta Home do usuário (~).
    """
    music_dir = os.path.join(os.path.expanduser("~"), "Music")
    if os.path.exists(music_dir):
        return music_dir
    return os.path.expanduser("~")


# =============================================================================
# BLOCO 2: Configuração Padrão Inicial (Fallback Seguro)
# =============================================================================

DEFAULT_CONFIG: Dict[str, Any] = {
    # Diretório raiz padrão escaneado em busca de músicas
    "music_directory": get_default_music_dir(),
    # Volume inicial (de 0.0 a 1.0 -> 80% do volume)
    "volume": 0.8,
    # Modo aleatório desligado por padrão
    "shuffle": False,
    # Modos de repetição: "none" (não repete), "all" (reinicia ao fim), "one" (repete a mesma faixa)
    "repeat_mode": "none",
    # Dimensões e estado da janela para restaurar na próxima inicialização
    "window_width": 1120,
    "window_height": 720,
    "is_maximized": False,
}


# =============================================================================
# BLOCO 3: Classe Gerenciadora de Configurações (ConfigManager)
# =============================================================================

class ConfigManager:
    """
    Lida com o ciclo de vida da configuração persistida em formato JSON.
    Garante que se o arquivo não existir, seja gerado automaticamente.
    """

    def __init__(self, filename: str = "config.json") -> None:
        # Define o caminho completo até o config.json ao lado do executável
        self.app_dir = get_application_dir()
        self.config_path = os.path.join(self.app_dir, filename)
        self.config: Dict[str, Any] = {}
        # Carrega ou cria na inicialização
        self.load()

    def load(self) -> Dict[str, Any]:
        """
        Carrega as configurações do disco.
        - Se config.json não existir: cria com os valores padrão e salva.
        - Se existir mas estiver corrompido: regenera com valores padrão sem quebrar o app.
        - Mescla chaves ausentes caso novas propriedades sejam adicionadas futuramente.
        """
        # Caso 1: Primeira execução (arquivo inexistente)
        if not os.path.exists(self.config_path):
            self.config = dict(DEFAULT_CONFIG)
            self.config["music_directory"] = get_default_music_dir()
            self.save()
            return self.config

        # Caso 2: Arquivo já existe no disco
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)

            if not isinstance(loaded, dict):
                raise ValueError("A raiz do config.json deve ser um objeto JSON.")

            # Preserva os valores padrão e sobrescreve com os valores que o usuário salvou
            self.config = dict(DEFAULT_CONFIG)
            self.config.update(loaded)

        except Exception as e:
            # Em caso de JSON inválido/corrompido, restaura padrão seguro
            print(f"[ConfigManager] Aviso: config.json inválido ({e}), restaurando padrões.")
            self.config = dict(DEFAULT_CONFIG)
            self.config["music_directory"] = get_default_music_dir()
            self.save()

        return self.config

    def save(self) -> bool:
        """
        Escreve as configurações atuais no disco em formato JSON legível (indentado).
        Usa codificação UTF-8 para suportar caminhos com acentuação e caracteres especiais.
        """
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[ConfigManager] Erro ao gravar config.json: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor arbitrário pelo nome da chave."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        """Define um valor arbitrário e opcionalmente já persiste no disco."""
        self.config[key] = value
        if auto_save:
            self.save()

    # =========================================================================
    # Propriedades de Acesso Direto (Getters e Setters Tipados)
    # =========================================================================

    @property
    def music_directory(self) -> str:
        """Retorna o diretório raiz das músicas."""
        return str(self.config.get("music_directory", get_default_music_dir()))

    @music_directory.setter
    def music_directory(self, path: str) -> None:
        """Atualiza a pasta raiz e salva imediatamente no config.json."""
        self.config["music_directory"] = path
        self.save()

    @property
    def volume(self) -> float:
        """Retorna o volume atual no intervalo normalizado [0.0, 1.0]."""
        val = self.config.get("volume", 0.8)
        try:
            return max(0.0, min(1.0, float(val)))
        except (ValueError, TypeError):
            return 0.8

    @volume.setter
    def volume(self, val: float) -> None:
        """Atualiza o volume e persiste no config.json."""
        self.config["volume"] = max(0.0, min(1.0, float(val)))
        self.save()

    @property
    def shuffle(self) -> bool:
        """Indica se a reprodução aleatória está ligada."""
        return bool(self.config.get("shuffle", False))

    @shuffle.setter
    def shuffle(self, val: bool) -> None:
        """Liga ou desliga o modo shuffle e salva."""
        self.config["shuffle"] = bool(val)
        self.save()

    @property
    def repeat_mode(self) -> str:
        """Retorna o modo de repetição: 'none', 'all' ou 'one'."""
        mode = self.config.get("repeat_mode", "none")
        return mode if mode in ("none", "all", "one") else "none"

    @repeat_mode.setter
    def repeat_mode(self, mode: str) -> None:
        """Define o modo de repetição e salva no config.json."""
        if mode in ("none", "all", "one"):
            self.config["repeat_mode"] = mode
            self.save()
