"""
Modelos de dados (Data Transfer Objects) do PlayMusica.
Estruturas que representam faixas de áudio e nós da árvore de diretórios.
"""

from dataclasses import dataclass
from typing import List


# =============================================================================
# BLOCO 1: Modelo de Dados de uma Faixa de Áudio (Track)
# =============================================================================

@dataclass
class Track:
    """
    Representa uma música individual com seus metadados extraídos e caminho no disco.
    """
    # Identificador único sequencial na sessão
    id: int
    # Caminho absoluto no disco (ex: 'C:\\Musicas\\Rock\\Queen\\Bohemian.mp3')
    file_path: str
    # Nome do arquivo físico (ex: 'Bohemian.mp3')
    filename: str
    # Título da faixa (extraído da tag ID3 ou derivado do nome do arquivo)
    title: str
    # Artista da música
    artist: str
    # Nome do álbum ou nome da pasta mãe
    album: str
    # Duração total em milissegundos (ex: 215000)
    duration_ms: int
    # Duração formatada para exibição visual (ex: '03:35')
    duration_str: str
    # Tamanho do arquivo em bytes no disco
    file_size: int
    # Caminho relativo da subpasta em relação à pasta raiz (ex: 'Rock\\Queen')
    folder_relative: str
    # Extensão do arquivo em minúsculo (ex: '.mp3', '.flac', '.wav')
    extension: str

    def matches_query(self, query: str) -> bool:
        """
        Verifica se a faixa bate com o termo de busca digitado pelo usuário.
        Busca case-insensitive em: Título, Artista, Álbum, Nome do Arquivo e Pasta.
        """
        q = query.lower().strip()
        # Se a busca estiver vazia, todas as faixas passam no filtro
        if not q:
            return True

        return (
            q in self.title.lower()
            or q in self.artist.lower()
            or q in self.album.lower()
            or q in self.filename.lower()
            or q in self.folder_relative.lower()
        )


# =============================================================================
# BLOCO 2: Modelo de Nó da Hierarquia de Pastas (FolderNode)
# =============================================================================

@dataclass
class FolderNode:
    """
    Representa uma pasta na árvore de diretórios exibida no painel lateral.
    Permite navegação hierárquica em estilo árvore (pastas e subpastas).
    """
    # Nome visível da pasta (ex: 'Pink Floyd' ou 'The Dark Side of the Moon')
    name: str
    # Caminho absoluto no disco
    full_path: str
    # Caminho relativo a partir da biblioteca raiz
    relative_path: str
    # Total de músicas contidas nesta pasta e em todas as suas subpastas
    track_count: int
    # Lista de subdiretórios filhos (estrutura em árvore)
    children: List["FolderNode"]
