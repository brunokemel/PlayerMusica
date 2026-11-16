"""
Scanner Assíncrono de Biblioteca de Áudio para o PlayMusica.
Utiliza QThread para indexar pastas e ler metadados em segundo plano,
garantindo que a interface permaneça 100% responsiva (sem travamentos).
"""

import os
from typing import Dict, List, Set
from PySide6.QtCore import QThread, Signal

from core.models import FolderNode, Track
from core.tag_reader import AudioTagReader


# =============================================================================
# BLOCO 1: Extensões de Arquivo de Áudio Suportadas
# =============================================================================

SUPPORTED_EXTENSIONS: Set[str] = {
    ".mp3",
    ".wav",
    ".flac",
    ".ogg",
    ".oga",
    ".m4a",
    ".aac",
    ".wma",
}


# =============================================================================
# BLOCO 2: Construção da Árvore de Pastas (Hierarquia Visual)
# =============================================================================

def build_folder_tree(root_dir: str, tracks: List[Track]) -> FolderNode:
    """
    Constrói a árvore de nós `FolderNode` espelhando a estrutura física de diretórios
    onde as faixas foram encontradas.
    Calcula a contagem de faixas para cada pasta e subpasta.
    """
    root_norm = os.path.normpath(root_dir)
    root_node = FolderNode(
        name=os.path.basename(root_norm) or root_norm,
        full_path=root_norm,
        relative_path="",
        track_count=len(tracks),
        children=[],
    )

    # Dicionário auxiliar para localizar nós existentes por caminho relativo
    node_map: Dict[str, FolderNode] = {"": root_node}

    # 1. Cria nós intermediários para cada pasta e subpasta
    for track in tracks:
        rel = track.folder_relative
        if not rel:
            continue

        parts = rel.split(os.sep)
        current_rel = ""
        parent_node = root_node

        for part in parts:
            current_rel = os.path.join(current_rel, part) if current_rel else part
            if current_rel not in node_map:
                full_path = os.path.join(root_norm, current_rel)
                new_node = FolderNode(
                    name=part,
                    full_path=full_path,
                    relative_path=current_rel,
                    track_count=0,
                    children=[],
                )
                parent_node.children.append(new_node)
                node_map[current_rel] = new_node
            parent_node = node_map[current_rel]

    # 2. Incrementa a contagem de faixas em cada nó correspondente
    for track in tracks:
        rel = track.folder_relative
        parts = rel.split(os.sep) if rel else []
        current_rel = ""
        for part in parts:
            current_rel = os.path.join(current_rel, part) if current_rel else part
            if current_rel in node_map and current_rel != "":
                node_map[current_rel].track_count += 1

    return root_node


# =============================================================================
# BLOCO 3: Thread de Escaneamento da Biblioteca (LibraryScannerWorker)
# =============================================================================

class LibraryScannerWorker(QThread):
    """
    Worker que roda em uma thread dedicada do sistema operacional.
    Varre recursivamente o sistema de arquivos buscando músicas e emitindo
    sinais Qt para atualizar a barra de progresso da interface.
    """

    # Sinais emitidos pela thread para a interface:
    # 1. progress: emite (total_faixas_encontradas, nome_da_pasta_atual)
    progress = Signal(int, str)
    # 2. finished: emite (lista_de_faixas, raiz_da_arvore_de_pastas)
    finished = Signal(list, object)
    # 3. error: emite mensagem caso a pasta não possa ser lida
    error = Signal(str)

    def __init__(self, root_directory: str) -> None:
        super().__init__()
        self.root_directory = os.path.normpath(root_directory)

    def run(self) -> None:
        """
        Executado automaticamente ao chamar worker.start().
        Percorre pastas com os.walk, extrai metadados e monta a lista de Track.
        """
        tracks: List[Track] = []
        track_id = 1

        # Validação: verifica se a pasta existe antes de começar
        if not os.path.exists(self.root_directory) or not os.path.isdir(self.root_directory):
            self.error.emit(f"Diretório não encontrado: {self.root_directory}")
            self.finished.emit([], FolderNode("Biblioteca", self.root_directory, "", 0, []))
            return

        try:
            # Varredura recursiva de diretórios
            for root, dirs, files in os.walk(self.root_directory):
                # Se o usuário trocou de pasta enquanto esta varredura ocorria, cancela graciosamente
                if self.isInterruptionRequested():
                    return

                rel_dir = os.path.relpath(root, self.root_directory)
                if rel_dir == ".":
                    rel_dir = ""

                # Notifica a interface sobre o progresso atual
                folder_display = os.path.basename(root) or root
                self.progress.emit(len(tracks), folder_display)

                # Filtra apenas extensões de áudio suportadas
                audio_files = [f for f in files if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS]
                audio_files.sort(key=lambda s: s.lower())

                for fname in audio_files:
                    if self.isInterruptionRequested():
                        return

                    full_path = os.path.join(root, fname)
                    try:
                        file_size = os.path.getsize(full_path)
                    except OSError:
                        file_size = 0

                    # Extrai título, artista, álbum e duração
                    metadata = AudioTagReader.read_metadata(full_path)
                    ext = os.path.splitext(fname)[1].lower()

                    # Cria o objeto de dados da faixa
                    track = Track(
                        id=track_id,
                        file_path=full_path,
                        filename=fname,
                        title=metadata["title"],
                        artist=metadata["artist"],
                        album=metadata["album"],
                        duration_ms=metadata["duration_ms"],
                        duration_str=metadata["duration_str"],
                        file_size=file_size,
                        folder_relative=rel_dir,
                        extension=ext,
                    )
                    tracks.append(track)
                    track_id += 1

            # Constrói a árvore de diretórios após escanear todas as faixas
            folder_tree = build_folder_tree(self.root_directory, tracks)
            # Emite resultado final de sucesso para a interface
            self.finished.emit(tracks, folder_tree)

        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit([], FolderNode("Biblioteca", self.root_directory, "", 0, []))
